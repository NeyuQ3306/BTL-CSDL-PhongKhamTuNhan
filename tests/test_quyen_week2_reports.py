"""Independent seed oracle for every patient's Q3 and week-2 report parity."""
import os
from datetime import date
from decimal import Decimal
from collections import Counter, defaultdict
import pytest
from tools.quyen_db import connect, statements, ROOT
from test_quyen_database import seed_rows

ROWS = seed_rows()

def plain(value):
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Decimal):
        return int(value)
    return value

def projected(rows, keys):
    return sorted((tuple(plain(row[key]) for key in keys) for row in rows), key=repr)

def same(actual, expected, keys):
    assert projected(actual, keys) == projected(expected, keys)

def expected_history(patient_id):
    data = ROWS
    patient = next(x for x in data['benh_nhan'] if x['ma_benh_nhan'] == patient_id)
    visits = [x for x in data['luot_den_kham'] if x['ma_benh_nhan'] == patient_id]
    episodes = [dict(x) for x in data['dot_dieu_tri'] if x['ma_benh_nhan'] == patient_id]
    episode_ids = {x['ma_dot'] for x in episodes}
    exams = [x for x in data['lan_kham_benh'] if x['ma_dot'] in episode_ids]
    diseases = {x['ma_benh']: x['ten_benh'] for x in data['benh']}
    doctors = {x['ma_bac_si']: x['ho_ten'] for x in data['bac_si']}
    for row in episodes:
        row.update(ten_benh=diseases[row['ma_benh']], bac_si=doctors[row['ma_bac_si']],
                   lan_kham_hien_tai=max((x['so_thu_tu_trong_dot'] for x in exams if x['ma_dot']==row['ma_dot']), default=0))
    orders = {x['ma_don']: x for x in data['don_thuoc'] if x['ma_lan_kham'] in {k['ma_lan_kham'] for k in exams}}
    drugs = {x['ma_thuoc']: x for x in data['thuoc']}
    medicines = []
    for row in data['chi_tiet_don_thuoc']:
        if row['ma_don'] in orders:
            drug = drugs[row['ma_thuoc']]
            medicines.append(dict(row, **{k: v for k, v in orders[row['ma_don']].items() if k!='ma_don'},
                                  ten_thuoc=drug['ten_thuoc'], don_vi_tinh=drug['don_vi_tinh'],
                                  thanh_tien=row['so_luong']*row['don_gia_ban']))
    nurses = {x['ma_y_ta']:x['ho_ten'] for x in data['y_ta']}
    support = [dict(x, ho_ten=nurses[x['ma_y_ta']]) for x in data['ho_tro']
               if x['ma_luot'] in {v['ma_luot'] for v in visits}]
    return [ [patient], visits, episodes,
            [x for x in episodes if x['trang_thai']=='Đang điều trị'], exams, medicines, support ]

def sql_results(patient_id, month='2026-10'):
    db = connect()
    try:
        output = []
        with db.cursor() as cur:
            for sql in statements((ROOT/'database/queries.sql').read_text(encoding='utf-8')):
                if sql.startswith('SET @ma_benh_nhan'):
                    cur.execute('SET @ma_benh_nhan=%s', (patient_id,))
                elif sql.startswith('SET @thang'):
                    cur.execute('SET @thang=%s', (month+'-01',))
                else:
                    cur.execute(sql)
                if cur.description:
                    output.append(cur.fetchall())
        return output
    finally:
        db.rollback()
        db.close()

def backend():
    if os.getenv('QUYEN_CHECK_WEEK2') != '1':
        return None
    from clinic_app import reports
    return reports

