# Từ điển dữ liệu vật lý — Quyền tuần 1

Cập nhật đổi tên cột định danh thành `cccd` ngày 09/11/2026. Giữ nguyên 11 bảng, kiểu dữ liệu và ràng buộc; database cũ cần chạy migration trước khi dùng backend mới. Mã VARCHAR(12), CCCD/điện thoại là chuỗi, tiền VND DECIMAL(12,0), ngày DATE theo Việt Nam. FK đều NOT NULL; chỉ ngày ra viện và ngày khỏi được NULL. Collation utf8mb4_0900_ai_ci không phân biệt hoa/thường và dấu; không dùng mã chỉ khác hoa/thường hoặc dấu. Không lưu tổng tiền suy diễn.

## bac_si

| Cột | Kiểu | NULL | Khóa / ý nghĩa |
|---|---|---|---|
| ma_bac_si | VARCHAR(12) | Không | PK |
| cccd | VARCHAR(20) | Không | UQ |
| ho_ten | VARCHAR(100) | Không | Họ tên |
| ngay_sinh | DATE | Không | Ngày sinh |
| dia_chi | VARCHAR(255) | Không | Địa chỉ |
| bac_nghe | VARCHAR(40) | Không | Bậc nghề |
| tham_nien | INT | Không | Thâm niên (năm, không âm) |
| chuyen_mon | VARCHAR(100) | Không | Chuyên môn |
| trinh_do_dao_tao | VARCHAR(100) | Không | Trình độ đào tạo |

Khóa và CHECK trong SQL:
```sql
tham_nien INT NOT NULL CHECK (tham_nien >= 0), chuyen_mon VARCHAR(100) NOT NULL, trinh_do_dao_tao VARCHAR(100) NOT NULL
```

## y_ta

| Cột | Kiểu | NULL | Khóa / ý nghĩa |
|---|---|---|---|
| ma_y_ta | VARCHAR(12) | Không | PK |
| cccd | VARCHAR(20) | Không | UQ |
| ho_ten | VARCHAR(100) | Không | Họ tên |
| ngay_sinh | DATE | Không | Ngày sinh |
| dia_chi | VARCHAR(255) | Không | Địa chỉ |
| so_dien_thoai | VARCHAR(20) | Không | Số điện thoại |
| trinh_do | VARCHAR(100) | Không | Trình độ |
| tham_nien | INT | Không | Thâm niên (năm, không âm) |

Khóa và CHECK trong SQL:
```sql
trinh_do VARCHAR(100) NOT NULL, tham_nien INT NOT NULL CHECK (tham_nien >= 0)
```

## benh_nhan

| Cột | Kiểu | NULL | Khóa / ý nghĩa |
|---|---|---|---|
| ma_benh_nhan | VARCHAR(12) | Không | PK |
| cccd | VARCHAR(20) | Không | UQ |
| ho_ten | VARCHAR(100) | Không | Họ tên |
| ngay_sinh | DATE | Không | Ngày sinh |
| dia_chi | VARCHAR(255) | Không | Địa chỉ |
| so_dien_thoai | VARCHAR(20) | Không | Số điện thoại |

Khóa chính/duy nhất đã ghi ở bảng trên.

## benh

| Cột | Kiểu | NULL | Khóa / ý nghĩa |
|---|---|---|---|
| ma_benh | VARCHAR(12) | Không | PK |
| ten_benh | VARCHAR(150) | Không | UQ |

Khóa chính/duy nhất đã ghi ở bảng trên.

## thuoc

| Cột | Kiểu | NULL | Khóa / ý nghĩa |
|---|---|---|---|
| ma_thuoc | VARCHAR(12) | Không | PK |
| ten_thuoc | VARCHAR(150) | Không | Tên thuốc |
| don_vi_tinh | VARCHAR(30) | Không | Đơn vị tính |
| gia_hien_tai | DECIMAL(12,0) | Không | Giá danh mục hiện tại, không âm |

Khóa và CHECK trong SQL:
```sql
gia_hien_tai DECIMAL(12,0) NOT NULL CHECK (gia_hien_tai >= 0)
```

## dot_dieu_tri

| Cột | Kiểu | NULL | Khóa / ý nghĩa |
|---|---|---|---|
| ma_dot | VARCHAR(12) | Không | PK |
| ngay_bat_dau | DATE | Không | Ngày bắt đầu đợt |
| ngay_khoi | DATE | Có | NULL = chưa kết thúc |
| trang_thai | VARCHAR(30) | Không | Đang điều trị / Đã khỏi |
| ma_benh_nhan | VARCHAR(12) | Không | FK → benh_nhan.ma_benh_nhan |
| ma_benh | VARCHAR(12) | Không | FK → benh.ma_benh |
| ma_bac_si | VARCHAR(12) | Không | FK → bac_si.ma_bac_si |

Khóa và CHECK trong SQL:
```sql
CONSTRAINT fk_dot_bn FOREIGN KEY (ma_benh_nhan) REFERENCES benh_nhan(ma_benh_nhan),
CONSTRAINT fk_dot_benh FOREIGN KEY (ma_benh) REFERENCES benh(ma_benh),
CONSTRAINT fk_dot_bs FOREIGN KEY (ma_bac_si) REFERENCES bac_si(ma_bac_si),
CONSTRAINT chk_dot_thoi_gian CHECK (ngay_khoi IS NULL OR ngay_khoi >= ngay_bat_dau),
CONSTRAINT chk_dot_trang_thai CHECK (trang_thai IN ('Đang điều trị','Đã khỏi')),
CONSTRAINT chk_dot_khoi CHECK ((trang_thai='Đã khỏi' AND ngay_khoi IS NOT NULL) OR (trang_thai='Đang điều trị' AND ngay_khoi IS NULL))
```

