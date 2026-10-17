"""Isolated hand-calculated clinical scenarios, rollback and concurrent requests."""
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from decimal import Decimal
import pytest
from werkzeug.exceptions import HTTPException
from clinic_app import workflows as w, reports as r
from clinic_app.db import transaction, fetch_one, fetch_all
from clinic_app.workflow_validation import money, day, quantity


@pytest.fixture
def clinical_data(app):
    with app.app_context():
        with transaction() as db, db.cursor() as c:
            for key in ['W2BN1','W2BN2']:
                c.execute('INSERT INTO benh_nhan VALUES (%s,%s,%s,%s,%s,%s)', (key,'99900000000'+key[-1], 'Bệnh nhân thử '+key, '1980-01-01','Hà Nội','0901234567'))
            c.execute('INSERT INTO bac_si VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)', ('W2BS','999000000003','Bác sĩ thử','1960-01-01','Hà Nội','Bậc 1',10,'Nội','Đại học'))
            for i in [1,2]:
                c.execute('INSERT INTO y_ta VALUES (%s,%s,%s,%s,%s,%s,%s,%s)', ('W2YT'+str(i),'99900000001'+str(i),'Y tá thử','1980-01-01','Hà Nội','0901234567','Đại học',5))
            for i in [1,2]:
                c.execute('INSERT INTO benh VALUES (%s,%s)', ('W2B'+str(i),'Bệnh kiểm thử '+str(i)))
                c.execute('INSERT INTO thuoc VALUES (%s,%s,%s,%s)', ('W2T'+str(i),'Thuốc thử '+str(i),'Viên',1000*i))
    yield
    with app.app_context():
        with transaction() as db, db.cursor() as c:
            c.execute("DELETE c FROM chi_tiet_don_thuoc c JOIN don_thuoc p ON p.ma_don=c.ma_don JOIN lan_kham_benh k ON k.ma_lan_kham=p.ma_lan_kham JOIN dot_dieu_tri d ON d.ma_dot=k.ma_dot WHERE d.ma_benh_nhan IN ('W2BN1','W2BN2')")
            c.execute("DELETE p FROM don_thuoc p JOIN lan_kham_benh k ON k.ma_lan_kham=p.ma_lan_kham JOIN dot_dieu_tri d ON d.ma_dot=k.ma_dot WHERE d.ma_benh_nhan IN ('W2BN1','W2BN2')")
            c.execute("DELETE k FROM lan_kham_benh k JOIN dot_dieu_tri d ON d.ma_dot=k.ma_dot WHERE d.ma_benh_nhan IN ('W2BN1','W2BN2')")
            c.execute("DELETE h FROM ho_tro h JOIN luot_den_kham l ON l.ma_luot=h.ma_luot WHERE l.ma_benh_nhan IN ('W2BN1','W2BN2')")
            for table in ['luot_den_kham','dot_dieu_tri','benh_nhan']:
                c.execute(f"DELETE FROM {table} WHERE ma_benh_nhan IN ('W2BN1','W2BN2')")
            c.execute("DELETE FROM bac_si WHERE ma_bac_si='W2BS'")
            c.execute("DELETE FROM y_ta WHERE ma_y_ta IN ('W2YT1','W2YT2')")
            c.execute("DELETE FROM benh WHERE ma_benh IN ('W2B1','W2B2')")
            c.execute("DELETE FROM thuoc WHERE ma_thuoc IN ('W2T1','W2T2')")


def visit(i=1, when='2001-01-30', **changes):
    return dict(dict(ma_luot=f'W2L{i}',ma_benh_nhan='W2BN1',ngay_vao_vien=when,
         che_do_dot='new',ma_dot='W2D1',ma_benh='W2B1',ma_bac_si='W2BS',
         ma_lan_kham=f'W2K{i}',ngay_kham=when,tien_kham_chua='100',ket_luan='Theo dõi',
         ma_y_ta='W2YT1',ngay_ho_tro=when,noi_dung_ho_tro='Tiếp đón'), **changes)


def expect_error(status, fn, *args):
    with pytest.raises(HTTPException) as exc:
        fn(*args)
    assert exc.value.code == status


