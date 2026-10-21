-- Bốn nhóm truy vấn tuần 2 của Quyền, dùng cùng hợp đồng backend Trung.
-- Sửa @thang (ngày đầu tháng) và @ma_benh_nhan bên dưới rồi chạy cả file.
-- 11 tập kết quả: Q1, Q2a, Q2b, 7 tập Q3, Q4. Không thay đổi dữ liệu.
-- Kỳ tính [@thang, @den): gồm ngày đầu, loại ngày đầu kỳ kế tiếp.
-- Q3 luôn trả toàn bộ lịch sử, không bị lọc theo @thang.
-- Mã không tồn tại: cả 7 tập Q3 rỗng; hồ sơ chưa khám: chỉ tập hồ sơ có dòng.
-- Chọn tháng YYYY-MM-01, giờ Việt Nam; tháng hiện tại dừng ở ngày hôm nay.
SET time_zone = '+07:00';
SET @thang = DATE('2026-10-01');
SET @den = IF(DATE_FORMAT(@thang,'%Y-%m')=DATE_FORMAT(CURRENT_DATE(),'%Y-%m'),
              CURRENT_DATE()+INTERVAL 1 DAY, @thang+INTERVAL 1 MONTH);
SET @ma_benh_nhan = 'BN001';
-- Q1: Một đợt có khám trong tháng chỉ đếm một lần.
SELECT b.ma_benh,b.ten_benh,COUNT(DISTINCT d.ma_dot) AS so_dot_mac
FROM lan_kham_benh k JOIN dot_dieu_tri d ON d.ma_dot=k.ma_dot
JOIN benh b ON b.ma_benh=d.ma_benh
WHERE k.ngay_kham>=@thang AND k.ngay_kham<@den
GROUP BY b.ma_benh,b.ten_benh ORDER BY so_dot_mac DESC,b.ma_benh;
-- Q2a: Bác sĩ chưa có thưởng vẫn có lương cơ bản.
SELECT bs.ma_bac_si,bs.ho_ten,7000000 AS luong_co_ban,
 COALESCE(t.n,0) AS so_dot_khoi,COALESCE(t.n,0)*1000000 AS tien_thuong,
 7000000+COALESCE(t.n,0)*1000000 AS tong_luong
FROM bac_si bs LEFT JOIN (
 SELECT ma_bac_si,COUNT(*) n FROM dot_dieu_tri
 WHERE trang_thai='Đã khỏi' AND ngay_khoi>=@thang AND ngay_khoi<@den
 GROUP BY ma_bac_si) t ON t.ma_bac_si=bs.ma_bac_si ORDER BY bs.ma_bac_si;
-- Q2b: PK(ma_luot,ma_y_ta) chống thưởng lặp cho nhiều công việc cùng lượt.
SELECT y.ma_y_ta,y.ho_ten,5000000 AS luong_co_ban,COALESCE(t.n,0) AS so_luot_ho_tro,
 COALESCE(t.n,0)*200000 AS tien_thuong,5000000+COALESCE(t.n,0)*200000 AS tong_luong
FROM y_ta y LEFT JOIN (
 SELECT ma_y_ta,COUNT(*) n FROM ho_tro WHERE ngay_ho_tro>=@thang AND ngay_ho_tro<@den
 GROUP BY ma_y_ta) t ON t.ma_y_ta=y.ma_y_ta ORDER BY y.ma_y_ta;
-- Q3: Trả các tập kết quả riêng để không nhân bản khám/thuốc/y tá.
SELECT * FROM benh_nhan WHERE ma_benh_nhan=@ma_benh_nhan;
SELECT * FROM luot_den_kham WHERE ma_benh_nhan=@ma_benh_nhan ORDER BY ngay_vao_vien,ma_luot;
SELECT d.*,b.ten_benh,bs.ho_ten AS bac_si,COALESCE(k.stt,0) AS lan_kham_hien_tai
FROM dot_dieu_tri d JOIN benh b ON b.ma_benh=d.ma_benh JOIN bac_si bs ON bs.ma_bac_si=d.ma_bac_si
LEFT JOIN (SELECT ma_dot,MAX(so_thu_tu_trong_dot) stt FROM lan_kham_benh GROUP BY ma_dot) k ON k.ma_dot=d.ma_dot
WHERE d.ma_benh_nhan=@ma_benh_nhan ORDER BY d.ngay_bat_dau,d.ma_dot;
SELECT d.ma_dot,b.ten_benh,MAX(k.so_thu_tu_trong_dot) AS lan_kham_hien_tai
FROM dot_dieu_tri d JOIN benh b ON b.ma_benh=d.ma_benh LEFT JOIN lan_kham_benh k ON k.ma_dot=d.ma_dot
WHERE d.ma_benh_nhan=@ma_benh_nhan AND d.trang_thai='Đang điều trị'
GROUP BY d.ma_dot,b.ten_benh ORDER BY d.ma_dot;
SELECT k.* FROM lan_kham_benh k JOIN dot_dieu_tri d ON d.ma_dot=k.ma_dot
WHERE d.ma_benh_nhan=@ma_benh_nhan ORDER BY k.ngay_kham,k.ma_lan_kham;
SELECT p.*,c.ma_thuoc,t.ten_thuoc,t.don_vi_tinh,c.so_luong,c.lieu_dung,c.don_gia_ban,
 c.so_luong*c.don_gia_ban AS thanh_tien
FROM don_thuoc p JOIN chi_tiet_don_thuoc c ON c.ma_don=p.ma_don JOIN thuoc t ON t.ma_thuoc=c.ma_thuoc
JOIN lan_kham_benh k ON k.ma_lan_kham=p.ma_lan_kham JOIN dot_dieu_tri d ON d.ma_dot=k.ma_dot
WHERE d.ma_benh_nhan=@ma_benh_nhan ORDER BY p.ngay_lap_don,p.ma_don,c.ma_thuoc;
SELECT h.*,y.ho_ten FROM ho_tro h JOIN y_ta y ON y.ma_y_ta=h.ma_y_ta
JOIN luot_den_kham l ON l.ma_luot=h.ma_luot WHERE l.ma_benh_nhan=@ma_benh_nhan
ORDER BY h.ngay_ho_tro,h.ma_luot,h.ma_y_ta;
-- Q4: Tính riêng tiền khám và tiền thuốc, dùng giá bán lịch sử.
SELECT a.tien_kham,b.tien_thuoc,a.tien_kham+b.tien_thuoc AS doanh_thu
FROM (SELECT COALESCE(SUM(tien_kham_chua),0) AS tien_kham FROM lan_kham_benh
      WHERE ngay_kham>=@thang AND ngay_kham<@den) a
CROSS JOIN (SELECT COALESCE(SUM(c.so_luong*c.don_gia_ban),0) AS tien_thuoc
      FROM chi_tiet_don_thuoc c JOIN don_thuoc p ON p.ma_don=c.ma_don
      WHERE p.ngay_lap_don>=@thang AND p.ngay_lap_don<@den) b;
