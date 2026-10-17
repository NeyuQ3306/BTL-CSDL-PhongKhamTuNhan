"""Four required reports. Independent aggregates prevent join multiplication."""
import re
from datetime import date, timedelta
from werkzeug.exceptions import BadRequest
from .db import fetch_all, fetch_one
from .validation import today_vn
from .entities import ENTITIES
from .services import get_record, visits, treatments, examinations


def month_range(month=None):
    today = today_vn()
    month = month if month is not None else today.strftime('%Y-%m')
    try:
        if not re.fullmatch(r'[0-9]{4}-[0-9]{2}', month):
            raise ValueError
        year, number = map(int, month.split('-'))
        if not 1900 <= year <= 9998:
            raise ValueError
        start = date(year, number, 1)
        stop = date(year + (number == 12), number % 12 + 1, 1)
        if (year, number) == (today.year, today.month):
            stop = today + timedelta(days=1)
        return month, start, stop
    except (ValueError, TypeError):
        raise BadRequest('Tháng hợp lệ dạng YYYY-MM, năm từ 1900 đến 9998.')


def diseases(month=None):
    month, start, stop = month_range(month)
    rows = fetch_all('''SELECT b.ma_benh,b.ten_benh,COUNT(DISTINCT d.ma_dot) AS so_dot_mac
        FROM lan_kham_benh k JOIN dot_dieu_tri d ON d.ma_dot=k.ma_dot
        JOIN benh b ON b.ma_benh=d.ma_benh WHERE k.ngay_kham>=%s AND k.ngay_kham<%s
        GROUP BY b.ma_benh,b.ten_benh ORDER BY so_dot_mac DESC,b.ma_benh''', (start, stop))
    return dict(month=month, rows=rows, total=sum(x['so_dot_mac'] for x in rows))


def salaries(month=None):
    month, start, stop = month_range(month)
    doctors = fetch_all('''SELECT bs.ma_bac_si AS ma_nhan_vien,bs.ho_ten,7000000 AS luong_co_ban,
        COALESCE(t.n,0) AS so_lan_thuong,COALESCE(t.n,0)*1000000 AS tien_thuong,
        7000000+COALESCE(t.n,0)*1000000 AS tong_luong
        FROM bac_si bs LEFT JOIN (SELECT ma_bac_si,COUNT(*) n FROM dot_dieu_tri
          WHERE trang_thai='Đã khỏi' AND ngay_khoi>=%s AND ngay_khoi<%s GROUP BY ma_bac_si) t
        ON t.ma_bac_si=bs.ma_bac_si ORDER BY bs.ma_bac_si''', (start, stop))
    nurses = fetch_all('''SELECT y.ma_y_ta AS ma_nhan_vien,y.ho_ten,5000000 AS luong_co_ban,
        COALESCE(t.n,0) AS so_lan_thuong,COALESCE(t.n,0)*200000 AS tien_thuong,
        5000000+COALESCE(t.n,0)*200000 AS tong_luong
        FROM y_ta y LEFT JOIN (SELECT ma_y_ta,COUNT(*) n FROM ho_tro
          WHERE ngay_ho_tro>=%s AND ngay_ho_tro<%s GROUP BY ma_y_ta) t
        ON t.ma_y_ta=y.ma_y_ta ORDER BY y.ma_y_ta''', (start, stop))
    return dict(month=month, doctors=doctors, nurses=nurses,
                total=sum(x['tong_luong'] for x in doctors+nurses))


def revenue(month=None):
    month, start, stop = month_range(month)
    consult = fetch_one('SELECT COALESCE(SUM(tien_kham_chua),0) n FROM lan_kham_benh WHERE ngay_kham>=%s AND ngay_kham<%s', (start, stop))['n']
    medicine = fetch_one('''SELECT COALESCE(SUM(c.so_luong*c.don_gia_ban),0) n
        FROM chi_tiet_don_thuoc c JOIN don_thuoc d ON d.ma_don=c.ma_don
        WHERE d.ngay_lap_don>=%s AND d.ngay_lap_don<%s''', (start, stop))['n']
    return dict(month=month, consultation=consult, medicine=medicine, total=consult+medicine)


def history(patient_id):
    patient = get_record(ENTITIES['patients'], patient_id)
    episode_rows = treatments(patient_id)
    drug_rows = fetch_all('''SELECT c.*,t.ten_thuoc,t.don_vi_tinh,c.so_luong*c.don_gia_ban AS thanh_tien,
        p.ma_lan_kham,p.ngay_lap_don FROM chi_tiet_don_thuoc c
        JOIN thuoc t ON t.ma_thuoc=c.ma_thuoc JOIN don_thuoc p ON p.ma_don=c.ma_don
        JOIN lan_kham_benh k ON k.ma_lan_kham=p.ma_lan_kham
        JOIN dot_dieu_tri d ON d.ma_dot=k.ma_dot WHERE d.ma_benh_nhan=%s
        ORDER BY p.ngay_lap_don,p.ma_don,c.ma_thuoc''', (patient_id,))
    nurse_rows = fetch_all('''SELECT h.*,y.ho_ten FROM ho_tro h JOIN y_ta y ON y.ma_y_ta=h.ma_y_ta
        JOIN luot_den_kham l ON l.ma_luot=h.ma_luot WHERE l.ma_benh_nhan=%s
        ORDER BY h.ngay_ho_tro,h.ma_luot,h.ma_y_ta''', (patient_id,))
    return dict(patient=patient, visits=visits(patient_id), treatments=episode_rows,
                current=[x for x in episode_rows if x['trang_thai']=='Đang điều trị'],
                examinations=examinations(patient_id), medicines=drug_rows, support=nurse_rows)
