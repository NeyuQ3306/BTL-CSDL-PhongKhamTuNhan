"""Independent T01-T15 acceptance: real browser, HTTP and MySQL, fixed hand answers."""
import json
import os
import platform
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, timedelta
from http.client import HTTPConnection
from pathlib import Path
from urllib.parse import urlencode, urlsplit
import pymysql
import pytest
from werkzeug.serving import make_server
from test_week2 import clinical_data, visit
from clinic_app.db import fetch_all, fetch_one, transaction
from tools.quyen_db import connect

OUT = Path('test-artifacts/vuong-acceptance')
pytestmark = pytest.mark.skipif(os.getenv('RUN_BROWSER_TESTS') != '1', reason='Requires real Chromium')


def record(identifier, inputs, expected, actual, mode, images=None):
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / 'cases.json'
    run_id=os.getenv('VUONG_ACCEPTANCE_RUN','manual')
    data = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    data = {key:value for key,value in data.items() if value.get('run_id')==run_id}
    data[identifier] = dict(status='PASS', run_at=datetime.now(timezone(timedelta(hours=7))).isoformat(),
        run_id=run_id,source_sha=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        working_tree=True, python=platform.python_version(), db_name=os.environ['DB_NAME'],
        inputs=inputs, expected=expected, actual=actual, mode=mode, images=images or [])
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2,default=str),encoding='utf-8')


@pytest.fixture
def ui(app, clinical_data):
    from playwright.sync_api import sync_playwright
    assert os.environ['DB_NAME'].endswith('_test')
    server = make_server('127.0.0.1',0,app,threaded=True)
    thread=threading.Thread(target=server.serve_forever,daemon=True); thread.start()
    OUT.mkdir(parents=True,exist_ok=True)
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch()
            page=browser.new_page(viewport={'width':1440,'height':1000},locale='vi-VN')
            errors=[]
            page.on('pageerror',lambda error: errors.append(str(error)))
            yield page, f'http://127.0.0.1:{server.server_port}', browser
            assert not errors,errors
            browser.close()
    finally:
        server.shutdown(); thread.join(timeout=5); server.server_close()


def scalar(app,sql,params=()):
    with app.app_context():
        return next(iter(fetch_one(sql,params).values()))


def fill(page,values):
    for key,value in values.items():
        field=page.locator(f'[name="{key}"]')
        if field.evaluate('(x)=>x.tagName')=='SELECT': field.select_option(value)
        else: field.fill(value)


def save(page):
    with page.expect_response(lambda r:r.request.method=='POST') as response:
        page.get_by_role('button',name='Lưu',exact=True).click()
    return response.value.status


def capture(page,name):
    page.screenshot(path=str(OUT/name),full_page=True)
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    return name


def payload(index,when='2001-09-28',**updates):
    return visit(index,when,ma_luot=f'AC{index}',ma_lan_kham=f'AK{index}',ma_dot='AD1',
                 tien_kham_chua='100000',**updates)


def browser_visit(page,base,index,when,episode,mode='new'):
    from playwright.sync_api import expect
    page.goto(base+'/visits/new')
    fill(page,dict(ma_luot=f'AC{index}',ma_benh_nhan='W2BN1',ngay_vao_vien=when,
        che_do_dot=mode,ma_lan_kham=f'AK{index}',ngay_kham=when,tien_kham_chua='100000',
        ket_luan='Theo dõi nghiệm thu',ma_y_ta='W2YT1',ngay_ho_tro=when,noi_dung_ho_tro='Tiếp đón'))
    if mode=='new': fill(page,dict(ma_dot=episode,ma_benh='W2B1',ma_bac_si='W2BS'))
    else: page.locator('#episode-picker').select_option(episode)
    assert save(page)==303
    expect(page).to_have_url(base+f'/visits/AC{index}')


