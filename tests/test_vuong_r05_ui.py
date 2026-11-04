"""Independent R05 desktop UI checks; SQL stubbed, no MySQL acceptance."""
from urllib.parse import parse_qs, urlsplit

import pytest
from clinic_app import analytics
from test_vuong_analytics_ui import ui, submit, R05_SEED, OUT

FIELDS = ('ma_dot','ma_benh_nhan','ho_ten','ma_benh','ten_benh','ngay_bat_dau','ngay_khoi_truoc','so_ngay_tu_lan_khoi_truoc')


def select_r05(page):
    page.locator('#analytics-report').select_option('R05')


def bars(page):
    return page.locator('#r05-chart .chart-segment').evaluate_all('''nodes => nodes.map(n => ({
      ma_benh:n.dataset.disease, so_dot:Number(n.dataset.episodes)
    }))''')


def assert_parity(page, data):
    assert page.locator('#analytics-table tbody tr').evaluate_all('(rows)=>rows.map(r=>[...r.cells].map(c=>c.textContent))') == [[str(r[k]) for k in FIELDS] for r in data['rows']]
    assert bars(page) == [{k:g[k] for k in ('ma_benh','so_dot')} for g in data['chart_groups']]


def test_r05_seed_single_response_period_and_switch(ui):
    from playwright.sync_api import expect
    page, calls = ui
    requests = []
    page.on('request', lambda r: requests.append(r.url) if '/api/analytics/' in r.url else None)
    page.locator('#analytics-age').select_option('2')
    select_r05(page); submit(page)
    expect(page.locator('#analytics-status')).to_have_text('Đã tải 6 dòng R05.')
    data = analytics.payload('R05', R05_SEED, analytics.DEFAULTS)
    assert_parity(page, data)
    assert len(calls) == len(requests) == 1
    assert urlsplit(requests[0]).path == '/api/analytics/R05'
    assert parse_qs(urlsplit(requests[0]).query) == {'start':['2026-07-01'],'end':['2026-10-15']}
    expect(page.locator('#analytics-age')).to_be_disabled()
    expect(page.locator('#analytics-table thead th')).to_have_count(8)
    expect(page.locator('#r05-description')).to_be_visible()
    expect(page.locator('#r04-description')).to_be_hidden()
    page.screenshot(path=str(OUT/'r05-desktop.png'), full_page=True)
    page.locator('#r05-chart-section').screenshot(path=str(OUT/'r05-chart.png'))
    page.locator('#analytics-start').fill('2004-02-29')
    page.locator('#analytics-through').fill('2004-02-29')
    expect(page.locator('#r05-chart .chart-segment')).to_have_count(0)
    submit(page)
    expect(page.locator('#r05-chart-empty')).to_be_visible()
    expect(page.locator('#r05-chart-scroll')).to_be_hidden()
    assert calls[-1]['end'] == '2004-03-01'
    expect(page.locator('#analytics-table')).to_contain_text('Không có dữ liệu phù hợp')
    page.locator('#analytics-start').fill('2026-07-01')
    page.locator('#analytics-through').fill('2026-10-14')
    for report, columns in [('R04',5),('R03',6),('R02',4),('R01',6),('R05',8)]:
        page.locator('#analytics-report').select_option(report)
        expect(page.locator('#analytics-result')).to_be_hidden()
        submit(page)
        expect(page.locator('#analytics-result')).to_be_visible()
        expect(page.locator('#analytics-table thead th')).to_have_count(columns)
        expect(page.locator(f'#{report.lower()}-chart-section')).to_be_visible()
        assert calls[-1]['report_id'] == report
    assert calls[-2]['age_group'] == 2
    assert 'age_group' not in calls[-1]
    assert_parity(page, data)


def test_r05_episode_not_people_and_api_groups_keyboard_safe_text(ui):
    from playwright.sync_api import expect
    page, _ = ui
    name = '<img src=x onerror=alert(1)> ' + 'Tên bệnh rất dài ' * 8
    base = dict(ma_benh_nhan='BN01',ho_ten='<svg onload=alert(1)>',ma_benh='B01',ten_benh=name,ngay_khoi_truoc='2026-06-01')
    rows = [dict(base,ma_dot='D01',ngay_bat_dau='2026-07-01',so_ngay_tu_lan_khoi_truoc=30),
            dict(base,ma_dot='D02',ngay_bat_dau='2026-07-03',so_ngay_tu_lan_khoi_truoc=32),
            dict(base,ma_dot='D03',ma_benh='B02',ten_benh='Bệnh khác',ngay_bat_dau='2026-07-04',so_ngay_tu_lan_khoi_truoc=33)]
    data = analytics.payload('R05', rows, analytics.DEFAULTS)
    # API group order is independent of detailed rows; consume it unchanged.
    data['chart_groups'].reverse()
    page.route('**/api/analytics/R05?*', lambda route: route.fulfill(json=data))
    select_r05(page); submit(page)
    expect(page.locator('#analytics-result')).to_be_visible()
    assert_parity(page, data)
    assert bars(page) == [{'ma_benh':'B02','so_dot':1},{'ma_benh':'B01','so_dot':2}]
    first = page.locator('#r05-chart [data-disease="B02"]')
    twice = page.locator('#r05-chart [data-disease="B01"]')
    # Counts are episodes; two episodes for the same person are not one patient.
    dimension = 'height' if first.get_attribute('height') != twice.get_attribute('height') else 'width'
    geometry = lambda n: float(n.get_attribute(dimension))
    assert geometry(twice)/geometry(first) == pytest.approx(2)
    first.focus(); page.keyboard.press('Tab')
    expect(twice).to_be_focused()
    expect(page.locator('#r05-chart-detail')).to_contain_text(name)
    expect(page.locator('#r05-chart-detail')).to_contain_text('2')
    expect(page.locator('#analytics-result img, #analytics-result svg svg')).to_have_count(0)
    expect(page.locator('#r05-description')).to_contain_text('lịch sử')


