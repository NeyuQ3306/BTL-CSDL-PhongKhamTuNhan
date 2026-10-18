# Hướng dẫn thống nhất: import và chạy thử tuần 1 trên Windows

Cập nhật 18/10/2026. Đây là hướng dẫn tích hợp thử SQL PR #6 và UI/backend PR #7. PR #7 đã squash merge tại e174f626; #6 còn chờ xác nhận lại review. Không dùng riêng main để nghiệm thu đầy đủ ở thời điểm này. Tài liệu trong PR #8 chờ Trung/Vương review theo RULES.md.

## 1. Chuẩn bị và lấy đúng source

Cần Git, Python 3.11 (có pip), MySQL Server 8.4 đang chạy và MySQL Workbench. Workbench chỉ là công cụ kết nối, không thay MySQL Server. Dùng PowerShell mới. Kiểm tra:

```powershell
git --version
python --version
python -m pip --version
```

Nếu python không tìm thấy, mở Microsoft Store hoặc trỏ tới MSYS2, chọn đúng Python đã cài trước khi tiếp tục; có thể dùng đường dẫn đầy đủ tới python.exe của Python 3.11.

Để không ảnh hưởng thư mục làm việc cũ, tạo bản clone riêng tại C:\Users\LENOVO (hoặc thư mục người dùng của mỗi thành viên). Nếu clinic-week1-demo đã tồn tại, chọn tên thư mục mới, không xóa bản cũ.

```powershell
cd $env:USERPROFILE
git clone https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan.git clinic-week1-demo
cd clinic-week1-demo
git fetch origin
git switch -c local/week1-demo 8c5be9469976333195eb67c9d2689638d02c045f
git restore --source=08e4427f6ac8e9ba55eaba859ddab4067330ec04 -- database/schema.sql database/seed.sql database/audit.sql database/constraints.sql database/queries.sql database/expected_results.md
git status --short
```

Đây là snapshot UI/backend Vương đã đồng bộ main, ghép riêng sáu file SQL Quyền. Các file SQL hiện chưa commit trên nhánh local là bình thường; không push nhánh thử này và không merge thủ công vào main. Không lấy cả nhánh tuần 2. Hai SHA được cố định để cả nhóm thử cùng phiên bản. Sau khi #6/#7 được review và merge, clone mới từ main và kiểm tra có đủ sáu file trên; bỏ bước ghép snapshot.

## 2. Cài môi trường Python

Từ thư mục clinic-week1-demo:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
if (!(Test-Path .env)) { Copy-Item .env.example .env }
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_hex(32))"
notepad .env
```

Chỉ Copy-Item khi chưa có .env. Không cần activate nên không cần đổi ExecutionPolicy. Điền các dòng sau (giữ các dòng MYSQL_* khác nếu có):

```dotenv
FLASK_SECRET_KEY=CHUOI_VUA_TAO
FLASK_DEBUG=false
COOKIE_SECURE=false
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD='MAT_KHAU_MYSQL_TREN_MAY_BAN'
DB_NAME=clinic_week1_demo
```

Dùng root chỉ để chạy demo cục bộ lần đầu. Nếu có user demo được cấp quyền thì dùng user đó; import cần quyền tạo bảng/chỉ mục/trigger và đọc/ghi trong DB này, chạy app cần SELECT/INSERT/UPDATE/DELETE. Không gửi mật khẩu hoặc ảnh .env lên nhóm/GitHub. Nếu mật khẩu chứa dấu nháy đơn, dùng chuỗi nháy kép và escape phù hợp định dạng dotenv.

Cổng 3306 áp dụng MySQL cài trực tiếp. Nếu đã có MySQL Docker của repo, dùng cổng 3307 và tài khoản thực tế của container; tạo DB demo mới và cấp quyền bằng quản trị viên, không đổi/xóa volume cũ. Hướng dẫn chính này dùng MySQL cài trực tiếp.

Mở PowerShell mới để tránh DB_* từ buổi trước ghi đè .env. Flask đọc .env, nhưng biến môi trường đã tồn tại có độ ưu tiên cao hơn.

## 3. Import chuẩn bằng MySQL Workbench

Kết nối MySQL trên máy. Chạy trong SQL tab:

```sql
SELECT VERSION();
CREATE DATABASE clinic_week1_demo
  CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE clinic_week1_demo;
