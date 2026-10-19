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

Đáp án chi tiết: [WEEK2_EXPECTED_RESULTS.md](WEEK2_EXPECTED_RESULTS.md). CI còn chạy Chromium qua form thật và lưu ảnh vào artifact 30 ngày. Muốn chạy browser local: `python -m pip install playwright`, `python -m playwright install chromium`, đặt thêm `RUN_BROWSER_TESTS=1` trước pytest.

Kết quả xác minh: **59/59 test đạt**, không bỏ qua, trên Python 3.11 / MySQL 8.4.11 / Chromium ở commit `26bc627`. [CI thành công](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/actions/runs/39009890037). Sau test, seed giữ nguyên 11 bảng / 1.144 dòng, chín truy vấn audit không có phát hiện. Local chỉ chạy 36 ca không cần DB, 23 ca bỏ qua.

[Bằng chứng chạy](evidence/trung_week2_results.txt). Ảnh thật đã kiểm tra và lưu lâu dài trong repo:

- [Lượt khám](evidence/week2/01-visit.png)
- [Đơn thuốc](evidence/week2/02-prescription.png)
- [Doanh thu](evidence/week2/03-revenue.png)
- [Lịch sử](evidence/week2/04-history.png)
- [Validation ngày](evidence/week2/05-validation.png)

Bản commit tài liệu sau kết quả này không thay code đã kiểm thử.

## Còn cần nhóm nghiệm thu

Quyền đối chiếu truy vấn/constraints; Vương xác nhận hợp đồng và tích hợp giao diện; chạy cùng hướng dẫn trên máy nhóm; review rồi merge theo RULES.md. Đây không phải tuyên bố hoàn thành nghiệm thu toàn nhóm.

## Đồng bộ bản sửa tuần 1 tối 17/10

Bản code `6b0786f` đồng bộ sửa mã chuẩn edit/delete, sáu ca hồi quy và ba luồng CRUD Chromium tuần 1. **68/68 test đạt**, [CI](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/actions/runs/39035295523). Mốc 59 test phía trên là trước bản bổ sung này; không có test bị bỏ.

## Cập nhật tích hợp 19/10/2026

Nền main 20cd47a (đã merge #9); giữ SQL/seed/9 trigger và UI tuần 1. Route báo cáo dùng duy nhất clinic.reports để gọi bộ báo cáo tuần 2; JSON và HTML cùng dữ liệu. Bổ sung điều hướng tiếp nhận, chi tiết lượt và xác nhận khỏi. Lịch sử giữ layout tuần 1 và thêm thuốc/y tá.

CI chuyển sang import canonical có audit trước/sau constraints; chạy toàn bộ test SQL/backend/browser và audit sau dọn. Log 59/68 test phía trên là lịch sử, không phải kết quả bản mới.

Kiểm tra local Linux/Python 3.12: 49 passed, 32 skipped khi bỏ riêng module SQL bắt buộc MySQL (test_quyen_database.py); compile đạt. Môi trường này chưa có MySQL/Chromium, phải đọc CI mới để xác nhận tích hợp. Lần gọi toàn bộ suite local ban đầu có 25 lỗi cấu hình DB_PASSWORD ở module SQL bắt buộc; không coi skipped hoặc thiếu DB là đạt.

Đính chính review sơ bộ: visit_lock đã trả bản ghi với mã bệnh nhân chuẩn, nên chưa đủ căn cứ nói URL viết thường gây sai so sánh chủ hồ sơ. Bản mới chuẩn hóa thêm mã đợt lấy từ DB; cần ca hồi quy tích hợp kiểm tra URL/mã khác hoa thường.

Cần Quyền review công thức báo cáo, khóa/transaction với trigger và oracle độc lập. Cần Vương xác nhận hợp đồng field/CSRF/JSON, hoàn thiện trình bày/responsive form tuần 2 và chạy browser nghiệm thu. Trung chạy nghiệm thu Windows tuần 2 sau CI. Không tự approve hoặc merge #5.
