"""R02 browser parity/lifecycle; SQL service stubbed, no MySQL acceptance."""
from urllib.parse import parse_qs, urlsplit

import pytest
from clinic_app import analytics
from test_vuong_analytics_ui import ui, submit, R02_SEED, OUT


def select_r02(page):
    page.locator('#analytics-report').select_option('R02')


def bars(page):
    return page.locator('#r02-chart .chart-segment').evaluate_all('''nodes => nodes.map(n => ({
        date:n.dataset.date, series:n.dataset.series, count:Number(n.dataset.count), patients:Number(n.dataset.patients)
    }))''')


def assert_r02_parity(page, rows):
    keys = ('ngay', 'so_luot', 'so_benh_nhan_tiep_nhan', 'so_lan_kham')
    assert page.locator('#analytics-table tbody tr').evaluate_all('(rows) => rows.map(r => [...r.cells].map(c => c.textContent))') == [[str(r[k]) for k in keys] for r in rows]
    assert bars(page) == [dict(date=r['ngay'], series=key, count=r[key], patients=r['so_benh_nhan_tiep_nhan']) for r in rows for key in ('so_luot', 'so_lan_kham')]


def test_r02_seed_one_response_filters_and_switch_back(ui):
    from playwright.sync_api import expect
    page, calls = ui
    requests = []
    page.on('request', lambda r: requests.append(r.url) if '/api/analytics/' in r.url else None)
    page.locator('#analytics-age').select_option('2')
    select_r02(page)
    expect(page.locator('#analytics-age-field')).to_be_hidden()
    expect(page.locator('#analytics-age')).to_be_disabled()
    submit(page)
    expect(page.locator('#analytics-status')).to_have_text('Đã tải 83 dòng R02.')
    assert_r02_parity(page, R02_SEED)
    assert len(calls) == 1 and calls[0]['report_id'] == 'R02'
    assert len(requests) == 1
    assert urlsplit(requests[0]).path == '/api/analytics/R02'
    assert parse_qs(urlsplit(requests[0]).query) == {'start': ['2026-07-01'], 'end': ['2026-10-15']}
    expect(page.locator('#analytics-table thead th')).to_have_count(4)
    expect(page.locator('#analytics-table')).to_contain_text('Bệnh nhân tiếp nhận (người/ngày)')
    expect(page.locator('#r01-chart-section')).to_be_hidden()
    expect(page.locator('#r02-chart-section')).to_be_visible()
    page.screenshot(path=str(OUT/'r02-desktop.png'), full_page=True)
    page.locator('#r02-chart-section').screenshot(path=str(OUT/'r02-chart.png'))
    # Date change hides both old views and makes one fresh request; empty is not zero.
    page.locator('#analytics-start').fill('2004-02-29')
    page.locator('#analytics-through').fill('2004-02-29')
    expect(page.locator('#analytics-result')).to_be_hidden()
    expect(page.locator('#r02-chart .chart-segment')).to_have_count(0)
    submit(page)
    expect(page.locator('#r02-chart-empty')).to_be_visible()
    expect(page.locator('#r02-chart-scroll')).to_be_hidden()
    assert calls[-1]['start'] == '2004-02-29' and calls[-1]['end'] == '2004-03-01'
    expect(page.locator('#analytics-table')).to_contain_text('Không có dữ liệu phù hợp')
    page.locator('#analytics-start').fill('2026-07-01')
    page.locator('#analytics-through').fill('2026-10-14')
    page.locator('#analytics-report').select_option('R01')
    expect(page.locator('#analytics-age')).to_be_enabled()
    expect(page.locator('#analytics-age')).to_have_value('2')
    submit(page)
    expect(page.locator('#analytics-result')).to_be_visible()
    expect(page.locator('#analytics-table thead th')).to_have_count(6)
    assert calls[-1]['report_id'] == 'R01' and calls[-1]['age_group'] == 2
    expect(page.locator('#r01-chart-section')).to_be_visible()
    expect(page.locator('#r02-chart-section')).to_be_hidden()
    expect(page.locator('#r02-chart .chart-segment')).to_have_count(0)


