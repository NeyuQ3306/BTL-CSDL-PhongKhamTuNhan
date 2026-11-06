"""R07 exact-money desktop checks with stubbed SQL, no MySQL acceptance."""
from urllib.parse import parse_qs,urlsplit
import math

import pytest
from clinic_app import analytics
from test_vuong_analytics_ui import ui,submit,R07_SEED,OUT

FIELDS=('ma_benh','ten_benh','so_dot_tinh','so_dot_loai','tb_tien_kham','tb_tien_thuoc','tb_tong','min_tong','max_tong')
MONEY=FIELDS[4:]


def select_r07(page):
    page.locator('#analytics-report').select_option('R07')


def segments(page):
    return page.locator('#r07-chart .chart-segment').evaluate_all('''nodes=>nodes.map(n=>({
      ma_benh:n.dataset.disease,series:n.dataset.series,money:n.dataset.money
    }))''')


def assert_parity(page,data):
    expected=[[('Không có mẫu' if r[k] is None else r[k]+' VND') if k in MONEY else str(r[k]) for k in FIELDS] for r in data['rows']]
    assert page.locator('#analytics-table tbody tr').evaluate_all('(rows)=>rows.map(r=>[...r.cells].map(c=>c.textContent))')==expected
    assert segments(page)==[dict(ma_benh=r['ma_benh'],series=k,money=r[k]) for r in data['rows'] if r['so_dot_tinh']>0 for k in ('tb_tien_kham','tb_tien_thuoc')]
    assert page.locator('#analytics-table tbody td[data-money]').evaluate_all('(cells)=>cells.map(c=>c.dataset.money)')==[('null' if r[k] is None else r[k]) for r in data['rows'] for k in MONEY]


def test_r07_seed_one_response_filters_switch_and_empty(ui):
    from playwright.sync_api import expect
    page,calls=ui
    requests=[]
    page.on('request',lambda r:requests.append(r.url) if '/api/analytics/' in r.url else None)
    # Invalid inactive R06 values cannot block the period-based R07 form.
    page.locator('#analytics-report').select_option('R06')
    page.locator('#analytics-as-of').fill('')
    page.locator('#analytics-threshold').fill('-1')
    select_r07(page)
    expect(page.locator('#analytics-as-of')).to_be_disabled()
    expect(page.locator('#analytics-threshold')).to_be_disabled()
    submit(page)
    expect(page.locator('#analytics-status')).to_have_text('Đã tải 15 dòng R07.')
    data=analytics.payload('R07',R07_SEED,analytics.DEFAULTS)
    assert_parity(page,data)
    assert len(calls)==len(requests)==1
    assert urlsplit(requests[0]).path=='/api/analytics/R07'
    assert parse_qs(urlsplit(requests[0]).query)=={'start':['2026-07-01'],'end':['2026-10-15']}
    expect(page.locator('#analytics-table thead th')).to_have_count(9)
    expect(page.locator('#r07-description')).to_be_visible()
    page.screenshot(path=str(OUT/'r07-desktop.png'),full_page=True)
    page.locator('#r07-chart-section').screenshot(path=str(OUT/'r07-chart.png'))
    page.locator('#analytics-start').fill('2004-02-29')
    page.locator('#analytics-through').fill('2004-02-29')
    expect(page.locator('#r07-chart .chart-segment')).to_have_count(0)
    submit(page)
    expect(page.locator('#r07-chart-empty')).to_be_visible()
    assert calls[-1]['end']=='2004-03-01'
    page.locator('#analytics-start').fill('2026-07-01')
    page.locator('#analytics-through').fill('2026-10-14')
    for report,columns in [('R04',5),('R03',6),('R02',4),('R01',6),('R05',8),('R07',9)]:
        page.locator('#analytics-report').select_option(report)
        expect(page.locator('#analytics-result')).to_be_hidden()
        submit(page)
        expect(page.locator('#analytics-result')).to_be_visible()
        expect(page.locator('#analytics-table thead th')).to_have_count(columns)
    assert_parity(page,data)


