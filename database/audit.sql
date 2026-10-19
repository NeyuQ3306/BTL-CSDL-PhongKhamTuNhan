-- Mọi truy vấn phải trả 0 dòng trên seed và nghiệp vụ đã hoàn tất.
-- different_patient
SELECT k.ma_lan_kham FROM lan_kham_benh k
        JOIN dot_dieu_tri d ON d.ma_dot=k.ma_dot JOIN luot_den_kham l ON l.ma_luot=k.ma_luot
        WHERE d.ma_benh_nhan<>l.ma_benh_nhan;

-- exam_outside_visit_or_treatment
SELECT k.ma_lan_kham FROM lan_kham_benh k
        JOIN dot_dieu_tri d ON d.ma_dot=k.ma_dot JOIN luot_den_kham l ON l.ma_luot=k.ma_luot
        WHERE k.ngay_kham<l.ngay_vao_vien OR k.ngay_kham>l.ngay_ra_vien
        OR k.ngay_kham<d.ngay_bat_dau OR k.ngay_kham>d.ngay_khoi;

-- duplicate_active_episode
SELECT ma_benh_nhan,ma_benh,COUNT(*) AS n FROM dot_dieu_tri
        WHERE trang_thai='Đang điều trị' GROUP BY ma_benh_nhan,ma_benh HAVING COUNT(*)>1;

-- nonconsecutive_exam_numbers
SELECT d.ma_dot FROM dot_dieu_tri d LEFT JOIN lan_kham_benh k
        ON k.ma_dot=d.ma_dot GROUP BY d.ma_dot HAVING MIN(k.so_thu_tu_trong_dot)<>1
        OR MAX(k.so_thu_tu_trong_dot)<>COUNT(k.ma_lan_kham) OR COUNT(k.ma_lan_kham)=0;

-- empty_visit
SELECT l.ma_luot FROM luot_den_kham l LEFT JOIN lan_kham_benh k
        ON k.ma_luot=l.ma_luot WHERE k.ma_lan_kham IS NULL;

-- empty_prescription
SELECT d.ma_don FROM don_thuoc d LEFT JOIN chi_tiet_don_thuoc c
        ON c.ma_don=d.ma_don WHERE c.ma_don IS NULL;

-- support_outside_visit
SELECT h.ma_luot,h.ma_y_ta FROM ho_tro h JOIN luot_den_kham l
        ON l.ma_luot=h.ma_luot WHERE h.ngay_ho_tro<l.ngay_vao_vien OR h.ngay_ho_tro>l.ngay_ra_vien;

-- prescription_date_mismatch
SELECT d.ma_don FROM don_thuoc d JOIN lan_kham_benh k
        ON k.ma_lan_kham=d.ma_lan_kham WHERE d.ngay_lap_don<>k.ngay_kham;

-- overlapping_episodes
SELECT a.ma_dot AS first_episode,b.ma_dot AS second_episode
        FROM dot_dieu_tri a JOIN dot_dieu_tri b ON a.ma_benh_nhan=b.ma_benh_nhan
        AND a.ma_benh=b.ma_benh AND a.ma_dot<b.ma_dot
        WHERE a.ngay_bat_dau<=COALESCE(b.ngay_khoi,'9999-12-31')
        AND b.ngay_bat_dau<=COALESCE(a.ngay_khoi,'9999-12-31');

-- visit_without_nurse
SELECT l.ma_luot FROM luot_den_kham l LEFT JOIN ho_tro h ON h.ma_luot=l.ma_luot WHERE h.ma_luot IS NULL;