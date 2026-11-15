"""Authentication and role boundaries exercised through Flask's real request hooks."""
from contextlib import contextmanager
import pytest
from werkzeug.security import generate_password_hash
from clinic_app import create_app, auth


@pytest.fixture
def secured(monkeypatch):
    users = {
        i: dict(id=i, username=role, role=role, doctor_id='BS01' if role=='doctor' else None,
                nurse_id='YT01' if role=='nurse' else None, active=1, version=1,
                password_hash=generate_password_hash('correct-password-123'), locked=0)
        for i, role in enumerate(auth.ROLES, 1)
    }
    writes = []
    def read(sql, args=()):
        if 'WHERE username=' in sql:
            return next((u for u in users.values() if u['username']==args[0]), None)
        if 'FROM app_user WHERE id=' in sql:
            return users.get(args[0])
        if 'ma_bac_si FROM' in sql:
            return {'ma_bac_si': 'BS02' if args[0]=='foreign' else 'BS01'}
        return None
    monkeypatch.setattr(auth, 'fetch_one', read)
    class Cursor:
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def execute(self, sql, args=()):
            self.sql, self.args = sql, args
            writes.append((sql,args))
            if sql.startswith('DELETE FROM app_user'):
                users.pop(args[0], None)
        def fetchall(self): return list(users.values())
        def fetchone(self):
            if 'COUNT(*)' in self.sql:
                return {'n': sum(u['role']=='admin' and u['active'] and u['id']!=self.args[0] for u in users.values())}
            return users.get(self.args[0])
    class DB:
        def cursor(self): return Cursor()
    @contextmanager
    def tx(): yield DB()
    monkeypatch.setattr(auth, 'transaction', tx)
    auth._attempts.clear()
    app = create_app({'TESTING': True, 'SECRET_KEY': 'test-only-auth-secret'})
    return app, users, writes


def signin(client, user_id):
    with client.session_transaction() as s:
        s['user_id'] = user_id
        s['user_version'] = 1
        s['_csrf'] = 'valid-token'


def test_login_and_logout(secured):
    app, users, writes = secured
    client = app.test_client()
    assert client.get('/patients').status_code == 302
    assert client.get('/api/analytics/R07').status_code == 401
    assert client.get('/auth/login').status_code == 200
    with client.session_transaction() as s:
        token = s['_csrf']
        s['old_session_value'] = 'must-disappear'
    assert client.post('/auth/login', data={'username':'admin','password':'correct-password-123'}).status_code == 400
    response = client.post('/auth/login', data={'username':'admin','password':'wrong','csrf_token':token})
    assert response.status_code == 401
    response = client.post('/auth/login', data={'username':'admin','password':'correct-password-123','csrf_token':token})
    assert response.status_code == 303
    with client.session_transaction() as s:
        assert s['user_id'] == 1 and 'old_session_value' not in s and '_csrf' not in s
    assert client.get('/auth/logout').status_code in (403,404,405)
    assert client.post('/auth/logout').status_code == 400
    client.get('/auth/login')
    with client.session_transaction() as s: s['_csrf']='logout-token'
    assert client.post('/auth/logout', data={'csrf_token':'logout-token'}).status_code == 303
    assert client.get('/patients').status_code == 302


@pytest.mark.parametrize('role,uid', [('admin',1),('reception',2),('doctor',3),('nurse',4)])
@pytest.mark.parametrize('path,endpoint,args,allowed', [
    ('/patients','clinic.listing',{'slug':'patients'}, {'admin','reception','doctor','nurse'}),
    ('/doctors','clinic.listing',{'slug':'doctors'}, {'admin'}),
    ('/nurses','clinic.listing',{'slug':'nurses'}, {'admin'}),
    ('/patients/new','clinic.create',{'slug':'patients'}, {'admin','reception'}),
    ('/patients/BN01/edit','clinic.edit',{'slug':'patients','record_id':'BN01'}, {'admin','reception'}),
    ('/visits/new','clinical.new_visit',{}, {'admin','reception','doctor'}),
    ('/visits/L01/examinations/new','clinical.new_exam',{'visit_id':'L01'}, {'admin','doctor'}),
    ('/visits/L01/support','clinical.support',{'visit_id':'L01'}, {'admin','nurse'}),
    ('/visits/L01/close','clinical.close_visit',{'visit_id':'L01'}, {'admin','reception'}),
    ('/treatments/D01/cure','clinical.cure',{'episode_id':'D01'}, {'admin','doctor'}),
    ('/examinations/K01/prescription','clinical.prescription',{'exam_id':'K01'}, {'admin','doctor'}),
    ('/reports/revenue','clinic.reports',{'report':'revenue'}, {'admin'}),
    ('/reports/salaries?format=json','clinic.reports',{'report':'salaries'}, {'admin'}),
    ('/api/analytics/R07','analytics.one_report',{'report_id':'R07'}, {'admin'}),
    ('/auth/users','auth.users',{}, {'admin'}),
])
def test_roles_on_direct_urls(secured, role, uid, path, endpoint, args, allowed):
    app, _, _ = secured
    # Replace only view body: real routing, authorization, session and CSRF hooks still execute.
    app.view_functions[endpoint] = lambda **kwargs: 'reached-view'
    client=app.test_client(); signin(client,uid)
    assert client.get(path).status_code == (200 if role in allowed else 403)
    if endpoint in ('clinic.create','clinic.edit','clinical.new_visit','clinical.new_exam','clinical.support','clinical.close_visit','clinical.cure','clinical.prescription','auth.users'):
        data={'csrf_token':'valid-token','ma_bac_si':'BS01','che_do_dot':'new','ma_y_ta':'YT01'}
        assert client.post(path,data=data).status_code == (200 if role in allowed else 403)