@pytest.mark.parametrize('patient_id', [x['ma_benh_nhan'] for x in ROWS['benh_nhan']])
def test_q3_all_seed_patients(patient_id):
    expected = expected_history(patient_id)
    results = sql_results(patient_id)
    assert len(results) == 11
    groups = [
        list(ROWS['benh_nhan'][0]), list(ROWS['luot_den_kham'][0]),
        list(ROWS['dot_dieu_tri'][0])+['ten_benh','bac_si','lan_kham_hien_tai'],
        ['ma_dot','ten_benh','lan_kham_hien_tai'], list(ROWS['lan_kham_benh'][0]),
        list(ROWS['chi_tiet_don_thuoc'][0])+['ma_lan_kham','ngay_lap_don','ten_thuoc','don_vi_tinh','thanh_tien'],
        list(ROWS['ho_tro'][0])+['ho_ten']]
    for actual, wanted, keys in zip(results[3:10], expected, groups):
        same(actual, wanted, keys)
    reports = backend()
    if reports is not None:
        from clinic_app import create_app
        with create_app({'TESTING':True, 'SECRET_KEY':'oracle-test-key'}).app_context():
            history = reports.history(patient_id)
        actual = [[history['patient']],history['visits'],history['treatments'],
                  history['current'],history['examinations'],history['medicines'],history['support']]
        for row in actual[2]:
            row['bac_si'] = row['ten_bac_si']
        for observed, wanted, keys in zip(actual, expected, groups):
            same(observed, wanted, keys)

@pytest.mark.parametrize('month',['2026-07','2026-08','2026-09','2026-10','2025-12'])
def test_monthly_seed_oracle_and_backend(month):
    data = ROWS
    episodes = {x['ma_dot']:x for x in data['dot_dieu_tri']}
    disease = defaultdict(set)
    for row in data['lan_kham_benh']:
        if row['ngay_kham'].startswith(month):
            disease[episodes[row['ma_dot']]['ma_benh']].add(row['ma_dot'])
    expected_disease = {k:len(v) for k,v in disease.items()}
    doctors = Counter(x['ma_bac_si'] for x in data['dot_dieu_tri'] if x['ngay_khoi'] and x['ngay_khoi'].startswith(month))
    nurses = Counter(x['ma_y_ta'] for x in data['ho_tro'] if x['ngay_ho_tro'].startswith(month))
    exams = sum(x['tien_kham_chua'] for x in data['lan_kham_benh'] if x['ngay_kham'].startswith(month))
    orders = {x['ma_don'] for x in data['don_thuoc'] if x['ngay_lap_don'].startswith(month)}
    drugs = sum(x['so_luong']*x['don_gia_ban'] for x in data['chi_tiet_don_thuoc'] if x['ma_don'] in orders)
    results = sql_results('BN001', month)
    assert {x['ma_benh']:x['so_dot_mac'] for x in results[0]} == expected_disease
    assert results[-1][0] == dict(tien_kham=exams,tien_thuoc=drugs,doanh_thu=exams+drugs)
    reports = backend()
    if reports is None:
        return
    from clinic_app import create_app
    with create_app({'TESTING':True, 'SECRET_KEY':'oracle-test-key'}).app_context():
        report = reports.diseases(month)
        assert {x['ma_benh']:x['so_dot_mac'] for x in report['rows']} == expected_disease
        assert report['total'] == sum(expected_disease.values())
        assert reports.revenue(month) == dict(month=month,consultation=exams,medicine=drugs,total=exams+drugs)
        salaries = reports.salaries(month)
        for kind, source, pk, counts, base, bonus in [
            ('doctors','bac_si','ma_bac_si',doctors,7000000,1000000),
            ('nurses','y_ta','ma_y_ta',nurses,5000000,200000)]:
            assert {x['ma_nhan_vien']:x['tong_luong'] for x in salaries[kind]} == {
                x[pk]:base+bonus*counts[x[pk]] for x in data[source]}
        assert salaries['total'] == sum(x['tong_luong'] for x in salaries['doctors']+salaries['nurses'])