def test_acceptance_browser_t01_t04_t08_t12_t14_t15(app,ui):
    from playwright.sync_api import expect
    page,base,_=ui
    for i,day in [(1,'2001-09-28'),(2,'2001-09-29'),(3,'2001-09-30')]:
        browser_visit(page,base,i,day,'AD1','new' if i==1 else 'existing')
    page.goto(base+'/reports/diseases?month=2001-09')
    expect(page.locator('[data-disease="W2B1"] [data-count]')).to_have_text('1')
    with app.app_context():
        sequence=[x['so_thu_tu_trong_dot'] for x in fetch_all("SELECT so_thu_tu_trong_dot FROM lan_kham_benh WHERE ma_dot='AD1' ORDER BY so_thu_tu_trong_dot")]
    assert sequence==[1,2,3]
    record('T01','AD1 khám 28/29/30-09-2001','Q1=1, STT=[1,2,3]',dict(episodes=1,sequence=sequence),'Browser + SQL',[capture(page,'T01-three-visits.png')])
    browser_visit(page,base,4,'2001-10-01','AD1','existing')
    for month in ['2001-09','2001-10']:
        page.goto(base+'/reports/diseases?month='+month)
        expect(page.locator('[data-disease="W2B1"] [data-count]')).to_have_text('1')
    record('T03','AD1 khám cả 09/2001 và 10/2001','Mỗi tháng tính 1 đợt',{'2001-09':1,'2001-10':1},'Browser + JSON',[capture(page,'T03-cross-month.png')])
    page.goto(base+'/treatments/AD1/cure'); fill(page,dict(ngay_khoi='2001-10-01')); assert save(page)==303
    bonuses={}
    for month,amount in [('2001-09',7000000),('2001-10',8000000)]:
        page.goto(base+'/reports/salaries?month='+month)
        expect(page.locator('[data-employee="W2BS"] [data-salary]')).to_have_text(f'{amount:,}'.replace(',','.')+' đ')
        bonuses[month]=amount-7000000
    record('T08','Tái khám 09/2001, khỏi 01/10/2001','Thưởng BS tháng 9=0, tháng 10=1.000.000',bonuses,'Browser + SQL',[capture(page,'T08-cure-month.png')])
    browser_visit(page,base,5,'2001-10-02','AD2')
    page.goto(base+'/reports/diseases?month=2001-10')
    expect(page.locator('[data-disease="W2B1"] [data-count]')).to_have_text('2')
    assert scalar(app,"SELECT COUNT(*) n FROM dot_dieu_tri WHERE ma_benh_nhan='W2BN1' AND ma_benh='W2B1'")==2
    record('T02','AD1 khỏi 01/10, AD2 tái mắc 02/10/2001','Hai mã đợt, Q1 tháng 10=2',dict(episodes=['AD1','AD2'],q1=2),'Browser + SQL',[capture(page,'T02-recurrence.png')])
    page.goto(base+'/visits/AC5/examinations/new')
    fill(page,dict(ma_dot='AD3',ma_benh='W2B2',ma_bac_si='W2BS',ma_lan_kham='AK6',ngay_kham='2001-10-02',tien_kham_chua='50000',ket_luan='Bệnh thứ hai'))
    assert save(page)==303
    with app.app_context():
        owners=fetch_all("SELECT k.ma_dot,d.ma_benh_nhan FROM lan_kham_benh k JOIN dot_dieu_tri d ON d.ma_dot=k.ma_dot WHERE k.ma_luot='AC5' ORDER BY k.ma_dot")
    assert owners==[dict(ma_dot='AD2',ma_benh_nhan='W2BN1'),dict(ma_dot='AD3',ma_benh_nhan='W2BN1')]
    record('T04','AC5 thêm bệnh W2B2, đợt AD3','Hai bệnh/đợt, cùng bệnh nhân',owners,'Browser + SQL',[capture(page,'T04-two-diseases.png')])
    page.goto(base+'/visits/AC5/support?ma_y_ta=W2YT1')
    fill(page,dict(noi_dung_ho_tro='Tiếp đón, đo huyết áp, theo dõi')); assert save(page)==303
    page.goto(base+'/visits/AC5/support')
    fill(page,dict(ma_y_ta='W2YT2',ngay_ho_tro='2001-10-02',noi_dung_ho_tro='Y tá thứ hai')); assert save(page)==303
    page.goto(base+'/reports/salaries?month=2001-10')
    for key,amount in [('W2YT1','5.400.000 đ'),('W2YT2','5.200.000 đ')]:
        expect(page.locator(f'[data-employee="{key}"] [data-salary]')).to_have_text(amount)
    assert scalar(app,"SELECT COUNT(*) n FROM ho_tro WHERE ma_luot='AC5'")==2
    record('T09','YT1 nhiều việc AC5, thêm YT2; YT1 còn hỗ trợ AC4','AC5 mỗi y tá 1 khoản 200.000',dict(pairs_ac5=2,yt1_oct_bonus=400000,yt2_oct_bonus=200000),'Browser + SQL',[capture(page,'T09-nurse-bonuses.png')])
    history=page.request.get(base+'/reports/history?patient_id=W2BN1&format=json').json()
    exam=next(x for x in history['examinations'] if x['ma_lan_kham']=='AK1')
    assert exam['ma_don'] is None and int(exam['tien_thuoc'])==0
    record('T10','AK1 không kê đơn','Hợp lệ, tiền thuốc 0',dict(order=exam['ma_don'],medicine=exam['tien_thuoc']),'Browser JSON + SQL')
    page.goto(base+'/examinations/AK5/prescription')
    fill(page,dict(ma_don='AR1'))
    for i,key in enumerate(['W2T1','W2T2']):
        page.locator('[name="ma_thuoc"]').nth(i).select_option(key)
        page.locator('[name="so_luong"]').nth(i).fill(str(i+2))
        page.locator('[name="lieu_dung"]').nth(i).fill('Sáng' if i==0 else 'Tối')
    quantity_status=[]
    for number in ['0','-1']:
        page.locator('[name="so_luong"]').first.fill(number)
        page.locator('form').evaluate('(f)=>f.noValidate=true')
        assert save(page)==422
        expect(page.get_by_role('alert')).to_contain_text('Số lượng thuốc')
        expect(page.locator('[name="so_luong"]').first).to_have_value(number)
        assert scalar(app,"SELECT COUNT(*) n FROM don_thuoc WHERE ma_don='AR1'")==0
        quantity_status.append(dict(input=number,status=422,header_count=0))
    page.locator('[name="so_luong"]').first.fill('2'); assert save(page)==303
    with app.app_context():
        with transaction() as db,db.cursor() as cur: cur.execute("UPDATE thuoc SET gia_hien_tai=9999 WHERE ma_thuoc='W2T1'")
    page.reload(); expect(page.get_by_role('heading',name='Tổng: 8.000 đ',exact=True)).to_be_visible()
    page.goto(base+'/reports/revenue?month=2001-10')
    expect(page.locator('[data-revenue="consultation"]')).to_have_text('250.000 đ')
    expect(page.locator('[data-revenue="medicine"]')).to_have_text('8.000 đ')
    expect(page.locator('[data-revenue="total"]')).to_have_text('258.000 đ')
    record('T11','AR1: 2×1.000+3×2.000; giá W2T1 đổi 9.999; AC5 có 2 y tá','Thuốc=8.000, khám=250.000, doanh thu=258.000',dict(medicine=8000,fees=250000,total=258000),'Browser + SQL',[capture(page,'T11-historical-prices.png')])
    page.goto(base+'/visits/new')
    # Deliberately bypass browser limits to verify the server boundary and rollback.
    data=payload(6,'2001-10-03',che_do_dot='existing')
    data['tien_kham_chua']='-1'; data['csrf_token']=page.locator('[name="csrf_token"]').input_value()
    response=page.request.post(base+'/visits/new',form=data,max_redirects=0)
    assert response.status==422 and 'Tiền khám' in response.text()
    assert scalar(app,"SELECT COUNT(*) n FROM luot_den_kham WHERE ma_luot='AC6'")==0
    page.goto(base+'/visits/AC5/close'); fill(page,dict(ngay_ra_vien='2001-10-01'))
    assert save(page)==422
    expect(page.get_by_role('alert')).to_contain_text('Ngày ra viện không được trước ngày vào viện')
    assert scalar(app,"SELECT ngay_ra_vien FROM luot_den_kham WHERE ma_luot='AC5'") is None
    record('T12','Số lượng 0/-1; tiền khám -1; ngày ra 01/10 trước ngày vào 02/10','422, giữ dữ liệu nhập, không ghi một phần',dict(quantity=quantity_status,negative_fee=422,visit_ac6=0,invalid_close=422,end_date=None),'Browser + tampered HTTP + SQL',[capture(page,'T12-invalid-close.png')])
    fill(page,dict(ngay_ra_vien='2001-10-02')); assert save(page)==303
    page.goto(base+'/reports/revenue?month=2000-12')
    expect(page.locator('[data-revenue="total"]')).to_have_text('0 đ')
    empty=page.request.get(base+'/reports/diseases?month=2000-12&format=json').json()
    assert empty['rows']==[] and empty['total']==0
    page.goto(base+'/reports/salaries?month=2000-12')
    expect(page.locator('[data-employee="W2BS"] [data-salary]')).to_have_text('7.000.000 đ')
    expect(page.locator('[data-employee="W2YT1"] [data-salary]')).to_have_text('5.000.000 đ')
    record('T14','Tháng 12/2000 không có dữ liệu khám','Q1 rỗng, doanh thu 0, lương cơ bản',dict(diseases=empty,total_revenue=0,doctor=7000000,nurse=5000000),'Browser + JSON',[capture(page,'T14-empty-month.png')])
    history=page.request.get(base+'/reports/history?patient_id=W2BN1&month=2000-12&format=json').json()
    counts={k:len(history[k]) for k in ['visits','treatments','examinations','medicines','support','current']}
    assert counts==dict(visits=5,treatments=3,examinations=6,medicines=2,support=6,current=2)
    assert next(x for x in history['treatments'] if x['ma_dot']=='AD1')['lan_kham_hien_tai']==4
    page.goto(base+'/reports/history?patient_id=W2BN1')
    expect(page.locator('[data-history-fees]')).to_have_text('550.000 đ')
    expect(page.locator('[data-history-medicines]')).to_have_text('8.000 đ')
    for width in [1440,390,320]:
        page.set_viewport_size(dict(width=width,height=1000))
        capture(page,f'T15-history-{width}.png')
    record('T15','W2BN1, thêm month rỗng để kiểm tra toàn lịch sử','5 lượt/3 đợt/6 lần/2 thuốc/6 hỗ trợ/2 đang điều trị, STT AD1=4',dict(counts=counts,sequence_ad1=4,fees=550000,medicines=8000),'Browser + JSON + SQL',['T15-history-1440.png','T15-history-390.png','T15-history-320.png'])


