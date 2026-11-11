# Bộ thiết kế yêu cầu 1

Bộ thiết kế hiện hành của Nhóm 02:

- `ER_Phong_kham_Ban_chot.pdf`: sơ đồ Chen cập nhật ngày 11/11/2026. Trang 1 thể hiện 9 thực thể, các liên kết, lực lượng 1/N và mức tham gia bằng nét đơn, nét đôi. Trang 2–3 thể hiện các thuộc tính.
- `Luoc_do_quan_he_Phong_kham_Ban_chot.pdf`: 11 bảng, PK/FK/UQ; trang 2 ràng buộc.
- `DATA_DICTIONARY.md`: phụ lục tên/kiểu vật lý để triển khai SQL, không thay mô hình khái niệm.

Phòng khám lưu hồ sơ bệnh nhân, bác sĩ, y tá; bệnh nhân có nhiều lượt đến khám và nhiều đợt theo bệnh. Một lượt có nhiều lần khám cho các bệnh khác nhau. Tái khám chưa khỏi nối cùng đợt, tái mắc sau khỏi mở đợt mới. Mỗi đợt do một bác sĩ cố định phụ trách; mỗi lần khám tối đa một đơn. Hỗ trợ y tá gắn lượt và lưu ngày bắt đầu; chi tiết đơn lưu số lượng, liều dùng, giá bán lịch sử. Tổng tiền là giá trị tính từ dữ liệu gốc.

Trước nộp cuối: đối chiếu tên/khóa và các quy ước trong SQL với hai PDF, kiểm tra đủ trang rõ nét, ghi nguồn tham khảo. Trạng thái thiết kế đã chốt theo nhóm; chưa khẳng định giảng viên đã duyệt hoặc toàn project hoàn tất.

Cập nhật tên vật lý 09/11/2026: thuộc tính CMT trong lược đồ PDF gốc tương ứng cột `cccd` trong SQL hiện hành. Không thay đổi ý nghĩa, kiểu hoặc lực lượng tham gia. Xem [migration](../CCCD_MIGRATION.md); bằng chứng lịch sử vẫn giữ tên cũ.