def test_r07_exact_large_strings_rounding_zero_null_and_safe_labels(ui):
    from playwright.sync_api import expect
    page,_=ui
    name='<img src=x onerror=alert(1)> '+'Tên bệnh dài '*8
    rows=[dict(ma_benh='B01',ten_benh=name,so_dot_tinh=2,so_dot_loai=1,tb_tien_kham='9007199254740993.01',tb_tien_thuoc='0.02',tb_tong='9007199254740993.03',min_tong='9007199254740000.00',max_tong='9007199254750000.00'),
          dict(ma_benh='B02',ten_benh='Bệnh làm tròn',so_dot_tinh=3,so_dot_loai=0,tb_tien_kham='0.33',tb_tien_thuoc='0.33',tb_tong='0.67',min_tong='0.60',max_tong='0.70'),
          dict(ma_benh='B03',ten_benh='Mẫu thật zero',so_dot_tinh=1,so_dot_loai=0,**{k:'0.00' for k in MONEY}),
          dict(ma_benh='B04',ten_benh='Nhóm thiếu hồ sơ',so_dot_tinh=0,so_dot_loai=3,**{k:None for k in MONEY})]
    data=analytics.payload('R07',rows,analytics.DEFAULTS)
    page.route('**/api/analytics/R07?*',lambda route:route.fulfill(json=data))
    select_r07(page);submit(page)
    expect(page.locator('#analytics-result')).to_be_visible()
    assert_parity(page,data)
    expect(page.locator('#analytics-table')).to_contain_text('9007199254740993.01 VND')
    expect(page.locator('#analytics-result img')).to_have_count(0)
    expect(page.locator('#r07-chart [data-disease="B04"]')).to_have_count(0)
    expect(page.locator('#analytics-table')).to_contain_text('B04')
    first=page.locator('#r07-chart [data-disease="B01"][data-series="tb_tien_kham"]')
    first.focus()
    for value in ('9007199254740993.01','9007199254740993.03','9007199254740000.00','9007199254750000.00'):
        expect(page.locator('#r07-chart-detail')).to_contain_text(value)
    expect(page.locator('#r07-chart-detail')).to_contain_text(name)
    page.keyboard.press('Tab')
    expect(page.locator('#r07-chart [data-disease="B01"][data-series="tb_tien_thuoc"]')).to_be_focused()
    rounded=page.locator('#r07-chart [data-disease="B02"]').first
    rounded.focus()
    expect(page.locator('#r07-chart-detail')).to_contain_text('0.67')
    zero=page.locator('#r07-chart [data-disease="B03"]').first
    assert float(zero.get_attribute('height'))==0
    zero.focus();expect(zero).to_be_focused()
    expect(page.locator('#r07-chart-detail')).to_contain_text('0.00')
    geometry=page.locator('#r07-chart .chart-segment').evaluate_all('(nodes)=>nodes.map(n=>[n.getAttribute("x"),n.getAttribute("y"),n.getAttribute("width"),n.getAttribute("height")])')
    assert all(all(math.isfinite(float(v)) for v in rectangle) for rectangle in geometry)
    # No eligible samples still retain the disease row, never a zero money bar.
    data['rows']=[rows[-1]];data['row_count']=1
    submit(page)
    expect(page.locator('#analytics-status')).to_have_text('Đã tải 1 dòng R07.')
    assert_parity(page,data)
    expect(page.locator('#r07-chart .chart-segment')).to_have_count(0)
    expect(page.locator('#r07-chart')).to_contain_text('Không có mẫu')
    expect(page.locator('#r07-chart-empty')).to_be_visible()
    expect(page.locator('#r07-chart-empty')).to_contain_text('mẫu')


def test_r07_near_number_max_geometry_is_finite_or_explicitly_rejected(ui):
    from playwright.sync_api import expect
    page,_=ui
    # 1.79e308 is finite as a drawing Number; it is not an actual SQL money claim.
    amount='179'+'0'*306+'.00'
    row=dict(ma_benh='MAX',ten_benh='Biên biểu diễn',so_dot_tinh=1,so_dot_loai=0,
             tb_tien_kham=amount,tb_tien_thuoc='0.00',tb_tong=amount,min_tong=amount,max_tong=amount)
    data=analytics.payload('R07',[row],analytics.DEFAULTS)
    page.route('**/api/analytics/R07?*',lambda route:route.fulfill(json=data))
    select_r07(page);submit(page)
    page.wait_for_function('!document.querySelector("#analytics-result").hidden || !document.querySelector("#analytics-error").hidden',timeout=5000)
    if page.locator('#analytics-error').is_visible():
        expect(page.locator('#analytics-error')).to_contain_text('biểu đồ')
        expect(page.locator('#analytics-result')).to_be_hidden()
        expect(page.locator('#r07-chart .chart-segment')).to_have_count(0)
    else:
        assert_parity(page,data)
        geometry=page.locator('#r07-chart .chart-segment').evaluate_all('(nodes)=>nodes.map(n=>[n.getAttribute("x"),n.getAttribute("y"),n.getAttribute("width"),n.getAttribute("height")])')
        assert all(all(math.isfinite(float(v)) for v in rectangle) for rectangle in geometry)
        assert len(geometry)==2


