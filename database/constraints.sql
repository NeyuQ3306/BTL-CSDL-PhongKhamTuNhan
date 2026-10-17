-- MySQL 8.4. Chạy MỘT LẦN sau schema.sql + seed.sql + audit dữ liệu.
-- Không DROP, không sửa/xóa dữ liệu có sẵn. DDL có implicit commit.
-- Functional unique index không thêm cột nghiệp vụ vào mô hình 11 bảng.
CREATE UNIQUE INDEX uq_dot_active ON dot_dieu_tri
(ma_benh_nhan, ((CASE WHEN trang_thai='Đang điều trị' THEN ma_benh ELSE NULL END)));
CREATE INDEX ix_kham_ngay ON lan_kham_benh(ngay_kham);
CREATE INDEX ix_dot_khoi ON dot_dieu_tri(ngay_khoi,ma_bac_si);
CREATE INDEX ix_hotro_ngay ON ho_tro(ngay_ho_tro,ma_y_ta);
CREATE INDEX ix_don_ngay ON don_thuoc(ngay_lap_don);
DELIMITER $$

CREATE TRIGGER q_dot_insert BEFORE INSERT ON dot_dieu_tri
FOR EACH ROW
BEGIN
  DECLARE owner_id VARCHAR(12);
  DECLARE overlap_id VARCHAR(12) DEFAULT NULL;
  SELECT ma_benh_nhan INTO owner_id FROM benh_nhan WHERE ma_benh_nhan=NEW.ma_benh_nhan FOR UPDATE;
  IF NEW.trang_thai<>'Đang điều trị' OR NEW.ngay_khoi IS NOT NULL THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='New episode must be active'; END IF;
  SELECT ma_dot INTO overlap_id FROM dot_dieu_tri
  WHERE ma_benh_nhan=NEW.ma_benh_nhan AND ma_benh=NEW.ma_benh
    AND (ngay_khoi IS NULL OR ngay_khoi>=NEW.ngay_bat_dau) LIMIT 1;
  IF overlap_id IS NOT NULL THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Overlapping episode'; END IF;

END$$

CREATE TRIGGER q_dot_update BEFORE UPDATE ON dot_dieu_tri
FOR EACH ROW
BEGIN
  DECLARE last_day DATE;
  DECLARE n INT;
  IF NEW.ma_dot<>OLD.ma_dot OR NEW.ma_benh_nhan<>OLD.ma_benh_nhan OR NEW.ma_benh<>OLD.ma_benh OR NEW.ma_bac_si<>OLD.ma_bac_si OR NEW.ngay_bat_dau<>OLD.ngay_bat_dau THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Episode identity and doctor are immutable'; END IF;
  IF OLD.trang_thai='Đã khỏi' AND (NEW.trang_thai<>OLD.trang_thai OR NOT (NEW.ngay_khoi<=>OLD.ngay_khoi)) THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Closed episode is immutable'; END IF;
  IF NEW.ngay_khoi IS NOT NULL THEN
    SELECT COUNT(*),MAX(ngay_kham) INTO n,last_day FROM lan_kham_benh WHERE ma_dot=OLD.ma_dot FOR UPDATE;
  IF n=0 OR NEW.ngay_khoi<last_day THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Cure date before last examination or empty episode'; END IF;
  END IF;
END$$

CREATE TRIGGER q_visit_update BEFORE UPDATE ON luot_den_kham
FOR EACH ROW
BEGIN
  DECLARE exams INT; DECLARE nurses INT; DECLARE last_exam DATE; DECLARE last_support DATE;
  IF NEW.ma_luot<>OLD.ma_luot OR NEW.ma_benh_nhan<>OLD.ma_benh_nhan OR NEW.ngay_vao_vien<>OLD.ngay_vao_vien THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Visit identity and start date are immutable'; END IF;
  IF OLD.ngay_ra_vien IS NOT NULL AND NOT (NEW.ngay_ra_vien<=>OLD.ngay_ra_vien) THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Closed visit date is immutable'; END IF;
  IF NEW.ngay_ra_vien IS NOT NULL THEN
    SELECT COUNT(*),MAX(ngay_kham) INTO exams,last_exam FROM lan_kham_benh WHERE ma_luot=OLD.ma_luot FOR UPDATE;
    SELECT COUNT(*),MAX(ngay_ho_tro) INTO nurses,last_support FROM ho_tro WHERE ma_luot=OLD.ma_luot FOR UPDATE;
  IF exams=0 OR nurses=0 OR NEW.ngay_ra_vien<last_exam OR NEW.ngay_ra_vien<last_support THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Visit needs examinations and support within dates'; END IF;
  END IF;
END$$

