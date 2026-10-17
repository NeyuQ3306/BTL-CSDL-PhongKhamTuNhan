# Bàn giao Minh Quyền — tuần 1

Ngày 17/10/2026, trước mốc nhóm 20/10. Nhánh `quyen/week-1`, PR về `main`; chờ Trung hoặc Vương review, không tự merge.

## Phần đã triển khai

- Đối chiếu đề Project 1 và bản chốt 9 thực thể/11 bảng; giữ bác sĩ tại đợt, một đơn mỗi lần khám, PK hỗ trợ theo lượt/y tá, giá bán thuốc lịch sử.
- Kế thừa SQL Vương/adapter Trung, tách schema và seed, giữ đúng 1.144 dòng; không nhận phần dữ liệu của Vương là tự viết.
- Từ điển dữ liệu: `docs/design/DATA_DICTIONARY.md`; giữ tên/kiểu đang được backend Trung sử dụng.
- `database/constraints.sql`: ràng buộc bổ sung. Phạm vi và giới hạn ghi rõ trong `database/README.md`.
- `database/queries.sql`: bản nháp đủ bốn nhóm truy vấn; `expected_results.md`: kết quả độc lập, ca tính tay nhỏ và số lượng bảng.
- `database/audit.sql`: kiểm tra liên bảng/cận dưới/thời gian; bộ test trực tiếp MySQL và workflow riêng `Quyen database MySQL 8.4`.

## Phối hợp trước chốt tuần 1

1. Trung review constraints/schema và đường import. CI tương thích dùng snapshot tuần 2 `26bc627b5bd8943f275d369a0d86f2d640aaf06f`, không merge hay thay code Trung. Nếu nhánh Trung đổi sau snapshot, cần chạy lại trên phiên bản mới trước merge.
2. Vương xác nhận field từ điển và route/form của Trung; chạy luồng thêm/xem bệnh nhân trên máy nhóm. Không thay dữ liệu mẫu bằng dữ liệu thật.
3. Cả nhóm import DB mới theo README database, kiểm tra audit rỗng và kết quả báo cáo; ghi bằng chứng demo vào issue #1. SQL test không thay thế thao tác UI thực tế.
4. PR #4 hiện chờ review; PR #5 dựa trên nhánh tuần 1 của Trung. Các file SQL mới của Quyền tách riêng để hạn chế conflict. `database/README.md` có thể cần gộp hướng dẫn khi merge; giữ attribution.
5. Mốc từ điển 15/10 đã qua: bản này bàn giao 17/10, vì vậy không ghi hoàn thành đúng hạn ban đầu. Ưu tiên xác nhận ngay tên/kiểu trước 19/10.

## YC1 và bộ nộp

Hai PDF đã chốt trong `docs/design` giữ nguyên. Từ điển và ma trận ràng buộc là phụ lục triển khai, không thiết kế lại ER. Bộ nộp YC1 cần gồm mô tả, ER, lược đồ và ràng buộc; xem `docs/design/YC1_MANIFEST.md`. Chưa đánh dấu YC2/YC3 hoặc toàn bộ tuần 1 đã nghiệm thu vì còn review/merge và chạy máy nhóm.

## Học và giải thích phần của Quyền

Đọc schema theo thứ tự bảng cha → bảng con; giải thích vì sao MaBacSi ở đợt, vì sao không dùng COUNT(lần khám) cho Q1, vì sao thưởng theo ngày khỏi/ngày hỗ trợ, vì sao phải cộng tiền khám và tiền thuốc riêng. Thử thay tháng ở queries.sql, đối chiếu expected_results; chỉ thử câu SQL sai trong DB thử và rollback.

## Kết quả kiểm chứng

Đã qua 25 test SQL và 58 test backend tương thích trên MySQL 8.4.11; có log CI trong `docs/evidence/quyen_week1_validation.md`. Test coverage seed bổ sung đã qua local; xem Checks của PR để lấy lần chạy cuối. Không có MySQL server cục bộ trong môi trường làm việc, nên bằng chứng chạy DB là GitHub Actions, không phải giả lập SQLite.