```

Nếu báo database đã tồn tại: dừng và chọn tên mới (ví dụ clinic_week1_demo2), cập nhật DB_NAME tương ứng. Không DROP database cũ.

Refresh SCHEMAS rồi nhấp đúp clinic_week1_demo để tên in đậm. Mở từng file bằng File → Open SQL Script. Mỗi tab phải chọn đúng default schema; có thể thêm USE clinic_week1_demo; vào đầu tab để chạy (không cần lưu thay đổi file). Chạy toàn bộ file, không chỉ câu đang đặt con trỏ, theo đúng thứ tự:

| Bước | File | Kết quả bắt buộc |
|---|---|---|
| 1 | database/schema.sql | Tạo đủ 11 bảng, không có lỗi |
| 2 | database/seed.sql | Nhập dữ liệu mẫu, không có lỗi |
| 3 | database/audit.sql | Tất cả 10 truy vấn đều trả 0 dòng; có dòng thì dừng |
| 4 | database/constraints.sql | Tạo chỉ mục/trigger thành công |
| 5 | database/audit.sql | Kiểm tra lại, vẫn 0 dòng |
| 6 | database/queries.sql | Báo cáo SQL; đối chiếu database/expected_results.md với tham số mẫu trong file |

Kiểm tra Action Output sau mỗi file; có lỗi thì dừng, không chạy file tiếp theo. DDL có implicit commit: import lỗi có thể để lại bảng dù rollback. Ghi lại lỗi, dùng DB thử trống mới để chạy lại từ đầu.

**Chỉ dùng thứ tự schema → seed → audit → constraints → audit → queries.** Seed chứa lịch sử đã hoàn tất nên phải nhập trước trigger.

Không chạy tools.import_seed, không nhập database/week1/clinic_seed.sql hoặc hospital_db.sql cho quy trình này. tools.quyen_db hiện không tự đọc .env và không chạy audit trước constraints nên cũng không phải lệnh import chuẩn của hướng dẫn này. Các hướng dẫn cũ trong bàn giao là lịch sử, nhường ưu tiên cho tài liệu này.

Trong Workbench kiểm tra thêm:
```sql
USE clinic_week1_demo;
SHOW TABLES;
SHOW TRIGGERS;
```
Phải có 11 bảng và đúng 9 trigger.

## 4. Đối chiếu dữ liệu rồi chạy web

Trong PowerShell, từ thư mục clinic-week1-demo:

```powershell
.\.venv\Scripts\python.exe -m tools.audit_seed
.\.venv\Scripts\python.exe app.py
```

Ngay sau import, audit phải cho total = 1144, matches_expected_counts = true, mọi findings đều là []. Công cụ này chỉ in kết quả; phải đọc kết quả, không chỉ dựa vào exit code. audit.sql ở bước 3 có thêm kiểm tra lượt không có y tá.

Giữ cửa sổ chạy app mở. Truy cập:
- http://127.0.0.1:5000/health — kiểm tra Flask.
- http://127.0.0.1:5000/health/db — kiểm tra kết nối MySQL.
- http://127.0.0.1:5000/patients — giao diện bệnh nhân.

Dừng bằng Ctrl+C. Những lần sau chỉ cần MySQL đang chạy, vào đúng thư mục và chạy lại app.py; không import lại.

## 5. Checklist thử máy thật

Dùng dữ liệu giả:
- Mã: BNTESTQ1; họ tên: Bệnh nhân thử Quyền; CMT: 999000001001.
- Ngày sinh: 2000-01-01; địa chỉ: Hà Nội; điện thoại: 0900000001.
- Nếu mã/CMT đã dùng, chọn giá trị mới.

1. Thêm bệnh nhân → thấy trang chi tiết, tải lại trang vẫn còn.
2. Trong Workbench: SELECT * FROM benh_nhan WHERE ma_benh_nhan = 'BNTESTQ1'; phải thấy đúng bản ghi.
3. Sửa địa chỉ → tải lại và SELECT xác nhận đã lưu.
4. Thêm lại mã hoặc CMT đang có → báo lỗi rõ, không tạo bản sao.
5. Thử ngày sinh tương lai hoặc CMT không hợp lệ → bị từ chối.
6. Mở bệnh nhân BN001 → xem lịch sử; thử xóa hồ sơ có lịch sử → bị chặn, hồ sơ còn nguyên.
7. Thử thêm/xem/sửa/xóa hồ sơ giả không có lịch sử ở bác sĩ và y tá.
8. Xóa riêng hồ sơ giả vừa tạo để trả dữ liệu về nền, chạy audit_seed lần nữa. Không xóa seed để đạt số lượng.

Trong lúc giữ hồ sơ thử, total khác 1144 là bình thường; không import lại để sửa chênh lệch. Ba báo cáo bệnh/lương/doanh thu trên UI tuần 1 còn là khung chờ; kiểm tra kết quả bằng queries.sql, không đánh dấu UI báo cáo hoàn tất.

## 6. Lỗi thường gặp

| Lỗi | Xử lý |
|---|---|
| Không tìm thấy python/pip | Kiểm tra đúng Python Windows; dùng đường dẫn đầy đủ rồi tạo lại venv trong thư mục demo mới |
| CREATE DATABASE bị từ chối / 1044 | Nhờ quản trị viên tạo DB thử trống và cấp quyền đúng DB; không nới quyền DB đang làm việc |
| Access denied / 1045 | Kiểm tra user, mật khẩu, cổng và quyền DB; không gửi mật khẩu |
| Can't connect / 2003 | Kiểm tra dịch vụ MySQL đang chạy và đúng 3306/3307 |
| Unknown database / 1049 | Tạo đúng DB và sửa DB_NAME |
| No database selected / 1046 | Chọn schema mặc định hoặc chạy USE trước mỗi file |
| Table already exists / 1050 hoặc duplicate key khi import | Đã nhập một phần; dùng DB thử trống mới, không nhập chồng |
| Không tạo được trigger | Kiểm tra quyền TRIGGER và log MySQL; không bỏ qua constraints |
| Thiếu SECRET_KEY | Sinh khóa, điền FLASK_SECRET_KEY trong .env |
| 503 trên web | Xem lỗi kết nối và /health/db; kiểm tra .env và DB_* đang ghi đè |
| Cổng 5000 đang dùng | Dừng phiên app cũ bằng Ctrl+C rồi chạy lại |
| Lỗi CSRF sau đổi khóa | Tải lại form rồi gửi lại |

## 7. Bằng chứng chốt tuần 1

Mỗi thành viên ghi: tên, ngày giờ, phiên bản Python/MySQL, hai SHA ở bước 1, tên DB (không mật khẩu), kết quả từng bước, lỗi và ảnh. Chụp audit trước/sau, trang bệnh nhân mới, kết quả SELECT và thông báo chặn xóa. Cập nhật issue tuần 1.

Cập nhật 18/10/2026, 19:51 (Asia/Ho_Chi_Minh): PR #7 đã hết Draft; Vương đã cập nhật bàn giao, rà 4/4 trang PDF và chạy tích hợp local. Quyền đã chạy Windows/Python 3.11.9/MySQL 8.4.11 trên DB clinic_week1_demo2: đủ 9 trigger, audit 1.144 dòng đúng và 9 nhóm findings rỗng; web và thêm/tìm/sửa/tải lại bệnh nhân được xác nhận. Chưa xác minh đầy đủ checklist/queries.sql trên máy Quyền hoặc nghiệm thu máy Trung. #7 đã merge; #6/#8 đã được Vuong-it review nhưng còn CHANGES_REQUESTED cần xác nhận lại sau cập nhật. Xem WEEK1_REVIEW_2026-10-18.md và bằng chứng Vương trong PR #7; không coi CI hoặc một máy là nghiệm thu cả ba máy.

## 8. Lỗi đã gặp khi chạy trên máy Quyền

- Workbench có thể mở file SQL qua VS Code: copy toàn bộ nội dung vào SQL tab, chọn đúng USE, Ctrl+A rồi Run. Kiểm tra đủ 11 bảng sau schema trước khi nhập seed.
- constraints.sql đã tạo chỉ mục nhưng lỗi 1064 và chưa có trigger: không chạy lại cả file. Kiểm tra information_schema.TRIGGERS, rồi chạy riêng từng CREATE TRIGGER nguyên khối bằng PyMySQL (không gửi DELIMITER hoặc dấu $$ cho server). Phiên Quyền xác nhận đủ 9 trigger sau cách này. Không coi nguyên nhân parser là đã được chứng minh chỉ từ lỗi 1064.
- MySQL trực tiếp dùng 3306 nhưng .env.example có 3307 cho Docker: sửa DB_PORT=3306. Test-NetConnection 127.0.0.1 -Port 3306 kiểm tra cổng, không kiểm tra tài khoản.
- Lỗi 1045 với user clinic_app: cấu hình DB_USER và DB_PASSWORD đúng tài khoản local. Biến DB_* trong PowerShell có thể ghi đè .env; dùng terminal mới sau khi lưu file. Không gửi mật khẩu/ảnh .env.
- Nếu chọn clinic_week1_demo2, phải dùng cùng tên trong USE và DB_NAME. Không tạo/import thêm DB chỉ vì cấu hình ứng dụng sai.