def test_t05_wrong_owner_and_csrf(app,ui):
    page,base,_=ui
    page.goto(base+'/visits/new')
    data=payload(1);data['csrf_token']=page.locator('[name="csrf_token"]').input_value()
    assert page.request.post(base+'/visits/new',form=data,max_redirects=0).status==303
    wrong=payload(2,'2001-09-29',ma_benh_nhan='W2BN2',che_do_dot='existing')
    wrong['csrf_token']=data['csrf_token']
    response=page.request.post(base+'/visits/new',form=wrong,max_redirects=0)
    assert response.status==422 and 'cùng bệnh nhân' in response.text()
    actual={table:scalar(app,f'SELECT COUNT(*) n FROM {table} WHERE {pk}=%s',(key,)) for table,pk,key in
        [('luot_den_kham','ma_luot','AC2'),('lan_kham_benh','ma_lan_kham','AK2'),('dot_dieu_tri','ma_dot','AD1')]}
    assert actual==dict(luot_den_kham=0,lan_kham_benh=0,dot_dieu_tri=1)
    record('T05','AC2 của W2BN2 tham chiếu AD1 của W2BN1','422; không có AC2/AK2, AD1 giữ nguyên',actual,'Browser HTTP + SQL')
    for token in [None,'invalid']:
        bad={**wrong};bad.pop('csrf_token')
        if token: bad['csrf_token']=token
        assert page.request.post(base+'/visits/new',form=bad,max_redirects=0).status==400
    assert scalar(app,"SELECT COUNT(*) n FROM luot_den_kham WHERE ma_luot='AC2'")==0
    record('CSRF','POST thiếu token hoặc token sai','400, không ghi AC2',dict(statuses=[400,400],visit=0),'Browser HTTP + SQL')


