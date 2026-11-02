"""R01-R07: independent seed oracle, explicit adversarial history, rollback."""
import os
from datetime import date
import pytest
from tools.quyen_db import connect, statements, ROOT
from tools.analytics_sql import run
from tools.analytics_oracle import seed_rows, expected, canonical


@pytest.fixture
def analytics_db():
    if os.getenv('RUN_MYSQL_TESTS') != '1':
        pytest.skip('Set RUN_MYSQL_TESTS=1 for MySQL analytics tests')
    if not os.getenv('DB_NAME', '').endswith('_test'):
        pytest.fail('Use an isolated *_test database')
    db = connect()
    try:
        yield db
    finally:
        db.rollback()
        db.close()


@pytest.mark.parametrize('start,end,as_of,threshold', [
    ('2026-07-01','2026-10-15','2026-10-14',14),
    ('2026-07-01','2026-08-01','2026-07-31',0),
    ('2026-08-01','2026-09-01','2026-08-31',7),
    ('2026-09-01','2026-10-01','2026-09-30',14),
    ('2026-10-01','2026-10-15','2026-10-14',30),
    ('2026-10-14','2026-10-15','2026-10-14',0),
    ('1999-01-01','1999-02-01','1999-01-31',0),
])
def test_seed_oracle(analytics_db, start, end, as_of, threshold):
    actual = run(analytics_db,start,end,as_of,threshold)
    wanted = expected(seed_rows(),start,end,as_of,threshold)
    for name in wanted:
        assert canonical(actual[name]) == canonical(wanted[name]), name


def test_standalone_file_matches_runner(analytics_db):
    outputs = []
    with analytics_db.cursor() as c:
        for sql in statements((ROOT/'database/analytics_queries.sql').read_text(encoding='utf-8')):
            c.execute(sql)
            if c.description:
                outputs.append(c.fetchall())
    wanted = run(analytics_db,'2026-07-01','2026-10-15','2026-10-14',14)
    assert len(outputs) == 7
    for actual, name in zip(outputs,wanted):
        assert canonical(actual) == canonical(wanted[name])


@pytest.mark.parametrize('args', [
    ('2026-02-30','2026-03-01','2026-03-01',14),
    ('2026-10-15','2026-10-15','2026-10-14',14),
    ('2026-10-16','2026-10-15','2026-10-14',14),
    ('2026-07-01','2026-10-15',"2026-10-14'; DROP TABLE benh; --",14),
    ('2026-07-01','2026-10-15','2026-10-14',-1),
    ('2026-07-01','2026-10-15','2026-10-14',True),
    ('2026-07-01','2026-10-15','2026-10-14',1.5),
    ('2026-07-01','2026-10-15','2026-10-14',36501),
])
def test_bad_parameters_before_database_access(args):
    with pytest.raises(ValueError):
        run(None,*args)


@pytest.fixture
def edge_db(analytics_db):
    with analytics_db.cursor() as c:
        c.execute("INSERT INTO benh_nhan VALUES ('QAP','QA-CMT-01','Analytics fixture','1986-03-01','Test','0900000000')")
        c.execute("INSERT INTO benh VALUES ('QAB','Analytics fixture disease'),('QAB2','Analytics second disease')")
        def episode(eid,day,disease='QAB'):
            c.execute("INSERT INTO dot_dieu_tri VALUES (%s,%s,NULL,'Đang điều trị','QAP',%s,'BS001')",(eid,day,disease))
        def visit(vid,day):
            c.execute("INSERT INTO luot_den_kham VALUES (%s,%s,NULL,'QAP')",(vid,day))
        def exam(kid,seq,day,fee,eid,vid):
            c.execute("INSERT INTO lan_kham_benh VALUES (%s,%s,%s,%s,'Fixture',%s,%s)",(kid,seq,day,fee,eid,vid))
        def cure(eid,day):
            c.execute("UPDATE dot_dieu_tri SET ngay_khoi=%s,trang_thai='Đã khỏi' WHERE ma_dot=%s",(day,eid))
        episode('QAD0','2004-01-01');visit('QAL0','2004-01-01')
        exam('QAK0',1,'2004-01-01',50,'QAD0','QAL0');cure('QAD0','2004-01-02')
        episode('QAD1','2004-02-28');visit('QAL1','2004-02-28')
        exam('QAK1',1,'2004-02-28',100,'QAD1','QAL1')
        visit('QAL2','2004-02-29');exam('QAK2',2,'2004-02-29',200,'QAD1','QAL2')
        # Two diseases and two nurses on one visit must not multiply intake/cost.
        episode('QADX','2004-02-28','QAB2');exam('QAKX',1,'2004-02-28',40,'QADX','QAL1')
        c.execute("INSERT INTO ho_tro VALUES ('QAL1','YT001','Fixture','2004-02-28'),('QAL1','YT002','Fixture','2004-02-28')")
        c.execute("INSERT INTO don_thuoc VALUES ('QARX','2004-02-29','QAK2')")
        c.execute("INSERT INTO chi_tiet_don_thuoc VALUES ('QARX','T001',2,'Fixture',1000),('QARX','T002',3,'Fixture',2000)")
        c.execute("UPDATE thuoc SET gia_hien_tai=999999 WHERE ma_thuoc='T001'")
        # Exam-only day: arrival was Feb 29; exam on March 1.
        visit('QAL3','2004-02-29');exam('QAK3',3,'2004-03-01',300,'QAD1','QAL3')
        cure('QAD1','2004-03-02')
        episode('QAD2','2004-03-03');visit('QAL4','2004-03-03')
        exam('QAK4',1,'2004-03-03',400,'QAD2','QAL4');cure('QAD2','2004-03-04')
        episode('QAD3','2004-03-05')
    yield analytics_db


