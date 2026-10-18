"""CRUD and read-only foundation for visits/treatments on the 11-table schema."""
from werkzeug.exceptions import NotFound
from .db import fetch_all, fetch_one, transaction


def get_record(entity, record_id):
    record = fetch_one(f'SELECT * FROM {entity.table} WHERE {entity.pk}=%s', (record_id,))
    if record is None:
        raise NotFound('Không tìm thấy hồ sơ.')
    return record


def list_records(entity, q='', page=1, per_page=20):
    # Identifiers come exclusively from Entity objects defined in entities.py.
    where, params = '', []
    if q:
        # Treat % and _ literally instead of granting wildcard meaning to user input.
        escaped = q.replace('!', '!!').replace('%', '!%').replace('_', '!_')
        where = f" WHERE ho_ten LIKE %s ESCAPE '!' OR {entity.pk} LIKE %s ESCAPE '!'"
        params = [f'%{escaped}%', f'%{escaped}%']
    total = fetch_one(f'SELECT COUNT(*) AS total FROM {entity.table}' + where, params)['total']
    rows = fetch_all(f'SELECT * FROM {entity.table}' + where +
                     f' ORDER BY ho_ten, {entity.pk} LIMIT %s OFFSET %s',
                     (*params, per_page, (page - 1) * per_page))
    return rows, total


def save_record(entity, values, record_id=None):
    with transaction() as db, db.cursor() as cur:
        if record_id is None:
            columns = [f.name for f in entity.fields]
            cur.execute(f'INSERT INTO {entity.table} ({", ".join(columns)}) '
                        f'VALUES ({", ".join(["%s"] * len(columns))})',
                        [values[c] for c in columns])
        else:
            cur.execute(f'SELECT {entity.pk} FROM {entity.table} WHERE {entity.pk}=%s FOR UPDATE',
                        (record_id,))
            if cur.fetchone() is None:
                raise NotFound('Hồ sơ đã bị xóa.')
            columns = [f.name for f in entity.fields if f.name != entity.pk]
            cur.execute(f'UPDATE {entity.table} SET ' + ', '.join(f'{c}=%s' for c in columns) +
                        f' WHERE {entity.pk}=%s', [values[c] for c in columns] + [record_id])
    return values[entity.pk]


def delete_record(entity, record_id):
    # FK RESTRICT protects history, including concurrent dependent inserts.
    with transaction() as db, db.cursor() as cur:
        cur.execute(f'DELETE FROM {entity.table} WHERE {entity.pk}=%s', (record_id,))
        if cur.rowcount == 0:
            raise NotFound('Hồ sơ không tồn tại hoặc đã được xóa.')


def visits(patient_id=None):
    return fetch_all('''SELECT l.*, bn.ho_ten,
           (SELECT COUNT(*) FROM lan_kham_benh k WHERE k.ma_luot=l.ma_luot) AS so_lan_kham,
           (SELECT COALESCE(SUM(k.tien_kham_chua),0) FROM lan_kham_benh k
            WHERE k.ma_luot=l.ma_luot) AS tong_tien_kham
        FROM luot_den_kham l JOIN benh_nhan bn ON bn.ma_benh_nhan=l.ma_benh_nhan
        WHERE (%s IS NULL OR l.ma_benh_nhan=%s)
        ORDER BY l.ngay_vao_vien DESC, l.ma_luot''', (patient_id, patient_id))


def treatments(patient_id=None):
    return fetch_all('''SELECT d.*, b.ten_benh, bn.ho_ten, bs.ho_ten AS ten_bac_si,
           (SELECT COALESCE(MAX(k.so_thu_tu_trong_dot),0) FROM lan_kham_benh k
            WHERE k.ma_dot=d.ma_dot) AS lan_kham_hien_tai
        FROM dot_dieu_tri d JOIN benh b ON b.ma_benh=d.ma_benh
        JOIN benh_nhan bn ON bn.ma_benh_nhan=d.ma_benh_nhan
        JOIN bac_si bs ON bs.ma_bac_si=d.ma_bac_si
        WHERE (%s IS NULL OR d.ma_benh_nhan=%s)
        ORDER BY d.ngay_bat_dau DESC, d.ma_dot''', (patient_id, patient_id))


def examinations(patient_id):
    return fetch_all('''SELECT k.*, b.ten_benh, bs.ho_ten AS ten_bac_si,
        dt.ma_don, dt.ngay_lap_don,
        (SELECT COALESCE(SUM(ct.so_luong*ct.don_gia_ban),0)
         FROM chi_tiet_don_thuoc ct WHERE ct.ma_don=dt.ma_don) AS tien_thuoc
        FROM lan_kham_benh k JOIN dot_dieu_tri d ON d.ma_dot=k.ma_dot
        JOIN benh b ON b.ma_benh=d.ma_benh
        JOIN bac_si bs ON bs.ma_bac_si=d.ma_bac_si
        LEFT JOIN don_thuoc dt ON dt.ma_lan_kham=k.ma_lan_kham
        WHERE d.ma_benh_nhan=%s ORDER BY k.ngay_kham DESC, k.ma_lan_kham''', (patient_id,))
