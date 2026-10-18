# Chạy backend tuần 1 của Trung

## Python 3.11 và MySQL 8.4

Trên Windows PowerShell, từ thư mục repository:

```powershell
git fetch origin
git switch trung/week-1
git pull --ff-only origin trung/week-1
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_hex(32))"
```

Chép chuỗi vừa tạo vào `FLASK_SECRET_KEY` trong `.env`. Điền mật khẩu do bạn tự đặt vào `MYSQL_ROOT_PASSWORD`, `MYSQL_PASSWORD`; `DB_PASSWORD` phải bằng `MYSQL_PASSWORD`. Không đưa `.env` lên Git.

Nếu đã có `.env`, sửa file hiện có, không chạy lệnh Copy-Item đè lên cấu hình.

## Tạo database trống

Chọn **một** cách:

- Docker: `docker compose up -d db`. Chờ trạng thái healthy bằng `docker compose ps`. Cấu hình mặc định `.env.example`: host `127.0.0.1`, port `3307`, user `clinic_app`, database `clinic_project1`.
- MySQL cài trực tiếp: tạo DB `clinic_project1` với charset `utf8mb4`, tạo user ứng dụng và cấp quyền cho DB này bằng Workbench. Sửa `DB_PORT=3306` và thông tin đăng nhập trong `.env`. Tài khoản nhập seed cần CREATE, REFERENCES, INSERT, SELECT; tài khoản chạy CRUD cần SELECT, INSERT, UPDATE, DELETE. Có thể dùng một tài khoản riêng cho database demo khi học.

Compose chỉ áp dụng MYSQL_* lúc tạo volume lần đầu. Đổi mật khẩu trong `.env` không đổi mật khẩu của database đã tồn tại. Không xóa volume chứa dữ liệu cần giữ để khắc phục đăng nhập.

## Nhập dữ liệu và chạy

```powershell
.\.venv\Scripts\python.exe -m tools.import_seed
.\.venv\Scripts\python.exe -m tools.audit_seed
.\.venv\Scripts\python.exe app.py
```

Mở http://127.0.0.1:5000/patients. Kiểm tra `/health` (Flask) và `/health/db` (kết nối MySQL).

Importer dùng `database/week1/clinic_seed.sql`: bản đổi tên định danh của SQL Vương bàn giao, 11 bảng/1.144 bản ghi. Importer từ chối DB không trống; không DROP, không tắt FK. MySQL DDL tự commit: nếu nhập lỗi giữa chừng, có thể còn bảng rỗng; giữ log và dùng một DB demo trống khác. Không nhập lại vào DB đang có dữ liệu.

**Không nhập `hospital_db.sql` cho backend này.** File đó thuộc ứng dụng bệnh viện tham khảo, không cùng schema. Bản adapter tuần 1 chờ Quyền review; chưa thay thế bộ SQL nộp cuối của nhóm.

Trên Linux/macOS, dùng `python3 -m venv .venv`, rồi `.venv/bin/python` thay cho đường dẫn Python Windows. Chạy các lệnh từ thư mục gốc repository.

## Kiểm thử

`python -m pytest -q` chạy unit test, bỏ qua integration nếu chưa bật. Muốn kiểm thử DB thật, tạo **DB trống riêng có tên kết thúc `_test`**, ví dụ `clinic_week1_test`, cấp quyền rồi cấu hình DB_NAME/đăng nhập cho DB đó. Import seed một lần, đặt `RUN_MYSQL_TESTS=1`, chạy pytest. Không chạy test trên database làm việc.

PowerShell ví dụ sau khi đã tạo DB test và cấu hình user có quyền:

```powershell
$env:DB_NAME = 'clinic_week1_test'
$env:RUN_MYSQL_TESTS = '1'
.\.venv\Scripts\python.exe -m tools.import_seed
.\.venv\Scripts\python.exe -m pytest -v
.\.venv\Scripts\python.exe -m tools.audit_seed
Remove-Item Env:RUN_MYSQL_TESTS
Remove-Item Env:DB_NAME
```

CI dùng MySQL 8.4, Python 3.11, nhập seed và chạy cùng các test. Xem kết quả thực tế trong tab Actions của PR; cấu hình workflow không tự chứng minh test đã qua.
