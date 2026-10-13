# Cài đặt môi trường

## Công cụ thống nhất

Git, Python 3.11, MySQL 8.4 và VS Code/PyCharm. Nhóm dùng cùng MySQL để tránh khác biệt ràng buộc. Có thể cài MySQL trực tiếp hoặc dùng Docker Compose bên dưới, không cần cả hai.

## Clone và Python trên Windows PowerShell

```powershell
git clone https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan.git
cd BTL-CSDL-PhongKhamTuNhan
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Repo private: cần đăng nhập GitHub và được mời collaborator. Không gửi mật khẩu/token trong chat. Sửa `.env` với thông tin DB của máy mình và tự tạo FLASK_SECRET_KEY bằng `python -c "import secrets; print(secrets.token_hex(32))"`.

## Hai giai đoạn CSDL

- Hiện tại source gốc dùng `hospital_db.sql` và DB `hospital_db`. Import file bằng MySQL Workbench rồi chạy `python app.py` để khảo sát. Trên Linux, tên bảng hoa/thường của source còn cần chuẩn hóa; đây là việc Trung làm tuần 1. Chưa xác nhận source chạy hoàn chỉnh.
- Sau khi PR schema nhóm hoàn thành: dùng DB `clinic_project1`, chạy lần lượt `database/schema.sql`, `database/constraints.sql`, `database/seed.sql`, rồi đổi `DB_NAME=clinic_project1`. Chỉ làm khi backend đã chuyển sang 11 bảng; đổi tên DB đơn thuần không đủ.
- Không import schema gốc và schema nhóm chung một DB. Dữ liệu mẫu chỉ là dữ liệu giả.

## MySQL bằng Docker (tùy chọn)

Điền `MYSQL_ROOT_PASSWORD` và `MYSQL_PASSWORD` trong `.env`, sau đó:

```sh
docker compose up -d db
```

Container mở cổng localhost 3307; dùng `DB_HOST=127.0.0.1`, `DB_PORT=3307`, `DB_USER=clinic_app`, `DB_PASSWORD` bằng `MYSQL_PASSWORD`, `DB_NAME=clinic_project1`. Dịch vụ này tạo DB trống, không tự import schema gốc hay schema nhóm. Nếu khảo sát upstream, tạo/import DB `hospital_db` bằng tài khoản quản trị riêng rồi cấu hình đúng quyền; không dùng tài khoản root cho app lâu dài.

## Chạy và kiểm tra

```powershell
.\.venv\Scripts\python.exe app.py
.\.venv\Scripts\python.exe -m compileall -q app.py
```

Mở http://127.0.0.1:5000. CI ban đầu chỉ kiểm tra cú pháp và cú pháp template; các bài test MySQL/nghiệp vụ phải được bổ sung theo kế hoạch.
