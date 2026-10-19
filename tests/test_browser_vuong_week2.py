"""User-facing regressions on real Chromium + disposable MySQL; no mocked writes."""
import os
import threading
from pathlib import Path
import pytest
from werkzeug.serving import make_server
from test_week2 import clinical_data
from clinic_app.db import fetch_one

pytestmark = pytest.mark.skipif(os.getenv('RUN_BROWSER_TESTS') != '1', reason='Requires Chromium')


def test_vuong_clinical_workflow(app, clinical_data):
    from playwright.sync_api import sync_playwright, expect
    server = make_server('127.0.0.1', 0, app, threaded=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f'http://127.0.0.1:{server.server_port}'
    out = Path('test-artifacts/vuong-week2'); out.mkdir(parents=True, exist_ok=True)
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            page = browser.new_page(viewport={'width': 390, 'height': 900}, locale='vi-VN')
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))

            def fill(values):
                for key, value in values.items():
                    item = page.locator(f'[name="{key}"]')
                    if item.evaluate('(el) => el.tagName') == 'SELECT':
                        item.select_option(value)
                    else:
                        item.fill(value)

            def save():
                page.get_by_role('button', name='Lưu', exact=True).click()

            def shot(name):
                page.screenshot(path=str(out / name), full_page=True)
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')

            def reception(l, k, episode, mode='new', when='2001-02-01'):
                page.goto(base + '/visits/new')
                fill(dict(ma_luot=l, ma_benh_nhan='W2BN1', ngay_vao_vien=when,
                          che_do_dot=mode, ma_lan_kham=k, ngay_kham=when,
                          tien_kham_chua='120000', ket_luan='Theo dõi', ma_y_ta='W2YT1',
                          ngay_ho_tro=when, noi_dung_ho_tro='Tiếp đón'))
                if mode == 'new':
                    fill(dict(ma_dot=episode, ma_benh='W2B1', ma_bac_si='W2BS'))
                else:
                    page.locator('#episode-picker').select_option(episode)
                    expect(page.locator('[name="ma_dot"]')).to_have_value(episode)
                    expect(page.locator('[name="ma_bac_si"]')).to_be_disabled()
                save()
                expect(page).to_have_url(base + '/visits/' + l)

            reception('W2L8', 'W2K8', 'W2D8')
            shot('01-visit-mobile.png')
            page.get_by_role('link', name='Khám thêm bệnh', exact=True).click()
            fill(dict(ma_dot='W2D9', ma_benh='W2B2', ma_bac_si='W2BS', ma_lan_kham='W2K9',
                      ngay_kham='2001-02-01', tien_kham_chua='80000', ket_luan='Bệnh thứ hai'))
            save()
            expect(page.get_by_role('region', name='Các bệnh được khám', exact=True)).to_contain_text('Bệnh kiểm thử 2')
            # Existing support populates the original date/content and keeps day readonly.
            page.get_by_role('link', name='Cập nhật hỗ trợ W2YT1', exact=True).click()
            expect(page.locator('[name="ngay_ho_tro"]')).to_have_value('2001-02-01')
            expect(page.locator('[name="noi_dung_ho_tro"]')).to_have_value('Tiếp đón')
            assert page.locator('[name="ngay_ho_tro"]').evaluate('(x)=>x.readOnly')
            page.locator('[name="noi_dung_ho_tro"]').fill('Đo huyết áp và theo dõi')
            save()
            page.get_by_role('link', name='Ghi hỗ trợ y tá', exact=True).click()
            fill(dict(ma_y_ta='W2YT2', ngay_ho_tro='2001-02-01', noi_dung_ho_tro='Hỗ trợ thêm'))
            save()
            # Duplicate medicine is rejected by the server, preserving every repeated field.
            page.locator('a[href="/examinations/W2K8/prescription"]').click()
            page.set_viewport_size({'width': 320, 'height': 900})
            fill(dict(ma_don='W2P8'))
            for i, usage in [(0, 'Sáng'), (1, 'Tối')]:
                page.locator('[name="ma_thuoc"]').nth(i).select_option('W2T1')
                page.locator('[name="so_luong"]').nth(i).fill(str(i+2))
                page.locator('[name="lieu_dung"]').nth(i).fill(usage)
            save()
            expect(page.get_by_role('alert')).to_contain_text('Mỗi thuốc chỉ có một dòng')
            expect(page.locator('#clinical-error')).to_be_focused()
            expect(page.locator('[name="so_luong"]').nth(1)).to_have_value('3')
            expect(page.locator('[name="lieu_dung"]').nth(1)).to_have_value('Tối')
            shot('02-error-preserves-lines-320.png')
            page.locator('[name="ma_thuoc"]').nth(1).select_option('W2T2')
            page.get_by_role('button', name='Thêm dòng thuốc', exact=True).focus()
            page.keyboard.press('Enter')
            expect(page.locator('#medicine-lines fieldset')).to_have_count(4)
            expect(page.locator('[name="ma_thuoc"]').nth(3)).to_be_focused()
            page.get_by_role('button', name='Xóa dòng 4', exact=True).focus()
            page.keyboard.press('Enter')
            expect(page.locator('#medicine-lines fieldset')).to_have_count(3)
            assert page.locator('[id]').evaluate_all('(els)=>new Set(els.map(x=>x.id)).size===els.length')
            shot('03-prescription-320.png')
            save()
            expect(page.get_by_role('heading', name='Tổng: 8.000 đ', exact=True)).to_be_visible()
            page.reload()
            expect(page.get_by_text('Tối', exact=True)).to_be_visible()
            shot('04-saved-prescription-320.png')
            page.get_by_role('link', name='← Quay lại lượt khám', exact=True).click()
            page.get_by_role('link', name='Kết thúc lượt', exact=True).click()
            fill(dict(ngay_ra_vien='2001-01-31'))
            save()
            expect(page.get_by_role('alert')).to_contain_text('Ngày ra viện không được trước')
            expect(page.locator('[name="ngay_ra_vien"]')).to_have_value('2001-01-31')
            shot('05-close-validation.png')
            fill(dict(ngay_ra_vien='2001-02-01')); save()
            expect(page.get_by_role('link', name='Khám thêm bệnh', exact=True)).to_have_count(0)
            # The episode is still active after closing its first visit.
            reception('W2L9', 'W2K10', 'W2D8', 'existing', '2001-02-02')
            shot('06-revisit.png')
            page.get_by_role('link', name='Xác nhận khỏi', exact=True).click()
            fill(dict(ngay_khoi='2001-02-01')); save()
            expect(page.get_by_role('alert')).to_contain_text('Ngày khỏi phải từ ngày khám cuối cùng')
            fill(dict(ngay_khoi='2001-02-02')); save()
            expect(page).to_have_url(base + '/treatments')
            # Cure and close are separate; close the second visit before recurrence.
            page.goto(base + '/visits/W2L9/close')
            fill(dict(ngay_ra_vien='2001-02-02')); save()
            reception('W2L10', 'W2K11', 'W2D10', when='2001-02-03')
            for width in [1440, 390, 320]:
                page.set_viewport_size({'width': width, 'height': 900})
                page.goto(base + '/visits/W2L10'); shot(f'07-recurrence-{width}.png')
                page.goto(base + '/visits/W2L10/close'); shot(f'08-close-{width}.png')
            # Patient changes must never retain another patient's episode selection.
            page.goto(base + '/visits/new')
            fill(dict(ma_benh_nhan='W2BN1', che_do_dot='existing'))
            page.locator('#episode-picker').select_option('W2D10')
            fill(dict(ma_benh_nhan='W2BN2'))
            expect(page.locator('[name="ma_dot"]')).to_have_value('')
            expect(page.locator('#episode-picker option')).to_have_count(1)
            assert not errors, errors
            browser.close()
        with app.app_context():
            assert fetch_one("SELECT COUNT(*) n FROM ho_tro WHERE ma_luot='W2L8'")['n'] == 2
            assert fetch_one("SELECT so_thu_tu_trong_dot n FROM lan_kham_benh WHERE ma_lan_kham='W2K10'")['n'] == 2
            assert fetch_one("SELECT trang_thai FROM dot_dieu_tri WHERE ma_dot='W2D8'")['trang_thai'] == 'Đã khỏi'
    finally:
        server.shutdown(); thread.join(timeout=5); server.server_close()
