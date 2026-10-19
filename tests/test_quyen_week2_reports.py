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
