"""Direct MySQL tests: seed oracle, rejected writes, history and rollback."""
import ast
import re
from collections import Counter, defaultdict
import pymysql
import pytest
from tools.quyen_db import connect, statements, ROOT

def seed_rows():
    source=(ROOT/'database/seed.sql').read_text(encoding='utf-8');result={}
    for m in re.finditer(r'INSERT INTO (\w+) \(([^)]+)\) VALUES\s*(.*?);',source,re.S):
        cols=[x.strip() for x in m[2].split(',')]
        result[m[1]]=[dict(zip(cols,v)) for v in ast.literal_eval('['+re.sub(r'\bNULL\b','None',m[3])+']')]
    return result

@pytest.fixture
def db():
    db=connect()
    try: yield db
    finally: db.rollback(); db.close()

@pytest.fixture
def clinical(db):
    with db.cursor() as c:
        c.execute("INSERT INTO benh VALUES ('QB1','Benh test Quyen')")
        for sql in ["INSERT INTO luot_den_kham VALUES ('QL1','2001-01-01',NULL,'BN001')",
          "INSERT INTO dot_dieu_tri VALUES ('QD1','2001-01-01',NULL,'Đang điều trị','BN001','QB1','BS001')",
          "INSERT INTO lan_kham_benh VALUES ('QK1',1,'2001-01-01',100,'Test','QD1','QL1')",
          "INSERT INTO ho_tro VALUES ('QL1','YT001','Test','2001-01-01')"]:c.execute(sql)
    return db

def scalar(db,sql):
    with db.cursor() as c:c.execute(sql);return next(iter(c.fetchone().values()))

def test_seed_and_audit(db):
    rows=seed_rows();assert sum(map(len,rows.values()))==1144
    for table,data in rows.items():assert scalar(db,f'SELECT COUNT(*) FROM {table}')==len(data)
    for sql in statements((ROOT/'database/audit.sql').read_text(encoding='utf-8')):
        with db.cursor() as c:c.execute(sql);assert not c.fetchall(),sql

@pytest.mark.parametrize('month',['2026-07','2026-08','2026-09','2026-10','2025-12'])
def test_reports_python_oracle(db,month):
    rows=seed_rows();episodes={x['ma_dot']:x for x in rows['dot_dieu_tri']};diseases=defaultdict(set)
    for k in rows['lan_kham_benh']:
        if k['ngay_kham'].startswith(month):diseases[episodes[k['ma_dot']]['ma_benh']].add(k['ma_dot'])
    doctors=Counter(x['ma_bac_si'] for x in rows['dot_dieu_tri'] if x['ngay_khoi'] and x['ngay_khoi'].startswith(month))
    nurses=Counter(x['ma_y_ta'] for x in rows['ho_tro'] if x['ngay_ho_tro'].startswith(month))
    exam=sum(x['tien_kham_chua'] for x in rows['lan_kham_benh'] if x['ngay_kham'].startswith(month))
    orders={x['ma_don'] for x in rows['don_thuoc'] if x['ngay_lap_don'].startswith(month)}
    med=sum(x['so_luong']*x['don_gia_ban'] for x in rows['chi_tiet_don_thuoc'] if x['ma_don'] in orders)
    selects=[]
    with db.cursor() as c:
        c.execute("INSERT INTO benh VALUES ('QB1','Benh test Quyen')")
        for sql in statements((ROOT/'database/queries.sql').read_text(encoding='utf-8')):
            if sql.startswith('SET @thang'):sql=f"SET @thang=DATE('{month}-01')"
            c.execute(sql)
            if c.description:selects.append(c.fetchall())
    assert {x['ma_benh']:x['so_dot_mac'] for x in selects[0]}=={k:len(v) for k,v in diseases.items()}
    assert {x['ma_bac_si']:int(x['tong_luong']) for x in selects[1]}=={x['ma_bac_si']:7000000+doctors[x['ma_bac_si']]*1000000 for x in rows['bac_si']}
    assert {x['ma_y_ta']:int(x['tong_luong']) for x in selects[2]}=={x['ma_y_ta']:5000000+nurses[x['ma_y_ta']]*200000 for x in rows['y_ta']}
    assert selects[-1][0]==dict(tien_kham=exam,tien_thuoc=med,doanh_thu=exam+med)
    assert selects[3][0]['ma_benh_nhan']=='BN001'
    assert len(selects[7])==sum(episodes[x['ma_dot']]['ma_benh_nhan']=='BN001' for x in rows['lan_kham_benh'])

