# Tích hợp tuần 2 — 21/10/2026

> Phạm vi hiện hành 21/10/2026: bỏ T16/máy thứ hai theo quyết định Quyền; demo trên laptop Quyền. Các nhận xét T16 bên dưới là lịch sử của phiên trước, không còn là điều kiện nghiệm thu hoặc release. Không sửa kết quả kiểm thử gốc.

- #5 da59e56 đã squash merge tại 7575eb5; #10 1bf9f8b đã squash merge tại e9d4c97.
- Cập nhật nền #11 bằng merge commit có parent head Vương e1119e9 và main e9d4c97; không force push, không xóa nhánh.
- Giữ nguyên mọi file clinic_app của e1119e9 đã được Quyền/Trung review. Các sửa JSON/title/CSS Trung có cùng hành vi trong UI Vương; không đưa lại form tối thiểu.
- Nhập nguyên test_week2_review_regressions.py và hai tài liệu bàn giao/sửa của Trung da59e56. Hợp đồng giữ cả context Vương và ghi chú lỗi hạ tầng Trung.
- Giữ nguyên SQL/oracle #10; CI tổng bật QUYEN_CHECK_WEEK2=1 để đối chiếu backend hiện tại. Workflow riêng còn candidate pin lịch sử; không coi đó là bằng chứng thay bản cuối.
- Nghiệm thu Windows Quyền trên e1119e9: Python3.12.10/MySQL8.4.11, 168 passed/0 skipped, audit nền sạch; thao tác tay tái khám/đơn14.800đ/đóng lượt/doanh thu10.615.600đ. Bằng chứng: https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/pull/11#issuecomment-6306938226 . Không gán 168 cho bản mới thêm test Trung.
- Chờ CI trên tree tích hợp trước merge #11; kết quả cuối và SHA sẽ ghi ở PR/issue #2. T16 máy thứ hai thuộc tuần3, chưa xác nhận.
