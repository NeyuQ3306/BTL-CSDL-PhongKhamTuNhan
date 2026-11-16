# Đăng nhập và phân quyền

Không có đăng ký công khai hoặc mật khẩu mặc định. Admin có thể cấp vai trò Người xem cho lớp dùng chung. Tất cả màn hình nghiệp vụ và API yêu cầu đăng nhập; `/health` chỉ trả trạng thái ứng dụng.

## Phạm vi quyền

| Vai trò | Chức năng |
|---|---|
| Admin | Tất cả chức năng hiện có; quản lý nhân sự, báo cáo Q1–Q4/R01–R07; tạo tài khoản, gán vai trò, đặt lại mật khẩu, khóa/mở hoặc xóa tài khoản tạo nhầm |
| Người xem | Xem hồ sơ bệnh nhân, lịch sử, lượt/đợt/đơn thuốc, Q1–Q4 và R01–R07, sử dụng bộ lọc; không xem trang quản lý nhân sự/tài khoản, không thêm/sửa/xóa |
| Tiếp nhận | Xem/thêm/sửa/xóa hồ sơ bệnh nhân theo ràng buộc FK; tiếp nhận lượt chờ khám; xem danh sách/chi tiết lượt và kết thúc lượt khi đủ lần khám/hỗ trợ |
| Bác sĩ | Tra cứu bệnh nhân và lịch sử, xem lượt/đợt/đơn; khám, kê đơn, xác nhận khỏi cho đợt do chính bác sĩ liên kết với tài khoản phụ trách |
| Y tá | Tra cứu bệnh nhân và lịch sử, xem lượt/đợt/đơn; ghi/cập nhật hỗ trợ dưới mã y tá liên kết với tài khoản |

Hồ sơ và lịch sử bệnh nhân là dữ liệu dùng chung trong đội ngũ khám/chăm sóc. Giới hạn sở hữu bác sĩ áp dụng cho thao tác khám, kê đơn, xác nhận khỏi; không tách lịch sử của một bệnh nhân thành nhiều phần. Hiện tại chưa có phân công bệnh nhân cho từng nhân viên hoặc giới hạn truy cập theo khoa. Admin và Người xem xem được báo cáo tổng hợp, lương/doanh thu phục vụ demo dữ liệu giả lập. Chỉ admin quản lý hồ sơ nhân sự và tài khoản.

Quyền được kiểm tra ở backend, kể cả URL trực tiếp và POST giả mạo. Nút không phù hợp cũng được ẩn. Admin không bỏ qua các ràng buộc nghiệp vụ/FK.

Luồng tiếp nhận mới chỉ tạo lượt đang chờ khám. Bác sĩ thêm lần khám từ chi tiết lượt, y tá ghi hỗ trợ rồi tiếp nhận kết thúc lượt. Giới hạn có ít nhất một lần khám và hỗ trợ vẫn được kiểm tra khi kết thúc lượt. Admin/bác sĩ vẫn có thể dùng luồng gộp tiếp nhận + khám ban đầu đang có.

## Cài lần đầu trên máy thử

Sau khi cấu hình `.env` và nhập CSDL mới theo [SETUP](SETUP.md), chạy từ gốc repo bằng PowerShell:

```powershell
.\.venv\Scripts\python.exe -m flask --app app init-auth --username admin
.\.venv\Scripts\python.exe app.py
```

Nhập mật khẩu riêng **6–36 ký tự** hai lần; lúc nhập không hiện ký tự là bình thường. Bước khởi tạo cần tài khoản MySQL có quyền CREATE bảng. Nếu admin đã có, lệnh từ chối tạo lại hoặc ghi đè mật khẩu. Máy đã có bảng tài khoản bản cũ dùng `upgrade-auth` ở phần bên dưới; không import lại seed hoặc bộ SQL nộp bài.

Mở `http://127.0.0.1:5000/auth/login`. Admin mở **Tài khoản** để tạo Tiếp nhận, Bác sĩ, Y tá hoặc Người xem; chọn mã nhân sự có thật cho bác sĩ/y tá. Thử nhiều tài khoản bằng các trình duyệt/profile riêng. Tab ẩn danh trong cùng một phiên có thể dùng chung cookie. Mật khẩu và phiên đăng nhập không đưa vào repo hoặc ảnh/log bằng chứng.

Phương án Trung trình chiếu, Vương mở QR và điều kiện hai database độc lập: [DEMO_TWO_MACHINES](DEMO_TWO_MACHINES.md).

## Dữ liệu và bảo mật

