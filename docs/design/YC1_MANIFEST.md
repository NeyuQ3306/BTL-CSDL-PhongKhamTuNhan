# Bộ thiết kế yêu cầu 1

Giữ bản chốt 13/10/2026:

- `ER_Phong_kham_Ban_chot.pdf`: 9 thực thể và các liên kết, min/max; trang 2 mô tả ràng buộc.
- `Luoc_do_quan_he_Phong_kham_Ban_chot.pdf`: 11 bảng, PK/FK/UQ; trang 2 ràng buộc.
- `DATA_DICTIONARY.md`: phụ lục tên/kiểu vật lý để triển khai SQL, không thay mô hình khái niệm.

Phòng khám lưu hồ sơ bệnh nhân, bác sĩ, y tá; bệnh nhân có nhiều lượt đến khám và nhiều đợt theo bệnh. Một lượt có nhiều lần khám cho các bệnh khác nhau. Tái khám chưa khỏi nối cùng đợt, tái mắc sau khỏi mở đợt mới. Mỗi đợt do một bác sĩ cố định phụ trách; mỗi lần khám tối đa một đơn. Hỗ trợ y tá gắn lượt và lưu ngày bắt đầu; chi tiết đơn lưu số lượng, liều dùng, giá bán lịch sử. Tổng tiền là giá trị tính từ dữ liệu gốc.

Trước nộp cuối: đối chiếu tên/khóa và các quy ước trong SQL với hai PDF, kiểm tra đủ trang rõ nét, ghi nguồn tham khảo. Trạng thái thiết kế đã chốt theo nhóm; chưa khẳng định giảng viên đã duyệt hoặc toàn project hoàn tất.