@pytest.mark.parametrize('sql',[
 "INSERT INTO dot_dieu_tri VALUES ('QD2','2001-01-02',NULL,'Đang điều trị','BN001','QB1','BS002')",
 "INSERT INTO dot_dieu_tri VALUES ('QD2','2001-01-02','2001-01-03','Đã khỏi','BN002','QB1','BS002')",
 "INSERT INTO lan_kham_benh VALUES ('QK2',3,'2001-01-02',100,'Test','QD1','QL1')",
 "UPDATE dot_dieu_tri SET ma_bac_si='BS002' WHERE ma_dot='QD1'",
 "UPDATE dot_dieu_tri SET ngay_khoi='2000-12-31',trang_thai='Đã khỏi' WHERE ma_dot='QD1'",
 "UPDATE lan_kham_benh SET ma_dot='D0001' WHERE ma_lan_kham='QK1'",
 "UPDATE lan_kham_benh SET ngay_kham='2001-01-02' WHERE ma_lan_kham='QK1'",
 "UPDATE lan_kham_benh SET so_thu_tu_trong_dot=2 WHERE ma_lan_kham='QK1'",
 "UPDATE luot_den_kham SET ma_benh_nhan='BN002' WHERE ma_luot='QL1'",
 "UPDATE luot_den_kham SET ngay_ra_vien='2000-12-31' WHERE ma_luot='QL1'",
 "INSERT INTO ho_tro VALUES ('QL1','YT002','Test','2000-12-31')",
 "INSERT INTO ho_tro VALUES ('QL1','YT001','Duplicate','2001-01-01')",
 "UPDATE ho_tro SET ngay_ho_tro='2001-01-02' WHERE ma_luot='QL1'",
 "INSERT INTO don_thuoc VALUES ('QP1','2001-01-02','QK1')",
 "UPDATE lan_kham_benh SET tien_kham_chua=-1 WHERE ma_lan_kham='QK1'",
 "DELETE FROM benh_nhan WHERE ma_benh_nhan='BN001'",
])
def test_invalid_write(clinical,sql):
    with clinical.cursor() as c,pytest.raises(pymysql.MySQLError):c.execute(sql)

def test_valid_workflow_and_rollback(clinical):
    with clinical.cursor() as c:
        for sql in ["INSERT INTO don_thuoc VALUES ('QP1','2001-01-01','QK1')",
          "INSERT INTO chi_tiet_don_thuoc VALUES ('QP1','T001',2,'Test',1000),('QP1','T002',3,'Test',2000)",
          "UPDATE thuoc SET gia_hien_tai=9999 WHERE ma_thuoc='T001'",
          "UPDATE ho_tro SET noi_dung_ho_tro='Multiple tasks' WHERE ma_luot='QL1'",
          "UPDATE luot_den_kham SET ngay_ra_vien='2001-01-01' WHERE ma_luot='QL1'",
          "UPDATE dot_dieu_tri SET ngay_khoi='2001-01-02',trang_thai='Đã khỏi' WHERE ma_dot='QD1'",
          "INSERT INTO dot_dieu_tri VALUES ('QD2','2001-01-03',NULL,'Đang điều trị','BN001','QB1','BS001')"]:c.execute(sql)
    assert scalar(clinical,"SELECT SUM(so_luong*don_gia_ban) FROM chi_tiet_don_thuoc WHERE ma_don='QP1'")==8000
    assert scalar(clinical,"SELECT COUNT(*) FROM ho_tro WHERE ma_luot='QL1'")==1
    clinical.rollback()
    assert scalar(clinical,"SELECT COUNT(*) FROM dot_dieu_tri WHERE ma_dot IN ('QD1','QD2')")==0

def test_wrong_patient_and_closed_episode(clinical):
    with clinical.cursor() as c:
        c.execute("INSERT INTO luot_den_kham VALUES ('QL2','2001-01-02',NULL,'BN002')")
        with pytest.raises(pymysql.MySQLError):c.execute("INSERT INTO lan_kham_benh VALUES ('QK2',2,'2001-01-02',100,'Test','QD1','QL2')")
        c.execute("UPDATE dot_dieu_tri SET ngay_khoi='2001-01-02',trang_thai='Đã khỏi' WHERE ma_dot='QD1'")
        c.execute("INSERT INTO luot_den_kham VALUES ('QL3','2001-01-01',NULL,'BN001')")
        with pytest.raises(pymysql.MySQLError):c.execute("INSERT INTO lan_kham_benh VALUES ('QK2',2,'2001-01-01',100,'Test','QD1','QL3')")

def test_empty_completed_visit(db):
    with db.cursor() as c:
        c.execute("INSERT INTO luot_den_kham VALUES ('QL0','2001-01-01',NULL,'BN001')")
        with pytest.raises(pymysql.MySQLError):c.execute("UPDATE luot_den_kham SET ngay_ra_vien='2001-01-01' WHERE ma_luot='QL0'")
