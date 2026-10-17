"""Week 2 transactions. Lock the patient first to serialize their clinical writes.

All mutation paths use a current locking read after taking this lock. This avoids
REPEATABLE READ snapshots missing a concurrent episode/examination. Direct SQL
writers must follow the same protocol or use constraints maintained by Quyền.
"""
from werkzeug.exceptions import Conflict, NotFound
from .db import transaction
from . import workflow_validation as v


def one(cur, sql, params=(), missing='Không tìm thấy dữ liệu.'):
    cur.execute(sql, params)
    row = cur.fetchone()
    if row is None:
        raise NotFound(missing)
    return row


def patient_lock(cur, patient):
    return one(cur, 'SELECT * FROM benh_nhan WHERE ma_benh_nhan=%s FOR UPDATE', (patient,), 'Không tìm thấy bệnh nhân.')


def visit_lock(cur, visit_id):
    # Nonlocking read only identifies the immutable owner; reread after patient lock.
    row = one(cur, 'SELECT ma_benh_nhan FROM luot_den_kham WHERE ma_luot=%s', (visit_id,))
    patient_lock(cur, row['ma_benh_nhan'])
    return one(cur, 'SELECT * FROM luot_den_kham WHERE ma_luot=%s FOR UPDATE', (visit_id,))


def episode_lock(cur, episode_id):
    row = one(cur, 'SELECT ma_benh_nhan FROM dot_dieu_tri WHERE ma_dot=%s', (episode_id,))
    patient_lock(cur, row['ma_benh_nhan'])
    return one(cur, 'SELECT * FROM dot_dieu_tri WHERE ma_dot=%s FOR UPDATE', (episode_id,))


def within_visit(visit, day):
    if day < visit['ngay_vao_vien'] or (visit['ngay_ra_vien'] and day > visit['ngay_ra_vien']):
        v.invalid('Ngày phải nằm trong khoảng vào/ra viện của lượt.')


def examination(cur, visit, data):
    exam_id = v.code(data.get('ma_lan_kham'), 'Mã lần khám')
    exam_day = v.day(data.get('ngay_kham'), 'Ngày khám')
    cost = v.money(data.get('tien_kham_chua'))
    conclusion = v.text(data.get('ket_luan'), 'Kết luận')
    within_visit(visit, exam_day)
    if visit['ngay_ra_vien']:
        raise Conflict('Lượt đã kết thúc, không thể thêm lần khám.')
    mode = data.get('che_do_dot')
    episode_id = v.code(data.get('ma_dot'), 'Mã đợt')
    if mode == 'new':
        disease = v.code(data.get('ma_benh'), 'Mã bệnh')
        doctor = v.code(data.get('ma_bac_si'), 'Mã bác sĩ')
        one(cur, 'SELECT ma_benh FROM benh WHERE ma_benh=%s FOR SHARE', (disease,))
        one(cur, 'SELECT ma_bac_si FROM bac_si WHERE ma_bac_si=%s FOR SHARE', (doctor,))
        cur.execute('''SELECT ma_dot FROM dot_dieu_tri WHERE ma_benh_nhan=%s AND ma_benh=%s
            AND (ngay_khoi IS NULL OR ngay_khoi>=%s) FOR UPDATE''',
            (visit['ma_benh_nhan'], disease, exam_day))
        if cur.fetchone():
            raise Conflict('Bệnh đã có đợt đang điều trị hoặc trùng khoảng điều trị. Chọn tái khám; tái mắc phải sau ngày khỏi.')
        cur.execute('''INSERT INTO dot_dieu_tri
            (ma_dot,ngay_bat_dau,ngay_khoi,trang_thai,ma_benh_nhan,ma_benh,ma_bac_si)
            VALUES (%s,%s,NULL,'Đang điều trị',%s,%s,%s)''',
            (episode_id, exam_day, visit['ma_benh_nhan'], disease, doctor))
    elif mode != 'existing':
        v.invalid('Chọn đợt mới hoặc tái khám.')
    episode = one(cur, 'SELECT * FROM dot_dieu_tri WHERE ma_dot=%s FOR UPDATE', (episode_id,))
    if episode['ma_benh_nhan'] != visit['ma_benh_nhan']:
        v.invalid('Lượt và đợt phải thuộc cùng bệnh nhân.')
    if episode['trang_thai'] != 'Đang điều trị':
        raise Conflict('Đợt đã khỏi; tái mắc phải tạo đợt mới.')
    if exam_day < episode['ngay_bat_dau']:
        v.invalid('Ngày khám không được trước ngày bắt đầu đợt.')
    cur.execute('''SELECT k.ma_lan_kham FROM lan_kham_benh k JOIN dot_dieu_tri d ON d.ma_dot=k.ma_dot
        WHERE k.ma_luot=%s AND d.ma_benh=%s FOR UPDATE''', (visit['ma_luot'], episode['ma_benh']))
    if cur.fetchone():
        raise Conflict('Mỗi bệnh chỉ khám một lần trong cùng lượt.')
    cur.execute('SELECT so_thu_tu_trong_dot,ngay_kham FROM lan_kham_benh WHERE ma_dot=%s FOR UPDATE', (episode_id,))
    previous = cur.fetchall()
    if previous and exam_day < max(x['ngay_kham'] for x in previous):
        v.invalid('Tái khám không được trước lần khám đã ghi gần nhất.')
    seq = len(previous) + 1
    if previous and max(x['so_thu_tu_trong_dot'] for x in previous) != len(previous):
        raise Conflict('Thứ tự lần khám cũ không liên tiếp; cần kiểm tra dữ liệu.')
    cur.execute('''INSERT INTO lan_kham_benh
        (ma_lan_kham,so_thu_tu_trong_dot,ngay_kham,tien_kham_chua,ket_luan,ma_dot,ma_luot)
        VALUES (%s,%s,%s,%s,%s,%s,%s)''', (exam_id, seq, exam_day, cost, conclusion, episode_id, visit['ma_luot']))
    return exam_id


