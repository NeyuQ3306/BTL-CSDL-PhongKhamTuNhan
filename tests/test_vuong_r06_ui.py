"""R06 desktop UI contract checks; SQL service stubbed, no DB acceptance."""
from urllib.parse import parse_qs,urlsplit

import pytest
from clinic_app import analytics
from test_vuong_analytics_ui import ui,submit,R06_SEED,OUT

FIELDS=('ma_dot','ma_benh_nhan','ho_ten','so_dien_thoai','ma_benh','ten_benh','ma_bac_si','ten_bac_si','ngay_bat_dau','ngay_kham_cuoi','chua_co_lan_kham','so_ngay_chua_ghi_nhan','nhom_ngay')
GROUPS=('0–6','7–13','14–29','30+')


def select_r06(page):
    page.locator('#analytics-report').select_option('R06')


def bars(page):
    return page.locator('#r06-chart .chart-segment').evaluate_all('''nodes=>nodes.map(n=>({nhom_ngay:n.dataset.group,so_dot:Number(n.dataset.episodes)}))''')


def assert_parity(page,data):
    expected=[[('Chưa có lần khám' if r[k] is None and k=='ngay_kham_cuoi' else str(r[k])) for k in FIELDS] for r in data['rows']]
    assert page.locator('#analytics-table tbody tr').evaluate_all('(rows)=>rows.map(r=>[...r.cells].map(c=>c.textContent))')==expected
    assert bars(page)==data['chart_groups']


def test_r06_seed_one_response_independent_filters_and_switch(ui):
    from playwright.sync_api import expect
    page,calls=ui
    requests=[]
    page.on('request',lambda r:requests.append(r.url) if '/api/analytics/' in r.url else None)
    # Hidden invalid period controls must not block the independent R06 form.
    page.locator('#analytics-start').fill('2026-10-15')
    page.locator('#analytics-through').fill('2026-10-14')
    page.locator('#analytics-age').select_option('2')
    select_r06(page)
    for name in ('start','through','age_group'):
        expect(page.locator(f'[name="{name}"]')).to_be_disabled()
    submit(page)
    expect(page.locator('#analytics-status')).to_have_text('Đã tải 19 dòng R06.')
    data=analytics.payload('R06',R06_SEED,analytics.DEFAULTS)
    assert_parity(page,data)
    assert len(calls)==len(requests)==1
    assert urlsplit(requests[0]).path=='/api/analytics/R06'
    assert parse_qs(urlsplit(requests[0]).query)=={'as_of':['2026-10-14'],'threshold':['14']}
    expect(page.locator('#analytics-table thead th')).to_have_count(13)
    expect(page.locator('#r06-description')).to_be_visible()
    page.screenshot(path=str(OUT/'r06-desktop.png'),full_page=True)
    page.locator('#r06-chart-section').screenshot(path=str(OUT/'r06-chart.png'))
    page.locator('#analytics-as-of').fill('9999-12-31')
    page.locator('#analytics-threshold').fill('36500')
    expect(page.locator('#r06-chart .chart-segment')).to_have_count(0)
    submit(page)
    expect(page.locator('#analytics-result')).to_be_visible()
    assert calls[-1]['as_of']=='9999-12-31' and calls[-1]['threshold']==36500
    assert bars(page)==[dict(nhom_ngay=g,so_dot=0) for g in GROUPS]
    expect(page.locator('#r06-chart-scroll')).to_be_visible()
    expect(page.locator('#analytics-table')).to_contain_text('Không có dữ liệu phù hợp')
    # Switch away restores regular period and hides/disables R06 inputs.
    page.locator('#analytics-report').select_option('R01')
    for name in ('as_of','threshold'):
        expect(page.locator(f'[name="{name}"]')).to_be_disabled()
    expect(page.locator('#analytics-start')).to_be_enabled()
    page.locator('#analytics-start').fill('2026-07-01')
    submit(page)
    expect(page.locator('#analytics-result')).to_be_visible()
    assert calls[-1]['report_id']=='R01' and calls[-1]['age_group']==2
    expect(page.locator('#analytics-table thead th')).to_have_count(6)
    expect(page.locator('#r06-chart .chart-segment')).to_have_count(0)


