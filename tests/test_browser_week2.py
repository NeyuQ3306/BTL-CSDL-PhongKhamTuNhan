"""Real Chromium form -> Flask -> MySQL smoke; screenshot artifacts in CI."""
import os
import threading
from pathlib import Path
import pytest
from werkzeug.serving import make_server
from test_week2 import clinical_data  # reuse isolated fixture, including cleanup
from clinic_app.db import fetch_one


@pytest.mark.skipif(os.getenv('RUN_BROWSER_TESTS') != '1', reason='Set RUN_BROWSER_TESTS=1 and install Playwright Chromium')
def test_browser_clinical_flow(app, clinical_data):
    from playwright.sync_api import sync_playwright, expect
    server=make_server('127.0.0.1',0,app,threaded=True)
    thread=threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()
    base=f'http://127.0.0.1:{server.server_port}'
    output=Path('test-artifacts/week2');output.mkdir(parents=True,exist_ok=True)
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch()
            page=browser.new_page(viewport={'width':1440,'height':1000})
            page.goto(base+'/visits/new')
            for key,value in dict(ma_luot='W2L7',ngay_vao_vien='2001-02-01',ma_dot='W2D7',ma_lan_kham='W2K7',ngay_kham='2001-02-01',tien_kham_chua='120000',ket_luan='Theo dõi',ngay_ho_tro='2001-02-01',noi_dung_ho_tro='Tiếp đón').items():
                page.locator(f'[name="{key}"]').fill(value)
            for key,value in dict(ma_benh_nhan='W2BN1',ma_benh='W2B1',ma_bac_si='W2BS',ma_y_ta='W2YT1').items():
                page.locator(f'[name="{key}"]').select_option(value)
            page.get_by_role('button',name='Lưu',exact=True).click()
            expect(page).to_have_url(base+'/visits/W2L7')
            expect(page.get_by_text('Đã lưu thành công.',exact=True)).to_be_visible()
            page.screenshot(path=str(output/'01-visit.png'),full_page=True)
            page.get_by_role('link',name='Kê đơn',exact=True).click()
            page.locator('[name="ma_don"]').fill('W2P7')
            expect(page.locator('[name="ngay_lap_don"]')).to_have_value('2001-02-01')
            page.locator('[name="ma_thuoc"]').first.select_option('W2T1')
            page.locator('[name="so_luong"]').first.fill('2')
            page.locator('[name="lieu_dung"]').first.fill('Sáng và tối')
            page.get_by_role('button',name='Lưu',exact=True).click()
            expect(page).to_have_url(base+'/prescriptions/W2P7')
            expect(page.get_by_role('heading',name='Tổng: 2.000 đ')).to_be_visible()
            page.screenshot(path=str(output/'02-prescription.png'),full_page=True)
            page.goto(base+'/treatments/W2D7/cure')
            page.locator('[name="ngay_khoi"]').fill('2001-02-02')
            page.get_by_role('button',name='Lưu',exact=True).click()
            expect(page).to_have_url(base+'/treatments')
            page.goto(base+'/reports/revenue?month=2001-02')
            expect(page.get_by_text('122.000 đ',exact=True)).to_be_visible()
            page.screenshot(path=str(output/'03-revenue.png'),full_page=True)
            page.goto(base+'/reports/history?patient_id=W2BN1')
            expect(page.get_by_role('heading',name='Thuốc đã kê')).to_be_visible()
            page.screenshot(path=str(output/'04-history.png'),full_page=True)
            # Server-side date validation preserves the open visit.
            page.goto(base+'/visits/W2L7/close')
            page.locator('[name="ngay_ra_vien"]').fill('2001-01-31')
            page.get_by_role('button',name='Lưu',exact=True).click()
            expect(page.get_by_role('alert')).to_contain_text('Ngày ra viện không được trước ngày vào viện')
            page.screenshot(path=str(output/'05-validation.png'),full_page=True)
            browser.close()
        with app.app_context():
            assert fetch_one("SELECT ngay_ra_vien FROM luot_den_kham WHERE ma_luot='W2L7'")['ngay_ra_vien'] is None
            assert fetch_one("SELECT trang_thai FROM dot_dieu_tri WHERE ma_dot='W2D7'")['trang_thai']=='Đã khỏi'
    finally:
        server.shutdown();thread.join(timeout=5);server.server_close()