def row(rows,key,value):
    return next(x for x in rows if x[key] == value)


def test_explicit_edge_results(edge_db):
    feb = run(edge_db,'2004-02-28','2004-03-01','2004-02-29',0)
    age = row(feb['R01'],'ma_benh','QAB')
    assert (age['nhom_tuoi'],age['so_dot'],age['so_benh_nhan']) == ('6–17',1,1)
    daily = {x['ngay'].isoformat():(x['so_luot'],x['so_benh_nhan_tiep_nhan'],x['so_lan_kham']) for x in feb['R02']}
    assert daily == {'2004-02-28':(1,1,2),'2004-02-29':(2,1,1)}
    doctor = row(feb['R03'],'ma_bac_si','BS001')
    assert (doctor['so_lan_kham'],doctor['so_dot'],doctor['so_benh_nhan']) == (3,2,1)
    assert [(x['ma_thuoc'],x['so_don'],int(x['tong_so_luong'])) for x in feb['R04']] == [('T001',1,2),('T002',1,3)]
    assert [x['ma_dot'] for x in feb['R05']] == ['QAD1']
    historical = row(feb['R06'],'ma_dot','QAD1')
    assert historical['ngay_kham_cuoi'] == date(2004,2,29)
    assert historical['so_ngay_chua_ghi_nhan'] == 0
    march = run(edge_db,'2004-03-01','2004-04-01','2004-03-06',1)
    assert row(march['R01'],'ma_benh','QAB')['nhom_tuoi'] == '18–59'
    day = row(march['R02'],'ngay',date(2004,3,1))
    assert (day['so_luot'],day['so_lan_kham']) == (0,1)
    assert [(x['ma_dot'],x['ngay_khoi_truoc'].isoformat()) for x in march['R05']] == [('QAD2','2004-03-02'),('QAD3','2004-03-04')]
    pending = row(march['R06'],'ma_dot','QAD3')
    assert (pending['chua_co_lan_kham'],pending['ngay_kham_cuoi'],pending['so_ngay_chua_ghi_nhan']) == (1,None,1)
    cost = row(march['R07'],'ma_benh','QAB')
    assert (cost['so_dot_tinh'],cost['so_dot_loai'],cost['tb_tien_kham'],cost['tb_tien_thuoc'],cost['tb_tong'],cost['min_tong'],cost['max_tong']) == (2,0,500,4000,4500,400,8600)
    cure_day = run(edge_db,'2004-03-01','2004-03-02','2004-03-02',0)
    assert 'QAD1' not in {x['ma_dot'] for x in cure_day['R06']}
    assert cure_day['R07'] == []


@pytest.mark.parametrize('fault',['empty_order','sequence_gap','no_exams'])
def test_incomplete_cost_records_are_excluded(edge_db,fault):
    with edge_db.cursor() as c:
        if fault in ('empty_order','sequence_gap'):
            c.execute("DELETE FROM chi_tiet_don_thuoc WHERE ma_don='QARX'")
        if fault == 'sequence_gap':
            c.execute("DELETE FROM don_thuoc WHERE ma_don='QARX'")
            c.execute("DELETE FROM lan_kham_benh WHERE ma_lan_kham='QAK2'")
        if fault == 'no_exams':
            c.execute("DELETE FROM lan_kham_benh WHERE ma_lan_kham='QAK4'")
    result = run(edge_db,'2004-03-01','2004-04-01','2004-03-06',1)
    cost = row(result['R07'],'ma_benh','QAB')
    assert (cost['so_dot_tinh'],cost['so_dot_loai']) == (1,1)
    assert cost['tb_tong'] == (8600 if fault=='no_exams' else 400)


@pytest.mark.parametrize('birth,group',[('1998-03-01','0–5'),('1998-02-28','6–17'),('1944-02-28','60+'),('2005-01-01','Ngày sinh không hợp lệ')])
def test_age_boundaries(edge_db,birth,group):
    with edge_db.cursor() as c:
        c.execute("UPDATE benh_nhan SET ngay_sinh=%s WHERE ma_benh_nhan='QAP'",(birth,))
    actual = run(edge_db,'2004-02-28','2004-02-29','2004-02-28',0)
    assert row(actual['R01'],'ma_benh','QAB')['nhom_tuoi'] == group


def test_read_only_seed_unchanged(analytics_db):
    data = seed_rows()
    with analytics_db.cursor() as c:
        before = {}
        for table in data:
            c.execute('SELECT * FROM '+table)
            before[table] = canonical(c.fetchall())
    run(analytics_db,'2026-07-01','2026-10-15','2026-10-14')
    with analytics_db.cursor() as c:
        for table in data:
            c.execute('SELECT * FROM '+table)
            assert canonical(c.fetchall()) == before[table]