def test_r02_missing_day_units_zero_geometry_keyboard(ui):
    from playwright.sync_api import expect
    page, _ = ui
    rows = [dict(ngay='2026-07-01', so_luot=2, so_benh_nhan_tiep_nhan=1, so_lan_kham=5),
            dict(ngay='2026-07-03', so_luot=0, so_benh_nhan_tiep_nhan=0, so_lan_kham=3)]
    data = analytics.payload('R02', rows, analytics.DEFAULTS)
    page.route('**/api/analytics/R02?*', lambda route: route.fulfill(json=data))
    select_r02(page); submit(page)
    expect(page.locator('#analytics-result')).to_be_visible()
    assert_r02_parity(page, rows)
    expect(page.locator('#r02-chart [data-date="2026-07-02"]')).to_have_count(0)
    assert '2026-07-02' not in page.locator('#analytics-table').inner_text()
    first = page.locator('#r02-chart [data-date="2026-07-01"][data-series="so_luot"]')
    exam = page.locator('#r02-chart [data-date="2026-07-01"][data-series="so_lan_kham"]')
    assert float(first.get_attribute('height')) / float(exam.get_attribute('height')) == pytest.approx(2 / 5)
    assert float(first.get_attribute('x')) + float(first.get_attribute('width')) < float(exam.get_attribute('x'))
    assert float(first.get_attribute('y')) + float(first.get_attribute('height')) == pytest.approx(float(exam.get_attribute('y')) + float(exam.get_attribute('height')))
    first.focus()
    expect(page.locator('#r02-chart-detail')).to_contain_text('2 lượt tiếp nhận; 5 lần khám; 1 bệnh nhân tiếp nhận')
    page.keyboard.press('Tab')
    expect(exam).to_be_focused()
    zero = page.locator('#r02-chart [data-date="2026-07-03"][data-series="so_luot"]')
    assert float(zero.get_attribute('height')) == 0
    zero.focus()
    expect(page.locator('#r02-chart-detail')).to_contain_text('0 lượt tiếp nhận; 3 lần khám; 0 bệnh nhân tiếp nhận')
    # Explicit all-zero rows are retained without an invalid scale.
    data['rows'] = [dict(rows[0], so_luot=0, so_benh_nhan_tiep_nhan=0, so_lan_kham=0)]
    data['row_count'] = 1
    submit(page)
    expect(page.locator('#analytics-status')).to_have_text('Đã tải 1 dòng R02.')
    assert_r02_parity(page, data['rows'])
    assert all(float(n) == 0 for n in page.locator('#r02-chart .chart-segment').evaluate_all('(nodes) => nodes.map(n=>n.getAttribute("height"))'))
    assert 'NaN' not in page.locator('#r02-chart').inner_html()


@pytest.mark.parametrize('status', [400, 404, 500, 503])
def test_r02_errors_clear_both_views(ui, status):
    from playwright.sync_api import expect
    page, _ = ui
    select_r02(page); submit(page)
    expect(page.locator('#analytics-result')).to_be_visible()
    page.route('**/api/analytics/R02?*', lambda route: route.fulfill(status=status, json={'error': 'test'}))
    submit(page)
    expect(page.locator('#analytics-error')).to_contain_text(f'Lỗi {status}:')
    expect(page.locator('#analytics-result')).to_be_hidden()
    expect(page.locator('#r02-chart .chart-segment')).to_have_count(0)
    expect(page.locator('#analytics-table tbody tr')).to_have_count(0)