@pytest.fixture
def boundary_db():
    """New clinical history in one transaction; always rollback, never commit."""
    if not os.getenv('DB_NAME', '').endswith('_test'):
        pytest.fail('Boundary tests require an isolated *_test database')
    db = connect()
    try:
        with db.cursor() as c:
            c.execute("INSERT INTO benh_nhan VALUES ('QW2P','998877665544','Quyen boundary','1980-01-01','Test','0900000000')")
            c.execute("INSERT INTO benh_nhan VALUES ('QW2EMPTY','998877665545','Empty history','1980-01-01','Test','0900000001')")
            c.execute("INSERT INTO benh VALUES ('QW2B','Quyen boundary disease')")
            c.execute("INSERT INTO dot_dieu_tri VALUES ('QW2D1','2004-02-28',NULL,'Đang điều trị','QW2P','QW2B','BS001')")
            for i, day in [(1,'2004-02-28'),(2,'2004-02-29'),(3,'2004-03-01')]:
                c.execute("INSERT INTO luot_den_kham VALUES (%s,%s,NULL,'QW2P')", (f'QW2L{i}',day))
                c.execute("INSERT INTO lan_kham_benh VALUES (%s,%s,%s,%s,'Follow-up','QW2D1',%s)",
                          (f'QW2K{i}',i,day,i*100,f'QW2L{i}'))
                c.execute("INSERT INTO ho_tro VALUES (%s,'YT001','Support',%s)",(f'QW2L{i}',day))
            c.execute("INSERT INTO ho_tro VALUES ('QW2L2','YT002','Second nurse','2004-02-29')")
            c.execute("INSERT INTO don_thuoc VALUES ('QW2RX','2004-02-29','QW2K2')")
            c.execute("INSERT INTO chi_tiet_don_thuoc VALUES ('QW2RX','T001',2,'Morning',1000),('QW2RX','T002',3,'Evening',2000)")
            c.execute("UPDATE thuoc SET gia_hien_tai=9999 WHERE ma_thuoc='T001'")
            c.execute("UPDATE dot_dieu_tri SET ngay_khoi='2004-03-01',trang_thai='Đã khỏi' WHERE ma_dot='QW2D1'")
            c.execute("INSERT INTO dot_dieu_tri VALUES ('QW2D2','2004-03-02',NULL,'Đang điều trị','QW2P','QW2B','BS001')")
            c.execute("INSERT INTO luot_den_kham VALUES ('QW2L4','2004-03-02',NULL,'QW2P')")
            c.execute("INSERT INTO lan_kham_benh VALUES ('QW2K4',1,'2004-03-02',400,'Recurrence','QW2D2','QW2L4')")
            c.execute("INSERT INTO ho_tro VALUES ('QW2L4','YT001','Support','2004-03-02')")
        yield db
    finally:
        db.rollback()
        db.close()

def boundary_results(db, month, as_of, patient='QW2P'):
    output = []
    with db.cursor() as c:
        c.execute("SET time_zone='+07:00'")
        # Session-only MySQL clock; exercise the actual CURRENT_DATE expression.
        c.execute("SET timestamp=UNIX_TIMESTAMP(%s)", (as_of+' 12:00:00',))
        for sql in statements((ROOT/'database/queries.sql').read_text(encoding='utf-8')):
            if sql.startswith('SET @thang'):
                c.execute('SET @thang=%s',(month+'-01',))
            elif sql.startswith('SET @ma_benh_nhan'):
                c.execute('SET @ma_benh_nhan=%s',(patient,))
            else:
                c.execute(sql)
            if c.description:
                output.append(c.fetchall())
    return output

