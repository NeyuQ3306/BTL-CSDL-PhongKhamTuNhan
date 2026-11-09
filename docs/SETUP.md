# Cài đặt và chạy trên Windows

Chuẩn bị Git, Python 3.11 hoặc 3.12, MySQL Server 8.4 và MySQL Workbench. Dùng nhánh `main`.

## 1. Lấy mã nguồn

Repo private: tài khoản clone phải được cấp quyền. Chọn thư mục mới, chạy PowerShell:

```powershell
git clone --branch main https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan.git clinic-project1
Set-Location clinic-project1
git rev-parse HEAD
```

Ghi SHA thực tế khi cần đối chiếu mã nguồn và kết quả kiểm thử.

## 2. Venv và .env

Từ gốc clone:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
if (!(Test-Path -LiteralPath .env)) { Copy-Item -LiteralPath .env.example -Destination .env }
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_hex(32))"
notepad .env
```

Nếu cài Python 3.12, thay `py -3.11` bằng `py -3.12`. Không cần activate hoặc đổi ExecutionPolicy. Nếu thiếu launcher `py`, dùng đường dẫn đầy đủ tới Python đã cài. Điền khóa vừa sinh và cấu hình thật của DB thử:

```dotenv
FLASK_SECRET_KEY=CHUOI_VUA_TAO
FLASK_DEBUG=false
COOKIE_SECURE=false
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD='MAT_KHAU_MYSQL_TREN_MAY_BAN'
DB_NAME=clinic_week3_demo_test
```

MySQL cài trực tiếp thường dùng 3306; `.env.example` mặc định 3307 cho `compose.yaml`. Nếu dùng Docker có sẵn, dùng cổng/tài khoản thực tế và DB thử mới được cấp quyền, không thay volume cũ. Root chỉ dành cho demo local nếu chưa có tài khoản riêng. Import cần quyền tạo DB (hoặc nhờ quản trị viên tạo), DDL/index/trigger và đọc/ghi DB thử; app cần SELECT/INSERT/UPDATE/DELETE. App đọc `DB_*`; `MYSQL_ROOT_PASSWORD`/`MYSQL_PASSWORD` dùng cho Compose.

Không ghi đè `.env` đã có, không đưa mật khẩu/khóa/ảnh `.env` vào Git/bằng chứng. Mật khẩu có ký tự đặc biệt cần chuỗi hợp lệ theo dotenv. `load_dotenv()` không ghi đè biến môi trường có sẵn: dùng terminal mới; kiểm tra các biến `DB_*`, `FLASK_SECRET_KEY`, `PYTHON_DOTENV_DISABLED` còn sót nếu cấu hình không được nhận, không in giá trị bí mật.

## 3. Tạo DB và import trong Workbench

Kết nối đúng server/cổng, chạy:

```sql
SELECT VERSION();
CREATE DATABASE clinic_week3_demo_test
  CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE clinic_week3_demo_test;
```

Nếu DB đã tồn tại, dừng và chọn tên mới; cập nhật cả `USE` và `DB_NAME`. Không DROP/nhập chồng. Refresh SCHEMAS, chọn DB thử làm default schema. Mở từng file bằng File → Open SQL Script; mỗi tab phải chọn đúng schema (có thể thêm `USE clinic_week3_demo_test;` vào tab mà không lưu source). Chọn và chạy **toàn bộ file**, kiểm tra Action Output sau mỗi bước:

| Thứ tự | File | Điều kiện tiếp tục |
|---|---|---|
| 1 | `database/schema.sql` | Đủ 11 bảng, không lỗi |
| 2 | `database/seed.sql` | Nhập seed thành công |
| 3 | `database/audit.sql` | Cả 10 tập kết quả đều 0 dòng |
| 4 | `database/constraints.sql` | Tạo index/trigger thành công |
| 5 | `database/audit.sql` | Cả 10 tập vẫn 0 dòng |
| 6 | `database/queries.sql` | Đối chiếu tham số mẫu với `database/expected_results.md` |

**schema → seed → audit → constraints → audit → queries** là thứ tự của bộ file nguồn. Seed chứa lịch sử hoàn tất nên nhập trước trigger.

**Cách nhập file gộp:** sau khi tạo DB mới trống và chọn đúng default schema của tab Workbench, mở `database/project1_submission.sql` và Execute toàn bộ **một lần**, thay cho cả sáu bước của bảng. File không có `CREATE DATABASE`/`USE`; phải tự chọn đúng schema trước khi chạy. Giữ `DELIMITER`, kiểm tra Action Output, cả hai lần audit đều 10 tập rỗng và đủ 11 bảng/9 trigger. Chỉ chọn **một** cách: file gộp hoặc bộ file nguồn; không chạy cả hai trên cùng DB. Các công cụ nhập/kiểm thử cũ không thay quy trình cài đặt này. Tiện ích `tools.quyen_db` không đọc `.env`; chỉ dùng khi chuẩn bị kiểm thử theo hướng dẫn riêng.

```sql
SHOW TABLES;
SHOW TRIGGERS;
```

Kỳ vọng 11 bảng, 9 trigger. Có lỗi thì dừng; DDL implicit commit có thể để lại bảng dù rollback. Ghi lỗi và dùng DB thử mới. `DELIMITER` là lệnh SQL client: với PyMySQL phải dùng parser của repo, không gửi nguyên `DELIMITER` cho server hoặc bỏ qua constraints.

Sau khi nhập, mở `database/analytics_queries.sql` và chọn cùng schema nếu muốn đối chiếu R01–R07 bằng SQL. Website sử dụng các truy vấn này cho báo cáo phân tích; không cần tạo thêm bảng hoặc trigger.

## 4. Audit và chạy app

Từ gốc clone:

```powershell
.\.venv\Scripts\python.exe -m tools.audit_seed
.\.venv\Scripts\python.exe app.py
```

Ngay sau import, đọc JSON audit: `total=1144`, `matches_expected_counts=true`, cả 9 nhóm `findings` đều `[]`. Exit 0 của audit chưa đủ chứng minh sạch. `audit.sql` có thêm kiểm tra lượt không y tá. Sau ghi dữ liệu giả, count thay đổi là bình thường, không import lại để ép số lượng.

Giữ terminal mở, truy cập:

- `http://127.0.0.1:5000/health`: HTTP 200, `status=ok`.
- `http://127.0.0.1:5000/health/db`: HTTP 200, `status=ok`, `database=mysql`.
- `http://127.0.0.1:5000/patients`: danh sách bệnh nhân.
- `http://127.0.0.1:5000/visits/new`: tiếp nhận/khám.
- `http://127.0.0.1:5000/reports`: bốn báo cáo nghiệp vụ và bộ lọc/bảng/biểu đồ R01–R07.

