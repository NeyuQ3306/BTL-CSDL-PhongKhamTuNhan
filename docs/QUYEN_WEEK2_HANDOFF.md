# Quyền — khởi động tuần 2, 19/10/2026

## Phạm vi
Bắt đầu từ main 20cd47ab7530b1f088213fd5ab08a27dfc87f25a đã chốt tuần 1.
Đối chiếu Project 1 trong đề BTL người dùng cung cấp và phân công tuần 2.
Không đổi schema/seed hoặc đưa code Trung vào main trong PR này.

## Tình trạng thành viên đã kiểm tra
- Trung: PR #5, head 10c808238ef2f8f4f0a1aabcfc59da19079b38f8, base main.
  Đã có transaction nghiệp vụ, bốn báo cáo HTML/JSON và UI tích hợp thử.
  CI 39250586251 báo 108 test; kết quả phải đối chiếu log trước nghiệm thu.
- Vương: chưa có nhánh/PR tuần 2 trong danh sách repo tại lần kiểm tra này.
  Không suy ra Vương chưa làm local. Cần review form, responsive, CSRF và hợp đồng của #5.

## Đối chiếu công thức với đề
- Q1: đếm DISTINCT ma_dot có ngày khám trong kỳ, không đếm số lần khám; tái mắc là đợt mới.
- Q2: bác sĩ 7 triệu + 1 triệu/đợt khỏi theo ngày khỏi; y tá 5 triệu + 200 nghìn/cặp lượt-y tá theo ngày hỗ trợ. Lương cơ bản vẫn có khi tháng rỗng.
- Q3: hồ sơ, lượt, đợt, trạng thái hiện tại, số thứ tự khám, lần khám, thuốc/giá lịch sử/liều dùng và y tá.
- Q4: cộng riêng phí khám và giá bán lịch sử nhân số lượng; không nhân phí khám do JOIN nhiều thuốc/y tá.
- Tháng hiện tại kết thúc trước ngày mai theo giờ Việt Nam; tháng quá khứ dùng trọn tháng. Tháng rỗng trả doanh thu 0.

## Đã bổ sung
tests/test_quyen_week2_reports.py dựng kết quả Q3 trực tiếp từ INSERT seed bằng Python:
40 bệnh nhân × 7 tập kết quả, so mọi thuộc tính gốc cùng trường bệnh/bác sĩ/STT/thuốc/y tá.
So sánh theo tập bản ghi, không áp đặt thứ tự hiển thị SQL tăng dần lên backend giảm dần.
Bổ sung đối chiếu backend Q1/Q2/Q4 cho 07–10/2026 và tháng rỗng 12/2025.
Không dùng output backend làm đáp án. Giữ bộ test SQL/ràng buộc hiện có.

Workflow quyen-week2.yml cài DB mới đúng thứ tự chuẩn, chạy SQL oracle, sau đó chạy cùng oracle
trên snapshot Trung pin 10c8082. QUYEN_CHECK_WEEK2=1 bắt buộc import backend báo cáo, không skip khi thiếu.
Kết quả CI thuộc merge thử của PR Quyền và candidate Trung được pin, không tự chứng minh head Trung tương lai.

## Review bước đầu phần Trung
Đã đọc reports.py, workflows.py, workflow_validation.py, services.py, hợp đồng và ca kiểm thử.
Công thức báo cáo hiện khớp SQL; patient lock + current locking reads dùng cho ghi nghiệp vụ;
tạo lượt và đơn nhiều bảng nằm trong transaction; giá lấy từ DB khi kê đơn.
Chưa phát hiện lỗi chặn có đủ bằng chứng trong phạm vi này.
Chưa approve toàn bộ PR #5: còn review UI Vương, nghiệm thu Windows tuần 2 và kết quả oracle độc lập.
Không coi CI tuần 1 thay nghiệm thu tuần 2.

## Việc tiếp theo của Quyền
- Đọc kết quả CI oracle mới và bổ sung bằng chứng.
- Hoàn thiện ca biên kỳ tính hiện tại, dữ liệu rỗng/không tồn tại và kiểm chứng Q3 dữ liệu mới sinh.
- Đối chiếu ràng buộc trực tiếp SQL với transaction backend, nhất là các cận dưới không thể bảo vệ ở COMMIT bằng CHECK/FK.
- Chốt expected_results và queries sau review; tài liệu hiện vẫn là bản tuần 1 có số đã kiểm chứng.
- PR của Quyền cần Trung/Vương review; mốc tuần 2: PR trước 20:00 26/10, chốt 20:00 27/10.

## Bổ sung ca biên 19/10, phiên tiếp theo

Đã đọc log run 39261798558: 71 SQL test và 45 backend parity test đạt ở head 686d08c (merge thử 05beaebc). Đây là kết quả trước bổ sung mới.
Bổ sung 6 ca kỳ tính bằng dữ liệu mới trong transaction: ngày hiện tại, ngày mai bị loại, năm nhuận 29/02, chuyển sang 01/03, tháng rỗng, tái mắc và thưởng đúng ngày khỏi. Thêm ca Q3 dữ liệu mới/không có lịch sử/mã không tồn tại; kiểm tra giá thuốc lịch sử khi giá danh mục đổi và nhiều y tá không nhân tiền khám.
Đáp án tính tay nằm trong database/expected_results.md; queries.sql được bổ sung hướng dẫn kỳ [đầu, cuối), cấu trúc 11 tập kết quả và hành vi Q3. Không đổi công thức/schema/seed.
Các test mới rollback và chỉ cho chạy trên DB *_test. Workflow hiện có chạy cả SQL và candidate Trung pin 10c8082; kết quả head mới phải xem Checks, không dùng số test cũ thay thế.
Phần còn lại để chốt: Trung/Vương review PR #10, review UI và nghiệm thu tuần 2 trên máy thành viên, kiểm tra sau tích hợp. Giới hạn cận dưới/SQL quản trị trong database/README.md vẫn áp dụng; bộ test không biến trigger thành bảo vệ mọi thao tác quản trị.