def test_r06_null_exam_flag_phone_table_only_api_groups_keyboard(ui):
    from playwright.sync_api import expect
    page,_=ui
    base=dict(ma_benh_nhan='BN01',ho_ten='<svg onload=alert(1)>',so_dien_thoai='0901234567',ma_benh='B01',ten_benh='Bệnh mẫu',ma_bac_si='BS01',ten_bac_si='Bác sĩ mẫu')
    rows=[dict(base,ma_dot='D01',ngay_bat_dau='2026-09-01',ngay_kham_cuoi='2026-09-01',chua_co_lan_kham=0,so_ngay_chua_ghi_nhan=43,nhom_ngay='30+'),
          dict(base,ma_dot='D02',ngay_bat_dau='2026-09-24',ngay_kham_cuoi=None,chua_co_lan_kham=1,so_ngay_chua_ghi_nhan=20,nhom_ngay='14–29')]
    data=analytics.payload('R06',rows,analytics.DEFAULTS)
    page.route('**/api/analytics/R06?*',lambda route:route.fulfill(json=data))
    select_r06(page);submit(page)
    expect(page.locator('#analytics-result')).to_be_visible()
    assert_parity(page,data)
    expect(page.locator('#analytics-table')).to_contain_text('Chưa có lần khám')
    expect(page.locator('#analytics-table')).to_contain_text('0901234567')
    expect(page.locator('#analytics-result svg svg')).to_have_count(0)
    for segment in page.locator('#r06-chart .chart-segment').all():
        segment.focus()
        assert '0901234567' not in (segment.get_attribute('aria-label') or '')
        assert '0901234567' not in page.locator('#r06-chart-detail').inner_text()
    first=page.locator('#r06-chart .chart-segment').first
    first.focus();page.keyboard.press('Tab')
    expect(page.locator('#r06-chart .chart-segment').nth(1)).to_be_focused()
    assert all(g in page.locator('#r06-chart').text_content() for g in GROUPS)


@pytest.mark.parametrize('value',['0','36500'])
def test_r06_threshold_boundaries(ui,value):
    from playwright.sync_api import expect
    page,calls=ui
    select_r06(page);page.locator('#analytics-threshold').fill(value);submit(page)
    expect(page.locator('#analytics-result')).to_be_visible()
    assert calls[-1]['threshold']==int(value)
    assert bars(page)==[dict(nhom_ngay=g,so_dot=0) for g in GROUPS]


@pytest.mark.parametrize('value',['-1','36501','1.5',''])
def test_r06_invalid_threshold_no_request(ui,value):
    from playwright.sync_api import expect
    page,calls=ui
    select_r06(page)
    page.locator('#analytics-filters').evaluate('(form)=>form.noValidate=true')
    page.locator('#analytics-threshold').fill(value);submit(page)
    expect(page.locator('#analytics-error')).to_be_visible()
    expect(page.locator('#analytics-result')).to_be_hidden()
    assert not calls


@pytest.mark.parametrize('status',[400,404,500,503])
def test_r06_http_errors_clear(ui,status):
    from playwright.sync_api import expect
    page,_=ui
    select_r06(page);submit(page)
    expect(page.locator('#analytics-result')).to_be_visible()
    page.route('**/api/analytics/R06?*',lambda route:route.fulfill(status=status,json={'error':'test'}))
    submit(page)
    expect(page.locator('#analytics-error')).to_contain_text(f'Lỗi {status}:')
    expect(page.locator('#analytics-result')).to_be_hidden()
    expect(page.locator('#r06-chart .chart-segment')).to_have_count(0)


