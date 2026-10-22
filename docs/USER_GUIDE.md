# Hướng dẫn sử dụng bản tích hợp

Hướng dẫn hiện hành ngày 21/10/2026. Cài/chạy và nhận diện source theo [SETUP.md](SETUP.md). Main đã xác minh: `f4869299c25fdfd0b711597e30b60ab277120f44`; ứng viên tuần 3 trên nhánh `vuong/week-3` có sửa UI và được đối chiếu với bằng chứng trong [bàn giao cuối](VUONG_WEEK3_HANDOFF.md). Không dùng hướng dẫn chọn nhánh tuần 2 để bắt đầu.

Chuẩn bị trình bày: [kịch bản demo tuần 3](VUONG_WEEK3_DEMO.md), gồm dữ liệu, expected, phân vai và lệnh tạo phiên demo mới. Diễn tập kỹ thuật đã có bằng chứng; Vương xác nhận hoàn thành bước 6 ngày 21/10/2026, chưa cung cấp chi tiết biên bản tập chung.

## 1. Kết nối và hồ sơ

Mở `/health` và `/health/db`, cả hai phải HTTP 200/status ok; sau đó vào **Bệnh nhân**, **Bác sĩ**, **Y tá** trên menu. Mỗi nhóm có danh sách/tìm kiếm, thêm, chi tiết, sửa và xóa. Dùng mã giả chưa tồn tại (tối đa 12 ký tự: chữ không dấu, số, `_`, `-`; tránh `new`), CMT/CCCD không trùng và ngày sinh hợp lệ.

Ví dụ CRUD bệnh nhân trên DB thử: mã `W3GUIDEBN`, tên “Bệnh nhân thử hướng dẫn”, CMT `999000005001`, ngày sinh `2000-01-01`, địa chỉ “Hà Nội”, điện thoại `0900000001`. Nếu mã/CMT đã có thì chọn bộ mới. Thêm → mở chi tiết → sửa địa chỉ → tải lại xác nhận đã lưu. Thử mã trùng/ngày sinh tương lai phải bị từ chối; kiểm tra giữ dữ liệu form. Bác sĩ/y tá: điền các trường bắt buộc trên form, thâm niên là số nguyên trong giới hạn hiển thị.

Chỉ xóa hồ sơ giả không có lịch sử do bạn vừa tạo. Hồ sơ bệnh nhân/nhân viên đã có lịch sử sẽ bị chặn xóa; không sửa SQL để vượt chặn. Seed là dữ liệu giả dùng chung cho báo cáo, không xóa để dọn demo.

## 2. Tiếp nhận, khám và tái khám

1. Mở **Tiếp nhận / khám** (`/visits/new`). Nhập mã lượt mới, chọn bệnh nhân, ngày vào và chế độ đợt mới/tái khám.
2. Đợt mới: mã đợt mới, bệnh và bác sĩ. Tái khám: chọn đợt **đang điều trị của đúng bệnh nhân**; bệnh/bác sĩ giữ nguyên, STT lần khám do hệ thống cấp liên tiếp.
3. Nhập mã lần khám mới, ngày khám, phí nguyên đồng chưa gồm thuốc, kết luận và y tá hỗ trợ rồi **Lưu**. Kiểm tra trang chi tiết lượt sau lưu.
4. Một lượt có thể khám nhiều bệnh: chọn **Khám thêm bệnh** trong chi tiết lượt; đợt/lần khám phải thuộc đúng bệnh nhân. Không tạo đợt đang điều trị thứ hai cho cùng bệnh nhân/bệnh.

Ngày khám phải nằm trong thời gian lượt và đợt. Dùng mã chưa tồn tại, không lấy mã seed làm mã ghi mới. Nếu lưu lỗi, đọc thông báo đầu form, sửa nguyên nhân rồi gửi lại; không thay mã chỉ để né lỗi nghiệp vụ.

## 3. Hỗ trợ y tá, đơn thuốc và kết thúc

