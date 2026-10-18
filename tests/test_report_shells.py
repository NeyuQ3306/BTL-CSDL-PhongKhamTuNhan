"""Week-1 filters must not execute future reporting queries."""
import pytest
from clinic_app import create_app, services


@pytest.fixture
def report_client(monkeypatch):
    def unexpected_query(*args, **kwargs):
        raise AssertionError('Report shells must not query the database')
    monkeypatch.setattr('pymysql.connect', unexpected_query)
    return create_app({'TESTING': True, 'SECRET_KEY': 'report-test-session'}).test_client()


@pytest.mark.parametrize('key', ['diseases', 'salaries', 'revenue'])
def test_monthly_shell_records_month_without_statistics(report_client, key):
    response = report_client.get(f'/reports/{key}?month=2026-10')
    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert 'value="2026-10"' in html
    assert 'Chưa tích hợp dữ liệu báo cáo' in html
    assert 'không phải giá trị 0' in html
    assert 'Chưa có kết quả thống kê.' in html
    assert '0 đ' not in html


@pytest.mark.parametrize('month', ['2026-13', '0000-01', '26-10', '', '<script>'])
def test_bad_month_stays_on_shell_with_error(report_client, month):
    response = report_client.get('/reports/revenue', query_string={'month': month})
    html = response.get_data(as_text=True)
    assert response.status_code == 400
    assert 'id="month-error"' in html
    assert 'Đã chọn tháng' not in html
    assert '<script>' not in html


def test_history_selector_reuses_existing_route(report_client):
    assert report_client.get('/reports/history').status_code == 200
    response = report_client.get('/reports/history?patient_id=BN001')
    assert response.status_code == 302
    assert response.location == '/patients/BN001/history'
    for code in ['', '../BN001', 'x' * 13]:
        assert report_client.get('/reports/history', query_string={'patient_id': code}).status_code == 400


def test_patient_with_no_history_shows_real_empty_state(monkeypatch):
    monkeypatch.setattr(services, 'get_record', lambda *args: {
        'ma_benh_nhan': 'EMPTY01', 'ho_ten': 'Hồ sơ chưa khám', 'so_dien_thoai': '0901234567'})
    monkeypatch.setattr(services, 'visits', lambda *args: [])
    monkeypatch.setattr(services, 'treatments', lambda *args: [])
    monkeypatch.setattr(services, 'examinations', lambda *args: [])
    client = create_app({'TESTING': True, 'SECRET_KEY': 'report-test-session'}).test_client()
    response = client.get('/patients/EMPTY01/history')
    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert 'Không có đợt đang điều trị trong dữ liệu hiện có.' in html
    assert 'chưa có lần khám được ghi nhận' in html
    assert 'chưa có lượt đến khám được ghi nhận' in html