@pytest.mark.parametrize('status',[400,404,500,503])
def test_r05_http_errors_clear_both_views(ui, status):
    from playwright.sync_api import expect
    page, _ = ui
    select_r05(page); submit(page)
    expect(page.locator('#analytics-result')).to_be_visible()
    page.route('**/api/analytics/R05?*', lambda route: route.fulfill(status=status,json={'error':'test'}))
    submit(page)
    expect(page.locator('#analytics-error')).to_contain_text(f'Lỗi {status}:')
    expect(page.locator('#analytics-result')).to_be_hidden()
    expect(page.locator('#r05-chart .chart-segment')).to_have_count(0)
    expect(page.locator('#analytics-table tbody tr')).to_have_count(0)


@pytest.mark.parametrize('case',['null_days','negative_days','string_days','duplicate_episode','bad_date','outside','null_group_count','negative_group_count','duplicate_group','missing_groups','wrong_period','wrong_id'])
def test_r05_malformed_response_not_empty_or_zero(ui, case):
    from playwright.sync_api import expect
    page, _ = ui
    data = analytics.payload('R05', R05_SEED[:2], analytics.DEFAULTS)
    if case in ('null_days','negative_days','string_days'):
        data['rows'][0]['so_ngay_tu_lan_khoi_truoc'] = {'null_days':None,'negative_days':-1,'string_days':'3'}[case]
    elif case == 'duplicate_episode': data['rows'][1]['ma_dot'] = data['rows'][0]['ma_dot']
    elif case == 'bad_date': data['rows'][0]['ngay_khoi_truoc'] = '2026-02-30'
    elif case == 'outside': data['rows'][0]['ngay_bat_dau'] = '2026-10-15'
    elif case == 'null_group_count': data['chart_groups'][0]['so_dot'] = None
    elif case == 'negative_group_count': data['chart_groups'][0]['so_dot'] = -1
    elif case == 'duplicate_group': data['chart_groups'].append(data['chart_groups'][0].copy())
    elif case == 'missing_groups': del data['chart_groups']
    elif case == 'wrong_period': data['filters']['end'] = '2026-10-16'
    else: data['report_id'] = 'R04'
    page.route('**/api/analytics/R05?*', lambda route: route.fulfill(json=data))
    select_r05(page); submit(page)
    expect(page.locator('#analytics-error')).to_contain_text('không đúng hợp đồng R05')
    expect(page.locator('#analytics-result')).to_be_hidden()
    expect(page.locator('#r05-chart .chart-segment')).to_have_count(0)


def test_r05_network_timeout_and_late_response(ui):
    from playwright.sync_api import expect
    page, _ = ui
    select_r05(page)
    page.route('**/api/analytics/R05?*', lambda route: route.abort())
    submit(page)
    expect(page.locator('#analytics-error')).to_contain_text('Không thể kết nối đến API')
    page.unroute('**/api/analytics/R05?*')
    page.evaluate('''() => {window.savedFetch=window.fetch;window.fetch=async(...args)=>{
      const r=await window.savedFetch(...args);await new Promise(resolve=>{window.releaseR05=resolve;});return r;
    };}''')
    submit(page)
    page.wait_for_function('typeof window.releaseR05 === "function"')
    page.locator('#analytics-report').select_option('R04')
    page.evaluate('window.releaseR05()')
    expect(page.locator('#analytics-result')).to_be_hidden()
    expect(page.locator('#r05-chart .chart-segment')).to_have_count(0)
    page.evaluate('window.fetch=window.savedFetch')
    select_r05(page); page.clock.install()
    page.evaluate('''() => {window.fetch=(_url,options)=>new Promise((_resolve,reject)=>{
      options.signal.addEventListener('abort',()=>reject(new DOMException('aborted','AbortError')));
    });}''')
    submit(page)
    expect(page.locator('#analytics-status')).to_have_text('Đang tải R05…')
    page.clock.fast_forward(20001)
    expect(page.locator('#analytics-error')).to_contain_text('Tải báo cáo quá lâu')


def test_r05_desktop_offline(ui):
    from playwright.sync_api import expect
    page, _ = ui
    external = []
    page.route('**/*',lambda route:route.continue_() if route.request.url.startswith('http://127.0.0.1:') else (external.append(route.request.url),route.abort())[-1])
    data = analytics.payload('R05',R05_SEED,analytics.DEFAULTS)
    for width in [1440,1280]:
        page.set_viewport_size({'width':width,'height':900})
        page.reload();select_r05(page);submit(page)
        expect(page.locator('#analytics-result')).to_be_visible()
        assert_parity(page,data)
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.screenshot(path=str(OUT/f'r05-{width}.png'),full_page=True)
    assert not external
    page.context.set_offline(True)
    page.locator('#r05-chart .chart-segment').first.focus()
    expect(page.locator('#r05-chart-detail')).to_contain_text('đợt')
    assert_parity(page,data)
    page.context.set_offline(False)
