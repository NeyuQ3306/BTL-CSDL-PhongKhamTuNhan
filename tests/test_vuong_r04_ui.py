"""R04 desktop UI parity and lifecycle; SQL service stubbed, no DB acceptance."""
from urllib.parse import parse_qs, urlsplit

import pytest
from clinic_app import analytics
from test_vuong_analytics_ui import ui, submit, R04_SEED, OUT


def select_r04(page):
    page.locator('#analytics-report').select_option('R04')


def bars(page):
    return page.locator('#r04-chart .chart-segment').evaluate_all('''nodes => nodes.map(n => ({
        ma_thuoc:n.dataset.drug, so_don:Number(n.dataset.orders),
        tong_so_luong:Number(n.dataset.quantity), don_vi_tinh:n.dataset.unit
    }))''')


def assert_parity(page, rows):
    keys = ('ma_thuoc', 'ten_thuoc', 'don_vi_tinh', 'so_don', 'tong_so_luong')
    assert page.locator('#analytics-table tbody tr').evaluate_all('(rows)=>rows.map(r=>[...r.cells].map(c=>c.textContent))') == [[str(r[k]) for k in keys] for r in rows]
    assert bars(page) == [{k:r[k] for k in ('ma_thuoc','so_don','tong_so_luong','don_vi_tinh')} for r in rows]


def test_r04_seed_single_response_period_and_switch(ui):
    from playwright.sync_api import expect
    page, calls = ui
    requests = []
    page.on('request', lambda r: requests.append(r.url) if '/api/analytics/' in r.url else None)
    page.locator('#analytics-age').select_option('2')
    select_r04(page); submit(page)
    expect(page.locator('#analytics-status')).to_have_text('Đã tải 29 dòng R04.')
    assert_parity(page, R04_SEED)
    assert len(calls) == len(requests) == 1
    assert urlsplit(requests[0]).path == '/api/analytics/R04'
    assert parse_qs(urlsplit(requests[0]).query) == {'start':['2026-07-01'],'end':['2026-10-15']}
    expect(page.locator('#analytics-age')).to_be_disabled()
    expect(page.locator('#analytics-table thead th')).to_have_count(5)
    expect(page.locator('#r03-description')).to_be_hidden()
    expect(page.locator('#r04-description')).to_be_visible()
    expect(page.locator('#r04-chart-hint')).to_contain_text('không phải lượng kê')
    page.screenshot(path=str(OUT/'r04-desktop.png'), full_page=True)
    page.locator('#r04-chart-section').screenshot(path=str(OUT/'r04-chart.png'))
    # Inclusive single leap day; empty results do not become invented zero drugs.
    page.locator('#analytics-start').fill('2004-02-29')
    page.locator('#analytics-through').fill('2004-02-29')
    expect(page.locator('#r04-chart .chart-segment')).to_have_count(0)
    submit(page)
    expect(page.locator('#r04-chart-empty')).to_be_visible()
    expect(page.locator('#r04-chart-scroll')).to_be_hidden()
    assert calls[-1]['end'] == '2004-03-01'
    page.locator('#analytics-start').fill('2026-07-01')
    page.locator('#analytics-through').fill('2026-10-14')
    for report, columns in [('R03',6),('R01',6),('R02',4),('R04',5)]:
        page.locator('#analytics-report').select_option(report)
        expect(page.locator('#analytics-result')).to_be_hidden()
        submit(page)
        expect(page.locator('#analytics-result')).to_be_visible()
        expect(page.locator('#analytics-table thead th')).to_have_count(columns)
        expect(page.locator(f'#{report.lower()}-chart-section')).to_be_visible()
        assert calls[-1]['report_id'] == report
    assert calls[-3]['age_group'] == 2
    assert 'age_group' not in calls[-1]
    assert_parity(page, R04_SEED)


def test_r04_order_metric_units_keyboard_zero_safe_names(ui):
    from playwright.sync_api import expect
    page, _ = ui
    name = '<img src=x onerror=alert(1)> ' + 'Tên thuốc dài ' * 10
    rows = [dict(ma_thuoc='T01',ten_thuoc=name,don_vi_tinh='Viên',so_don=6,tong_so_luong=12),
            dict(ma_thuoc='T02',ten_thuoc=name,don_vi_tinh='Chai',so_don=3,tong_so_luong=999),
            dict(ma_thuoc='T03',ten_thuoc='Thuốc mẫu',don_vi_tinh='Gói',so_don=3,tong_so_luong=8),
            dict(ma_thuoc='T04',ten_thuoc='Thuốc zero',don_vi_tinh='Ống',so_don=0,tong_so_luong=0)]
    data = analytics.payload('R04', rows, analytics.DEFAULTS)
    page.route('**/api/analytics/R04?*', lambda route: route.fulfill(json=data))
    select_r04(page); submit(page)
    expect(page.locator('#analytics-result')).to_be_visible()
    assert_parity(page, rows)
    first = page.locator('#r04-chart [data-drug="T01"]')
    half = page.locator('#r04-chart [data-drug="T02"]')
    zero = page.locator('#r04-chart [data-drug="T04"]')
    # Width is 6:3 orders even though quantities have the opposite relationship.
    assert float(first.get_attribute('width')) / float(half.get_attribute('width')) == pytest.approx(2)
    assert first.get_attribute('x') == half.get_attribute('x')
    first.focus()
    expect(page.locator('#r04-chart-detail')).to_contain_text('6 đơn có thuốc; tổng lượng kê: 12 Viên')
    expect(page.locator('#r04-chart-detail')).to_contain_text(name)
    expect(page.locator('#analytics-result img')).to_have_count(0)
    page.keyboard.press('Tab')
    expect(half).to_be_focused()
    expect(page.locator('#r04-chart-detail')).to_contain_text('3 đơn có thuốc; tổng lượng kê: 999 Chai')
    assert float(zero.get_attribute('width')) == 0
    zero.focus()
    expect(page.locator('#r04-chart-detail')).to_contain_text('0 đơn có thuốc; tổng lượng kê: 0 Ống')
    data['rows'] = [rows[-1]]; data['row_count'] = 1
    submit(page)
    expect(page.locator('#analytics-status')).to_have_text('Đã tải 1 dòng R04.')
    assert_parity(page, data['rows'])
    assert 'NaN' not in page.locator('#r04-chart').inner_html()
    expect(page.locator('#r04-chart-empty')).to_be_hidden()


