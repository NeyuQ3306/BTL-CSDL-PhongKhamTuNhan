# Cài đặt và chạy trên Windows

Dùng bản main đã tích hợp. Chuẩn: Git, Python 3.11, MySQL Server 8.4 và Workbench. Hạn và bộ nộp xem [SUBMISSION](SUBMISSION.md).

## 1. Lấy mã nguồn

Repo private: tài khoản clone phải được cấp quyền. Chọn thư mục mới, chạy PowerShell:

```powershell
git clone --branch main https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan.git clinic-project1
Set-Location clinic-project1
git rev-parse HEAD
```

Ghi SHA thực tế khi kiểm thử/nộp. Bản tích hợp kỹ thuật gốc là 98bd2675bfffc64be09c87dd2897148f8b02b440; lịch sử bằng chứng xem [WEEK3_FINAL_STATUS](WEEK3_FINAL_STATUS.md).

## 2. Venv và .env

Từ gốc clone:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
if (!(Test-Path -LiteralPath .env)) { Copy-Item -LiteralPath .env.example -Destination .env }
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_hex(32))"
notepad .env
```

Không cần activate hoặc đổi ExecutionPolicy. Nếu thiếu launcher `py`, thay `py -3.11` bằng đường dẫn đầy đủ tới Python Windows 3.11. Điền khóa vừa sinh và cấu hình thật của DB thử:

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

**Cách nhập file nộp gộp trong #15/#17:** sau khi tạo DB mới trống và chọn đúng default schema của tab Workbench, mở `database/project1_submission.sql` và Execute toàn bộ **một lần**, thay cho cả sáu bước của bảng. File không có `CREATE DATABASE`/`USE`; phải tự chọn đúng schema trước khi chạy. Giữ `DELIMITER`, kiểm tra Action Output, cả hai lần audit đều 10 tập rỗng và đủ 11 bảng/9 trigger. Chỉ chọn **một** cách: file gộp hoặc bộ file nguồn; không chạy cả hai trên cùng DB. [Bằng chứng Workbench của Quyền](evidence/quyen-week3-submission/acceptance.md) là xác nhận người chạy, CI thông thường không tự chứng minh đã nhập file gộp. Hash local đã thử khác blob Git; chưa kết luận cùng byte hoặc nguyên nhân chênh lệch, xem [review #15](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/pull/15#pullrequestreview-5602203513). Không dùng `tools.import_seed`, `database/week1/clinic_seed.sql`, `hospital_db.sql` hoặc `python -m tools.quyen_db` thay quy trình này. Tiện ích cuối không đọc `.env` và thiếu audit trước constraints.

```sql
SHOW TABLES;
SHOW TRIGGERS;
```

Kỳ vọng 11 bảng, 9 trigger. Có lỗi thì dừng; DDL implicit commit có thể để lại bảng dù rollback. Ghi lỗi và dùng DB thử mới. `DELIMITER` là lệnh SQL client: với PyMySQL phải dùng parser của repo, không gửi nguyên `DELIMITER` cho server hoặc bỏ qua constraints.

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
- `http://127.0.0.1:5000/reports`: đủ bốn báo cáo thật.

Dừng app bằng Ctrl+C. Lần sau chỉ chạy lại app khi MySQL đang chạy, không import lại. Thao tác chi tiết: [USER_GUIDE.md](USER_GUIDE.md).

## 5. Hồi quy cách ly tùy chọn