def test_t06_duplicate_keys(app,ui):
    page,base,_=ui
    browser_visit(page,base,1,'2001-09-28','AD1')
    browser_visit(page,base,2,'2001-09-29','AD1','existing')
    # A third visit has another disease, so the duplicate-STT attempt below
    # does NOT also violate UNIQUE(luot,dot). Isolate the two rejection cases.
    page.goto(base+'/visits/new')
    third=payload(3,'2001-09-30'); third.update(ma_dot='AD2',ma_benh='W2B2')
    fill(page,third); assert save(page)==303
    db=connect()
    attempts=[]
    try:
        for name,seq,visit_id,day in [('duplicate_visit_episode',3,'AC2','2001-09-29'),('duplicate_episode_sequence',1,'AC3','2001-09-30')]:
            with db.cursor() as cur:
                with pytest.raises(pymysql.MySQLError) as error:
                    cur.execute("INSERT INTO lan_kham_benh VALUES ('AKBAD',%s,%s,100,'Duplicate','AD1',%s)",(seq,day,visit_id))
                assert error.value.args[0] in (1062,1644)
                attempts.append(dict(kind=name,visit=visit_id,sequence=seq,date=day,mysql_code=error.value.args[0]))
            db.rollback()
        assert scalar(app,"SELECT COUNT(*) n FROM lan_kham_benh WHERE ma_dot='AD1'")==2
        assert scalar(app,"SELECT COUNT(*) n FROM lan_kham_benh WHERE ma_lan_kham='AKBAD'")==0
        record('T06','Trùng (AC2,AD1), trùng (AD1,STT=1)','SQL từ chối, vẫn chỉ có 2 lần khám',dict(attempts=attempts,exam_count=2,rejected_row=0),'Browser setup + direct SQL')
    finally: db.close()


