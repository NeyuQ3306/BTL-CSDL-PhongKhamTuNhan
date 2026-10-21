"""English-browser regression for Vietnamese numeric messages and recovery."""
import json
import os
from pathlib import Path
import subprocess
import threading

import pytest
from werkzeug.serving import make_server
from test_week2 import clinical_data, visit
from clinic_app import workflows

pytestmark = pytest.mark.skipif(os.getenv('RUN_BROWSER_TESTS') != '1', reason='Requires real Chromium')


@pytest.mark.parametrize('kind', ['doctor', 'nurse', 'fee', 'quantity'])
def test_numeric_validation_vietnamese_in_english_browser(app, clinical_data, kind):
    from playwright.sync_api import sync_playwright
    if kind == 'quantity':
        with app.app_context():
            workflows.create_visit(visit())
    server = make_server('127.0.0.1', 0, app, threaded=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f'http://127.0.0.1:{server.server_port}'
    out = Path('test-artifacts/vuong-week3')
    out.mkdir(parents=True, exist_ok=True)
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            try:
                page = browser.new_page(locale='en-US', viewport={'width': 390, 'height': 1000})
                errors, posts = [], []
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.on('request', lambda req: posts.append(req.url) if req.method == 'POST' else None)
                if kind in ('doctor', 'nurse'):
                    page.goto(base + ('/doctors/new' if kind == 'doctor' else '/nurses/new'))
                    values = dict(cmt='999004000001', ho_ten='Nhân viên giả kiểm tra số',
                                  ngay_sinh='1980-01-01', dia_chi='Địa chỉ giả', tham_nien='5')
                    if kind == 'doctor':
                        values.update(ma_bac_si='U4BS', bac_nghe='Bậc 1', chuyen_mon='Nội', trinh_do_dao_tao='Đại học')
                    else:
                        values.update(ma_y_ta='U4YT', so_dien_thoai='0900000401', trinh_do='Đại học')
                    target = '[name="tham_nien"]'
                    invalids = [('-1', 'Giá trị phải lớn hơn hoặc bằng 0.'),
                                ('101', 'Giá trị không được lớn hơn 100.'),
                                ('1.5', 'Vui lòng nhập số nguyên.')]
                    save = 'Thêm hồ sơ'
                elif kind == 'fee':
                    page.goto(base + '/visits/new')
                    values = visit()
                    target = '[name="tien_kham_chua"]'
                    invalids = [('-1', 'Giá trị phải lớn hơn hoặc bằng 0.'),
                                ('1000000000000', 'Giá trị không được lớn hơn 999999999999.'),
                                ('1.5', 'Vui lòng nhập số nguyên.')]
                    save = 'Lưu'
                else:
                    page.goto(base + '/examinations/W2K1/prescription')
                    values = dict(ma_don='U4RX')
                    page.locator('[name="ma_thuoc"]').first.select_option('W2T1')
                    page.locator('[name="lieu_dung"]').first.fill('Dữ liệu giả')
                    target = '[name="so_luong"]'
                    invalids = [('0', 'Giá trị phải lớn hơn hoặc bằng 1.'),
                                ('-1', 'Giá trị phải lớn hơn hoặc bằng 1.'),
                                ('2147483648', 'Giá trị không được lớn hơn 2147483647.'),
                                ('1.5', 'Vui lòng nhập số nguyên.')]
                    save = 'Lưu'
                for key, value in values.items():
                    field = page.locator(f'[name="{key}"]')
                    if field.evaluate('(el) => el.tagName') == 'SELECT':
                        field.select_option(str(value))
                    else:
                        field.fill(str(value))
                field = page.locator(target).first
                actual = []
                for value, message in invalids:
                    field.fill(value)
                    page.get_by_role('button', name=save, exact=True).click()
                    assert field.evaluate('(el) => el.validationMessage') == message
                    assert field.input_value() == value
                    assert posts == []
                    actual.append(dict(input=value, expected=message, actual=message, posts=0))
                    field.fill('1')
                    assert field.evaluate('(el) => el.checkValidity() && !el.validity.customError')
                # Optional blank medicine quantities and cloned rows must retain native semantics.
                if kind == 'quantity':
                    field.fill('')
                    assert field.evaluate('(el) => el.checkValidity()')
                    field.fill('1')
                    page.get_by_role('button', name='Thêm dòng thuốc', exact=True).press('Enter')
                    dynamic = page.locator(target).nth(3)
                    dynamic.fill('0')
                    assert not dynamic.evaluate('(el) => el.reportValidity()')
                    assert dynamic.evaluate('(el) => el.validationMessage') == invalids[0][1]
                    dynamic.fill('')
                    assert dynamic.evaluate('(el) => el.checkValidity()')
                    page.get_by_role('button', name='Xóa dòng 4', exact=True).press('Enter')
                    actual.append(dict(dynamic_row_localized=True, optional_blank_valid=True))
                assert page.locator('[name="ho_ten"]' if kind in ('doctor', 'nurse') else
                                    '[name="ma_don"]' if kind == 'quantity' else '[name="ket_luan"]').input_value() == (
                    values['ho_ten'] if kind in ('doctor', 'nurse') else values['ma_don'] if kind == 'quantity' else values['ket_luan'])
                assert not errors
                page.screenshot(path=str(out / f'{kind}-390.png'), full_page=True)
                (out / f'{kind}.json').write_text(json.dumps(dict(source_sha=subprocess.check_output(
                    ['git', 'rev-parse', 'HEAD'], text=True).strip(), kind=kind, browser_locale='en-US',
                    actual=actual, error_recovery=True, input_preserved=True, posts=posts,
                    js_errors=errors), ensure_ascii=False, indent=2), encoding='utf-8')
            finally:
                browser.close()
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()
