"""R01–R07 HTTP contract, snapshot safety and real MySQL/oracle regression."""
from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock

import pymysql
import pytest
from werkzeug.datastructures import MultiDict
from werkzeug.exceptions import BadRequest
from clinic_app import create_app, analytics
from tools.analytics_oracle import expected, seed_rows


@pytest.fixture
def api():
    return create_app({'TESTING': True, 'SECRET_KEY': 'analytics-test', 'CSRF_ENABLED': False}).test_client()


@pytest.mark.parametrize('path', [
    '/R00', '/r01', '/R08',
    '/R01?start=2026-02-30', '/R01?start=', '/R01?start=2026-1-01',
    '/R01?start=2026-10-15&end=2026-10-15',
    '/R01?start=2026-10-16&end=2026-10-15',
    '/R01?start=2026-10-14T00:00:00', '/R01?start=2026-10-14%27%3BDROP+TABLE+benh',
    '/R01?age_group=4', '/R01?age_group=0+OR+1=1',
    '/R01?start=2026-07-01&start=2026-08-01',
    '/R02?age_group=0', '/R02?patient_id=wrong',
    '/R06?threshold=-1', '/R06?threshold=36501', '/R06?threshold=1.5',
    '/R06?threshold=', '/R06?threshold=1e2', '/R06?threshold=true',
    '/R06?as_of=2026-02-29', '/R06?start=2026-07-01',
    '?threshold=-1', '?as_of=bad', '?unexpected=x',
])
def test_invalid_request_never_opens_database(api, monkeypatch, path):
    def forbidden():
        pytest.fail('Invalid request reached MySQL')
    monkeypatch.setattr(analytics, 'get_db', forbidden)
    response = api.get('/api/analytics' + path)
    assert response.status_code == (404 if path in ('/R00','/r01','/R08') else 400)
    assert response.is_json and response.json['error']


@pytest.mark.parametrize('value', [True, False, 1.5, None, -1, 36501])
def test_threshold_service_rejects_non_integer_and_out_of_range(value):
    with pytest.raises(BadRequest):
        analytics.filters({'threshold': value}, 'R06')


def test_dates_leap_boundary_and_independent_filters():
    assert analytics.filters({'start':'2004-02-29','end':'2004-03-01'},'R01')['start'] == '2004-02-29'
    assert analytics.filters({'as_of':'9999-12-31','threshold':'0'},'R06')['threshold'] == 0
    assert analytics.filters({'threshold':'36500'},'R06')['threshold'] == 36500
    assert analytics.filters({'age_group':'-1'},'R01')['age_group'] == -1


def test_decimal_null_and_date_json_contract():
    rows = analytics.serialize([dict(tb_tong=Decimal('9007199254740993.01'),
        tb_tien_thuoc=None, so_dot_tinh=Decimal(3), ngay=date(2004,2,29))])
    assert rows == [dict(tb_tong='9007199254740993.01',tb_tien_thuoc=None,
                         so_dot_tinh=3,ngay='2004-02-29')]
    with pytest.raises(ValueError):
        analytics.serialize([{'so_dot':Decimal('1.5')}])


def test_chart_groups_derive_only_from_filtered_rows():
    values = analytics.filters({})
    rows = [dict(ma_benh='B001',ten_benh='A'),dict(ma_benh='B001',ten_benh='A'),
            dict(ma_benh='B002',ten_benh='B')]
    assert [r['so_dot'] for r in analytics.payload('R05',rows,values)['chart_groups']] == [2,1]
    r6 = analytics.payload('R06',[dict(nhom_ngay='30+'),dict(nhom_ngay='14–29')],values)
    assert [r['so_dot'] for r in r6['chart_groups']] == [0,0,1,1]
    age = analytics.payload('R01',[dict(thu_tu_nhom=0),dict(thu_tu_nhom=3)],dict(values,age_group=3))
    assert age['rows'] == [dict(thu_tu_nhom=3)] and age['row_count'] == 1


@pytest.mark.parametrize('failed', [False, True])
def test_single_snapshot_and_rollback_on_success_or_query_failure(monkeypatch, failed):
    db = MagicMock()
    cursor = db.cursor.return_value.__enter__.return_value
    cursor.fetchall.return_value = []
    def execute(sql, params=()):
        if failed and sql.startswith('WITH first_exam'):
            raise pymysql.OperationalError(2013, 'private-host-secret')
    cursor.execute.side_effect = execute
    monkeypatch.setattr(analytics, 'get_db', lambda: db)
    app = create_app({'TESTING':True,'SECRET_KEY':'test'})
    with app.app_context():
        if failed:
            with pytest.raises(pymysql.OperationalError):
                analytics.build(analytics.filters({}))
        else:
            result = analytics.build(analytics.filters({}))
            assert list(result['reports']) == list(analytics.REPORTS)
            assert all(v['rows']==[] for v in result['reports'].values())
    calls = cursor.execute.call_args_list
    assert calls[0].args[0] == 'SET TRANSACTION ISOLATION LEVEL REPEATABLE READ'
    assert calls[1].args[0] == 'START TRANSACTION WITH CONSISTENT SNAPSHOT, READ ONLY'
    db.rollback.assert_called_once()
    db.commit.assert_not_called()
    for call in calls[2:]:
        assert '@tu' not in call.args[0] and '@den' not in call.args[0]
        assert len(call.args) == 2


