-- R01-R07: báo cáo mô tả dữ liệu đã lưu, không dự báo/khuyến nghị điều trị.
-- MySQL 8.4. Chỉ SELECT + biến phiên; không sửa dữ liệu/schema.
-- Kỳ [@tu, @den): gồm @tu, không gồm @den. R06 chỉ dùng @ngay_doi_chieu/@nguong_ngay.
-- Backend phải kiểm tra ngày hợp lệ, @tu < @den, ngưỡng nguyên >= 0.
-- Mỗi marker Rxx-BEGIN/END bao quanh đúng một câu SELECT để tích hợp/kiểm thử.
SET @tu = DATE('2026-07-01');
SET @den = DATE('2026-10-15');
SET @ngay_doi_chieu = DATE('2026-10-14');
SET @nguong_ngay = 14;

-- R01-BEGIN
WITH first_exam AS (
 SELECT ma_dot, MIN(ngay_kham) AS ngay_moc
 FROM lan_kham_benh WHERE ngay_kham >= @tu AND ngay_kham < @den
 GROUP BY ma_dot
), ages AS (
 SELECT d.ma_dot,d.ma_benh,d.ma_benh_nhan,
 CASE WHEN p.ngay_sinh > f.ngay_moc THEN -1
      WHEN TIMESTAMPDIFF(YEAR,p.ngay_sinh,f.ngay_moc) < 6 THEN 0
      WHEN TIMESTAMPDIFF(YEAR,p.ngay_sinh,f.ngay_moc) < 18 THEN 1
      WHEN TIMESTAMPDIFF(YEAR,p.ngay_sinh,f.ngay_moc) < 60 THEN 2 ELSE 3 END AS thu_tu_nhom
 FROM first_exam f JOIN dot_dieu_tri d ON d.ma_dot=f.ma_dot
 JOIN benh_nhan p ON p.ma_benh_nhan=d.ma_benh_nhan
)
SELECT b.ma_benh,b.ten_benh,a.thu_tu_nhom,
 CASE a.thu_tu_nhom WHEN -1 THEN 'Ngày sinh không hợp lệ' WHEN 0 THEN '0–5'
 WHEN 1 THEN '6–17' WHEN 2 THEN '18–59' ELSE '60+' END AS nhom_tuoi,
 COUNT(DISTINCT a.ma_dot) AS so_dot,COUNT(DISTINCT a.ma_benh_nhan) AS so_benh_nhan
FROM ages a JOIN benh b ON b.ma_benh=a.ma_benh
GROUP BY b.ma_benh,b.ten_benh,a.thu_tu_nhom
ORDER BY b.ma_benh,a.thu_tu_nhom;
-- R01-END

-- R02-BEGIN
WITH visits AS (
 SELECT ngay_vao_vien AS ngay,COUNT(*) AS so_luot,COUNT(DISTINCT ma_benh_nhan) AS so_benh_nhan_tiep_nhan
 FROM luot_den_kham WHERE ngay_vao_vien >= @tu AND ngay_vao_vien < @den GROUP BY ngay_vao_vien
), exams AS (
 SELECT ngay_kham AS ngay,COUNT(*) AS so_lan_kham
 FROM lan_kham_benh WHERE ngay_kham >= @tu AND ngay_kham < @den GROUP BY ngay_kham
), days AS (SELECT ngay FROM visits UNION SELECT ngay FROM exams)
SELECT d.ngay,COALESCE(v.so_luot,0) AS so_luot,
 COALESCE(v.so_benh_nhan_tiep_nhan,0) AS so_benh_nhan_tiep_nhan,COALESCE(k.so_lan_kham,0) AS so_lan_kham
FROM days d LEFT JOIN visits v ON v.ngay=d.ngay LEFT JOIN exams k ON k.ngay=d.ngay
ORDER BY d.ngay;
-- R02-END

