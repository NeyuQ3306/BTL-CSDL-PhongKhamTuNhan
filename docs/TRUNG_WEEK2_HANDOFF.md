# Bàn giao backend tuần 2 — Trung

Phạm vi: luồng lượt/đợt/lần khám, hỗ trợ y tá, xác nhận khỏi, kê đơn và bốn báo cáo. Theo PDF phân công mốc 27/10/2026; PR trước 20:00 ngày 26/10.

## Quan hệ với tuần 1

Nhánh `trung/week-2` kế thừa `trung/week-1` commit `c442384` (PR #4 chưa merge khi bắt đầu). PR tuần 2 tạm đặt base `trung/week-1` để chỉ xem thay đổi mới. Sau khi PR #4 được squash merge, cần chuyển phần thay đổi tuần 2 lên main mới và đổi base; không tự merge hai PR, không force-push nhánh của người khác.

Không đổi 11 bảng hoặc seed của Vương. Không sửa thư mục UI gốc `templates/`, `static/`. UI chạy thử backend ở `clinic_app/templates/week2` và phần tuần 1 được nối thêm điều hướng để Vương tích hợp. SQL báo cáo nằm trong `clinic_app/reports.py`, chờ Quyền đối chiếu với queries.sql/đáp án độc lập của nhóm.

## Đã triển khai

- Tạo lượt + đợt mới hoặc tái khám + lần khám + hỗ trợ y tá trong một transaction. Không có lượt/đợt rỗng nếu một bước lỗi.
- Thêm bệnh khác vào lượt đang mở; tự cấp STT trong đợt, từ 1 tăng liên tiếp.
- Một bệnh nhân chỉ có một đợt đang điều trị cùng bệnh; tái mắc sau ngày khỏi tạo mã đợt mới. Không chồng khoảng điều trị.
- Kiểm tra cùng bệnh nhân giữa lượt và đợt; bác sĩ cố định theo đợt; không khám thêm sau khi khỏi hoặc lượt đóng; ngày phải trong khoảng hợp lệ.
- Hỗ trợ cùng y tá/lượt cập nhật nội dung, không tạo thêm khoản thưởng; ngày bắt đầu hỗ trợ cũ không thay đổi.
- Đóng lượt kiểm tra ngày ra không trước lần khám/hỗ trợ; xác nhận khỏi không trước lần khám cuối.
- Đơn + chi tiết lưu nguyên tử; mỗi lần khám tối đa một đơn, mỗi thuốc một dòng, đơn không rỗng. Server lấy giá hiện tại rồi lưu đơn giá bán. Không tin giá/tổng tiền từ browser.
- Thống kê bệnh đếm DISTINCT mã đợt có khám trong tháng; tái mắc tính đợt mới.
- Lương BS: 7 triệu + 1 triệu/đợt khỏi theo ngày khỏi; y tá: 5 triệu + 200 nghìn/cặp y tá/lượt theo ngày hỗ trợ.
- Lịch sử đủ thông tin bệnh nhân, lượt, đợt, lần khám, đơn/thuốc/liều/giá, y tá hỗ trợ, bệnh đang điều trị và STT hiện tại.
- Doanh thu cộng riêng tiền khám và chi tiết đơn; không nhân đôi tiền khám khi JOIN nhiều thuốc.

## Đồng thời và rollback

Mọi service ghi nghiệp vụ lấy khóa `SELECT ... FOR UPDATE` trên bệnh nhân trước, sau đó đọc khóa hiện thời trên lượt/đợt/lần khám. Nhờ đó hai request của cùng bệnh nhân không cùng tạo đợt đang điều trị hoặc cùng cấp STT. Tham chiếu danh mục dùng FOR SHARE; giá thuốc được khóa theo thứ tự mã. Lỗi rollback toàn bộ; không tự retry ghi vì có thể gây lặp.

Bảo đảm này áp dụng cho đường ghi qua backend. Chưa có trigger bảo vệ người dùng SQL trực tiếp; Quyền vẫn phụ trách constraints.sql và review schema. Không cho thay chủ bệnh nhân của lượt/đợt bằng các route này.

## Quy ước cần nhóm xác nhận

- Đợt mới bắt đầu vào ngày khám đầu tiên; tái mắc phải sau ngày khỏi đợt trước (không cùng ngày với độ chính xác DATE).
- Các lần khám nhập theo thứ tự ngày không giảm trong đợt; không sửa/xóa nghiệp vụ đã ghi trong phạm vi tuần 2.
- Ngày lập đơn bằng ngày khám; cho ghi đơn cho lần khám đã có, kể cả sau khi lượt đóng, nhưng không đổi ngày khám. Giá lấy lúc thao tác lưu đơn; đây không phải chức năng hồi dựng bảng giá lịch sử.
- Ngày nghiệp vụ không ở tương lai. Tháng hiện tại báo cáo đến hết ngày hôm nay theo Việt Nam; tháng khác theo [đầu tháng, đầu tháng sau).
- Tiền lưu nguyên đồng theo DECIMAL(12,0) của seed; không nhận tiền thập phân. JSON xuất Decimal dạng chuỗi, ngày ISO.
- Cập nhật nội dung hỗ trợ giữ ngày bắt đầu đã ghi. Chỉnh ngày hoặc hủy nghiệp vụ sai cần quy trình riêng, không tự xóa lịch sử.

## Chạy

Làm theo SETUP.md (DB trống, seed snake_case). `python app.py`. Vào `/visits/new` để nhập lượt; `/visits/<ma_luot>` cho thao tác tiếp theo. Bốn báo cáo trong menu. Hợp đồng chi tiết ở WEEK2_INTEGRATION.md.

## Kiểm thử

`python -m pytest -v` với `RUN_MYSQL_TESTS=1`, `DB_NAME` kết thúc `_test` trên DB thử nghiệm. Bộ tuần 1 giữ nguyên; bộ tuần 2 dùng dữ liệu riêng tiền tố W2 và dọn sau test, không thay seed. Có test đồng thời, rollback giữa ghi đơn, đầu vào sai, JSON/HTML và đáp án tính tay.

Kết quả tại thời điểm chuẩn bị PR: local 36 passed, 22 skipped (không có DB local). Chưa đánh dấu MySQL tuần 2 đạt trước khi có kết quả CI. Xem Actions đúng commit và bản kết quả được cập nhật sau chạy.

## Còn cần nhóm nghiệm thu

Quyền đối chiếu truy vấn/constraints; Vương xác nhận hợp đồng và tích hợp giao diện; chạy cùng hướng dẫn trên máy nhóm; review rồi merge theo RULES.md. Đây không phải tuyên bố hoàn thành nghiệm thu toàn nhóm.