def test_no_nested_write_transaction(monkeypatch):
    from flask import g
    app = create_app({'TESTING':True,'SECRET_KEY':'test'})
    with app.app_context():
        g.in_transaction = True
        with pytest.raises(RuntimeError):
            analytics.build(analytics.filters({}))


@pytest.mark.parametrize('error,status', [
    (pymysql.OperationalError(2003,'private-host password'),503),
    (pymysql.ProgrammingError(1146,'private schema'),500),
])
def test_database_failure_json_redacts_details(api, monkeypatch, error, status):
    def failed():
        raise error
    monkeypatch.setattr(analytics, 'get_db', failed)
    response = api.get('/api/analytics/R01')
    assert response.status_code == status and response.is_json
    assert 'private' not in response.get_data(as_text=True)


def test_get_only(api):
    response = api.post('/api/analytics/R01')
    assert response.status_code == 405


@pytest.mark.parametrize('start,end,as_of,threshold', [
    ('2026-07-01','2026-10-15','2026-10-14',14),
    ('2026-07-01','2026-08-01','2026-07-31',0),
    ('2026-08-01','2026-09-01','2026-08-31',7),
    ('2026-09-01','2026-10-01','2026-09-30',14),
    ('2026-10-01','2026-10-15','2026-10-14',30),
    ('2026-10-14','2026-10-15','2026-10-14',0),
    ('1999-01-01','1999-02-01','1999-01-31',0),
])
def test_mysql_api_all_columns_match_independent_seed_oracle(client,start,end,as_of,threshold):
    wanted = expected(seed_rows(),start,end,as_of,threshold)
    response = client.get('/api/analytics',query_string=dict(start=start,end=end,as_of=as_of,threshold=threshold))
    assert response.status_code == 200
    result = response.json['reports']
    for report_id, rows in wanted.items():
        # Explicit contract serializer: unlike SQL oracle canonical(), money stays string.
        reference = []
        for row in rows:
            item = {}
            for key, value in row.items():
                if key in analytics.MONEY and value is not None:
                    item[key] = format(Decimal(value), '.2f')
                elif isinstance(value, date):
                    item[key] = value.isoformat()
                elif isinstance(value, Decimal):
                    assert value == int(value)
                    item[key] = int(value)
                else:
                    item[key] = value
            reference.append(item)
        assert result[report_id]['rows'] == reference, report_id
        assert result[report_id]['row_count'] == len(reference)
        params = dict(as_of=as_of,threshold=threshold) if report_id=='R06' else dict(start=start,end=end)
        single = client.get('/api/analytics/'+report_id,query_string=params)
        assert single.status_code == 200
        assert single.json == result[report_id]


def test_mysql_age_group_filters_result_and_preserves_all_columns(client):
    all_rows = client.get('/api/analytics/R01').json['rows']
    for group in (-1,0,1,2,3):
        response = client.get('/api/analytics/R01',query_string={'age_group':group})
        assert response.status_code == 200
        assert response.json['rows'] == [r for r in all_rows if r['thu_tu_nhom']==group]


def test_mysql_empty_and_zero_doctors_contract(client):
    response = client.get('/api/analytics',query_string={'start':'1999-01-01','end':'1999-02-01','as_of':'1999-01-31'})
    reports = response.json['reports']
    assert len(reports['R03']['rows']) == 10
    assert all(r['so_lan_kham']==r['so_dot']==r['so_benh_nhan']==0 for r in reports['R03']['rows'])
    assert all(reports[k]['rows']==[] for k in ('R01','R02','R04','R05','R06','R07'))


# Reuse Quyen's adversarial data inside its rollback-only fixture; no fixture commit.
from test_quyen_analytics import analytics_db, edge_db  # noqa: E402,F401
from tools.analytics_sql import run as contract_run  # noqa: E402


@pytest.mark.parametrize('start,end,as_of,threshold', [
    ('2004-02-28','2004-03-01','2004-02-29',0),
    ('2004-03-01','2004-03-03','2004-03-02',0),
    ('2004-03-01','2004-03-10','2004-03-06',0),
])
def test_bound_service_sql_matches_contract_with_adversarial_data(edge_db,start,end,as_of,threshold):
    wanted = contract_run(edge_db,start,end,as_of,threshold)
    values = analytics.filters(dict(start=start,end=end,as_of=as_of,threshold=threshold))
    with edge_db.cursor() as cursor:
        for name, source in analytics.sql_queries().items():
            sql, params = analytics.bind(source,values)
            cursor.execute(sql,params)
            actual = analytics.payload(name,list(cursor.fetchall()),values)
            assert actual['rows'] == analytics.serialize(wanted[name])
    # Read snapshot lifecycle is tested independently; this fixture remains uncommitted.
