"""R03 browser parity/lifecycle with stubbed SQL, not MySQL acceptance."""
from urllib.parse import parse_qs, urlsplit

import pytest
from clinic_app import analytics
from test_vuong_analytics_ui import ui, submit, R03_SEED, OUT


def select_r03(page):
    page.locator('#analytics-report').select_option('R03')


def bars(page):
    return page.locator('#r03-chart .chart-segment').evaluate_all('''nodes => nodes.map(n => ({
        ma_bac_si:n.dataset.doctor, so_lan_kham:Number(n.dataset.examinations),
        so_dot:Number(n.dataset.episodes), so_benh_nhan:Number(n.dataset.patients)
    }))''')


def assert_parity(page, rows):
    keys = ('ma_bac_si', 'ho_ten', 'chuyen_mon', 'so_lan_kham', 'so_dot', 'so_benh_nhan')
    assert page.locator('#analytics-table tbody tr').evaluate_all('(rows)=>rows.map(r=>[...r.cells].map(c=>c.textContent))') == [[str(r[k]) for k in keys] for r in rows]
    assert bars(page) == [{k: r[k] for k in ('ma_bac_si', 'so_lan_kham', 'so_dot', 'so_benh_nhan')} for r in rows]


def test_r03_seed_one_response_filters_and_switch_reports(ui):
    from playwright.sync_api import expect
    page, calls = ui
    requests = []
    page.on('request', lambda r: requests.append(r.url) if '/api/analytics/' in r.url else None)
    page.locator('#analytics-age').select_option('2')
    select_r03(page); submit(page)
    expect(page.locator('#analytics-status')).to_have_text('Đã tải 10 dòng R03.')
    assert_parity(page, R03_SEED)
    assert len(calls) == len(requests) == 1
    assert calls[0]['report_id'] == 'R03'
    assert urlsplit(requests[0]).path == '/api/analytics/R03'
    assert parse_qs(urlsplit(requests[0]).query) == {'start':['2026-07-01'], 'end':['2026-10-15']}
    expect(page.locator('#analytics-age')).to_be_disabled()
    expect(page.locator('#analytics-table thead th')).to_have_count(6)
    expect(page.locator('#r01-description')).to_be_hidden()
    expect(page.locator('#r02-description')).to_be_hidden()
    expect(page.locator('#r03-description')).to_be_visible()
    expect(page.locator('#r03-chart-hint')).to_contain_text('không phải xếp hạng chất lượng')
    page.screenshot(path=str(OUT/'r03-desktop.png'), full_page=True)
    page.locator('#r03-chart-section').screenshot(path=str(OUT/'r03-chart.png'))
    # No activity in the selected period still keeps all doctors with zero counts.
    page.locator('#analytics-start').fill('2004-02-29')
    page.locator('#analytics-through').fill('2004-02-29')
    expect(page.locator('#analytics-result')).to_be_hidden()
    expect(page.locator('#r03-chart .chart-segment')).to_have_count(0)
    submit(page)
    expect(page.locator('#analytics-result')).to_be_visible()
    assert calls[-1]['end'] == '2004-03-01'
    assert len(bars(page)) == len(R03_SEED)
    assert all(r['so_lan_kham'] == r['so_dot'] == r['so_benh_nhan'] == 0 for r in bars(page))
    expect(page.locator('#r03-chart-empty')).to_be_hidden()
    # Restore dates and switch through R02 to R01, then back to R03.
    page.locator('#analytics-start').fill('2026-07-01')
    page.locator('#analytics-through').fill('2026-10-14')
    for report, columns in [('R02',4), ('R01',6), ('R03',6)]:
        page.locator('#analytics-report').select_option(report)
        expect(page.locator('#analytics-result')).to_be_hidden()
        submit(page)
        expect(page.locator('#analytics-result')).to_be_visible()
        expect(page.locator('#analytics-table thead th')).to_have_count(columns)
        expect(page.locator(f'#{report.lower()}-chart-section')).to_be_visible()
        assert calls[-1]['report_id'] == report
    assert calls[-2]['age_group'] == 2
    assert 'age_group' not in calls[-1]
    assert_parity(page, R03_SEED)


def test_r03_zero_ties_geometry_long_names_and_safe_text(ui):
    from playwright.sync_api import expect
    page, _ = ui
    name = '<img src=x onerror=alert(1)> ' + 'Tên bác sĩ rất dài ' * 10
    rows = [dict(ma_bac_si='BS01', ho_ten=name, chuyen_mon='Nội tổng hợp', so_lan_kham=6, so_dot=3, so_benh_nhan=2),
            dict(ma_bac_si='BS02', ho_ten=name, chuyen_mon='Nhi', so_lan_kham=6, so_dot=4, so_benh_nhan=3),
            dict(ma_bac_si='BS03', ho_ten='Bác sĩ thứ ba', chuyen_mon='Ngoại', so_lan_kham=3, so_dot=2, so_benh_nhan=1),
            dict(ma_bac_si='BS04', ho_ten='Bác sĩ chưa có khám', chuyen_mon='Da liễu', so_lan_kham=0, so_dot=0, so_benh_nhan=0)]
    data = analytics.payload('R03', rows, analytics.DEFAULTS)
    page.route('**/api/analytics/R03?*', lambda route: route.fulfill(json=data))
    select_r03(page); submit(page)
    expect(page.locator('#analytics-result')).to_be_visible()
    assert_parity(page, rows)
    first = page.locator('#r03-chart [data-doctor="BS01"]')
    half = page.locator('#r03-chart [data-doctor="BS03"]')
    zero = page.locator('#r03-chart [data-doctor="BS04"]')
    assert float(first.get_attribute('width')) / float(half.get_attribute('width')) == pytest.approx(2)
    assert first.get_attribute('x') == half.get_attribute('x')
    assert float(first.get_attribute('height')) < float(half.get_attribute('y')) - float(first.get_attribute('y'))
    first.focus()
    expect(page.locator('#r03-chart-detail')).to_contain_text('6 lần khám, 3 đợt điều trị, 2 bệnh nhân')
    expect(page.locator('#r03-chart-detail')).to_contain_text(name)
    expect(page.locator('#analytics-result img')).to_have_count(0)
    page.keyboard.press('Tab')
    expect(page.locator('#r03-chart [data-doctor="BS02"]')).to_be_focused()
    assert float(zero.get_attribute('width')) == 0
    zero.focus()
    expect(zero).to_be_focused()
    expect(page.locator('#r03-chart-detail')).to_contain_text('0 lần khám, 0 đợt điều trị, 0 bệnh nhân')
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    # Truly no returned doctors is an empty state, not invented zero doctors.
    data['rows'] = []; data['row_count'] = 0
    submit(page)
    expect(page.locator('#r03-chart-empty')).to_be_visible()
    expect(page.locator('#r03-chart-scroll')).to_be_hidden()
    expect(page.locator('#r03-chart .chart-segment')).to_have_count(0)
    expect(page.locator('#analytics-table')).to_contain_text('Không có dữ liệu phù hợp')