@pytest.mark.parametrize('status',[400,404,500,503])
def test_r07_http_errors_clear(ui,status):
    from playwright.sync_api import expect
    page,_=ui
    select_r07(page);submit(page)
    expect(page.locator('#analytics-result')).to_be_visible()
    page.route('**/api/analytics/R07?*',lambda route:route.fulfill(status=status,json={'error':'test'}))
    submit(page)
    expect(page.locator('#analytics-error')).to_contain_text(f'Lỗi {status}:')
    expect(page.locator('#analytics-result')).to_be_hidden()
    expect(page.locator('#r07-chart .chart-segment')).to_have_count(0)


@pytest.mark.parametrize('case',['null_count','negative_count','string_count','duplicate_disease','money_number','money_exponent','money_negative','partial_null_positive','no_sample_nonnull','wrong_period','wrong_id','money_infinity'])
def test_r07_bad_response_not_zero(ui,case):
    from playwright.sync_api import expect
    page,_=ui
    data=analytics.payload('R07',R07_SEED[:2],analytics.DEFAULTS)
    if case in ('null_count','negative_count','string_count'):
        data['rows'][0]['so_dot_tinh']={'null_count':None,'negative_count':-1,'string_count':'3'}[case]
    elif case=='duplicate_disease':data['rows'][1]['ma_benh']=data['rows'][0]['ma_benh']
    elif case=='money_number':data['rows'][0]['tb_tien_kham']=1.0
    elif case=='money_exponent':data['rows'][0]['tb_tien_kham']='1e3'
    elif case=='money_negative':data['rows'][0]['tb_tien_kham']='-1.00'
    elif case=='partial_null_positive':data['rows'][0]['min_tong']=None
    elif case=='no_sample_nonnull':data['rows'][0]['so_dot_tinh']=0
    elif case=='wrong_period':data['filters']['end']='2026-10-16'
    elif case=='wrong_id':data['report_id']='R06'
    else:data['rows'][0]['tb_tien_kham']='9'*400+'.00'
    page.route('**/api/analytics/R07?*',lambda route:route.fulfill(json=data))
    select_r07(page);submit(page)
    expect(page.locator('#analytics-error')).to_contain_text('Số tiền vượt khả năng biểu diễn' if case=='money_infinity' else 'không đúng hợp đồng R07')
    expect(page.locator('#analytics-result')).to_be_hidden()
    expect(page.locator('#r07-chart .chart-segment')).to_have_count(0)


def test_r07_network_timeout_stale(ui):
    from playwright.sync_api import expect
    page,_=ui
    select_r07(page)
    page.route('**/api/analytics/R07?*',lambda route:route.abort());submit(page)
    expect(page.locator('#analytics-error')).to_contain_text('Không thể kết nối đến API')
    page.unroute('**/api/analytics/R07?*')
    page.evaluate('''()=>{window.savedFetch=window.fetch;window.fetch=async(...args)=>{
      const r=await window.savedFetch(...args);await new Promise(resolve=>{window.releaseR07=resolve;});return r;
    };}''')
    submit(page);page.wait_for_function('typeof window.releaseR07==="function"')
    page.locator('#analytics-report').select_option('R06');page.evaluate('window.releaseR07()')
    expect(page.locator('#analytics-result')).to_be_hidden()
    expect(page.locator('#r07-chart .chart-segment')).to_have_count(0)
    page.evaluate('window.fetch=window.savedFetch');select_r07(page);page.clock.install()
    page.evaluate('''()=>{window.fetch=(_url,options)=>new Promise((_resolve,reject)=>{
      options.signal.addEventListener('abort',()=>reject(new DOMException('aborted','AbortError')));
    });}''')
    submit(page);expect(page.locator('#analytics-status')).to_have_text('Đang tải R07…')
    page.clock.fast_forward(20001)
    expect(page.locator('#analytics-error')).to_contain_text('Tải báo cáo quá lâu')


def test_r07_desktop_offline(ui):
    from playwright.sync_api import expect
    page,_=ui
    external=[]
    page.route('**/*',lambda route:route.continue_() if route.request.url.startswith('http://127.0.0.1:') else (external.append(route.request.url),route.abort())[-1])
    data=analytics.payload('R07',R07_SEED,analytics.DEFAULTS)
    for width in [1440,1280]:
        page.set_viewport_size({'width':width,'height':900});page.reload();select_r07(page);submit(page)
        expect(page.locator('#analytics-result')).to_be_visible();assert_parity(page,data)
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.screenshot(path=str(OUT/f'r07-{width}.png'),full_page=True)
    assert not external
    page.context.set_offline(True);page.locator('#r07-chart .chart-segment').first.focus()
    expect(page.locator('#r07-chart-detail')).to_contain_text('VND')
    assert_parity(page,data);page.context.set_offline(False)