def test_t07_concurrent_http(app,ui):
    page,base,browser=ui
    sessions=[]
    for i in [1,2]:
        context=browser.new_context(); tab=context.new_page();tab.goto(base+'/visits/new')
        body=payload(i)
        body['ma_dot']=f'AD{i}'
        body['csrf_token']=tab.locator('[name="csrf_token"]').input_value()
        cookie='; '.join(x['name']+'='+x['value'] for x in context.cookies())
        sessions.append((context,body,cookie))
    barrier=threading.Barrier(2)
    address=urlsplit(base)
    def send(item):
        _,body,cookie=item
        conn=HTTPConnection(address.hostname,address.port,timeout=20)
        try:
            barrier.wait(timeout=10); started=time.monotonic()
            conn.request('POST','/visits/new',body=urlencode(body),headers={'Content-Type':'application/x-www-form-urlencoded','Cookie':cookie})
            response=conn.getresponse();response.read()
            return dict(status=response.status,started=started,finished=time.monotonic(),visit=body['ma_luot'])
        finally:conn.close()
    try:
        with ThreadPoolExecutor(max_workers=2) as pool: results=list(pool.map(send,sessions))
        assert sorted(x['status'] for x in results)==[303,409]
        counts={table:scalar(app,f'SELECT COUNT(*) n FROM {table} WHERE {pk} LIKE %s',(pattern,)) for table,pk,pattern in
            [('luot_den_kham','ma_luot','AC%'),('dot_dieu_tri','ma_dot','AD%'),('lan_kham_benh','ma_lan_kham','AK%')]}
        assert set(counts.values())=={1}
        assert max(x['started'] for x in results)<min(x['finished'] for x in results)
        record('T07','Hai session CSRF độc lập cùng tạo đợt bệnh W2B1 cho W2BN1, bắt đầu bằng barrier','1×303, 1×409; một lượt/đợt/lần khám; không dữ liệu thừa',dict(requests=results,counts=counts),'Concurrent real HTTP + SQL')
    finally:
        for context,_,_ in sessions:context.close()


def test_t13_partial_prescription_rollback(app,ui):
    page,base,_=ui
    browser_visit(page,base,1,'2001-09-28','AD1')
    page.goto(base+'/examinations/AK1/prescription')
    pairs=[('csrf_token',page.locator('[name="csrf_token"]').input_value()),('ma_don','ARFAIL'),('ngay_lap_don','2001-09-28'),
           ('ma_thuoc','W2T1'),('so_luong','2'),('lieu_dung','Sáng'),
           ('ma_thuoc','ZZMISSING'),('so_luong','1'),('lieu_dung','Tối')]
    response=page.request.post(base+'/examinations/AK1/prescription',data=urlencode(pairs),headers={'Content-Type':'application/x-www-form-urlencoded'},max_redirects=0)
    assert response.status==404 and 'Không tìm thấy thuốc' in response.text()
    counts={table:scalar(app,f'SELECT COUNT(*) n FROM {table} WHERE ma_don=%s',('ARFAIL',)) for table in ['don_thuoc','chi_tiet_don_thuoc']}
    assert set(counts.values())=={0}
    page.goto(base+'/patients/W2BN1/history')
    from playwright.sync_api import expect
    expect(page.locator('[data-history-medicines]')).to_have_text('0 đ')
    record('T13','ARFAIL: W2T1 hợp lệ được ghi trước ZZMissing không tồn tại','404; header và detail đều rollback',dict(http_status=404,counts=counts),'Browser HTTP + SQL',[capture(page,'T13-no-partial-prescription.png')])