@pytest.mark.parametrize('status',[400,404,500,503])
def test_r03_http_errors_clear_both_views(ui, status):
    from playwright.sync_api import expect
    page, _ = ui
    select_r03(page); submit(page)
    expect(page.locator('#analytics-result')).to_be_visible()
    page.route('**/api/analytics/R03?*', lambda route: route.fulfill(status=status, json={'error':'test'}))
    submit(page)
    expect(page.locator('#analytics-error')).to_contain_text(f'Lỗi {status}:')
    expect(page.locator('#analytics-result')).to_be_hidden()
    expect(page.locator('#r03-chart .chart-segment')).to_have_count(0)
    expect(page.locator('#analytics-table tbody tr')).to_have_count(0)


@pytest.mark.parametrize('case',['null','negative','string','duplicate','wrong_period','wrong_id','bad_name'])
def test_r03_bad_response_does_not_become_zero(ui, case):
    from playwright.sync_api import expect
    page, _ = ui
    data = analytics.payload('R03', R03_SEED[:2], analytics.DEFAULTS)
    if case in ('null','negative','string'):
        data['rows'][0]['so_dot'] = {'null':None,'negative':-1,'string':'3'}[case]
    elif case == 'duplicate': data['rows'][1]['ma_bac_si'] = data['rows'][0]['ma_bac_si']
    elif case == 'wrong_period': data['filters']['end'] = '2026-10-16'
    elif case == 'wrong_id': data['report_id'] = 'R02'
    else: data['rows'][0]['ho_ten'] = None
    page.route('**/api/analytics/R03?*', lambda route: route.fulfill(json=data))
    select_r03(page); submit(page)
    expect(page.locator('#analytics-error')).to_contain_text('không đúng hợp đồng R03')
    expect(page.locator('#analytics-result')).to_be_hidden()
    expect(page.locator('#r03-chart .chart-segment')).to_have_count(0)


def test_r03_network_timeout_and_stale_response(ui):
    from playwright.sync_api import expect
    page, _ = ui
    select_r03(page)
    page.route('**/api/analytics/R03?*', lambda route: route.abort())
    submit(page)
    expect(page.locator('#analytics-error')).to_contain_text('Không thể kết nối đến API')
    page.unroute('**/api/analytics/R03?*')
    page.evaluate('''() => {
      window.savedFetch = window.fetch;
      window.fetch = async (...args) => {
        const response = await window.savedFetch(...args);
        await new Promise(resolve => {window.releaseR03 = resolve;});
        return response;
      };
    }''')
    submit(page)
    page.wait_for_function('typeof window.releaseR03 === "function"')
    page.locator('#analytics-report').select_option('R02')
    page.evaluate('window.releaseR03()')
    expect(page.locator('#analytics-result')).to_be_hidden()
    expect(page.locator('#r03-chart .chart-segment')).to_have_count(0)
    page.evaluate('window.fetch = window.savedFetch')
    select_r03(page)
    page.clock.install()
    page.evaluate('''() => {window.fetch = (_url, options) => new Promise((_resolve, reject) => {
      options.signal.addEventListener('abort',()=>reject(new DOMException('aborted','AbortError')));
    });}''')
    submit(page)
    expect(page.locator('#analytics-status')).to_have_text('Đang tải R03…')
    page.clock.fast_forward(20001)
    expect(page.locator('#analytics-error')).to_contain_text('Tải báo cáo quá lâu')
    expect(page.locator('#analytics-result')).to_be_hidden()


def test_r03_offline_desktop(ui):
    from playwright.sync_api import expect
    page, _ = ui
    external = []
    page.route('**/*', lambda route: route.continue_() if route.request.url.startswith('http://127.0.0.1:') else (external.append(route.request.url),route.abort())[-1])
    for width in [1440,1280]:
        page.set_viewport_size({'width':width,'height':900})
        page.reload(); select_r03(page); submit(page)
        expect(page.locator('#analytics-result')).to_be_visible()
        assert_parity(page, R03_SEED)
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.screenshot(path=str(OUT/f'r03-{width}.png'), full_page=True)
    assert not external
    page.context.set_offline(True)
    page.locator('#r03-chart .chart-segment').first.focus()
    expect(page.locator('#r03-chart-detail')).to_contain_text('đợt điều trị')
    assert_parity(page, R03_SEED)
    page.context.set_offline(False)
