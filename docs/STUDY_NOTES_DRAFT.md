# Ghi chú học chung — tích lũy trong quá trình phát triển

Ngày cập nhật: 18/10/2026. Đây là ghi chú để tổng hợp sau khi sản phẩm hoàn thiện, **chưa phải tài liệu ôn tập cuối**.

| Câu hỏi cần giải thích | Ý chính | Điểm đối chiếu |
|---|---|---|
| Lượt đến, lần khám và đợt điều trị khác nhau thế nào? | Lượt là một lần đến phòng khám; lần khám gắn lượt với một đợt/bệnh; đợt theo dõi một bệnh từ bắt đầu đến khỏi. Một lượt có nhiều bệnh; tái khám chưa khỏi giữ đợt; tái mắc mở đợt mới. | Hai PDF YC1, DATA_DICTIONARY, 11 bảng |
| Vì sao bác sĩ ở đợt điều trị? | Bác sĩ phụ trách cố định một đợt; lần khám kế thừa qua đợt. Thưởng chữa khỏi theo ngày khỏi, không thưởng lặp từng lần khám. | dot_dieu_tri, Q2a |
| Thống kê bệnh đếm gì? | COUNT DISTINCT ma_dot có lần khám trong tháng; một đợt nhiều lần khám tính một, tái mắc hai đợt tính hai, qua tháng có khám được tính trong từng tháng tương ứng. | queries.sql Q1 |
| Vì sao y tá gắn lượt? | PK(ma_luot, ma_y_ta) tránh cộng nhiều khoản 200.000 cho nhiều công việc trong cùng lượt; ngày bắt đầu hỗ trợ xác định tháng thưởng. | ho_tro, Q2b |
| Vì sao không SUM tiền khám sau JOIN chi tiết thuốc? | Một lần khám nhiều dòng thuốc làm nhân bản tiền khám. Tổng hợp hai nguồn riêng rồi cộng. | queries.sql Q4 |
| Vì sao lưu đơn giá bán? | Giá hiện tại thay đổi không được đổi tiền đơn lịch sử. Dùng DECIMAL và so_luong * don_gia_ban; không dùng float. | chi_tiet_don_thuoc |
| FK/UQ/CHECK khác trigger/transaction thế nào? | Khóa và CHECK bảo vệ quy tắc hàng/quan hệ; trigger kiểm tra liên bảng; transaction đảm bảo nhiều bước cùng commit/rollback. Không tuyên bố MySQL trigger kiểm tra đủ số con khi COMMIT. | schema.sql, constraints.sql, db.py |
| Chống hai yêu cầu mở đợt trùng thế nào? | Khóa bệnh nhân theo thứ tự thống nhất, unique index đợt đang điều trị, rollback toàn giao dịch khi lỗi/deadlock. Không tắt FK. | constraints.sql, backend tuần 2 sẽ bổ sung |
| Vì sao seed trước trigger? | Seed chứa lịch sử đã đóng; trigger cho đường ghi mới yêu cầu mở rồi khám/hỗ trợ rồi đóng. Chỉ import một đường vào DB trống; DDL có implicit commit. | database/README.md |
| Vì sao placeholder chưa đủ cho tên bảng? | Placeholder cho giá trị; tên bảng/cột phải từ whitelist Entity cố định. Tìm kiếm escape %/_; Jinja autoescape và CSRF bảo vệ hai loại vấn đề khác nhau. | services.py, security.py |
| CI xanh có đủ chốt tuần 1 không? | Phải biết SHA, loại test, skipped, môi trường, audit và luồng browser–backend–DB. Còn cần review và chạy cùng hướng dẫn trên máy thành viên. | RULES, ACCEPTANCE, log CI |
| Vì sao squash PR stacked cần đồng bộ? | Sau squash lịch sử commit khác dù nội dung giống. Xem diff với main mới; tuần 2 không được lẫn vào tuần 1. Không force push nhánh chung. | PR #4/#5/#7 |

Phân công chuẩn bị: Quyền giải thích thiết kế/SQL; Trung giải thích route/DB/validation/rollback; Vương giải thích form, lỗi, trạng thái rỗng và bằng chứng trình duyệt. Cả ba cần hiểu luồng tổng thể. Bổ sung ví dụ và ảnh của phiên bản cuối sau nghiệm thu.