Dừng app bằng Ctrl+C. Lần sau chỉ chạy lại app khi MySQL đang chạy, không import lại. Thao tác chi tiết: [USER_GUIDE.md](USER_GUIDE.md).

## 5. Kiểm thử tùy chọn

[Hướng dẫn kiểm thử](../tests/README.md) mô tả pytest, Playwright và DB thử riêng. [Runner Windows](evidence/quyen_laptop_acceptance_20261106/README.md) hỗ trợ chỉ định đường dẫn MySQL, tạo instance/cổng/datadir riêng và lưu bằng chứng.

Kết thúc phiên chạy, đọc kết quả cleanup và xác minh instance thử đã dừng. Không dừng dịch vụ MySQL làm việc để dọn instance thử.

## 6. Lỗi thường gặp

| Hiện tượng | Xử lý |
|---|---|
| Không thấy Python/pip | Dùng Python Windows 3.11/3.12 đúng đường dẫn, tránh alias Store/MSYS2 |
| 1044 / không tạo DB | Nhờ quản trị viên tạo DB thử trống và cấp quyền đúng DB |
| 1045 / Access denied | Kiểm tra user/mật khẩu/cổng/quyền và biến môi trường ghi đè `.env` |
| HTTP 503 / MySQL 2003 | Kiểm tra MySQL đang chạy, đúng instance/cổng và cấu hình DB; giữ log nếu lỗi lặp lại |
| 1049 / Unknown database | Đồng bộ `DB_NAME` và DB đã tạo |
| 1046 / No database selected | Chọn default schema hoặc `USE` đúng DB ở mỗi tab |
| 1050 / duplicate khi import | Dừng, dùng DB thử trống mới; không nhập chồng |
| 1064 khi tạo trigger | Kiểm tra log/client và cách chạy toàn khối `DELIMITER`, xác minh đủ 9 trigger |
| Thiếu secret | Sinh khóa, điền `FLASK_SECRET_KEY`, kiểm tra môi trường ghi đè |
| `/health` đạt, `/health/db` 503 | Flask đã lên nhưng DB chưa kết nối; kiểm tra cấu hình/server |
| Cổng 5000 bận | Dừng đúng app của bạn bằng Ctrl+C. Có thể chạy `.\.venv\Scripts\python.exe -m flask --app app run --host 127.0.0.1 --port 5001` rồi đổi URL tương ứng |
| CSRF lỗi sau đổi khóa | Tải lại form rồi gửi lại |
| Ô số báo tiếng Anh | Kiểm tra JavaScript được nạp và ngôn ngữ trình duyệt; server vẫn kiểm tra dữ liệu gửi lên |
| Count khác 1144 sau CRUD | Chỉ dọn hồ sơ giả không có lịch sử; không xóa seed/lịch sử hoặc import lại |
| Báo cáo khác đáp án | Kiểm tra kỳ lọc/dữ liệu thêm; Q2 vẫn cộng lương cơ bản nhân sự mới |
| Runner exit nhưng cổng còn mở | Kiểm tra log cleanup và đúng PID/executable/datadir theo hướng dẫn runner |

Xem [mục lục tài liệu](README.md) nếu cần thiết kế, hợp đồng báo cáo hoặc hồ sơ kiểm thử.