@pytest.mark.parametrize('month,as_of,episodes,fees,medicines,cures,supports', [
    ('2004-02','2004-02-28',1,100,0,0,(1,0)),
    ('2004-02','2004-02-29',1,300,8000,0,(2,1)),
    ('2004-02','2004-03-02',1,300,8000,0,(2,1)),
    ('2004-03','2004-03-01',1,300,0,1,(1,0)),
    ('2004-03','2004-03-02',2,700,0,1,(2,0)),
    ('2004-01','2004-03-02',0,0,0,0,(0,0)),
])
def test_period_boundaries(boundary_db, monkeypatch, month, as_of, episodes, fees, medicines, cures, supports):
    result = boundary_results(boundary_db, month, as_of)
    assert {x['ma_benh']:x['so_dot_mac'] for x in result[0]} == ({'QW2B':episodes} if episodes else {})
    assert result[-1][0] == dict(tien_kham=fees,tien_thuoc=medicines,doanh_thu=fees+medicines)
    doctors = {x['ma_bac_si']:x for x in result[1]}
    nurses = {x['ma_y_ta']:x for x in result[2]}
    assert doctors['BS001']['tong_luong'] == 7000000 + cures*1000000
    for nurse, count in zip(('YT001','YT002'),supports):
        assert nurses[nurse]['tong_luong'] == 5000000 + count*200000
    reports = backend()
    if reports is not None:
        from clinic_app import create_app
        monkeypatch.setattr('clinic_app.db.get_db', lambda: boundary_db)
        monkeypatch.setattr(reports,'today_vn',lambda:date.fromisoformat(as_of))
        with create_app({'TESTING':True,'SECRET_KEY':'boundary-test'}).app_context():
            assert reports.revenue(month)['total'] == fees+medicines
            assert {x['ma_benh']:x['so_dot_mac'] for x in reports.diseases(month)['rows']} == ({'QW2B':episodes} if episodes else {})
            salary = reports.salaries(month)
            assert next(x['tong_luong'] for x in salary['doctors'] if x['ma_nhan_vien']=='BS001') == 7000000+cures*1000000
            for nurse, count in zip(('YT001','YT002'),supports):
                assert next(x['tong_luong'] for x in salary['nurses'] if x['ma_nhan_vien']==nurse) == 5000000+count*200000

def test_new_history_and_empty_patient(boundary_db, monkeypatch):
    result = boundary_results(boundary_db,'2004-03','2004-03-02')
    assert result[3][0]['ma_benh_nhan'] == 'QW2P'
    assert len(result[4]) == 4
    assert {x['ma_dot']:x['lan_kham_hien_tai'] for x in result[5]} == {'QW2D1':3,'QW2D2':1}
    assert [(x['ma_dot'],x['lan_kham_hien_tai']) for x in result[6]] == [('QW2D2',1)]
    assert {x['ma_lan_kham']:int(x['tien_kham_chua']) for x in result[7]} == {'QW2K1':100,'QW2K2':200,'QW2K3':300,'QW2K4':400}
    assert {x['ma_thuoc']:int(x['thanh_tien']) for x in result[8]} == {'T001':2000,'T002':6000}
    assert len(result[9]) == 5
    empty = boundary_results(boundary_db,'2004-03','2004-03-02','QW2EMPTY')
    assert len(empty[3]) == 1 and all(not rows for rows in empty[4:10])
    missing = boundary_results(boundary_db,'2004-03','2004-03-02','QW2MISSING')
    assert all(not rows for rows in missing[3:10])
    reports = backend()
    if reports is not None:
        from clinic_app import create_app
        from werkzeug.exceptions import NotFound
        monkeypatch.setattr('clinic_app.db.get_db',lambda:boundary_db)
        with create_app({'TESTING':True,'SECRET_KEY':'boundary-test'}).app_context():
            history = reports.history('QW2P')
            assert {x['ma_dot']:x['lan_kham_hien_tai'] for x in history['treatments']} == {'QW2D1':3,'QW2D2':1}
            assert [x['ma_dot'] for x in history['current']] == ['QW2D2']
            assert len(history['visits']) == 4 and len(history['examinations']) == 4
            assert sum(x['thanh_tien'] for x in history['medicines']) == 8000
            assert len(history['support']) == 5
            empty = reports.history('QW2EMPTY')
            assert empty['patient']['ma_benh_nhan']=='QW2EMPTY'
            assert all(not empty[key] for key in ('visits','treatments','current','examinations','medicines','support'))
            with pytest.raises(NotFound):
                reports.history('QW2MISSING')
