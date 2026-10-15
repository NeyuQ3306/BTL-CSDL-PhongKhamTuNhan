import pytest
from clinic_app import create_app
from clinic_app.db import fetch_one, get_db, transaction
from clinic_app.entities import ENTITIES
from clinic_app.validation import validate
from tools.audit_seed import audit
from tools.import_seed import import_seed, statements


def payload(slug, key='TEST001'):
    e = ENTITIES[slug]
    values = {f.name: 'Thử nghiệm' for f in e.fields}
    values.update({e.pk: key, 'cmt': '000999888777', 'ngay_sinh': '2000-02-29',
                   'so_dien_thoai': '0901234567', 'tham_nien': '4'})
    return values


@pytest.mark.parametrize('field,value', [('cmt','abc'),('so_dien_thoai','12'),
    ('ngay_sinh','2001-02-29'),('ngay_sinh','2999-01-01'),('ho_ten',''),
    ('ma_benh_nhan','a/b'),('dia_chi','x'*256)])
def test_validation(field, value):
    data = payload('patients'); data[field] = value
    assert field in validate(ENTITIES['patients'], data)[1]


def test_start_without_database(monkeypatch):
    import pymysql
    def disconnected(**kwargs):
        raise pymysql.OperationalError(2003, 'private connection information')
    monkeypatch.setattr(pymysql, 'connect', disconnected)
    app = create_app({'TESTING':True, 'SECRET_KEY':'unit-test'})
    c = app.test_client()
    assert c.get('/health').json == {'status':'ok'}
    assert c.get('/health/db').status_code == 503
    assert b'private connection' not in c.get('/patients').data
    assert c.get('/unknown').status_code == 404
    assert c.post('/patients/new').status_code == 400


def test_sql_split():
    assert list(statements("-- comment ;\nSELECT 'a;b'; SELECT 'it''s';")) == ["SELECT 'a;b'", "SELECT 'it''s'"]


@pytest.mark.parametrize('slug', ['patients','doctors','nurses'])
def test_crud(client, token, slug):
    e = ENTITIES[slug]; values = payload(slug); values['csrf_token'] = token
    assert client.get(f'/{slug}').status_code == 200
    assert client.post(f'/{slug}/new', data=values).status_code == 303
    detail = client.get(f'/{slug}/TEST001')
    assert detail.status_code == 200
    assert 'Thử nghiệm' in detail.get_data(as_text=True)
    assert b'000999888777' in detail.data
    assert client.post(f'/{slug}/new',data=values).status_code == 409
    duplicate = {**values, e.pk:'TEST002'}
    assert client.post(f'/{slug}/new',data=duplicate).status_code == 409
    assert client.post(f'/{slug}/TEST001/edit',data=duplicate).status_code == 422
    values['ho_ten'] = '<script>alert(1)</script>'
    assert client.post(f'/{slug}/TEST001/edit',data=values).status_code == 303
    assert b'<script>' not in client.get(f'/{slug}/TEST001').data
    assert client.get(f'/{slug}/TEST001/delete').status_code == 405
    assert client.post(f'/{slug}/TEST001/delete',data={'csrf_token':token}).status_code == 400
    assert client.post(f'/{slug}/TEST001/delete',data={'csrf_token':token,'confirm_delete':'TEST001'}).status_code == 303
    assert client.get(f'/{slug}/TEST001').status_code == 404


@pytest.mark.parametrize('slug,key', [('patients','BN001'),('doctors','BS001'),('nurses','YT001')])
def test_history_prevents_delete(client, token, slug, key):
    assert client.post(f'/{slug}/{key}/delete',data={'csrf_token':token,'confirm_delete':key}).status_code == 409
    assert client.get(f'/{slug}/{key}').status_code == 200


def test_bad_form_and_queries(client, token):
    data = payload('patients'); data.update(csrf_token=token,ngay_sinh='2001-02-29')
    assert client.post('/patients/new',data=data).status_code == 422
    assert client.get('/patients?page=0').status_code == 400
    assert client.get('/patients?page=abc').status_code == 400
    assert client.get('/patients?q='+'a'*101).status_code == 400
    with client.application.app_context():
        from clinic_app.services import list_records
        for query in ["' OR 1=1 --", '%', '_']:
            assert list_records(ENTITIES['patients'],query)[1] == 0


def test_transaction_rollback_and_connection_lifecycle(app):
    with app.app_context():
        first = get_db()
        with pytest.raises(RuntimeError, match='deliberate'):
            with transaction() as db, db.cursor() as cur:
                cur.execute("INSERT INTO benh(ma_benh,ten_benh) VALUES('TESTROLL','Test rollback')")
                raise RuntimeError('deliberate')
        assert fetch_one("SELECT COUNT(*) n FROM benh WHERE ma_benh='TESTROLL'")['n'] == 0
        with pytest.raises(RuntimeError, match='Nested'):
            with transaction():
                with transaction():
                    pass
    assert not first.open
    with app.app_context():
        assert get_db() is not first
        assert fetch_one('SELECT 1 n')['n'] == 1


def test_read_foundation_and_seed_counts(client, app):
    for path in ['/visits','/treatments','/patients/BN001/history']:
        response = client.get(path)
        assert response.status_code == 200, path
    with app.app_context():
        report = audit()
        assert report['matches_expected_counts'], report
        assert report['total'] == 1144
        # Expose all rule findings in the separate audit, do not silently repair data.
        assert not report['findings']['different_patient']
        from clinic_app.services import visits
        total = sum(v['tong_tien_kham'] for v in visits())
        assert total == fetch_one('SELECT SUM(tien_kham_chua) n FROM lan_kham_benh')['n']
        with pytest.raises(RuntimeError, match='not empty'):
            import_seed(get_db())
        assert audit()['counts'] == report['counts']
