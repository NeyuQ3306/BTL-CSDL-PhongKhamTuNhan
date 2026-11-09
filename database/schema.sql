-- Adapter tuần 1 của Trung; dữ liệu giả lập do Vũ Đại Vương bàn giao.
-- SHA256 nguồn: 6dce234d4063b8e797c972186b4b1483c901defc4dec8ff111fbff2463209063
-- Chỉ đổi tên bảng/cột, bỏ CREATE DATABASE/USE; không đổi giá trị dữ liệu.
-- MySQL 8.0+, utf8mb4; DU LIEU GIA LAP - KHONG DUNG CHO BENH AN THUC

CREATE TABLE bac_si (
 ma_bac_si VARCHAR(12) PRIMARY KEY, cccd VARCHAR(20) NOT NULL UNIQUE, ho_ten VARCHAR(100) NOT NULL,
 ngay_sinh DATE NOT NULL, dia_chi VARCHAR(255) NOT NULL, bac_nghe VARCHAR(40) NOT NULL,
 tham_nien INT NOT NULL CHECK (tham_nien >= 0), chuyen_mon VARCHAR(100) NOT NULL, trinh_do_dao_tao VARCHAR(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
CREATE TABLE y_ta (
 ma_y_ta VARCHAR(12) PRIMARY KEY, cccd VARCHAR(20) NOT NULL UNIQUE, ho_ten VARCHAR(100) NOT NULL,
 ngay_sinh DATE NOT NULL, dia_chi VARCHAR(255) NOT NULL, so_dien_thoai VARCHAR(20) NOT NULL,
 trinh_do VARCHAR(100) NOT NULL, tham_nien INT NOT NULL CHECK (tham_nien >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
CREATE TABLE benh_nhan (
 ma_benh_nhan VARCHAR(12) PRIMARY KEY, cccd VARCHAR(20) NOT NULL UNIQUE, ho_ten VARCHAR(100) NOT NULL,
 ngay_sinh DATE NOT NULL, dia_chi VARCHAR(255) NOT NULL, so_dien_thoai VARCHAR(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
CREATE TABLE benh (
 ma_benh VARCHAR(12) PRIMARY KEY, ten_benh VARCHAR(150) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
CREATE TABLE thuoc (
 ma_thuoc VARCHAR(12) PRIMARY KEY, ten_thuoc VARCHAR(150) NOT NULL, don_vi_tinh VARCHAR(30) NOT NULL,
 gia_hien_tai DECIMAL(12,0) NOT NULL CHECK (gia_hien_tai >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
CREATE TABLE dot_dieu_tri (
 ma_dot VARCHAR(12) PRIMARY KEY, ngay_bat_dau DATE NOT NULL, ngay_khoi DATE NULL,
 trang_thai VARCHAR(30) NOT NULL, ma_benh_nhan VARCHAR(12) NOT NULL, ma_benh VARCHAR(12) NOT NULL, ma_bac_si VARCHAR(12) NOT NULL,
 CONSTRAINT fk_dot_bn FOREIGN KEY (ma_benh_nhan) REFERENCES benh_nhan(ma_benh_nhan),
 CONSTRAINT fk_dot_benh FOREIGN KEY (ma_benh) REFERENCES benh(ma_benh),
 CONSTRAINT fk_dot_bs FOREIGN KEY (ma_bac_si) REFERENCES bac_si(ma_bac_si),
 CONSTRAINT chk_dot_thoi_gian CHECK (ngay_khoi IS NULL OR ngay_khoi >= ngay_bat_dau),
 CONSTRAINT chk_dot_trang_thai CHECK (trang_thai IN ('Đang điều trị','Đã khỏi')),
 CONSTRAINT chk_dot_khoi CHECK ((trang_thai='Đã khỏi' AND ngay_khoi IS NOT NULL) OR (trang_thai='Đang điều trị' AND ngay_khoi IS NULL))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
CREATE TABLE luot_den_kham (
 ma_luot VARCHAR(12) PRIMARY KEY, ngay_vao_vien DATE NOT NULL, ngay_ra_vien DATE NULL, ma_benh_nhan VARCHAR(12) NOT NULL,
 FOREIGN KEY (ma_benh_nhan) REFERENCES benh_nhan(ma_benh_nhan),
 CHECK (ngay_ra_vien IS NULL OR ngay_ra_vien >= ngay_vao_vien)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
CREATE TABLE lan_kham_benh (
 ma_lan_kham VARCHAR(12) PRIMARY KEY, so_thu_tu_trong_dot INT NOT NULL CHECK (so_thu_tu_trong_dot >= 1),
 ngay_kham DATE NOT NULL, tien_kham_chua DECIMAL(12,0) NOT NULL CHECK (tien_kham_chua >= 0),
 ket_luan VARCHAR(255) NOT NULL, ma_dot VARCHAR(12) NOT NULL, ma_luot VARCHAR(12) NOT NULL,
 CONSTRAINT fk_kham_dot FOREIGN KEY (ma_dot) REFERENCES dot_dieu_tri(ma_dot),
 CONSTRAINT fk_kham_luot FOREIGN KEY (ma_luot) REFERENCES luot_den_kham(ma_luot),
 CONSTRAINT uq_luot_dot UNIQUE (ma_luot,ma_dot),
 CONSTRAINT uq_dot_stt UNIQUE (ma_dot,so_thu_tu_trong_dot)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
CREATE TABLE don_thuoc (
 ma_don VARCHAR(12) PRIMARY KEY, ngay_lap_don DATE NOT NULL, ma_lan_kham VARCHAR(12) NOT NULL UNIQUE,
 FOREIGN KEY (ma_lan_kham) REFERENCES lan_kham_benh(ma_lan_kham)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
CREATE TABLE chi_tiet_don_thuoc (
 ma_don VARCHAR(12) NOT NULL, ma_thuoc VARCHAR(12) NOT NULL,
 so_luong INT NOT NULL CHECK (so_luong > 0), lieu_dung VARCHAR(255) NOT NULL,
 don_gia_ban DECIMAL(12,0) NOT NULL CHECK (don_gia_ban >= 0),
 PRIMARY KEY (ma_don,ma_thuoc), FOREIGN KEY (ma_don) REFERENCES don_thuoc(ma_don),
 FOREIGN KEY (ma_thuoc) REFERENCES thuoc(ma_thuoc)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
CREATE TABLE ho_tro (
 ma_luot VARCHAR(12) NOT NULL, ma_y_ta VARCHAR(12) NOT NULL,
 noi_dung_ho_tro VARCHAR(255) NOT NULL, ngay_ho_tro DATE NOT NULL,
 PRIMARY KEY (ma_luot,ma_y_ta), FOREIGN KEY (ma_luot) REFERENCES luot_den_kham(ma_luot),
 FOREIGN KEY (ma_y_ta) REFERENCES y_ta(ma_y_ta)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