def test_reports_hand_calculated(app, clinical_data):
    with app.app_context():
        w.create_visit(visit())
        w.create_visit(visit(2,'2001-01-31',che_do_dot='existing',tien_kham_chua='150'))
        w.create_visit(visit(3,'2001-02-01',che_do_dot='existing',tien_kham_chua='200'))
        w.cure('W2D1',{'ngay_khoi':'2001-02-02'})
        w.create_visit(visit(4,'2001-02-03',ma_dot='W2D2',tien_kham_chua='300'))
        w.add_examination('W2L4',visit(5,'2001-02-03',ma_dot='W2D3',ma_benh='W2B2',tien_kham_chua='50'))
        w.record_support('W2L4',dict(ma_y_ta='W2YT1',ngay_ho_tro='2001-02-03',noi_dung_ho_tro='Tiếp đón, cấp thuốc, theo dõi'))
        w.record_support('W2L4',dict(ma_y_ta='W2YT2',ngay_ho_tro='2001-02-03',noi_dung_ho_tro='Tiêm thuốc'))
        w.prescribe('W2K3',{'ma_don':'W2P1','ngay_lap_don':'2001-02-01'},[
            dict(ma_thuoc='W2T1',so_luong='2',lieu_dung='Sáng'),dict(ma_thuoc='W2T2',so_luong='3',lieu_dung='Tối')])
        # Changing the catalog after prescribing must not change historical revenue.
        with transaction() as db, db.cursor() as c:
            c.execute("UPDATE thuoc SET gia_hien_tai=9999 WHERE ma_thuoc='W2T1'")
        assert r.diseases('2001-01')['rows'][0]['so_dot_mac'] == 1
        assert [(x['ma_benh'],x['so_dot_mac']) for x in r.diseases('2001-02')['rows']] == [('W2B1',2),('W2B2',1)]
        assert r.revenue('2001-01')['total'] == 250
        assert r.revenue('2001-02') == dict(month='2001-02',consultation=Decimal(550),medicine=Decimal(8000),total=Decimal(8550))
        jan, feb = r.salaries('2001-01'), r.salaries('2001-02')
        assert next(x for x in jan['doctors'] if x['ma_nhan_vien']=='W2BS')['tong_luong'] == 7000000
        assert next(x for x in feb['doctors'] if x['ma_nhan_vien']=='W2BS')['tong_luong'] == 8000000
        assert next(x for x in feb['nurses'] if x['ma_nhan_vien']=='W2YT1')['tong_luong'] == 5400000
        assert next(x for x in feb['nurses'] if x['ma_nhan_vien']=='W2YT2')['tong_luong'] == 5200000
        assert r.revenue('2001-03')['total'] == 0
        assert r.diseases('2001-03')['rows'] == []
        assert all(x['tong_luong']==7000000 for x in r.salaries('2001-03')['doctors'])
        hist = r.history('W2BN1')
        assert len(hist['examinations']) == 5 and len(hist['medicines']) == 2 and len(hist['support']) == 5
        assert {x['ma_dot'] for x in hist['current']} == {'W2D2','W2D3'}
        assert next(x for x in hist['treatments'] if x['ma_dot']=='W2D1')['lan_kham_hien_tai'] == 3
        assert r.history('W2BN2')['examinations'] == []


@pytest.mark.parametrize('changes,status', [({'ma_y_ta':'ABSENT'},404),({'ngay_kham':'2001-01-29'},422),
    ({'tien_kham_chua':'-1'},422),({'ma_bac_si':'ABSENT'},404),({'ngay_ho_tro':'2001-01-29'},422)])
def test_atomic_visit_rollback(app,clinical_data,changes,status):
    with app.app_context():
        expect_error(status,w.create_visit,visit(**changes))
        for table,key in [('luot_den_kham','ma_luot'),('dot_dieu_tri','ma_dot'),('lan_kham_benh','ma_lan_kham')]:
            assert fetch_one(f"SELECT COUNT(*) n FROM {table} WHERE {key} LIKE 'W2%'")['n'] == 0


def test_clinical_constraints(app,clinical_data):
    with app.app_context():
        w.create_visit(visit())
        expect_error(409,w.create_visit,visit(2,ma_dot='W2D2'))
        expect_error(422,w.create_visit,visit(2,ma_benh_nhan='W2BN2',che_do_dot='existing'))
        expect_error(409,w.add_examination,'W2L1',visit(2,che_do_dot='existing'))
        expect_error(422,w.create_visit,visit(2,'2001-01-29',che_do_dot='existing'))
        expect_error(422,w.cure,'W2D1',dict(ngay_khoi='2001-01-29'))
        expect_error(422,w.close_visit,'W2L1',dict(ngay_ra_vien='2001-01-29'))
        expect_error(409,w.record_support,'W2L1',dict(ma_y_ta='W2YT1',ngay_ho_tro='2001-01-31',noi_dung_ho_tro='Thay ngày'))
        w.close_visit('W2L1',dict(ngay_ra_vien='2001-01-30'))
        expect_error(409,w.add_examination,'W2L1',visit(2,ma_dot='W2D2',ma_benh='W2B2'))
        expect_error(409,w.close_visit,'W2L1',dict(ngay_ra_vien='2001-01-30'))
        w.cure('W2D1',dict(ngay_khoi='2001-01-31'))
        expect_error(409,w.cure,'W2D1',dict(ngay_khoi='2001-02-01'))
        expect_error(409,w.create_visit,visit(2,'2001-02-01',che_do_dot='existing'))
        expect_error(409,w.create_visit,visit(2,'2001-01-31',ma_dot='W2D2'))
        w.create_visit(visit(2,'2001-02-01',ma_dot='W2D2'))
        assert fetch_one("SELECT COUNT(*) n FROM dot_dieu_tri WHERE ma_benh_nhan='W2BN1'")['n'] == 2