Dùng clone/bản sao kiểm thử riêng vì test ghi `test-artifacts/`. Cài thêm:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt "playwright>=1.50,<2"
.\.venv\Scripts\python.exe -m playwright install chromium
.\.venv\Scripts\python.exe tools/vuong_week2_prepare.py --serve
```

Tên runner tuần 2 là lịch sử; runner chạy source checkout hiện tại, tạo instance MySQL bind loopback/datadir mới dưới `.venv/` và DB `_test`, không dùng DB làm việc trong `.env`. Runner bật MySQL/browser/oracle, nhập đúng thứ tự mục 3; ghi JUnit/audit/ảnh tại `docs/evidence/vuong_week2_prepare_<timestamp>/`. Nếu MySQL ngoài Program Files/PATH, thêm `--mysqld "D:/duong-dan/bin/mysqld.exe"`; cache browser tùy chọn `--browsers-path "D:/duong-dan/browsers"`. Mở URL/cổng runner in sau khi test đạt, không mặc định cổng 5000. Đọc JUnit/failure/error/skip và audit; số test phụ thuộc source, không lấy 168/179 làm điều kiện cứng.

**W3-RUN-01 đã đóng kỹ thuật theo hồ sơ tích hợp:** #17 đã chứa bản sửa runner/helper từ #12; Trung đã review tích hợp và bằng chứng Windows success/error. Sau Ctrl+C, đọc `mysql_cleanup`, `cleanup_errors`, `preparation_success` trong results; xác minh PID/cổng/launcher của instance private đã thoát. Không còn dùng mô tả “chưa sửa source” cho snapshot #17. Nếu còn process/cổng, giữ log và đối chiếu đúng executable/datadir trước khi xử lý; không dừng MySQL hệ thống/theo tên chung, nhờ Trung nếu không xác minh được. [Trạng thái và bằng chứng](VUONG_WEEK3_ISSUES.md#w3-run-01--runner-còn-mysql-con-sau-khi-kết-thúc-trên-windows).

## 6. Lỗi thường gặp

| Hiện tượng | Xử lý |
|---|---|
| Không thấy Python/pip | Dùng Python Windows 3.11 đúng đường dẫn, tránh alias Store/MSYS2 |
| 1044 / không tạo DB | Nhờ quản trị viên tạo DB thử trống và cấp quyền đúng DB |
| 1045 / Access denied | Kiểm tra user/mật khẩu/cổng/quyền và biến môi trường ghi đè `.env` |
| HTTP 503 / MySQL 2003 | Giữ app/MySQL console và bước tái hiện, xác minh đúng instance/cổng/config; runner dùng cổng ngẫu nhiên. Phiên đầu #17 gặp gián đoạn chưa rõ nguyên nhân, hai phiên sau không tái hiện; không tự retry thao tác ghi để che lỗi |
| 1049 / Unknown database | Đồng bộ `DB_NAME` và DB đã tạo |
| 1046 / No database selected | Chọn default schema hoặc `USE` đúng DB ở mỗi tab |
| 1050 / duplicate khi import | Dừng, dùng DB thử trống mới; không nhập chồng |
| 1064 khi tạo trigger | Kiểm tra log/client và cách chạy toàn khối `DELIMITER`, xác minh đủ 9 trigger |
| Thiếu secret | Sinh khóa, điền `FLASK_SECRET_KEY`, kiểm tra môi trường ghi đè |
| `/health` đạt, `/health/db` 503 | Flask đã lên nhưng DB chưa kết nối; kiểm tra cấu hình/server |
| Cổng 5000 bận | Dừng đúng app của bạn bằng Ctrl+C. Có thể chạy `.\.venv\Scripts\python.exe -m flask --app app run --host 127.0.0.1 --port 5001` rồi đổi URL tương ứng |
| CSRF lỗi sau đổi khóa | Tải lại form rồi gửi lại |
| Ô số báo tiếng Anh | Kiểm tra đúng SHA #17, JavaScript được nạp và loại ô number; #17 đã có bản sửa UI #13. validation server vẫn áp dụng |
| Count khác 1144 sau CRUD | Chỉ dọn hồ sơ giả không có lịch sử; không xóa seed/lịch sử hoặc import lại |
| Báo cáo khác đáp án | Kiểm tra kỳ lọc/dữ liệu thêm; Q2 vẫn cộng lương cơ bản nhân sự mới |
| Runner exit nhưng cổng còn mở | Xử lý W3-RUN-01 theo mục 5 |

## 7. Bằng chứng và giới hạn

[Bàn giao #17](VUONG_WEEK3_HANDOFF.md) tổng hợp Windows trên máy Quyền, CI đúng head và phiên lỗi còn theo dõi; không nhận trợ lý đã chạy lại trong lần cập nhật tài liệu. [Biên bản bước 5](VUONG_WEEK3_STEP5_VERIFICATION.md) và [bằng chứng bước 4](evidence/vuong_week3_final_20261021/README.md) chỉ áp dụng candidate ngày 21/10; không gán kết quả cho main/release hay commit tài liệu mới.

T16 **không thực hiện theo quyết định nhóm ngày 21/10/2026**, actual **chưa chạy**, không tính PASS hoặc việc còn thiếu. Clone/DB khác trên cùng máy không chứng minh chạy trên thiết bị khác.

## Cập nhật cột CCCD

Bản hiện tại dùng `cccd` cho hồ sơ bác sĩ, y tá và bệnh nhân. Database cũ có cột `cmt` phải dừng app, sao lưu và chạy migration trước khi khởi động backend mới. Xem [hướng dẫn đổi cột](CCCD_MIGRATION.md). Không nhập lại seed trên database đang có dữ liệu.