@pytest.mark.parametrize('case',['bad_flag','null_mismatch','negative_days','duplicate_episode','invalid_date','future_date','missing_group','duplicate_group','null_count','wrong_as_of','wrong_threshold','wrong_interval'])
def test_r06_invalid_payload_rejected(ui,case):
    from playwright.sync_api import expect
    page,_=ui
    data=analytics.payload('R06',R06_SEED[:2],analytics.DEFAULTS)
    if case=='bad_flag': data['rows'][0]['chua_co_lan_kham']=2
    elif case=='null_mismatch': data['rows'][0]['ngay_kham_cuoi']=None;data['rows'][0]['chua_co_lan_kham']=0
    elif case=='negative_days': data['rows'][0]['so_ngay_chua_ghi_nhan']=-1
    elif case=='duplicate_episode': data['rows'][1]['ma_dot']=data['rows'][0]['ma_dot']
    elif case=='invalid_date': data['rows'][0]['ngay_kham_cuoi']='2026-02-30'
    elif case=='future_date': data['rows'][0]['ngay_kham_cuoi']='2026-10-15'
    elif case=='missing_group': data['chart_groups'].pop()
    elif case=='duplicate_group': data['chart_groups'][1]=data['chart_groups'][0].copy()
    elif case=='null_count': data['chart_groups'][0]['so_dot']=None
    elif case=='wrong_as_of': data['filters']['as_of']='2026-10-13'
    elif case=='wrong_threshold': data['filters']['threshold']=15
    else: data['interval']='end_exclusive'
    page.route('**/api/analytics/R06?*',lambda route:route.fulfill(json=data))
    select_r06(page);submit(page)
    expect(page.locator('#analytics-error')).to_contain_text('không đúng hợp đồng R06')
    expect(page.locator('#analytics-result')).to_be_hidden()
    expect(page.locator('#r06-chart .chart-segment')).to_have_count(0)


def test_r06_network_timeout_stale(ui):
    from playwright.sync_api import expect
    page,_=ui
    select_r06(page)
    page.route('**/api/analytics/R06?*',lambda route:route.abort());submit(page)
    expect(page.locator('#analytics-error')).to_contain_text('Không thể kết nối đến API')
    page.unroute('**/api/analytics/R06?*')
    page.evaluate('''()=>{window.savedFetch=window.fetch;window.fetch=async(...args)=>{
      const r=await window.savedFetch(...args);await new Promise(resolve=>{window.releaseR06=resolve;});return r;
    };}''')
    submit(page);page.wait_for_function('typeof window.releaseR06==="function"')
    page.locator('#analytics-report').select_option('R05');page.evaluate('window.releaseR06()')
    expect(page.locator('#analytics-result')).to_be_hidden()
    expect(page.locator('#r06-chart .chart-segment')).to_have_count(0)
    page.evaluate('window.fetch=window.savedFetch');select_r06(page);page.clock.install()
    page.evaluate('''()=>{window.fetch=(_url,options)=>new Promise((_resolve,reject)=>{
      options.signal.addEventListener('abort',()=>reject(new DOMException('aborted','AbortError')));
    });}''')
    submit(page);expect(page.locator('#analytics-status')).to_have_text('Đang tải R06…')
    page.clock.fast_forward(20001)
    expect(page.locator('#analytics-error')).to_contain_text('Tải báo cáo quá lâu')


def test_r06_desktop_offline(ui):
    from playwright.sync_api import expect
    page,_=ui
    external=[]
    page.route('**/*',lambda route:route.continue_() if route.request.url.startswith('http://127.0.0.1:') else (external.append(route.request.url),route.abort())[-1])
    data=analytics.payload('R06',R06_SEED,analytics.DEFAULTS)
    for width in [1440,1280]:
        page.set_viewport_size({'width':width,'height':900});page.reload();select_r06(page);submit(page)
        expect(page.locator('#analytics-result')).to_be_visible();assert_parity(page,data)
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.screenshot(path=str(OUT/f'r06-{width}.png'),full_page=True)
    assert not external
    page.context.set_offline(True);page.locator('#r06-chart .chart-segment').first.focus()
    expect(page.locator('#r06-chart-detail')).to_contain_text('đợt')
    assert_parity(page,data);page.context.set_offline(False)