def support(cur, visit, data):
    nurse = v.code(data.get('ma_y_ta'), 'Mã y tá')
    day = v.day(data.get('ngay_ho_tro'), 'Ngày hỗ trợ')
    content = v.text(data.get('noi_dung_ho_tro'), 'Nội dung hỗ trợ')
    within_visit(visit, day)
    if visit['ngay_ra_vien']:
        raise Conflict('Lượt đã kết thúc, không thể sửa hỗ trợ.')
    one(cur, 'SELECT ma_y_ta FROM y_ta WHERE ma_y_ta=%s FOR SHARE', (nurse,))
    cur.execute('SELECT ngay_ho_tro FROM ho_tro WHERE ma_luot=%s AND ma_y_ta=%s FOR UPDATE', (visit['ma_luot'], nurse))
    existing = cur.fetchone()
    if existing:
        if day != existing['ngay_ho_tro']:
            raise Conflict('Giữ ngày bắt đầu hỗ trợ đã ghi; chỉ cập nhật nội dung công việc.')
        cur.execute('UPDATE ho_tro SET noi_dung_ho_tro=%s WHERE ma_luot=%s AND ma_y_ta=%s', (content, visit['ma_luot'], nurse))
    else:
        cur.execute('INSERT INTO ho_tro (ma_luot,ma_y_ta,ngay_ho_tro,noi_dung_ho_tro) VALUES (%s,%s,%s,%s)',
                    (visit['ma_luot'], nurse, day, content))


def create_visit(data):
    patient = v.code(data.get('ma_benh_nhan'), 'Mã bệnh nhân')
    visit_id = v.code(data.get('ma_luot'), 'Mã lượt')
    start = v.day(data.get('ngay_vao_vien'), 'Ngày vào viện')
    with transaction() as db, db.cursor() as cur:
        patient = patient_lock(cur, patient)['ma_benh_nhan']
        cur.execute('INSERT INTO luot_den_kham (ma_luot,ngay_vao_vien,ma_benh_nhan) VALUES (%s,%s,%s)', (visit_id, start, patient))
        visit = dict(ma_luot=visit_id, ma_benh_nhan=patient, ngay_vao_vien=start, ngay_ra_vien=None)
        examination(cur, visit, data)
        support(cur, visit, data)
    return visit_id


def add_examination(visit_id, data):
    with transaction() as db, db.cursor() as cur:
        return examination(cur, visit_lock(cur, visit_id), data)


def record_support(visit_id, data):
    with transaction() as db, db.cursor() as cur:
        support(cur, visit_lock(cur, visit_id), data)