CREATE TRIGGER q_exam_insert BEFORE INSERT ON lan_kham_benh
FOR EACH ROW
BEGIN
  DECLARE patient_d VARCHAR(12); DECLARE patient_l VARCHAR(12); DECLARE disease_id VARCHAR(12);
  DECLARE begin_d DATE; DECLARE end_d DATE; DECLARE begin_l DATE; DECLARE end_l DATE;
  DECLARE last_day DATE; DECLARE seq INT; DECLARE n INT; DECLARE duplicate_id VARCHAR(12) DEFAULT NULL;
  SELECT ma_benh_nhan,ma_benh,ngay_bat_dau,ngay_khoi INTO patient_d,disease_id,begin_d,end_d
    FROM dot_dieu_tri WHERE ma_dot=NEW.ma_dot FOR UPDATE;
  SELECT ma_benh_nhan,ngay_vao_vien,ngay_ra_vien INTO patient_l,begin_l,end_l
    FROM luot_den_kham WHERE ma_luot=NEW.ma_luot FOR UPDATE;
  IF patient_d IS NULL OR patient_l IS NULL OR patient_d<>patient_l THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Visit and episode must have same patient'; END IF;
  IF end_d IS NOT NULL THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Cannot add examination to cured episode'; END IF;
  IF end_l IS NOT NULL THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Cannot add examination to closed visit'; END IF;
  IF NEW.ngay_kham<begin_d OR NEW.ngay_kham<begin_l THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Examination outside episode or visit'; END IF;
  SELECT COUNT(*),COALESCE(MAX(so_thu_tu_trong_dot),0),MAX(ngay_kham) INTO n,seq,last_day
    FROM lan_kham_benh WHERE ma_dot=NEW.ma_dot;
  IF n<>seq OR NEW.so_thu_tu_trong_dot<>seq+1 OR NEW.ngay_kham<last_day THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Examination sequence or date is invalid'; END IF;
  SELECT k.ma_lan_kham INTO duplicate_id FROM lan_kham_benh k JOIN dot_dieu_tri d ON d.ma_dot=k.ma_dot
    WHERE k.ma_luot=NEW.ma_luot AND d.ma_benh=disease_id LIMIT 1;
  IF duplicate_id IS NOT NULL THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='One disease per visit'; END IF;

END$$

CREATE TRIGGER q_exam_update BEFORE UPDATE ON lan_kham_benh
FOR EACH ROW
BEGIN
  IF NEW.ma_lan_kham<>OLD.ma_lan_kham OR NEW.ma_dot<>OLD.ma_dot OR NEW.ma_luot<>OLD.ma_luot OR NEW.so_thu_tu_trong_dot<>OLD.so_thu_tu_trong_dot OR NEW.ngay_kham<>OLD.ngay_kham THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Examination identity sequence and date are immutable'; END IF;

END$$

CREATE TRIGGER q_support_insert BEFORE INSERT ON ho_tro
FOR EACH ROW
BEGIN
  DECLARE begin_l DATE; DECLARE end_l DATE;
  SELECT ngay_vao_vien,ngay_ra_vien INTO begin_l,end_l FROM luot_den_kham WHERE ma_luot=NEW.ma_luot FOR UPDATE;
  IF begin_l IS NULL OR NEW.ngay_ho_tro<begin_l OR end_l IS NOT NULL THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Support requires open visit and valid date'; END IF;

END$$

CREATE TRIGGER q_support_update BEFORE UPDATE ON ho_tro
FOR EACH ROW
BEGIN
  IF NEW.ma_luot<>OLD.ma_luot OR NEW.ma_y_ta<>OLD.ma_y_ta OR NEW.ngay_ho_tro<>OLD.ngay_ho_tro THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Support identity and first date are immutable'; END IF;

END$$

CREATE TRIGGER q_prescription_insert BEFORE INSERT ON don_thuoc
FOR EACH ROW
BEGIN
  DECLARE exam_day DATE;
  SELECT ngay_kham INTO exam_day FROM lan_kham_benh WHERE ma_lan_kham=NEW.ma_lan_kham FOR SHARE;
  IF exam_day IS NULL OR NEW.ngay_lap_don<>exam_day THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Prescription date must equal examination date'; END IF;

END$$

CREATE TRIGGER q_prescription_update BEFORE UPDATE ON don_thuoc
FOR EACH ROW
BEGIN
  IF NEW.ma_don<>OLD.ma_don OR NEW.ma_lan_kham<>OLD.ma_lan_kham OR NEW.ngay_lap_don<>OLD.ngay_lap_don THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Prescription identity and date are immutable'; END IF;

END$$

DELIMITER ;