- **Ghi hỗ trợ y tá**: thêm y tá/công việc; liên kết cập nhật của y tá sửa công việc và giữ ngày hỗ trợ đã ghi. Nhiều công việc trên cùng cặp lượt–y tá không nhân đôi dòng thưởng.
- **Kê đơn** từ lần khám: mã đơn mới, ngày đơn bằng ngày khám, chọn thuốc/số lượng/liều dùng. **Thêm dòng thuốc**/**Xóa dòng** để tạo đơn nhiều thuốc; mỗi thuốc một dòng. Giá/tổng do server tính. Xem đơn sau lưu để kiểm tra số lượng, giá bán lịch sử và tổng. Lần khám không có đơn vẫn hợp lệ.
- **Kết thúc lượt**: nhập ngày ra hợp lệ, khóa thêm lần khám/sửa hỗ trợ cho lượt đó; thao tác này không tự xác nhận khỏi đợt.
- **Xác nhận khỏi** ở đợt: kết thúc đợt, không tự đóng các lượt. Tái mắc sau ngày khỏi tạo đợt mới. Không thử sửa/xóa lịch sử bằng SQL để diễn tập lại.

Khi lỗi, kiểm tra thông báo tiếng Việt và dữ liệu còn trên form. Với ô số, main có thể hiển thị thông báo native theo ngôn ngữ browser; ứng viên tuần 3 bổ sung thông báo tiếng Việt khi JavaScript bật. Không nhầm trạng thái bản sửa chưa merge với main. Không tắt validation để tiếp tục.

## 4. Bốn báo cáo

Vào **Báo cáo**; Q1/Q2/Q4 chọn tháng/năm rồi **Xem báo cáo**. Q3 chọn/nhập mã bệnh nhân rồi **Xem lịch sử**; dùng liên kết **Tìm bệnh nhân** nếu chưa biết mã. Q3 trả toàn bộ lịch sử, không cắt theo tháng.

| Báo cáo | Cần đọc/đối chiếu |
|---|---|
| Q1 — Thống kê bệnh | Đếm đợt có khám trong kỳ; tái khám nhiều lần trong cùng đợt không cộng trùng; đợt qua tháng có thể được tính ở mỗi tháng có khám |
| Q2 — Lương bác sĩ/y tá | Lương cơ bản + thưởng; bác sĩ theo ngày khỏi, y tá theo ngày hỗ trợ; kỳ trống vẫn có lương cơ bản |
| Q3 — Lịch sử và tình trạng | Hồ sơ, lượt, đợt/tình trạng, khám, đơn/thuốc và hỗ trợ; mã không tồn tại báo lỗi |
| Q4 — Doanh thu | Tiền khám + tiền thuốc theo giá bán đã lưu trong chi tiết đơn, không dùng giá danh mục hiện tại |

Trên seed nguyên trạng, chọn **10/2026**: tổng Q1 **24 đợt**; Q2 bác sĩ **78.000.000 đ**, y tá **65.600.000 đ**; Q4 khám **4.680.000 đ**, thuốc **5.820.800 đ**, tổng **10.500.800 đ**. Q3 thử `BN001` và đối chiếu các tập trong [đáp án SQL](../database/expected_results.md). Tháng **12/2025**: Q1/Q4 bằng 0, Q2 vẫn lương cơ bản bác sĩ **70.000.000 đ**, y tá **60.000.000 đ**.

Các số trên chỉ áp dụng seed chưa thêm/sửa dữ liệu. Nhân viên giả mới vẫn nhận lương cơ bản nên tổng Q2 sẽ thay đổi dù không khám. Dùng DB thử mới để đối chiếu seed nếu DB demo đã có lịch sử bổ sung; không nhập đè.

## 5. Thao tác và xử lý lỗi

Trên màn hình nhỏ, bảng rộng cuộn ngang trong vùng riêng; Tab tới vùng bảng rồi dùng phím mũi tên. Tab/Enter thao tác nút thêm/xóa dòng thuốc; sau lỗi sửa dữ liệu và gửi lại. Dùng menu/đường quay lại/hủy để tiếp tục đúng luồng.

Nếu `/health/db` 503, lỗi secret, CSRF, cổng bận hoặc import không đủ trigger: xem [bảng xử lý lỗi](SETUP.md#6-lỗi-thường-gặp). Với runner private, phải kiểm tra cleanup theo W3-RUN-01, không dừng MySQL hệ thống.

[Bằng chứng đúng phiên bản và giới hạn](VUONG_WEEK3_STEP5_VERIFICATION.md) · [T01–T15 và quyết định không chạy T16](VUONG_WEEK3_ACCEPTANCE.md). T16 chưa chạy, không tính PASS và không thuộc cổng nghiệm thu bắt buộc.
