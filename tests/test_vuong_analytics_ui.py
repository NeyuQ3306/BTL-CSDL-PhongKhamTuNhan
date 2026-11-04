"""R01 browser adapter checks with a real Flask API and stubbed SQL service.

RUN_BROWSER_TESTS=1, optional BROWSER_CHANNEL=chrome; no MySQL or writes.
These tests do not establish SQL parity or integrated acceptance.
"""
import json
import os
import threading
from pathlib import Path

import pytest
from werkzeug.serving import make_server
from clinic_app import create_app, analytics

OUT = Path('test-artifacts/vuong-analytics-ui')
SEED = json.loads(Path('database/analytics_expected.json').read_text(encoding='utf-8'))['results']['R01']


@pytest.fixture
def ui(monkeypatch):
    if os.getenv('RUN_BROWSER_TESTS') != '1':
        pytest.skip('Set RUN_BROWSER_TESTS=1 for browser adapter checks')
    from playwright.sync_api import sync_playwright
    calls = []

    def build(values, report_id=None):
        calls.append(values.copy())
        # The server's existing payload serializer/filter executes; SQL is stubbed.
        rows = SEED if (values['start'], values['end']) == ('2026-07-01', '2026-10-15') else []
        return analytics.payload(report_id, rows, values)

    monkeypatch.setattr(analytics, 'build', build)
    app = create_app({'TESTING': True, 'SECRET_KEY': 'disposable-ui-check'})
    server = make_server('127.0.0.1', 0, app, threaded=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    OUT.mkdir(parents=True, exist_ok=True)
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(channel=os.getenv('BROWSER_CHANNEL') or None)
            page = browser.new_page(viewport={'width': 1440, 'height': 1000}, locale='vi-VN')
            errors = []
            page.on('pageerror', lambda exc: errors.append(str(exc)))
            page.goto(f'http://127.0.0.1:{server.server_port}/reports')
            yield page, calls
            assert not errors
            browser.close()
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()


def submit(page):
    page.locator('#analytics-filters button').click()


def chart_values(page):
    return page.locator('#r01-chart .chart-segment').evaluate_all('''nodes => nodes.map(n => ({
        ma_benh: n.dataset.disease, thu_tu_nhom: Number(n.dataset.age),
        so_dot: Number(n.dataset.episodes), so_benh_nhan: Number(n.dataset.patients)
    }))''')


def assert_chart_rows(page, rows):
    keys = ('ma_benh', 'thu_tu_nhom', 'so_dot', 'so_benh_nhan')
    wanted = [{key: row[key] for key in keys} for row in rows]
    assert sorted(chart_values(page), key=lambda r: (r['ma_benh'], r['thu_tu_nhom'])) == sorted(wanted, key=lambda r: (r['ma_benh'], r['thu_tu_nhom']))


def test_r01_all_columns_age_filter_and_repeat(ui):
    from playwright.sync_api import expect
    page, calls = ui
    submit(page)
    expect(page.locator('#analytics-status')).to_have_text('Đã tải 29 dòng R01.')
    expected = [[str(row[k]) for k in ('ma_benh', 'ten_benh', 'thu_tu_nhom', 'nhom_tuoi', 'so_dot', 'so_benh_nhan')] for row in SEED]
    assert page.locator('#analytics-table tbody tr').evaluate_all('(rows) => rows.map(r => [...r.cells].map(c => c.textContent))') == expected
    assert calls[-1]['end'] == '2026-10-15'
    assert 'age_group' not in calls[-1]
    assert_chart_rows(page, SEED)
    assert len(calls) == 1  # Chart and table consume the same single API response.
    for age in ['-1', '0', '1', '2', '3', '']:
        page.locator('#analytics-age').select_option(age)
        expect(page.locator('#analytics-result')).to_be_hidden()
        expect(page.locator('#r01-chart .chart-segment')).to_have_count(0)
        submit(page)
        expect(page.locator('#analytics-result')).to_be_visible()
        count = len([r for r in SEED if age == '' or r['thu_tu_nhom'] == int(age)])
        expect(page.locator('#analytics-applied')).to_contain_text(f'Số dòng: {count}')
        assert_chart_rows(page, [r for r in SEED if age == '' or r['thu_tu_nhom'] == int(age)])
    submit(page)
    expect(page.locator('#analytics-result')).to_be_visible()
    assert all(c['end'] == '2026-10-15' for c in calls)
    assert len(calls) == 8
    page.screenshot(path=str(OUT/'r01-desktop.png'), full_page=True)
    page.locator('section[aria-labelledby="r01-chart-heading"]').screenshot(path=str(OUT/'r01-chart.png'))


@pytest.mark.parametrize('start,through,end', [
    ('2004-02-29', '2004-02-29', '2004-03-01'),
    ('2026-12-31', '2026-12-31', '2027-01-01'),
    ('0001-01-01', '0001-01-01', '0001-01-02'),
    ('9999-12-30', '9999-12-30', '9999-12-31'),
])
def test_calendar_boundaries(ui, start, through, end):
    from playwright.sync_api import expect
    page, calls = ui
    page.locator('#analytics-start').fill(start)
    page.locator('#analytics-through').fill(through)
    submit(page)
    expect(page.locator('#analytics-result')).to_be_visible()
    assert calls[-1]['start'] == start and calls[-1]['end'] == end
    expect(page.locator('#analytics-table')).to_contain_text('Không có dữ liệu phù hợp bộ lọc.')
    expect(page.locator('#r01-chart-scroll')).to_be_hidden()
    expect(page.locator('#r01-chart-empty')).to_be_visible()
    expect(page.locator('#r01-chart .chart-segment')).to_have_count(0)


def test_invalid_dates_never_reach_service(ui):
    from playwright.sync_api import expect
    page, calls = ui
    # Bypass native validation to exercise the JS adapter's own guard as well.
    page.locator('#analytics-filters').evaluate('(f) => f.noValidate = true')
    for start, through in [('2026-10-15', '2026-10-14'), ('9999-12-30', '9999-12-31')]:
        page.locator('#analytics-start').fill(start)
        page.locator('#analytics-through').fill(through)
        submit(page)
        expect(page.locator('#analytics-error')).to_be_visible()
        expect(page.locator('#analytics-result')).to_be_hidden()
    assert not calls


@pytest.mark.parametrize('status', [400, 404, 500, 503])
def test_http_errors_clear_previous_result(ui, status):
    from playwright.sync_api import expect
    page, _ = ui
    submit(page)
    expect(page.locator('#analytics-result')).to_be_visible()
    page.route('**/api/analytics/R01?*', lambda route: route.fulfill(status=status, json={'error': 'test'}))
    submit(page)
    expect(page.locator('#analytics-error')).to_contain_text(f'Lỗi {status}:')
    expect(page.locator('#analytics-result')).to_be_hidden()
    expect(page.locator('#analytics-table tbody tr')).to_have_count(0)
    expect(page.locator('#r01-chart .chart-segment')).to_have_count(0)


def test_response_contract_and_safe_text(ui):
    from playwright.sync_api import expect
    page, _ = ui
    data = analytics.payload('R01', [dict(SEED[0], ten_benh='<img src=x onerror=alert(1)>')], analytics.DEFAULTS)
    page.route('**/api/analytics/R01?*', lambda route: route.fulfill(json=data))
    submit(page)
    expect(page.locator('#analytics-result')).to_be_visible()
    expect(page.locator('#analytics-table tbody img')).to_have_count(0)
    expect(page.locator('#analytics-table')).to_contain_text('<img src=x onerror=alert(1)>')
    expect(page.locator('#r01-chart img')).to_have_count(0)
    page.locator('#r01-chart .chart-segment').focus()
    expect(page.locator('#r01-chart-detail')).to_contain_text('<img src=x onerror=alert(1)>')
    data['filters']['end'] = '2026-10-16'
    submit(page)
    expect(page.locator('#analytics-error')).to_contain_text('không đúng hợp đồng')
    expect(page.locator('#analytics-result')).to_be_hidden()
    expect(page.locator('#r01-chart .chart-segment')).to_have_count(0)


def test_stale_request_and_network_failure(ui):
    from playwright.sync_api import expect
    page, _ = ui
    page.route('**/api/analytics/R01?*', lambda route: route.abort())
    submit(page)
    expect(page.locator('#analytics-error')).to_contain_text('Không thể kết nối đến API')
    page.unroute('**/api/analytics/R01?*')
    # Hold the first response after fetch starts; change filter before releasing it.
    page.evaluate('''() => {
      const original = window.fetch;
      window.fetch = async (...args) => {
        const response = await original(...args);
        await new Promise(resolve => { window.releaseR01 = resolve; });
        return response;
      };
    }''')
    submit(page)
    page.wait_for_function('typeof window.releaseR01 === "function"')
    page.locator('#analytics-age').select_option('2')
    page.evaluate('window.releaseR01()')
    expect(page.locator('#analytics-result')).to_be_hidden()
    expect(page.locator('#analytics-status')).to_contain_text('Bộ lọc đã đổi')
    expect(page.locator('#r01-chart .chart-segment')).to_have_count(0)


def test_mobile_and_no_external_resources(ui):
    from playwright.sync_api import expect
    page, _ = ui
    external = []
    page.route('**/*', lambda route: route.continue_() if route.request.url.startswith('http://127.0.0.1:') else (external.append(route.request.url), route.abort())[-1])
    for width in [390, 320]:
        page.set_viewport_size({'width': width, 'height': 900})
        page.reload()
        submit(page)
        expect(page.locator('#analytics-result')).to_be_visible()
        assert_chart_rows(page, SEED)
        assert page.locator('#r01-chart-scroll').evaluate('(n) => n.scrollWidth > n.clientWidth')
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.screenshot(path=str(OUT/f'r01-{width}.png'), full_page=True)
    assert not external
    assert page.locator('.report-card a').count() == 4
    page.context.set_offline(True)
    page.locator('#r01-chart .chart-segment').first.focus()
    expect(page.locator('#r01-chart-detail')).to_contain_text('bệnh nhân trong nhóm')
    assert_chart_rows(page, SEED)
    page.context.set_offline(False)


def test_chart_stacking_keyboard_invalid_birth_and_zero(ui):
    from playwright.sync_api import expect
    page, _ = ui
    rows = [
        dict(ma_benh='X01', ten_benh='Tên bệnh rất dài ' * 12, thu_tu_nhom=2, nhom_tuoi='18–59', so_dot=3, so_benh_nhan=2),
        dict(ma_benh='X01', ten_benh='Tên bệnh rất dài ' * 12, thu_tu_nhom=-1, nhom_tuoi='Ngày sinh không hợp lệ', so_dot=2, so_benh_nhan=1),
        dict(ma_benh='X02', ten_benh='Tên bệnh rất dài ' * 12, thu_tu_nhom=0, nhom_tuoi='0–5', so_dot=0, so_benh_nhan=0),
    ]
    data = analytics.payload('R01', rows, analytics.DEFAULTS)
    page.route('**/api/analytics/R01?*', lambda route: route.fulfill(json=data))
    submit(page)
    expect(page.locator('#analytics-result')).to_be_visible()
    assert_chart_rows(page, rows)
    expect(page.locator('#r01-legend')).to_contain_text('Ngày sinh không hợp lệ (nhóm riêng)')
    segments = page.locator('#r01-chart .chart-segment')
    normal = page.locator('#r01-chart [data-disease="X01"][data-age="2"]')
    invalid = page.locator('#r01-chart [data-age="-1"]')
    assert float(normal.get_attribute('y')) == pytest.approx(float(invalid.get_attribute('y')) + float(invalid.get_attribute('height')))
    assert float(normal.get_attribute('height')) / float(invalid.get_attribute('height')) == pytest.approx(3 / 2)
    zero = page.locator('#r01-chart [data-disease="X02"]')
    assert float(zero.get_attribute('height')) == 0
    zero.focus()
    expect(zero).to_be_focused()
    expect(page.locator('#r01-chart-detail')).to_contain_text('0 đợt, 0 bệnh nhân trong nhóm')
    normal.focus()
    expect(page.locator('#r01-chart-detail')).to_contain_text('3 đợt, 2 bệnh nhân trong nhóm')
    page.keyboard.press('Tab')
    expect(invalid).to_be_focused()
    expect(page.locator('#r01-chart-detail')).to_contain_text('Ngày sinh không hợp lệ (nhóm riêng): 2 đợt, 1 bệnh nhân')
    assert segments.count() == 3
    page.set_viewport_size({'width': 320, 'height': 900})
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    # Real zero rows still have a defined scale and remain in both views.
    data['rows'] = [rows[2]]
    data['row_count'] = 1
    submit(page)
    expect(page.locator('#analytics-result')).to_be_visible()
    assert_chart_rows(page, [rows[2]])
    assert 'NaN' not in page.locator('#r01-chart').inner_html()
    expect(page.locator('#r01-chart-empty')).to_be_hidden()


@pytest.mark.parametrize('value', [None, -1, '3'])
def test_invalid_count_does_not_become_zero_chart(ui, value):
    from playwright.sync_api import expect
    page, _ = ui
    data = analytics.payload('R01', [SEED[0]], analytics.DEFAULTS)
    data['rows'][0]['so_dot'] = value
    page.route('**/api/analytics/R01?*', lambda route: route.fulfill(json=data))
    submit(page)
    expect(page.locator('#analytics-error')).to_contain_text('không đúng hợp đồng')
    expect(page.locator('#analytics-result')).to_be_hidden()
    expect(page.locator('#r01-chart .chart-segment')).to_have_count(0)


def test_duplicate_disease_age_rows_are_rejected(ui):
    from playwright.sync_api import expect
    page, _ = ui
    data = analytics.payload('R01', [SEED[0], SEED[0]], analytics.DEFAULTS)
    page.route('**/api/analytics/R01?*', lambda route: route.fulfill(json=data))
    submit(page)
    expect(page.locator('#analytics-error')).to_contain_text('không đúng hợp đồng')
    expect(page.locator('#analytics-result')).to_be_hidden()


def test_rows_must_match_selected_age(ui):
    from playwright.sync_api import expect
    page, _ = ui
    data = analytics.payload('R01', [SEED[0]], analytics.DEFAULTS)
    data['filters']['age_group'] = 3  # Seed's first row is group 2.
    page.route('**/api/analytics/R01?*', lambda route: route.fulfill(json=data))
    page.locator('#analytics-age').select_option('3')
    submit(page)
    expect(page.locator('#analytics-error')).to_contain_text('không đúng hợp đồng')
    expect(page.locator('#analytics-result')).to_be_hidden()
    expect(page.locator('#r01-chart .chart-segment')).to_have_count(0)
