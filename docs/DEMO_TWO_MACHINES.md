# Demo hai máy và chia sẻ QR

## Phân vai và dữ liệu

| Máy | Mục đích | Tài khoản website | Database |
|---|---|---|---|
| Trung | Trình chiếu và demo nghiệp vụ | Admin riêng trên máy Trung | MySQL/schema riêng của Trung |
| Vương | Chạy website để cả lớp truy cập qua tunnel/QR | Admin riêng để chuẩn bị; Người xem dùng chung cho lớp | MySQL/schema riêng của Vương |

Hai bản clone cùng repo không tự đồng bộ MySQL. Tài khoản lưu trong `app_user` của database mà app kết nối tới, không gắn cố định với máy tạo hay tài khoản GitHub. Mỗi app đọc `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER` và `DB_PASSWORD` của môi trường chạy.

Nếu hai app kết nối tới hai database độc lập, thêm/sửa/xóa trên app Vương chỉ thay đổi DB Vương, không thay đổi DB Trung. Nếu cùng kết nối tới một database từ xa, dữ liệu và tài khoản dùng chung dù chạy trên hai laptop. Khác tên thư mục, cổng Flask, admin hoặc khóa phiên không tạo sự tách biệt database.

## Chuẩn bị

1. Hai máy cập nhật cùng bản `main`, ghi SHA bằng `git rev-parse HEAD` và cài theo [SETUP](SETUP.md).
2. Mỗi máy kiểm cấu hình kết nối thực tế, kể cả biến môi trường có thể ghi đè `.env`. Đối chiếu server/schema bằng thông tin kết nối và `SELECT @@hostname, @@port, DATABASE();` trên từng kết nối. Không công khai mật khẩu hoặc chụp `.env`.
3. Máy mới nhập SQL vào schema mới trống rồi chạy `init-auth`; máy đã có tài khoản bản cũ chạy `upgrade-auth` theo [AUTHENTICATION](AUTHENTICATION.md). Không nhập lại seed lên DB đang sử dụng.
4. Trung đăng nhập admin riêng để trình chiếu. Vương đăng nhập admin của DB Vương, tạo tài khoản vai trò **Người xem** và mật khẩu riêng 6–36 ký tự cho lớp. Không chia sẻ admin.
5. Kiểm trên từng máy: đăng nhập, `/health`, `/health/db` bằng admin, hồ sơ, Q1–Q4 và R01–R07. Kiểm QR bằng một điện thoại trước buổi báo cáo; đây là checklist cần thực hiện trên máy thật, không phải xác nhận đã chạy.

## Tunnel và QR

Trên máy Vương, chạy Flask theo SETUP, sau đó dùng công cụ Cloudflare Tunnel đã cài để trỏ vào địa chỉ Flask thực chạy. Ví dụ với Quick Tunnel:

```powershell
cloudflared tunnel --url http://127.0.0.1:5000
```

Nếu Flask dùng cổng 5001, thay cổng đích tương ứng. Lấy URL HTTPS mà tunnel trả về, mở thử `/auth/login` trên điện thoại và tạo QR từ URL công khai đó. Không dùng `localhost` hoặc `127.0.0.1` làm URL trong QR cho lớp. Tunnel phải chạy trên máy Vương và trỏ tới app Vương. QR chỉ chứa địa chỉ website; không tự chọn/tạo tài khoản hoặc chứa mật khẩu.

Gửi riêng thông tin đăng nhập Người xem cho lớp. Mỗi trình duyệt có phiên riêng; đăng xuất một máy không đăng xuất các máy khác. Người xem dùng bộ lọc và đọc kết quả, backend chặn thao tác ghi. Nếu nhóm muốn thử ghi, chỉ người phụ trách dùng tài khoản có quyền trên DB Vương; không cấp admin cho cả lớp.

Máy Vương, Flask, MySQL, tunnel và Internet phải hoạt động trong suốt thời gian truy cập. Quick Tunnel đổi URL khi tạo phiên mới thì phải tạo QR mới. Chưa có bằng chứng kiểm thử tải đồng thời cả lớp.

## Trước và sau buổi báo cáo

- Trung giữ DB trình chiếu riêng và chuẩn bị luồng tiếp nhận → khám → đơn nhiều thuốc → lịch sử → báo cáo; cả nhóm trình bày 10 phút, hỏi đáp 5 phút theo thông báo môn CSDL.
- Vương xác nhận tài khoản Người xem không có nút ghi; thử truy cập trang tài khoản hoặc form ghi phải bị từ chối. R01–R07 phải trả dữ liệu sau đăng nhập.
- Kết thúc, dừng tunnel và khóa tài khoản dùng chung hoặc đổi mật khẩu nếu không tiếp tục chia sẻ. Thay đổi này chỉ tác động DB Vương khi hai DB độc lập.

Giới hạn đọc hồ sơ và cơ chế thu hồi phiên xem [AUTHENTICATION](AUTHENTICATION.md).