-- R03-BEGIN
WITH workload AS (
 SELECT d.ma_bac_si,COUNT(*) AS so_lan_kham,COUNT(DISTINCT d.ma_dot) AS so_dot,
 COUNT(DISTINCT d.ma_benh_nhan) AS so_benh_nhan
 FROM lan_kham_benh k JOIN dot_dieu_tri d ON d.ma_dot=k.ma_dot
 WHERE k.ngay_kham >= @tu AND k.ngay_kham < @den GROUP BY d.ma_bac_si
)
SELECT b.ma_bac_si,b.ho_ten,b.chuyen_mon,COALESCE(w.so_lan_kham,0) AS so_lan_kham,
 COALESCE(w.so_dot,0) AS so_dot,COALESCE(w.so_benh_nhan,0) AS so_benh_nhan
FROM bac_si b LEFT JOIN workload w ON w.ma_bac_si=b.ma_bac_si
ORDER BY so_lan_kham DESC,b.ma_bac_si;
-- R03-END

-- R04-BEGIN
SELECT t.ma_thuoc,t.ten_thuoc,t.don_vi_tinh,COUNT(DISTINCT p.ma_don) AS so_don,
 SUM(c.so_luong) AS tong_so_luong
FROM don_thuoc p JOIN chi_tiet_don_thuoc c ON c.ma_don=p.ma_don
JOIN thuoc t ON t.ma_thuoc=c.ma_thuoc
WHERE p.ngay_lap_don >= @tu AND p.ngay_lap_don < @den
GROUP BY t.ma_thuoc,t.ten_thuoc,t.don_vi_tinh ORDER BY so_don DESC,t.ma_thuoc;
-- R04-END

-- R05-BEGIN
WITH recurrence AS (
 SELECT d.ma_dot,d.ma_benh_nhan,d.ma_benh,d.ngay_bat_dau,
 (SELECT MAX(p.ngay_khoi) FROM dot_dieu_tri p
  WHERE p.ma_benh_nhan=d.ma_benh_nhan AND p.ma_benh=d.ma_benh
    AND p.ngay_khoi < d.ngay_bat_dau) AS ngay_khoi_truoc
 FROM dot_dieu_tri d WHERE d.ngay_bat_dau >= @tu AND d.ngay_bat_dau < @den
)
SELECT r.ma_dot,r.ma_benh_nhan,p.ho_ten,r.ma_benh,b.ten_benh,r.ngay_bat_dau,r.ngay_khoi_truoc,
 DATEDIFF(r.ngay_bat_dau,r.ngay_khoi_truoc) AS so_ngay_tu_lan_khoi_truoc
FROM recurrence r JOIN benh_nhan p ON p.ma_benh_nhan=r.ma_benh_nhan
JOIN benh b ON b.ma_benh=r.ma_benh WHERE r.ngay_khoi_truoc IS NOT NULL
ORDER BY r.ma_benh,r.ngay_bat_dau,r.ma_dot;
-- R05-END

-- R06-BEGIN
WITH last_exam AS (
 SELECT ma_dot,MAX(ngay_kham) AS ngay_kham_cuoi FROM lan_kham_benh
 WHERE ngay_kham <= @ngay_doi_chieu GROUP BY ma_dot
), pending AS (
 SELECT d.*,k.ngay_kham_cuoi,
 DATEDIFF(@ngay_doi_chieu,COALESCE(k.ngay_kham_cuoi,d.ngay_bat_dau)) AS so_ngay_chua_ghi_nhan
 FROM dot_dieu_tri d LEFT JOIN last_exam k ON k.ma_dot=d.ma_dot
 WHERE d.ngay_bat_dau <= @ngay_doi_chieu
 AND (d.ngay_khoi IS NULL OR d.ngay_khoi > @ngay_doi_chieu)
)
SELECT d.ma_dot,d.ma_benh_nhan,p.ho_ten,p.so_dien_thoai,d.ma_benh,b.ten_benh,
 d.ma_bac_si,bs.ho_ten AS ten_bac_si,d.ngay_bat_dau,d.ngay_kham_cuoi,
 (d.ngay_kham_cuoi IS NULL) AS chua_co_lan_kham,d.so_ngay_chua_ghi_nhan,
 CASE WHEN d.so_ngay_chua_ghi_nhan < 7 THEN '0–6'
      WHEN d.so_ngay_chua_ghi_nhan < 14 THEN '7–13'
      WHEN d.so_ngay_chua_ghi_nhan < 30 THEN '14–29' ELSE '30+' END AS nhom_ngay