## luot_den_kham

| Cột | Kiểu | NULL | Khóa / ý nghĩa |
|---|---|---|---|
| ma_luot | VARCHAR(12) | Không | PK |
| ngay_vao_vien | DATE | Không | Ngày bắt đầu lượt |
| ngay_ra_vien | DATE | Có | NULL = chưa kết thúc |
| ma_benh_nhan | VARCHAR(12) | Không | FK → benh_nhan.ma_benh_nhan |

Khóa và CHECK trong SQL:
```sql
CHECK (ngay_ra_vien IS NULL OR ngay_ra_vien >= ngay_vao_vien)
```

## lan_kham_benh

| Cột | Kiểu | NULL | Khóa / ý nghĩa |
|---|---|---|---|
| ma_lan_kham | VARCHAR(12) | Không | PK |
| so_thu_tu_trong_dot | INT | Không | Thứ tự khám từ 1, liên tiếp trong đợt |
| ngay_kham | DATE | Không | Ngày khám |
| tien_kham_chua | DECIMAL(12,0) | Không | Không gồm tiền thuốc |
| ket_luan | VARCHAR(255) | Không | Kết luận |
| ma_dot | VARCHAR(12) | Không | FK → dot_dieu_tri.ma_dot |
| ma_luot | VARCHAR(12) | Không | FK → luot_den_kham.ma_luot |

Khóa và CHECK trong SQL:
```sql
ma_lan_kham VARCHAR(12) PRIMARY KEY, so_thu_tu_trong_dot INT NOT NULL CHECK (so_thu_tu_trong_dot >= 1),
ngay_kham DATE NOT NULL, tien_kham_chua DECIMAL(12,0) NOT NULL CHECK (tien_kham_chua >= 0),
CONSTRAINT fk_kham_dot FOREIGN KEY (ma_dot) REFERENCES dot_dieu_tri(ma_dot),
CONSTRAINT fk_kham_luot FOREIGN KEY (ma_luot) REFERENCES luot_den_kham(ma_luot),
CONSTRAINT uq_luot_dot UNIQUE (ma_luot,ma_dot),
CONSTRAINT uq_dot_stt UNIQUE (ma_dot,so_thu_tu_trong_dot)
```

## don_thuoc

| Cột | Kiểu | NULL | Khóa / ý nghĩa |
|---|---|---|---|
| ma_don | VARCHAR(12) | Không | PK |
| ngay_lap_don | DATE | Không | Ngày lập đơn |
| ma_lan_kham | VARCHAR(12) | Không | UQ; FK → lan_kham_benh.ma_lan_kham |

Khóa chính/duy nhất đã ghi ở bảng trên.

## chi_tiet_don_thuoc

| Cột | Kiểu | NULL | Khóa / ý nghĩa |
|---|---|---|---|
| ma_don | VARCHAR(12) | Không | FK → don_thuoc.ma_don |
| ma_thuoc | VARCHAR(12) | Không | FK → thuoc.ma_thuoc |
| so_luong | INT | Không | Số lượng, nguyên dương |
| lieu_dung | VARCHAR(255) | Không | Liều dùng |
| don_gia_ban | DECIMAL(12,0) | Không | Giá lịch sử, không lấy lại giá danh mục khi báo cáo |

Khóa và CHECK trong SQL:
```sql
so_luong INT NOT NULL CHECK (so_luong > 0), lieu_dung VARCHAR(255) NOT NULL,
don_gia_ban DECIMAL(12,0) NOT NULL CHECK (don_gia_ban >= 0),
PRIMARY KEY (ma_don,ma_thuoc), FOREIGN KEY (ma_don) REFERENCES don_thuoc(ma_don),
```

## ho_tro

| Cột | Kiểu | NULL | Khóa / ý nghĩa |
|---|---|---|---|
| ma_luot | VARCHAR(12) | Không | FK → luot_den_kham.ma_luot |
| ma_y_ta | VARCHAR(12) | Không | FK → y_ta.ma_y_ta |
| noi_dung_ho_tro | VARCHAR(255) | Không | Nội dung hỗ trợ |
| ngay_ho_tro | DATE | Không | Ngày bắt đầu hỗ trợ; không đổi khi thêm công việc |

Khóa và CHECK trong SQL:
```sql
PRIMARY KEY (ma_luot,ma_y_ta), FOREIGN KEY (ma_luot) REFERENCES luot_den_kham(ma_luot),
```

## Ánh xạ và quy ước

- MaDot → ma_dot; MaLuot → ma_luot; MaLanKham → ma_lan_kham; các thuộc tính còn lại chuyển PascalCase sang snake_case theo các bảng trên.
- Bác sĩ cố định nằm ở dot_dieu_tri. Hai liên kết N–N ánh xạ thành ho_tro và chi_tiet_don_thuoc, PK ghép giữ nguyên.
- UNIQUE(ma_luot,ma_dot), UNIQUE(ma_dot,so_thu_tu_trong_dot), UNIQUE(don_thuoc.ma_lan_kham). Chỉ mục hàm uq_dot_active bảo vệ một đợt đang điều trị cho mỗi bệnh nhân/bệnh, không thêm thuộc tính nghiệp vụ.
- Mỗi bệnh chỉ có một lần khám trong một lượt. Ngày lập đơn bằng ngày khám là quy ước tích hợp bổ sung của backend Trung, không phải yêu cầu nguyên văn của đề.
- Không ghi thêm lần khám cho lượt đã đóng là quy ước vận hành backend. Chỉnh sửa lịch sử cần quy trình riêng và kiểm tra lại audit, không đổi khóa/ngày tùy ý.
