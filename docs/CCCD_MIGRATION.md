# Đổi tên cột định danh thành cccd

Bản cập nhật này đổi tên `cmt` thành `cccd` trong ba bảng `bac_si`, `y_ta`, `benh_nhan`, schema, seed, SQL gộp, backend, Jinja, công cụ demo và kiểm thử. Giữ nguyên dữ liệu, vị trí cột, VARCHAR(20), NOT NULL, UNIQUE và quy tắc nhập 9–20 chữ số để tương thích dữ liệu hiện có. Đây là đổi tên kỹ thuật, không phải xác thực CCCD theo cơ quan nhà nước.

## Database mới

Theo hướng dẫn SETUP, dùng schema mới và nhập `database/project1_submission.sql` hoặc bộ file rời. Không chạy cả hai cách. Các file mới đã dùng `cccd`; không cần migration trên schema trống.

## Database đã có dữ liệu

1. Dừng tất cả tiến trình app kết nối schema cần đổi, kể cả bản đang host. Sao lưu database và kiểm tra có thể khôi phục. Không nhập lại seed và không xóa bảng.
2. Lấy nhánh/commit có bản cập nhật này sau khi được review. Giữ nguyên `.env` đúng database đang dùng, không đăng mật khẩu lên GitHub.
3. Kiểm tra trước (chỉ đọc):

   ```powershell
   .\.venv\Scripts\python.exe -m tools.migrate_cccd
   ```

4. Đổi cột bằng lệnh tường minh:

   ```powershell
   .\.venv\Scripts\python.exe -m tools.migrate_cccd --apply
   ```

   Có thể thay bước 3–4 bằng cách chọn đúng schema trong MySQL Workbench và chạy toàn bộ `database/migrations/001_cmt_to_cccd.sql`. Tài khoản cần ALTER và CREATE/ALTER ROUTINE. Script chỉ tạo/xóa procedure phục vụ migration, không xóa dữ liệu bảng.

5. Kiểm tra cả ba bảng dùng `cccd`, chạy audit, rồi mở app mới để thử thêm/sửa, trùng CCCD, tìm kiếm, xem chi tiết và lịch sử:

   ```powershell
   .\.venv\Scripts\python.exe -m tools.migrate_cccd
   .\.venv\Scripts\python.exe -m tools.audit_seed
   .\.venv\Scripts\python.exe app.py
   ```

   `audit_seed` có kiểm tra số lượng seed; nếu database đã có dữ liệu demo thì số lượng có thể khác 1.144. Giữ log và đối chiếu với dữ liệu trước migration, không xóa bản ghi để ép khớp seed.

MySQL DDL có implicit commit. Ba ALTER không phải một transaction duy nhất; nếu bị ngắt, giữ app dừng và kiểm tra. Script kiểm tra cả ba bảng trước ALTER đầu tiên, cho phép chạy lại sau khi đã đổi một phần hoặc toàn bộ. Nếu một bảng có cả hai tên hoặc thiếu cả hai, script từ chối trước khi đổi cột. Không chạy đồng thời nhiều phiên migration. Backend cũ dùng `cmt` sẽ không tương thích sau migration; triển khai app mới và đổi schema trong cùng đợt bảo trì.

## Tài liệu và bằng chứng

Từ điển dữ liệu hiện hành dùng `cccd`; báo cáo của Vương đã dùng tên mới. CMT trong hai PDF thiết kế gốc và ảnh/log kiểm thử cũ là ký hiệu của bản thiết kế trước đổi tên, tương ứng với `cccd` trong SQL mới. Giữ nguyên bằng chứng lịch sử, không chỉnh ảnh/log hay hash cũ để giả thành lần kiểm thử mới. Khi cần ảnh giao diện dùng nhãn CCCD mới, chụp lại trên bản đã migrate.

PR chỉ chuẩn bị mã và script. Việc chạy script trên database laptop/hosting cần thực hiện tại nơi có kết nối tới database đó; không tự coi database bên ngoài đã được nâng cấp.
