# Quy tắc làm việc nhóm

Áp dụng từ 13/10/2026 cho Minh Quyền, Trung và Vương.

## Git và review

1. `main` chỉ chứa phiên bản đã review. Không push trực tiếp, force-push hoặc tự merge khi chưa có người khác review. Commit khởi tạo repo là ngoại lệ duy nhất.
2. Nhánh theo mẫu `quyen/week-1`, `trung/week-1`, `vuong/week-1`; nhánh tính năng nhỏ dùng `feat/<ten>-<viec>`, sửa lỗi dùng `fix/<ten>-<loi>`.
3. Mỗi PR mô tả vấn đề, thay đổi, cách chạy và bằng chứng kiểm thử. Một PR tập trung một đầu việc; liên kết issue bằng `Closes #...`.
4. Cần ít nhất một người khác review. Quyền duyệt thay đổi schema và điều phối merge; PR của Quyền do Trung hoặc Vương review. Resolve toàn bộ nhận xét trước merge.
5. Dùng squash merge. Không xóa nhánh làm việc của người khác. Sau khi PR được merge, tạo nhánh mới từ main cho phần tiếp theo để không lặp commit.
6. Trước khi làm: `git fetch origin`, cập nhật main và tạo/chuyển nhánh đúng. Không dùng `git reset --hard` hoặc force push để giải quyết xung đột chung.

## Phạm vi và dữ liệu

- Hai PDF trong docs/design là chuẩn thiết kế. Thay đổi bảng, khóa, công thức hay ý nghĩa thuộc tính phải có PR ghi lý do và cập nhật cả tài liệu, SQL, backend, UI liên quan.
- SQL vật lý dùng tên chữ thường snake_case tương ứng tên trong PDF: `benh_nhan`, `dot_dieu_tri`, `lan_kham_benh`... để thống nhất Windows/Linux.
- Tiền dùng DECIMAL, ngày dùng DATE/DATETIME, số điện thoại/CMT dùng chuỗi. Tham số người dùng đi qua placeholder SQL, không nối chuỗi vào câu truy vấn.
- Không commit .env, mật khẩu, token, dữ liệu bệnh nhân thật, thư mục venv/cache hoặc database dump cá nhân.
- Tạo lượt/đợt/lần khám/đơn nhiều bước phải có transaction và rollback khi lỗi. Không tắt kiểm tra FK để né lỗi dữ liệu.
- Tính thưởng và báo cáo đúng quy ước đã chốt; số tiền từ giao diện phải được server kiểm tra/tính lại.
- Giữ tác giả và nguồn upstream. Không tự gán giấy phép cho source bên thứ ba.

## Phân vùng tránh xung đột

- Quyền: `database/`, `docs/design/`, báo cáo SQL, review schema và tích hợp cuối.
- Trung: backend, kết nối DB, validation, transaction và route/service. Sở hữu `app.py` trong tuần 1.
- Vương: `templates/`, `static/`, hướng dẫn giao diện và bộ ca kiểm thử người dùng.
- `requirements.txt`, README, workflow và tài liệu tích hợp: báo trước trên issue/PR khi cùng sửa. Người khác được sửa vùng này sau trao đổi, không xem phân vùng là độc quyền.

## Nhịp làm việc

Cập nhật tiến độ sau mỗi buổi vào issue: đã làm / việc tiếp theo / vướng mắc. Báo blocker trong 24 giờ. PR trước 20:00 thứ Hai 19/10, 26/10, 02/11; chốt 20:00 thứ Ba 20/10, 27/10, 03/11 (Asia/Ho_Chi_Minh). Không đạt thì ghi phần thiếu, người chịu trách nhiệm và hạn bù cụ thể; không tự đánh dấu hoàn tất.

## Hoàn tất một đầu việc

Code chạy được theo hướng dẫn; test đúng/sai và ca biên; không lộ secrets; có bằng chứng; đã review và merge; cập nhật tài liệu. CI cú pháp xanh KHÔNG đồng nghĩa nghiệp vụ hay MySQL đã được kiểm thử.

## Trạng thái bảo vệ nhánh

Đã chọn chỉ squash merge, gợi ý cập nhật nhánh PR và giữ nhánh sau merge. GitHub thông báo bảo vệ nhánh không được thực thi với repo private/gói hiện tại; bước lưu rule còn yêu cầu xác thực lại (sudo). Vì vậy CHƯA có bảo vệ main được xác nhận lưu/thực thi. CODEOWNERS là tệp quy ước reviewer, không tự chặn push và tính năng thực thi cũng bị giới hạn gói. Nhóm phải tuân thủ PR/review thủ công; không đổi repo public để né giới hạn. Khi có gói hỗ trợ, bật PR + 1 approval + dismiss stale reviews + resolve conversations + không bypass/force-push/delete.
