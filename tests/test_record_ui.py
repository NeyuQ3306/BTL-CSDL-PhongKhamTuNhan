"""UI regression cases that do not require a database."""
import pymysql
import pytest
from clinic_app import create_app, services
from clinic_app.entities import ENTITIES


@pytest.mark.parametrize('code', [1217, 1451])
def test_referenced_record_delete_shows_conflict(monkeypatch, code):
    app = create_app({'TESTING': True, 'SECRET_KEY': 'ui-test-session'})
    entity = ENTITIES['patients']
    record = {field.name: 'Hồ sơ mẫu' for field in entity.fields}
    record['ma_benh_nhan'] = 'BN001'
    monkeypatch.setattr(services, 'get_record', lambda *args: record)

    def referenced(*args):
        raise pymysql.IntegrityError(code, 'Referenced record')

    monkeypatch.setattr(services, 'delete_record', referenced)
    client = app.test_client()
    client.get('/patients/new')
    with client.session_transaction() as session:
        token = session['_csrf']
    response = client.post('/patients/BN001/delete', data={
        'csrf_token': token, 'confirm_delete': 'BN001'})
    assert response.status_code == 409
    assert 'Chưa xóa được hồ sơ' in response.get_data(as_text=True)
    assert 'Hồ sơ và dữ liệu liên quan vẫn được giữ nguyên.' in response.get_data(as_text=True)


@pytest.mark.parametrize('url_code', ['BN001', 'bn001'])
def test_invalid_edit_keeps_original_navigation_and_readonly_code(monkeypatch, url_code):
    app = create_app({'TESTING': True, 'SECRET_KEY': 'ui-test-session'})
    record = dict(ma_benh_nhan='BN001', cmt='000123456789', ho_ten='Hồ sơ mẫu',
                  ngay_sinh='2000-01-01', dia_chi='Địa chỉ mẫu', so_dien_thoai='0901234567')
    monkeypatch.setattr(services, 'get_record', lambda *args: record)
    client = app.test_client()
    client.get(f'/patients/{url_code}/edit')
    with client.session_transaction() as session:
        token = session['_csrf']
    response = client.post(f'/patients/{url_code}/edit', data={
        **record, 'ma_benh_nhan': 'CHANGED', 'csrf_token': token})
    html = response.get_data(as_text=True)
    assert response.status_code == 422
    assert 'id="ma_benh_nhan" name="ma_benh_nhan" value="BN001"' in html
    assert 'href="/patients/BN001"' in html
    assert 'href="/patients/CHANGED"' not in html
    assert 'Không được thay đổi mã hồ sơ khi sửa.' in html