def close_visit(visit_id, data):
    end = v.day(data.get('ngay_ra_vien'), 'Ngày ra viện')
    with transaction() as db, db.cursor() as cur:
        visit = visit_lock(cur, visit_id)
        if visit['ngay_ra_vien']:
            raise Conflict('Lượt đã kết thúc.')
        if end < visit['ngay_vao_vien']:
            v.invalid('Ngày ra viện không được trước ngày vào viện.')
        cur.execute('SELECT ngay_kham FROM lan_kham_benh WHERE ma_luot=%s FOR UPDATE', (visit_id,))
        exams = cur.fetchall()
        cur.execute('SELECT ngay_ho_tro FROM ho_tro WHERE ma_luot=%s FOR UPDATE', (visit_id,))
        nurses = cur.fetchall()
        if not exams or not nurses:
            raise Conflict('Lượt hoàn tất phải có lần khám và y tá hỗ trợ.')
        if any(x['ngay_kham'] > end for x in exams) or any(x['ngay_ho_tro'] > end for x in nurses):
            v.invalid('Ngày ra viện không được trước ngày khám hoặc hỗ trợ đã ghi.')
        cur.execute('UPDATE luot_den_kham SET ngay_ra_vien=%s WHERE ma_luot=%s', (end, visit_id))


def cure(episode_id, data):
    end = v.day(data.get('ngay_khoi'), 'Ngày khỏi')
    with transaction() as db, db.cursor() as cur:
        episode = episode_lock(cur, episode_id)
        if episode['trang_thai'] != 'Đang điều trị':
            raise Conflict('Đợt đã được xác nhận khỏi.')
        cur.execute('SELECT ngay_kham FROM lan_kham_benh WHERE ma_dot=%s FOR UPDATE', (episode_id,))
        exams = cur.fetchall()
        if not exams or end < episode['ngay_bat_dau'] or any(x['ngay_kham'] > end for x in exams):
            v.invalid('Ngày khỏi phải từ ngày khám cuối cùng trở đi; đợt phải có lần khám.')
        cur.execute("UPDATE dot_dieu_tri SET ngay_khoi=%s,trang_thai='Đã khỏi' WHERE ma_dot=%s", (end, episode_id))


def prescribe(exam_id, data, lines):
    order_id = v.code(data.get('ma_don'), 'Mã đơn')
    order_day = v.day(data.get('ngay_lap_don'), 'Ngày lập đơn')
    if not isinstance(lines, list) or not 1 <= len(lines) <= 100:
        v.invalid('Đơn thuốc cần 1–100 dòng thuốc.')
    checked = []
    for line in lines:
        checked.append((v.code(line.get('ma_thuoc'), 'Mã thuốc'), v.quantity(line.get('so_luong')), v.text(line.get('lieu_dung'), 'Liều dùng')))
    if len({x[0].casefold() for x in checked}) != len(checked):
        v.invalid('Mỗi thuốc chỉ có một dòng trong đơn.')
    with transaction() as db, db.cursor() as cur:
        owner = one(cur, '''SELECT d.ma_benh_nhan FROM lan_kham_benh k JOIN dot_dieu_tri d ON d.ma_dot=k.ma_dot
            WHERE k.ma_lan_kham=%s''', (exam_id,))
        patient_lock(cur, owner['ma_benh_nhan'])
        exam = one(cur, 'SELECT * FROM lan_kham_benh WHERE ma_lan_kham=%s FOR UPDATE', (exam_id,))
        if order_day != exam['ngay_kham']:
            v.invalid('Ngày lập đơn phải bằng ngày khám (quy ước tích hợp).')
        cur.execute('SELECT ma_don FROM don_thuoc WHERE ma_lan_kham=%s FOR UPDATE', (exam_id,))
        if cur.fetchone():
            raise Conflict('Lần khám đã có đơn thuốc.')
        cur.execute('INSERT INTO don_thuoc (ma_don,ngay_lap_don,ma_lan_kham) VALUES (%s,%s,%s)', (order_id, order_day, exam_id))
        # Stable lock order across patients; price is read at write time, never trusted from the browser.
        for medicine_id, count, usage in sorted(checked):
            medicine = one(cur, 'SELECT ma_thuoc,gia_hien_tai FROM thuoc WHERE ma_thuoc=%s FOR SHARE', (medicine_id,), 'Không tìm thấy thuốc.')
            cur.execute('''INSERT INTO chi_tiet_don_thuoc (ma_don,ma_thuoc,so_luong,lieu_dung,don_gia_ban)
                VALUES (%s,%s,%s,%s,%s)''', (order_id, medicine['ma_thuoc'], count, usage, medicine['gia_hien_tai']))
    return order_id
