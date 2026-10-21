# Trung phối hợp Vương — clone sạch máy thứ hai

Trạng thái 21/10/2026: tuần 2 đã tích hợp tại main f486929; quy trình máy thứ hai CHƯA thực chạy. Nhóm cần chốt SHA chứa cả PR #12 sau review trước nghiệm thu tuần 3. Không dùng kết quả nghiệm thu Windows tuần2 của Trung thay máy thứ hai tuần3.

## Điều kiện

#5/#10/#11 đã merge. Quyền chốt SHA release sau review thay đổi tuần 3. Dùng Git, Python3.11, MySQL8.4 và trình duyệt trên một máy khác máy chạy đầu tiên. Workbench không thay MySQL Server. Cần tài khoản DB thử riêng đủ quyền tạo bảng/trigger; không dùng DB đang làm bài. Chọn thư mục clone và tên DB mới, không xóa dữ liệu cũ.

## Clone và cài

PowerShell thường, không cần Admin. Điền SHA release đã chốt khi Read-Host hỏi:

```powershell
cd $env:USERPROFILE
git clone https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan.git clinic-week3-second-machine
cd clinic-week3-second-machine
$ReleaseSha = Read-Host 'SHA release da duoc nhom chot'
git switch --detach $ReleaseSha
git rev-parse HEAD
git status --short
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
if (!(Test-Path .env)) { Copy-Item .env.example .env }
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_hex(32))"
notepad .env
```

Nếu thư mục đã có, chọn tên mới. Điền FLASK_SECRET_KEY, DB_HOST/PORT/USER/PASSWORD/NAME theo máy; native MySQL thường3306, compose3307. DB_NAME ví dụ clinic_week3_machine2_test. Không đưa .env/khóa/mật khẩu vào bằng chứng. Mở terminal mới nếu biến DB_* cũ ghi đè .env. Nếu py không có, dùng đầy đủ đường dẫn Python3.11.

Trong Workbench tạo DB mới với utf8mb4_0900_ai_ci, chọn đúng schema ở từng tab. Làm theo SETUP đã thống nhất: schema → seed → audit → constraints → audit → queries. Dừng khi có lỗi; DDL có implicit commit nên import dở phải dùng DB trống mới. Không chạy chồng importer adapter, không bỏ trigger.

Chỉ sau khi phần tuần3 được merge, release mới có sẵn bộ kiểm tra. Nếu nhóm cần thử PR nháp trước merge, ghi rõ overlay của nhánh trung/week-3: dùng git fetch origin, rồi git restore --source origin/trung/week-3 -- week3_checks tools/trung_week3_preflight.py. Đây là thử snapshot release + overlay test, không gọi là clone sạch bản nộp cuối. Sau merge phải thử clone sạch lại.

## Kiểm tra

Từ thư mục clone, receipt yêu cầu SHA giống giá trị vừa chốt:

```powershell
.\.venv\Scripts\python.exe -m tools.trung_week3_preflight --expected-sha $ReleaseSha --output test-artifacts/week3/machine2-before.json
if ($LASTEXITCODE -ne 0) { throw 'Preflight khong dat; dung de kiem tra' }
$env:RUN_MYSQL_TESTS = '1'
.\.venv\Scripts\python.exe -m pytest week3_checks -v --junitxml=test-artifacts/week3/machine2-pytest.xml
if ($LASTEXITCODE -ne 0) { throw 'Test khong dat; luu log va bao loi' }
.\.venv\Scripts\python.exe app.py
```

Giữ app mở; vào http://127.0.0.1:5000/health/db rồi chạy luồng tiếp nhận → tái khám → kê đơn → hỗ trợ → đóng lượt/khỏi; thử dữ liệu sai, kiểm tra4báo cáo theo đáp án Quyền. Vương điều phối regression UI/T16, ghi input/expected/actual, không chỉ xác nhận trang mở được. Chỉ dùng hồ sơ giả riêng và dọn đúng mã đã tạo theo FK.

Dừng app Ctrl+C, chạy preflight lần nữa với --output test-artifacts/week3/machine2-after.json. Receipt cũ không bị ghi đè; lần chạy sau chọn tên file mới. Audit phải sạch và counts đúng sau dọn. Preflight chỉ đọc; không tự sửa dữ liệu để đạt.

## Biên bản cần điền sau khi thực chạy

| Mục | Kết quả |
|---|---|
| Người chạy, máy thứ hai, giờ Việt Nam | CHƯA CHẠY |
| OS/Python/MySQL/trình duyệt | CHƯA ĐO |
| SHA release, SHA hướng dẫn/checks, git status | CHƯA CHỐT |
| DB thử, không credentials | CHƯA TẠO |
| Clone/cấu hình/import11bảng9trigger | CHƯA CHẠY |
| Test tuần3 và regression UI | CHƯA CHẠY |
| Expected/actual, lỗi/bước tái hiện | CHƯA CHẠY |
| Dọn hồ sơ và audit cuối | CHƯA CHẠY |

Chỉ thay trạng thái bằng kết quả thực. Không dùng CI hoặc bản chạy trên máy cũ làm bằng chứng máy thứ hai.