def test_prescription_rollback(app,clinical_data):
    with app.app_context():
        w.create_visit(visit())
        data=dict(ma_don='W2P1',ngay_lap_don='2001-01-30')
        good=dict(ma_thuoc='W2T1',so_luong='2',lieu_dung='Sáng')
        # First detail inserted, second FK target missing: rollback header AND detail.
        expect_error(404,w.prescribe,'W2K1',data,[good,dict(ma_thuoc='ZZMISSING',so_luong='1',lieu_dung='Tối')])
        assert fetch_one("SELECT COUNT(*) n FROM don_thuoc WHERE ma_don='W2P1'")['n'] == 0
        assert fetch_one("SELECT COUNT(*) n FROM chi_tiet_don_thuoc WHERE ma_don='W2P1'")['n'] == 0
        expect_error(422,w.prescribe,'W2K1',data,[])
        expect_error(422,w.prescribe,'W2K1',data,[good,good])
        expect_error(422,w.prescribe,'W2K1',dict(data,ngay_lap_don='2001-01-31'),[good])
        w.prescribe('W2K1',data,[good])
        expect_error(409,w.prescribe,'W2K1',dict(data,ma_don='W2P2'),[good])


def test_concurrent_episode_and_sequence(app,clinical_data):
    def submit(data):
        with app.app_context():
            try:
                return w.create_visit(data)
            except HTTPException as exc:
                return exc.code
    with ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(submit,[visit(1,ma_dot='W2D1'),visit(2,ma_dot='W2D2')]))
    assert sum(isinstance(x,str) for x in results)==1 and results.count(409)==1
    with app.app_context():
        episode=fetch_one("SELECT ma_dot FROM dot_dieu_tri WHERE ma_benh_nhan='W2BN1'")['ma_dot']
    with ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(submit,[visit(3,'2001-01-31',ma_dot=episode,che_do_dot='existing'),visit(4,'2001-01-31',ma_dot=episode,che_do_dot='existing')]))
    assert all(isinstance(x,str) for x in results)
    with app.app_context():
        assert [x['so_thu_tu_trong_dot'] for x in fetch_all('SELECT so_thu_tu_trong_dot FROM lan_kham_benh WHERE ma_dot=%s ORDER BY so_thu_tu_trong_dot',(episode,))] == [1,2,3]


def test_routes_and_json(client,token,clinical_data):
    for path in ['/visits/new','/reports/diseases','/reports/salaries','/reports/revenue','/reports/history']:
        assert client.get(path).status_code == 200
    data=visit();data['csrf_token']=token
    assert client.post('/visits/new',data=data).status_code == 303
    assert client.get('/visits/W2L1').status_code == 200
    for path in ['/visits/W2L1/examinations/new','/visits/W2L1/support','/visits/W2L1/close','/treatments/W2D1/cure','/examinations/W2K1/prescription']:
        assert client.get(path).status_code == 200
    # Malformed multi-row submission returns a readable form error and preserves values.
    assert client.post('/examinations/W2K1/prescription',data=dict(csrf_token=token,ma_don='W2P1',ngay_lap_don='2001-01-30',ma_thuoc=['W2T1','W2T2'],so_luong=['2'],lieu_dung=['Sáng'])).status_code == 422
    assert client.post('/examinations/W2K1/prescription',data=dict(csrf_token=token,ma_don='W2P1',ngay_lap_don='2001-01-30',ma_thuoc='W2T1',so_luong='2',lieu_dung='Sáng')).status_code == 303
    assert client.get('/prescriptions/W2P1').status_code == 200
    assert client.get('/patients/W2BN1/history').status_code == 200
    hist=client.get('/reports/history?patient_id=W2BN1&format=json').json
    assert hist['examinations'][0]['ngay_kham']=='2001-01-30'
    assert hist['medicines'][0]['don_gia_ban']=='1000'
    revenue=client.get('/reports/revenue?month=2001-01&format=json').json
    assert revenue['total']=='2100'
    assert client.get("/reports/revenue?month=2001-01'+OR+1=1").status_code==400
    assert client.get('/reports/history?patient_id=ABSENT').status_code==404
    assert client.post('/visits/W2L1/close',data={'ngay_ra_vien':'2001-01-30'}).status_code==400
    assert client.post('/visits/new',data=data).status_code==409


@pytest.mark.parametrize('value',['-1','NaN','Infinity','1.1','1e3','1000000000000','',None])
def test_invalid_money(value):
    expect_error(422,money,value)


@pytest.mark.parametrize('value',['0','-1','1.5','2147483648','',None])
def test_invalid_quantity(value):
    expect_error(422,quantity,value)


@pytest.mark.parametrize('value',['2001-02-29','2999-01-01','2001-1-01',None])
def test_invalid_day(value):
    expect_error(422,day,value)


@pytest.mark.parametrize('month',['','2026-13','2026-00','2026-1','9999-12',"' OR 1=1"])
def test_invalid_month(month):
    expect_error(400,r.month_range,month)


def test_month_boundaries(monkeypatch):
    monkeypatch.setattr(r,'today_vn',lambda: date(2026,10,17))
    assert r.month_range()==('2026-10',date(2026,10,1),date(2026,10,18))
    assert r.month_range('2025-12')[2]==date(2026,1,1)
    assert r.month_range('2024-02')[2]==date(2024,3,1)
