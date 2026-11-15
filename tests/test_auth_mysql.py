"""Optional authentication migration and actual account operations on disposable MySQL."""
import os
import pytest
from clinic_app import create_app, auth
from clinic_app.db import fetch_one, fetch_all, get_db


def test_real_mysql_account_lifecycle():
    if os.getenv('RUN_MYSQL_TESTS') != '1':
        pytest.skip('Requires disposable MySQL')
    app=create_app({'TESTING':True,'SECRET_KEY':'disposable-auth-integration'})
    assert app.config['DB_NAME'].endswith('_test')
    with app.app_context():
        if fetch_one("SELECT COUNT(*) AS n FROM information_schema.tables WHERE table_schema=DATABASE() AND table_name='app_user'")['n']:
            pytest.skip('Refuse to overwrite existing authentication table')
        doctors=fetch_all('SELECT ma_bac_si FROM bac_si ORDER BY ma_bac_si LIMIT 2')
        nurses=fetch_all('SELECT ma_y_ta FROM y_ta ORDER BY ma_y_ta LIMIT 2')
    password='six123'
    runner=app.test_cli_runner()
    try:
        result=runner.invoke(args=['init-auth','--username','test_admin'],input=password+'\n'+password+'\n')
        assert result.exit_code==0, result.output
        assert runner.invoke(args=['init-auth','--username','other_admin'],input=password+'\n'+password+'\n').exit_code!=0
        client=app.test_client()
        def token():
            with client.session_transaction() as session:
                session['_csrf']='mysql-test-csrf'
            return 'mysql-test-csrf'
        def login(username):
            return client.post('/auth/login',data={'username':username,'password':password,'csrf_token':token()})
        assert login('test_admin').status_code==303
        assert client.get('/auth/users').status_code==200
        # Upgrade an existing four-role database without changing credentials.
        with app.app_context():
            before=fetch_one("SELECT password_hash,version FROM app_user WHERE username='test_admin'")
            db=get_db()
            with db.cursor() as cur:
                cur.execute("""ALTER TABLE app_user DROP CHECK ck_app_user_role,
                    ADD CONSTRAINT ck_app_user_role CHECK (
                    (role IN ('admin','reception') AND doctor_id IS NULL AND nurse_id IS NULL) OR
                    (role='doctor' AND doctor_id IS NOT NULL AND nurse_id IS NULL) OR
                    (role='nurse' AND nurse_id IS NOT NULL AND doctor_id IS NULL))""")
            db.commit()
        for _ in range(2):
            result=runner.invoke(args=['upgrade-auth'])
            assert result.exit_code==0, result.output
        with app.app_context():
            assert fetch_one("SELECT password_hash,version FROM app_user WHERE username='test_admin'")==before
        assert client.post('/auth/users',data=dict(username='class_viewer',password=password,role='viewer',active='1',csrf_token=token())).status_code==303
        readers=[app.test_client(),app.test_client()]
        for reader in readers:
            reader.get('/auth/login')
            with reader.session_transaction() as session: rt=session['_csrf']
            assert reader.post('/auth/login',data=dict(username='class_viewer',password=password,csrf_token=rt)).status_code==303
            assert reader.get('/patients').status_code==200
            assert reader.get('/reports').status_code==200
            assert reader.get('/reports/salaries?month=2026-10&format=json').status_code==200
            assert reader.post('/patients/new',data={'csrf_token':rt}).status_code==403
            assert reader.get('/auth/users').status_code==403
        readers[0].get('/patients')
        with readers[0].session_transaction() as session: rt=session['_csrf']
        assert readers[0].post('/auth/logout',data={'csrf_token':rt}).status_code==303
        assert readers[1].get('/patients').status_code==200
        for role in ('reception','doctor','nurse'):
            data=dict(username='test_'+role,password=password,role=role,active='1',csrf_token=token(),
                      doctor_id=doctors[0]['ma_bac_si'],nurse_id=nurses[0]['ma_y_ta'])
            assert client.post('/auth/users',data=data).status_code==303
        with app.app_context():
            admin=fetch_one("SELECT * FROM app_user WHERE username='test_admin'")
            assert admin['password_hash']!=password
            nurse=fetch_one("SELECT * FROM app_user WHERE username='test_nurse'")
        assert client.post('/auth/users',data=dict(id=admin['id'],username='test_admin',role='reception',active='1',csrf_token=token())).status_code==422
        # Log in to a second session, then revoke it through the admin UI.
        other=app.test_client(); other.get('/auth/login')
        with other.session_transaction() as session: t=session['_csrf']
        assert other.post('/auth/login',data=dict(username='test_nurse',password=password,csrf_token=t)).status_code==303
        assert other.get('/patients').status_code==200
        assert client.post('/auth/users',data=dict(id=nurse['id'],username='test_nurse',role='nurse',nurse_id=nurses[0]['ma_y_ta'],csrf_token=token())).status_code==303
        assert other.get('/patients').status_code==302
        assert client.post('/auth/logout',data={'csrf_token':token()}).status_code==303
        assert login('test_reception').status_code==303
        assert client.get('/visits/new').status_code==200
        assert client.get('/reports/revenue?format=json').status_code==403
        assert client.get('/auth/users').status_code==403
        # Reception intake -> doctor examination -> nurse support -> reception close.
        patient = dict(ma_benh_nhan='AUTHP1',cccd='999900008887',ho_ten='Auth integration',ngay_sinh='1980-01-01',dia_chi='Test',so_dien_thoai='0900000001',csrf_token=token())
        assert client.post('/patients/new',data=patient).status_code==303
        assert client.post('/visits/new',data=dict(ma_luot='AUTHL1',ma_benh_nhan='AUTHP1',ngay_vao_vien='2002-01-01',csrf_token=token())).status_code==303
        assert client.post('/visits/AUTHL1/close',data=dict(ngay_ra_vien='2002-01-01',csrf_token=token())).status_code==409
        assert client.post('/auth/logout',data={'csrf_token':token()}).status_code==303
        assert login('test_doctor').status_code==303
        with app.app_context():
            disease=fetch_one('SELECT ma_benh FROM benh ORDER BY ma_benh LIMIT 1')['ma_benh']
        assert client.post('/visits/AUTHL1/examinations/new',data=dict(ma_dot='AUTHD1',ma_lan_kham='AUTHK1',che_do_dot='new',ma_benh=disease,ma_bac_si=doctors[0]['ma_bac_si'],ngay_kham='2002-01-01',tien_kham_chua='100000',ket_luan='Test only',csrf_token=token())).status_code==303
        assert client.post('/auth/logout',data={'csrf_token':token()}).status_code==303
        assert login('test_admin').status_code==303
        # Re-enable nurse for the handoff.
        assert client.post('/auth/users',data=dict(id=nurse['id'],username='test_nurse',role='nurse',nurse_id=nurses[0]['ma_y_ta'],active='1',csrf_token=token())).status_code==303
        assert client.post('/auth/logout',data={'csrf_token':token()}).status_code==303
        assert login('test_nurse').status_code==303
        assert client.post('/visits/AUTHL1/support',data=dict(ma_y_ta=nurses[0]['ma_y_ta'],ngay_ho_tro='2002-01-01',noi_dung_ho_tro='Test only',csrf_token=token())).status_code==303
        assert client.post('/auth/logout',data={'csrf_token':token()}).status_code==303
        assert login('test_reception').status_code==303
        assert client.post('/visits/AUTHL1/close',data=dict(ngay_ra_vien='2002-01-01',csrf_token=token())).status_code==303
        assert client.post('/auth/logout',data={'csrf_token':token()}).status_code==303
        # Persistent account lockout survives new clients and correct credentials.
        for _ in range(5):
            assert client.post('/auth/login',data=dict(username='test_doctor',password='wrong',csrf_token=token())).status_code==401
        assert login('test_doctor').status_code==401
        with app.app_context():
            row=fetch_one("SELECT failed_logins,locked_until FROM app_user WHERE username='test_doctor'")
            assert row['failed_logins']==5 and row['locked_until'] is not None
        # Delete an account, revoke an existing session, and preserve clinical staff.
        auth._attempts.clear()
        assert login('test_admin').status_code==303
        victim=app.test_client(); victim.get('/auth/login')
        with victim.session_transaction() as session: vt=session['_csrf']
        assert victim.post('/auth/login',data=dict(username='test_reception',password=password,csrf_token=vt)).status_code==303
        with app.app_context():
            target=fetch_one("SELECT id FROM app_user WHERE username='test_reception'")['id']
            staff_before=fetch_one('SELECT COUNT(*) AS n FROM y_ta')['n']
        assert client.post(f'/auth/users/{target}/delete',data=dict(confirm_username='wrong',csrf_token=token())).status_code==422
        assert client.post(f'/auth/users/{target}/delete',data=dict(confirm_username='test_reception',csrf_token=token())).status_code==303
        assert victim.get('/patients').status_code==302
        assert client.post(f"/auth/users/{admin['id']}/delete",data=dict(confirm_username='test_admin',csrf_token=token())).status_code==422
        assert client.post(f"/auth/users/{nurse['id']}/delete",data=dict(confirm_username='test_nurse',csrf_token=token())).status_code==303
        with app.app_context():
            assert fetch_one('SELECT COUNT(*) AS n FROM y_ta')['n']==staff_before
            assert fetch_one('SELECT id FROM app_user WHERE id=%s',(target,)) is None
    finally:
        with app.app_context():
            db=get_db()
            with db.cursor() as cur:
                cur.execute("DELETE FROM ho_tro WHERE ma_luot='AUTHL1'")
                cur.execute("DELETE FROM lan_kham_benh WHERE ma_lan_kham='AUTHK1'")
                cur.execute("DELETE FROM dot_dieu_tri WHERE ma_dot='AUTHD1'")
                cur.execute("DELETE FROM luot_den_kham WHERE ma_luot='AUTHL1'")
                cur.execute("DELETE FROM benh_nhan WHERE ma_benh_nhan='AUTHP1'")
                cur.execute('DROP TABLE IF EXISTS app_user')
            db.commit()
