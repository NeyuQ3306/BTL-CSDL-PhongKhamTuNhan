# Bàn giao Minh Quyền — tuần 1

Bàn giao ban đầu 17/10/2026; cập nhật 19/10/2026. Nhánh `quyen/week-1`, PR #6. Vuong-it đã review CHANGES_REQUESTED về import và bằng chứng; đã cập nhật tài liệu, còn chờ xác nhận lại trước merge.

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
4. Backend #4 và UI #7 đã squash merge; main e174f626. Nhánh SQL đã đồng bộ main, giữ nguyên code backend/UI. Hướng dẫn duy nhất là docs/SETUP.md: schema → seed → audit → constraints → audit → queries. PR #5 tuần 2 ngoài phạm vi.
5. Mốc từ điển 15/10 đã qua: bản này bàn giao 17/10, vì vậy không ghi hoàn thành đúng hạn ban đầu. Ưu tiên xác nhận ngay tên/kiểu trước 19/10.

## YC1 và bộ nộp

Hai PDF đã chốt trong `docs/design` giữ nguyên. Từ điển và ma trận ràng buộc là phụ lục triển khai, không thiết kế lại ER. Bộ nộp YC1 cần gồm mô tả, ER, lược đồ và ràng buộc; xem `docs/design/YC1_MANIFEST.md`. Chưa đánh dấu YC2/YC3 hoặc toàn bộ tuần 1 đã nghiệm thu vì còn review/merge và chạy máy nhóm.

## Học và giải thích phần của Quyền

Đọc schema theo thứ tự bảng cha → bảng con; giải thích vì sao MaBacSi ở đợt, vì sao không dùng COUNT(lần khám) cho Q1, vì sao thưởng theo ngày khỏi/ngày hỗ trợ, vì sao phải cộng tiền khám và tiền thuốc riêng. Thử thay tháng ở queries.sql, đối chiếu expected_results; chỉ thử câu SQL sai trong DB thử và rollback.

## Kết quả kiểm chứng

SQL 08e4427 đã qua 26 test SQL + 58 test backend snapshot; tích hợp với UI 33d45a0 đã qua 72/72 test. Giữ run 25 test trước đó là lịch sử, xem docs/evidence/quyen_week1_validation.md.

Vương đã có bằng chứng local 72/72 và rà 4/4 trang PDF. Quyền đã chạy trên Windows/Python 3.11.9/MySQL 8.4.11: audit 11 bảng/1.144 dòng sạch, xác nhận 9 trigger và thêm/tìm/sửa/tải lại bệnh nhân. Chưa coi đó là toàn bộ checklist hoặc nghiệm thu máy Trung.

Sau đồng bộ main, CI e46978d phát hiện thiếu Flask ở job SQL và job backend dùng seed adapter thiếu trigger (11 failed/61 passed). Đã sửa workflow dùng requirements-dev và bộ schema/seed/constraints chuẩn trong DB CI trống; xem Checks theo head mới để biết kết quả. Đây là sửa cấu hình CI, không đổi SQL/ứng dụng hoặc bỏ test.