- Thêm bảng kỹ thuật `app_user` qua lệnh `init-auth` (DDL đối chiếu: `database/auth.sql`); không đổi 11 bảng nghiệp vụ, seed hoặc các truy vấn hiện có. Database có **12 bảng khi bật tính năng này**. Tính năng là phần mở rộng sau bộ tư liệu đã nộp; cần bổ sung mô tả nếu nhóm quyết định đưa vào bản báo cáo chính thức.
- Mật khẩu lưu bằng hàm băm có salt của Werkzeug, không lưu mật khẩu rõ. Không có tài khoản/mật khẩu mặc định trong SQL.
- Bác sĩ/y tá liên kết bằng FK tới hồ sơ nhân sự. Không xóa nhân sự đang liên kết với tài khoản; khóa tài khoản khi ngừng sử dụng.
- CSRF cho đăng nhập, đăng xuất và mọi thao tác ghi. Đăng nhập xóa phiên cũ. Phiên có thời hạn 8 giờ; đặt `COOKIE_SECURE=true` khi chỉ phục vụ qua HTTPS (bỏ/false khi thử HTTP localhost).
- Mỗi request tải lại vai trò và trạng thái từ DB. Đổi quyền/mật khẩu hoặc khóa tài khoản sẽ làm phiên cũ hết hiệu lực. Không tự khóa/hạ quyền admin đang dùng và không bỏ admin cuối cùng.
- Sai mật khẩu 5 lần khóa tài khoản 15 phút; admin có thể lưu lại tài khoản để mở khóa. Có thêm giới hạn theo IP 20 lần thất bại/15 phút trong một tiến trình; đăng nhập thành công không tiêu hao hạn mức này, tránh chặn lớp dùng chung qua tunnel. Khi triển khai nhiều worker/proxy cần rate limiter dùng kho chung và cấu hình proxy tin cậy; chưa có MFA, email khôi phục hoặc audit thao tác người dùng.
- Chỉ được tắt auth bằng `AUTH_ENABLED=False` trong `TESTING=True` của các bộ kiểm thử hồi quy. Không có biến môi trường tắt xác thực ở bản chạy thông thường. Các runner kiểm thử riêng chạy với cấu hình này để giữ kiểm tra nghiệp vụ cũ, không dùng các runner đó làm máy chủ demo công khai.

## Checklist thử cùng nhóm

1. Chưa đăng nhập: mở trang bệnh nhân phải về đăng nhập; API không trả dữ liệu.
2. Admin: mở đủ màn hình Q1–Q4, R01–R07, nhân sự và Tài khoản; tạo ba tài khoản còn lại.
3. Tiếp nhận: tạo/sửa hồ sơ bệnh nhân, tiếp nhận lượt chờ; không thấy báo cáo/nhân sự/kê đơn. URL trực tiếp bị từ chối.
4. Bác sĩ: thêm lần khám vào lượt chờ, kê đơn/xác nhận khỏi trong đợt của mình; thử đợt bác sĩ khác phải bị từ chối.
5. Y tá: ghi hỗ trợ của mình; không sửa kết luận, kê đơn hoặc hỗ trợ dưới mã y tá khác.
6. Tiếp nhận kết thúc lượt khi đủ khám/hỗ trợ; không kết thúc lượt thiếu dữ liệu.
7. Admin khóa/đổi vai trò tài khoản đang đăng nhập ở trình duyệt khác: phiên đó phải đăng nhập lại.
8. Đăng xuất: mở lại URL cũ không được xem dữ liệu. Kiểm tra desktop và điện thoại.

Kiểm thử auth riêng: `python -m pytest tests/test_auth.py tests/test_auth_mysql.py -v`.
Kiểm thử MySQL cần `RUN_MYSQL_TESTS=1` và DB riêng kết thúc `_test`, đã import seed. Bài kiểm thử tự tạo/xóa bảng tài khoản của nó; từ chối chạy nếu bảng đó đã tồn tại.


### Xóa tài khoản tạo nhầm

Admin vào **Tài khoản**, mở tài khoản cần xóa rồi mở **Xóa tài khoản**, nhập chính xác tên đăng nhập và bấm **Xác nhận xóa tài khoản**. Không thể tự xóa admin đang đăng nhập hoặc xóa admin hoạt động cuối cùng. Tài khoản bị xóa không đăng nhập được, các phiên cũ hết hiệu lực ở request tiếp theo. Không xóa hồ sơ bác sĩ/y tá, bệnh nhân hay lịch sử khám liên quan.

Giới hạn 6–36 ký tự áp dụng khi tạo/đổi mật khẩu (kể cả init-auth). Mật khẩu đã tạo trước đó được giữ nguyên và vẫn đăng nhập được.


## Dùng chung tài khoản Người xem qua Cloudflare

Máy đã khởi tạo tài khoản ở bản trước: dừng web, cập nhật code rồi chạy `python -m flask --app app upgrade-auth` một lần bằng tài khoản MySQL có quyền ALTER bảng. Lệnh chạy lại an toàn, chỉ mở rộng CHECK vai trò; không xóa tài khoản/mật khẩu hay dữ liệu nghiệp vụ. Máy mới dùng init-auth như trên; không import lại seed.

Admin vào Tài khoản, tạo tên như `lop_demo`, đặt mật khẩu riêng 6–36 ký tự và chọn **Người xem**. Không chọn mã bác sĩ/y tá cho vai trò này. Chia sẻ link Cloudflare/QR và tài khoản đó; không chia sẻ admin. Mỗi trình duyệt có cookie/phiên riêng, nhiều người đăng nhập đồng thời được; một người đăng xuất không kết thúc phiên người khác. Các bộ lọc nằm trong URL/request, không sửa dữ liệu chung. Đổi mật khẩu/quyền, khóa hoặc xóa tài khoản dùng chung sẽ vô hiệu hóa tất cả phiên của tài khoản đó ở request tiếp theo.

Tài khoản dùng chung vẫn áp dụng khóa 15 phút nếu sai mật khẩu 5 lần; admin có thể lưu lại tài khoản để mở khóa. Chỉ dùng dữ liệu giả lập cho lớp; quyền đọc không ngăn người xem chụp/tải nội dung. Tunnel vẫn cần laptop, Flask, MySQL và Internet hoạt động; số người phục vụ đồng thời phụ thuộc tài nguyên máy, chưa có kiểm thử tải cả lớp.
