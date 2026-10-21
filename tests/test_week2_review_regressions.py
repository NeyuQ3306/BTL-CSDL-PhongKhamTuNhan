"""Regression cases from Vuong's review of Trung PR #5; no live DB required."""
import os
import re
from datetime import date
from pathlib import Path

import pytest
from flask import render_template
from werkzeug.exceptions import NotFound
from clinic_app import create_app, reports, clinical_routes


@pytest.fixture
def review_app():
    return create_app({'TESTING': True, 'SECRET_KEY': 'review-regression-session'})


@pytest.mark.parametrize('kind', ['diseases', 'salaries', 'revenue'])
def test_invalid_month_json_and_html(review_app, kind):
    client = review_app.test_client()
    response = client.get(f'/reports/{kind}?month=2026-13&format=json')
    assert response.status_code == 400
    assert response.is_json and set(response.json) == {'error'}
    assert 'YYYY-MM' in response.json['error']
    html = client.get(f'/reports/{kind}?month=2026-13')
    assert html.status_code == 400 and html.mimetype == 'text/html'


def test_missing_patient_json(review_app, monkeypatch):
    def missing(_patient):
        raise NotFound('Không tìm thấy bệnh nhân.')
    monkeypatch.setattr(reports, 'history', missing)
    response = review_app.test_client().get('/reports/history?patient_id=MISSING&format=json')
    assert response.status_code == 404
    assert response.json == {'error': 'Không tìm thấy bệnh nhân.'}


def test_invalid_patient_json_before_database(review_app, monkeypatch):
    def unexpected(_patient):
        pytest.fail('Invalid identifier must be rejected before querying')
    monkeypatch.setattr(reports, 'history', unexpected)
    response = review_app.test_client().get('/reports/history?patient_id=bad!&format=json')
    assert response.status_code == 422
    assert response.is_json and set(response.json) == {'error'}


def test_history_title_does_not_contain_clinical_tables(review_app):
    with review_app.test_request_context('/'):
        html = render_template('week1/history.html',
            patient={'ma_benh_nhan': 'TEST', 'ho_ten': 'Test patient'},
            treatments=[], visits=[], examinations=[],
            medicines=[dict(ngay_lap_don='2001-02-01', ten_thuoc='Test medicine',
                            so_luong=2, lieu_dung='Test dose', thanh_tien=5000)], support=[])
    title = re.search(r'<title>(.*?)</title>', html, re.S).group(1)
    assert title == 'Lịch sử Test patient · Phòng khám'
    assert html.count('Test medicine') == 1
    assert html.count('Test dose') == 1


@pytest.mark.skipif(os.getenv('RUN_BROWSER_TESTS') != '1', reason='Chromium opt-in')
def test_prescription_controls_fit_mobile(review_app, monkeypatch):
    from playwright.sync_api import sync_playwright
    # Support both Trung's original form and Vuong's read-only context adapter.
    context = dict(ngay_kham=date(2001, 2, 1), ma_luot='REVIEWL',
                   ma_benh_nhan='REVIEWBN', ho_ten='Review patient')
    monkeypatch.setattr(clinical_routes, 'fetch_one', lambda *args: dict(context))
    monkeypatch.setattr(clinical_routes, 'choices', lambda: dict(
        patients=[], doctors=[], nurses=[], diseases=[], episodes=[],
        medicines=[dict(ma_thuoc='T001', ten_thuoc='Ibuprofen 400 mg ' * 8, gia_hien_tai=2500)]))
    client = review_app.test_client()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            page = browser.new_page()
            def serve(route):
                response = client.get(route.request.url.removeprefix('http://clinic.test'))
                route.fulfill(status=response.status_code, body=response.data,
                              content_type=response.content_type)
            page.route('http://clinic.test/**', serve)
            for width in (320, 390, 1440):
                page.set_viewport_size({'width': width, 'height': 900})
                page.goto('http://clinic.test/examinations/TEST/prescription')
                page.get_by_role('button', name='Thêm dòng thuốc').click()
                assert page.locator('select[name="ma_thuoc"]').count() == 4
                boxes = page.locator('.clinical-form input:not([type="hidden"]), .clinical-form select').evaluate_all(
                    '(elements) => elements.map(e => ({left:e.getBoundingClientRect().left,right:e.getBoundingClientRect().right}))')
                assert all(b['left'] >= 0 and b['right'] <= width + 1 for b in boxes), boxes
                assert page.evaluate('document.documentElement.scrollWidth') <= width + 1
                output = Path('test-artifacts/week2'); output.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(output / f'review-prescription-{width}.png'), full_page=True)
        finally:
            browser.close()
