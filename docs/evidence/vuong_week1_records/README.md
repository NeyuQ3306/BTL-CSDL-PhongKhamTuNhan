# Kiểm tra các trang hồ sơ tuần 1 của Vương

Ngày: 17/10/2026. Nhánh `vuong/week-1`, nền `c442384` cùng thay đổi UI chưa commit.

## Thay đổi

- Danh sách ba nhóm có cột thông tin phù hợp, thao tác xem/sửa, ngày dạng dd/mm/yyyy, hướng dẫn tìm kiếm và cuộn bảng bằng bàn phím.
- Phân biệt chưa có hồ sơ, tìm không có kết quả và trang vượt số trang. Không xóa dữ liệu mẫu để mô phỏng danh sách trống.
- Form có nhãn bắt buộc, hướng dẫn theo từng field, lỗi tổng hợp liên kết đến input, giữ dữ liệu và thông báo xung đột. Form sửa giữ đúng mã và đường dẫn hủy cả khi người gửi sửa trái phép mã trong POST.
- Trang chi tiết hiển thị rõ thông tin, giá trị thiếu, thao tác sửa/lịch sử và xác nhận xóa. Field, route và CSRF giữ nguyên.
- Bổ sung mã lỗi khóa ngoại MySQL 1217 cùng 1451 vào nhánh trả 409 khi hồ sơ có tham chiếu. Lỗi 1217 được tái hiện trên MySQL 8.0.46 tại máy này; không thay đổi ràng buộc hoặc cho phép xóa lịch sử.

## Kiểm thử tự động

Lệnh: `.venv/Scripts/python.exe -m pytest -q` với `RUN_MYSQL_TESTS=0` trong tiến trình kiểm tra.

Kết quả: **14 passed, 12 skipped**. Các test tích hợp gốc được bỏ qua vì không cấu hình database riêng có hậu tố `_test`. Không chạy bộ test đó trên database làm việc.

Ba ca hồi quy mới trong `tests/test_record_ui.py`: hai mã lỗi xóa tham chiếu 1217/1451 và điều hướng/mã readonly khi POST sửa mã không hợp lệ.

## Kiểm tra MySQL thật độc lập

Flask test client dùng database demo `clinic_vuong_week1`, MySQL 8.0.46, Python 3.14.6. Thực hiện đầy đủ cho cả bệnh nhân, bác sĩ và y tá:

| Tình huống | Kết quả |
|---|---|
| GET form, tên field và liên kết hint/error | Đúng hợp đồng, các ID được tham chiếu tồn tại |
| POST thiếu CSRF | 400 |
| Thiếu trường, ngày sinh tương lai | 422, hiển thị lỗi và giữ thông tin |
| Thêm hồ sơ giả tạm | 303, trang chi tiết có thông báo thành công |
| Tìm và tải lại hồ sơ đã lưu | 200, đọc đúng dữ liệu MySQL |
| Trùng mã, trùng CMT/CCCD | 409, có hướng dẫn và giữ dữ liệu form |
| Sửa mã trái phép | 422, input readonly và liên kết hủy vẫn dùng mã gốc |
| Cập nhật họ tên | 303, có thông báo cập nhật; HTML trong dữ liệu được escape |
| Không có kết quả, trang 999, hồ sơ không tồn tại | Trạng thái rỗng phù hợp / 404 |
| Xóa BN001, BS001, YT001 đang có tham chiếu | 409, giữ nguyên hồ sơ |
| Xóa hồ sơ thử vừa tạo | 303, có thông báo thành công; GET hồ sơ trả 404 |
| Database trống / thông tin NULL | Kiểm tra render với context giả lập, không sửa seed |

Hồ sơ thử của cả ba nhóm được dọn trong khối finally. Audit cuối: **11 bảng, 1.144 dòng**, đúng số lượng mẫu, không có phát hiện. Hash `.env` không đổi.

## Trình duyệt

- Duyệt 12 trang danh sách/thêm/chi tiết/sửa ở 320px, 390px và 1440px: 36 lượt kiểm tra, không tràn ngang toàn trang, đều có tiêu đề.
- Thử gửi form bệnh nhân với ngày sinh 2999-01-01: hiện lỗi đúng trường và giữ giá trị nhập. Bấm liên kết ở tóm tắt lỗi đưa focus tới ô ngày sinh. Không lưu hồ sơ sai này.
- Xem trực quan form sửa y tá, danh sách, chi tiết và tìm không có kết quả. Ảnh PNG trong cùng thư mục.

Đây là kiểm tra cục bộ theo phạm vi hồ sơ tuần 1, chưa phải nghiệm thu toàn dự án hoặc CI mới. Không thêm nghiệp vụ lượt khám/đơn thuốc/báo cáo tuần 2.