FROM pending d JOIN benh_nhan p ON p.ma_benh_nhan=d.ma_benh_nhan
JOIN benh b ON b.ma_benh=d.ma_benh JOIN bac_si bs ON bs.ma_bac_si=d.ma_bac_si
WHERE @nguong_ngay >= 0 AND d.so_ngay_chua_ghi_nhan >= @nguong_ngay
ORDER BY d.so_ngay_chua_ghi_nhan DESC,d.ma_dot;
-- R06-END

-- R07-BEGIN
WITH exams AS (
 SELECT ma_dot,SUM(tien_kham_chua) AS tien_kham,COUNT(*) AS n,
 MIN(so_thu_tu_trong_dot) AS first_seq,MAX(so_thu_tu_trong_dot) AS last_seq
 FROM lan_kham_benh GROUP BY ma_dot
), medicine AS (
 SELECT k.ma_dot,SUM(c.so_luong*c.don_gia_ban) AS tien_thuoc
 FROM lan_kham_benh k JOIN don_thuoc p ON p.ma_lan_kham=k.ma_lan_kham
 JOIN chi_tiet_don_thuoc c ON c.ma_don=p.ma_don GROUP BY k.ma_dot
), incomplete_orders AS (
 SELECT DISTINCT k.ma_dot FROM lan_kham_benh k JOIN don_thuoc p ON p.ma_lan_kham=k.ma_lan_kham
 WHERE NOT EXISTS (SELECT 1 FROM chi_tiet_don_thuoc c WHERE c.ma_don=p.ma_don)
), costs AS (
 SELECT d.ma_dot,d.ma_benh,e.tien_kham,COALESCE(m.tien_thuoc,0) AS tien_thuoc,
 CASE WHEN e.first_seq=1 AND e.n=e.last_seq AND i.ma_dot IS NULL THEN 1 ELSE 0 END AS hop_le
 FROM dot_dieu_tri d LEFT JOIN exams e ON e.ma_dot=d.ma_dot
 LEFT JOIN medicine m ON m.ma_dot=d.ma_dot LEFT JOIN incomplete_orders i ON i.ma_dot=d.ma_dot
 WHERE d.ngay_khoi >= @tu AND d.ngay_khoi < @den AND d.trang_thai='Đã khỏi'
)
SELECT b.ma_benh,b.ten_benh,SUM(c.hop_le) AS so_dot_tinh,COUNT(*)-SUM(c.hop_le) AS so_dot_loai,
 ROUND(AVG(CASE WHEN c.hop_le=1 THEN c.tien_kham END),2) AS tb_tien_kham,
 ROUND(AVG(CASE WHEN c.hop_le=1 THEN c.tien_thuoc END),2) AS tb_tien_thuoc,
 ROUND(AVG(CASE WHEN c.hop_le=1 THEN c.tien_kham+c.tien_thuoc END),2) AS tb_tong,
 MIN(CASE WHEN c.hop_le=1 THEN c.tien_kham+c.tien_thuoc END) AS min_tong,
 MAX(CASE WHEN c.hop_le=1 THEN c.tien_kham+c.tien_thuoc END) AS max_tong
FROM costs c JOIN benh b ON b.ma_benh=c.ma_benh
GROUP BY b.ma_benh,b.ten_benh ORDER BY tb_tong DESC,b.ma_benh;
-- R07-END