@pytest.mark.parametrize('case', ['null', 'negative', 'string', 'duplicate', 'unsorted', 'invalid_date', 'outside', 'wrong_period', 'wrong_id'])
def test_r02_invalid_response_rejected(ui, case):
    from playwright.sync_api import expect
    page, _ = ui
    data = analytics.payload('R02', R02_SEED[:2], analytics.DEFAULTS)
    if case in ('null', 'negative', 'string'):
        data['rows'][0]['so_benh_nhan_tiep_nhan'] = {'null': None, 'negative': -1, 'string': '3'}[case]
    elif case == 'duplicate': data['rows'][1]['ngay'] = data['rows'][0]['ngay']
    elif case == 'unsorted': data['rows'].reverse()
    elif case == 'invalid_date': data['rows'][0]['ngay'] = '2026-07-00'
    elif case == 'outside': data['rows'][1]['ngay'] = '2026-10-15'
    elif case == 'wrong_period': data['filters']['end'] = '2026-10-16'
    else: data['report_id'] = 'R01'
    page.route('**/api/analytics/R02?*', lambda route: route.fulfill(json=data))
    select_r02(page); submit(page)
    expect(page.locator('#analytics-error')).to_contain_text('không đúng hợp đồng R02')
    expect(page.locator('#analytics-result')).to_be_hidden()
    expect(page.locator('#r02-chart .chart-segment')).to_have_count(0)


def test_r02_stale_network_and_timeout(ui):
    from playwright.sync_api import expect
    page, _ = ui
    select_r02(page)
    page.route('**/api/analytics/R02?*', lambda route: route.abort())
    submit(page)
    expect(page.locator('#analytics-error')).to_contain_text('Không thể kết nối đến API')
    page.unroute('**/api/analytics/R02?*')
    page.evaluate('''() => {
      window.savedFetch = window.fetch;
      window.fetch = async (...args) => {
        const response = await window.savedFetch(...args);
        await new Promise(resolve => {window.releaseR02 = resolve;});
        return response;
      };
    }''')
    submit(page)
    page.wait_for_function('typeof window.releaseR02 === "function"')
    page.locator('#analytics-report').select_option('R01')
    page.evaluate('window.releaseR02()')
    expect(page.locator('#analytics-result')).to_be_hidden()
    expect(page.locator('#r02-chart .chart-segment')).to_have_count(0)
    page.evaluate('window.fetch = window.savedFetch')
    select_r02(page)
    page.clock.install()
    page.evaluate('''() => { window.fetch = (_url, options) => new Promise((_resolve, reject) => {
      options.signal.addEventListener('abort', () => reject(new DOMException('aborted', 'AbortError')));
    }); }''')
    submit(page)
    expect(page.locator('#analytics-status')).to_have_text('Đang tải R02…')
    page.clock.fast_forward(20001)
    expect(page.locator('#analytics-error')).to_contain_text('Tải báo cáo quá lâu')
    expect(page.locator('#analytics-result')).to_be_hidden()


def test_r02_offline_mobile(ui):
    from playwright.sync_api import expect
    page, _ = ui
    external = []
    page.route('**/*', lambda route: route.continue_() if route.request.url.startswith('http://127.0.0.1:') else (external.append(route.request.url), route.abort())[-1])
    for width in [1440, 390, 320]:
        page.set_viewport_size({'width': width, 'height': 900})
        page.reload()
        select_r02(page); submit(page)
        expect(page.locator('#analytics-result')).to_be_visible()
        assert_r02_parity(page, R02_SEED)
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        assert page.locator('#r02-chart-scroll').evaluate('(n)=>n.scrollWidth>n.clientWidth')
        page.screenshot(path=str(OUT/f'r02-{width}.png'), full_page=True)
    assert not external
    page.context.set_offline(True)
    page.locator('#r02-chart .chart-segment').first.focus()
    expect(page.locator('#r02-chart-detail')).to_contain_text('bệnh nhân tiếp nhận')
    assert_r02_parity(page, R02_SEED)
    page.context.set_offline(False)