def test_ownership_cannot_be_forged(secured):
    app, _, _ = secured
    for endpoint in ('clinical.prescription','clinical.cure','clinical.new_exam','clinical.support'):
        app.view_functions[endpoint]=lambda **kw: 'reached-view'
    client=app.test_client(); signin(client,3)
    for path in ('/examinations/foreign/prescription','/treatments/foreign/cure'):
        assert client.get(path).status_code==403
        assert client.post(path,data={'csrf_token':'valid-token'}).status_code==403
    assert client.post('/visits/L01/examinations/new', data={'csrf_token':'valid-token','che_do_dot':'new','ma_bac_si':'BS02'}).status_code==403
    assert client.post('/visits/L01/examinations/new', data={'csrf_token':'valid-token','che_do_dot':'existing','ma_dot':'foreign'}).status_code==403
    signin(client,4)
    assert client.get('/visits/L01/support?ma_y_ta=YT02').status_code==403
    assert client.post('/visits/L01/support',data={'csrf_token':'valid-token','ma_y_ta':'YT02'}).status_code==403
    signin(client,1)
    assert client.get('/examinations/foreign/prescription').status_code==200


@pytest.mark.parametrize('change', ['active','version'])
def test_account_changes_invalidate_old_sessions(secured,change):
    app, users, _ = secured
    client=app.test_client(); signin(client,3)
    users[3][change] = 0 if change=='active' else 2
    assert client.get('/patients').status_code==302


def test_lock_and_ip_limit(secured):
    app,users,_=secured
    client=app.test_client(); client.get('/auth/login')
    with client.session_transaction() as s: token=s['_csrf']
    users[1]['locked']=1
    for _ in range(20):
        assert client.post('/auth/login',data={'username':'admin','password':'correct-password-123','csrf_token':token}).status_code==401
    assert client.post('/auth/login',data={'username':'admin','password':'correct-password-123','csrf_token':token}).status_code==429


def test_auth_cannot_be_disabled_outside_testing():
    with pytest.raises(RuntimeError):
        create_app({'SECRET_KEY':'test-only', 'AUTH_ENABLED':False})


def test_role_ui(secured, monkeypatch):
    app, _, _ = secured
    from clinic_app import services
    from clinic_app.entities import ENTITIES
    monkeypatch.setattr(services, 'list_records', lambda *a: ([], 0))
    client=app.test_client(); signin(client,3)
    body=client.get('/patients').get_data(as_text=True)
    assert 'Đăng xuất' in body and 'Tiếp nhận / khám' in body
    assert 'Báo cáo</a>' not in body and '+ Thêm bệnh nhân' not in body
    signin(client,2)
    monkeypatch.setattr(__import__('clinic_app.clinical_routes',fromlist=['patient_choices']), 'patient_choices', lambda: [])
    body=client.get('/visits/new').get_data(as_text=True)
    assert 'Tiếp nhận lượt mới' in body and 'Kết luận' not in body


@pytest.mark.parametrize('uid,status', [(1,303),(2,403),(3,403),(4,403)])
def test_delete_account_requires_admin(secured,uid,status):
    app,users,writes=secured
    client=app.test_client();signin(client,uid)
    response=client.post('/auth/users/3/delete',data={'csrf_token':'valid-token','confirm_username':'doctor'})
    assert response.status_code==status
    assert (3 not in users)==(uid==1)
    assert all('DELETE FROM bac_si' not in sql and 'DELETE FROM y_ta' not in sql for sql,_ in writes)


def test_delete_confirmation_csrf_and_current_admin(secured):
    app,users,_=secured
    client=app.test_client();signin(client,1)
    assert client.post('/auth/users/3/delete',data={'confirm_username':'doctor'}).status_code==400
    assert client.post('/auth/users/3/delete',data={'csrf_token':'valid-token','confirm_username':'wrong'}).status_code==422
    assert client.post('/auth/users/1/delete',data={'csrf_token':'valid-token','confirm_username':'admin'}).status_code==422
    assert client.post('/auth/users/999/delete',data={'csrf_token':'valid-token','confirm_username':'missing'}).status_code==404
    assert 3 in users and 1 in users


def test_delete_revokes_existing_session(secured):
    app,users,_=secured
    former=app.test_client();signin(former,3)
    admin=app.test_client();signin(admin,1)
    assert admin.post('/auth/users/3/delete',data={'csrf_token':'valid-token','confirm_username':'doctor'}).status_code==303
    assert former.get('/patients').status_code==302


def test_delete_keeps_last_active_admin_after_concurrent_change(secured):
    app,users,_=secured
    users[5]=dict(users[1],id=5,username='second_admin')
    @app.before_request
    def revoked_during_request(): users[1]['active']=0
    client=app.test_client();signin(client,1)
    assert client.post('/auth/users/5/delete',data={'csrf_token':'valid-token','confirm_username':'second_admin'}).status_code==422
    assert 5 in users