@pytest.mark.parametrize('status',[400,404,500,503])
def test_r04_http_errors_clear_both_views(ui, status):
    from playwright.sync_api import expect
    page, _ = ui
    select_r04(page); submit(page)
    expect(page.locator('#analytics-result')).to_be_visible()
    page.route('**/api/analytics/R04?*', lambda route: route.fulfill(status=status,json={'error':'test'}))
    submit(page)
    expect(page.locator('#analytics-error')).to_contain_text(f'Lỗi {status}:')
    expect(page.locator('#analytics-result')).to_be_hidden()
    expect(page.locator('#r04-chart .chart-segment')).to_have_count(0)
    expect(page.locator('#analytics-table tbody tr')).to_have_count(0)


@pytest.mark.parametrize('case',['null_count','null_quantity','negative','string','unit_null','duplicate','wrong_period','wrong_id','bad_name'])
def test_r04_bad_response_not_zero(ui, case):
    from playwright.sync_api import expect
    page, _ = ui
    data = analytics.payload('R04', R04_SEED[:2], analytics.DEFAULTS)
    if case == 'null_count': data['rows'][0]['so_don'] = None
    elif case in ('null_quantity','negative','string'):
        data['rows'][0]['tong_so_luong'] = {'null_quantity':None,'negative':-1,'string':'3'}[case]
    elif case == 'unit_null': data['rows'][0]['don_vi_tinh'] = None
    elif case == 'duplicate': data['rows'][1]['ma_thuoc'] = data['rows'][0]['ma_thuoc']
    elif case == 'wrong_period': data['filters']['end'] = '2026-10-16'
    elif case == 'wrong_id': data['report_id'] = 'R03'
    else: data['rows'][0]['ten_thuoc'] = None
    page.route('**/api/analytics/R04?*', lambda route: route.fulfill(json=data))
    select_r04(page); submit(page)
    expect(page.locator('#analytics-error')).to_contain_text('không đúng hợp đồng R04')
    expect(page.locator('#analytics-result')).to_be_hidden()
    expect(page.locator('#r04-chart .chart-segment')).to_have_count(0)


def test_r04_network_timeout_and_late_response(ui):
    from playwright.sync_api import expect
    page, _ = ui
    select_r04(page)
    page.route('**/api/analytics/R04?*', lambda route: route.abort())
    submit(page)
    expect(page.locator('#analytics-error')).to_contain_text('Không thể kết nối đến API')
    page.unroute('**/api/analytics/R04?*')
    page.evaluate('''() => {
      window.savedFetch = window.fetch;
      window.fetch = async (...args) => {
        const response = await window.savedFetch(...args);
        await new Promise(resolve => {window.releaseR04 = resolve;}); return response;
      };
    }''')
    submit(page)
    page.wait_for_function('typeof window.releaseR04 === "function"')
    page.locator('#analytics-report').select_option('R03')
    page.evaluate('window.releaseR04()')
    expect(page.locator('#analytics-result')).to_be_hidden()
    expect(page.locator('#r04-chart .chart-segment')).to_have_count(0)
    page.evaluate('window.fetch = window.savedFetch')
    select_r04(page)
    page.clock.install()
    page.evaluate('''() => {window.fetch = (_url, options) => new Promise((_resolve,reject) => {
      options.signal.addEventListener('abort',()=>reject(new DOMException('aborted','AbortError')));
    });}''')
    submit(page)
    expect(page.locator('#analytics-status')).to_have_text('Đang tải R04…')
    page.clock.fast_forward(20001)
    expect(page.locator('#analytics-error')).to_contain_text('Tải báo cáo quá lâu')
    expect(page.locator('#analytics-result')).to_be_hidden()


def test_r04_offline_desktop(ui):
    from playwright.sync_api import expect
    page, _ = ui
    external = []
    page.route('**/*', lambda route: route.continue_() if route.request.url.startswith('http://127.0.0.1:') else (external.append(route.request.url),route.abort())[-1])
    for width in [1440,1280]:
        page.set_viewport_size({'width':width,'height':900})
        page.reload(); select_r04(page); submit(page)
        expect(page.locator('#analytics-result')).to_be_visible()
        assert_parity(page, R04_SEED)
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.screenshot(path=str(OUT/f'r04-{width}.png'),full_page=True)
    assert not external
    page.context.set_offline(True)
    page.locator('#r04-chart .chart-segment').first.focus()
    expect(page.locator('#r04-chart-detail')).to_contain_text('đơn có thuốc')
    assert_parity(page, R04_SEED)
    page.context.set_offline(False)
