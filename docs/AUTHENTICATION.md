# Đăng nhập và phân quyền — bản thử nghiệm

Không có khách demo, đăng ký công khai hoặc mật khẩu mặc định. Tất cả màn hình nghiệp vụ và API yêu cầu đăng nhập; `/health` chỉ trả trạng thái ứng dụng.

## Phạm vi quyền

| Vai trò | Chức năng |
|---|---|
| Admin | Tất cả chức năng hiện có; quản lý nhân sự, báo cáo Q1–Q4/R01–R07; tạo tài khoản, gán vai trò, đặt lại mật khẩu, khóa/mở hoặc xóa tài khoản tạo nhầm |
| Tiếp nhận | Xem/thêm/sửa/xóa hồ sơ bệnh nhân theo ràng buộc FK; tiếp nhận lượt chờ khám; xem danh sách/chi tiết lượt và kết thúc lượt khi đủ lần khám/hỗ trợ |
| Bác sĩ | Tra cứu bệnh nhân và lịch sử, xem lượt/đợt/đơn; khám, kê đơn, xác nhận khỏi cho đợt do chính bác sĩ liên kết với tài khoản phụ trách |
| Y tá | Tra cứu bệnh nhân và lịch sử, xem lượt/đợt/đơn; ghi/cập nhật hỗ trợ dưới mã y tá liên kết với tài khoản |

Hồ sơ và lịch sử bệnh nhân là dữ liệu dùng chung trong đội ngũ khám/chăm sóc. Giới hạn sở hữu bác sĩ áp dụng cho thao tác khám, kê đơn, xác nhận khỏi; không tách lịch sử của một bệnh nhân thành nhiều phần. Bản thử nghiệm chưa có phân công bệnh nhân cho từng nhân viên hoặc giới hạn truy cập theo khoa. Chỉ admin xem báo cáo tổng hợp, lương/doanh thu và hồ sơ nhân sự.

Quyền được kiểm tra ở backend, kể cả URL trực tiếp và POST giả mạo. Nút không phù hợp cũng được ẩn. Admin không bỏ qua các ràng buộc nghiệp vụ/FK.

Luồng tiếp nhận mới chỉ tạo lượt đang chờ khám. Bác sĩ thêm lần khám từ chi tiết lượt, y tá ghi hỗ trợ rồi tiếp nhận kết thúc lượt. Giới hạn có ít nhất một lần khám và hỗ trợ vẫn được kiểm tra khi kết thúc lượt. Admin/bác sĩ vẫn có thể dùng luồng gộp tiếp nhận + khám ban đầu đang có.

## Cài lần đầu trên máy thử

Dùng nhánh `feat/quyen-login-roles`, không cần cài thêm thư viện. Có thể tạo worktree mới từ PowerShell tại repo gốc:

```powershell
Set-Location 'C:\Users\LENOVO\OneDrive\Desktop\BTL-CSDL-PhongKhamTuNhan'
git fetch origin
git worktree add --detach '..\BTL-CSDL-auth' origin/feat/quyen-login-roles
Copy-Item .env '..\BTL-CSDL-auth\.env'
Set-Location '..\BTL-CSDL-auth'
$demoPython = 'C:\Users\LENOVO\OneDrive\Desktop\BTL-CSDL-PhongKhamTuNhan\.venv\Scripts\python.exe'
$env:FLASK_SECRET_KEY = & $demoPython -c 'import secrets; print(secrets.token_hex(32))'
$env:FLASK_DEBUG = 'false'
& $demoPython -m flask --app app init-auth --username admin
```

Nhập mật khẩu riêng **6–36 ký tự** hai lần; lúc nhập không hiện ký tự là bình thường. Dùng tài khoản MySQL có quyền tạo bảng cho bước này. Nếu admin đã có, lệnh từ chối tạo lại hoặc ghi đè mật khẩu. Không import lại seed hoặc file SQL nộp bài lên database đang dùng.

```powershell
& $demoPython .\app.py
```

Mở `http://127.0.0.1:5000/auth/login`. Admin đăng nhập rồi mở **Tài khoản** để tạo tiếp nhận, bác sĩ và y tá; chọn mã nhân sự đang có trong DB, không tự đoán mã. Có thể cấp thêm admin. Muốn đổi người dùng, bấm Đăng xuất. Thử nhiều tài khoản đồng thời bằng các trình duyệt/profile riêng; tab ẩn danh trong cùng một phiên thường dùng chung cookie.

Để dừng thử, Ctrl+C; chạy lại worktree `BTL-CSDL-demo` nếu muốn quay về bản cũ. Bảng tài khoản bổ sung không làm bản cũ ngừng hoạt động. Mật khẩu/phiên đăng nhập không được ghi vào repo hoặc ảnh/log bằng chứng.

## Dữ liệu và bảo mật

- Thêm bảng kỹ thuật `app_user` qua lệnh `init-auth` (DDL đối chiếu: `database/auth.sql`); không đổi 11 bảng nghiệp vụ, seed hoặc các truy vấn hiện có. Database có **12 bảng khi bật tính năng này**. Tính năng là phần mở rộng sau bộ tư liệu đã nộp; cần bổ sung mô tả nếu nhóm quyết định đưa vào bản báo cáo chính thức.
- Mật khẩu lưu bằng hàm băm có salt của Werkzeug, không lưu mật khẩu rõ. Không có tài khoản/mật khẩu mặc định trong SQL.
- Bác sĩ/y tá liên kết bằng FK tới hồ sơ nhân sự. Không xóa nhân sự đang liên kết với tài khoản; khóa tài khoản khi ngừng sử dụng.
- CSRF cho đăng nhập, đăng xuất và mọi thao tác ghi. Đăng nhập xóa phiên cũ. Phiên có thời hạn 8 giờ; đặt `COOKIE_SECURE=true` khi chỉ phục vụ qua HTTPS (bỏ/false khi thử HTTP localhost).
- Mỗi request tải lại vai trò và trạng thái từ DB. Đổi quyền/mật khẩu hoặc khóa tài khoản sẽ làm phiên cũ hết hiệu lực. Không tự khóa/hạ quyền admin đang dùng và không bỏ admin cuối cùng.
- Sai mật khẩu 5 lần khóa tài khoản 15 phút; admin có thể lưu lại tài khoản để mở khóa. Có thêm giới hạn theo IP 20 lần/15 phút trong một tiến trình. Khi triển khai nhiều worker/proxy cần rate limiter dùng kho chung và cấu hình proxy tin cậy; chưa có MFA, email khôi phục hoặc audit thao tác người dùng.
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
