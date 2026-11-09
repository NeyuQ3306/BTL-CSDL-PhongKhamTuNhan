# Bộ nộp cho giảng viên

Theo thông báo giảng viên do Quyền cung cấp ngày 02/11/2026. Hạn: hết ngày 15/11/2026, giờ Việt Nam. Mốc chốt 03/11 của nhóm là nội bộ.

| Thành phần | Điểm học phần | Vị trí/trạng thái |
|---|---:|---|
| PDF thiết kế | 8% | Hai PDF trong docs/design/ |
| SQL | 6% | database/project1_submission.sql (YC2) và database/analytics_queries.sql (R01–R07 bổ sung) |
| Link GitHub app | 6% | https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan |
| DOCX mô tả chi tiết | 3% | Theo cập nhật Trung: đã chỉnh sửa R01–R10; chờ kiểm tra file cuối |
| PPTX thuyết trình | 2% | Trung báo đã sửa: 13 slide chính + 12 phụ lục; chờ kiểm tra file cuối |
| Thuyết trình | 5% | Chưa xác nhận hoàn thành |

Tạo thư mục Google Drive mang đúng số hiệu nhóm (chưa xác nhận; không tự lấy nhóm lớp 05 làm số hiệu). Đặt PDF, SQL, DOCX, PPTX và một tệp ghi link GitHub trong thư mục. Kiểm tra quyền xem/tải rồi gửi link tại https://forms.gle/7zy3YPksCrKtbNqr5 . Chưa xác nhận đã tạo Drive hoặc gửi form.

## Truy cập GitHub

Repo giữ private. Quyền chưa có tài khoản GitHub của giảng viên. Khi có tài khoản, cấp quyền và xác nhận giảng viên mở được repo. Nếu chưa có trước hạn, trao đổi với giảng viên về cách nhận source; có thể chuẩn bị ZIP source kèm Drive theo hướng dẫn của thầy, nhưng ZIP không tự thay yêu cầu link GitHub. Không tự chuyển repo public.

## Đối chiếu nội dung báo cáo và slide

Dùng [danh mục R01–R10](FEATURES.md): R01–R07 là báo cáo phân tích; R08 sửa/xóa hồ sơ (không tính thêm), R09 tìm kiếm/phân trang, R10 kê đơn/lưu giá lịch sử. Q1–Q4 giữ tên riêng cho yêu cầu 2. Phụ lục C phải phân biệt SQL Workbench và SQL PyMySQL có `%s`; R08–R10 đối chiếu với mã ứng dụng thay vì đổi bộ analytics thành 10 báo cáo.

Theo thông báo Trung, DOCX/slide đã cập nhật danh mục, ảnh và nội dung thuyết trình. Chưa có bản file cuối trong lần đối chiếu này để kiểm tra 13 slide chính/12 phụ lục, nguồn từng ảnh, mục lục hoặc liên kết commit thực tế. Chưa xác nhận số hiệu nhóm và link Drive.

## Báo cáo mở rộng và bằng chứng laptop

PR #23 đã tích hợp bộ lọc/bảng/biểu đồ offline R01–R07 trên main tại `2c01db2`. Kèm `database/analytics_queries.sql` trong bộ nộp để giảng viên đối chiếu các chức năng bổ sung; chạy sau khi tạo/nạp CSDL bằng file YC2. Không thay bốn truy vấn bắt buộc bằng bảy báo cáo mới. Hợp đồng và ý nghĩa: [ANALYTICS_HANDOFF](ANALYTICS_HANDOFF.md).

[Bằng chứng laptop Quyền ngày06/11](evidence/quyen_laptop_acceptance_20261106/README.md):485test đạt,0lỗi/skip, MySQL8.4.11; nguồn ứng dụng2c01db2 cộng test/runner bổ sung được ghi hash riêng. Đây không thay xác nhận import file SQL gộp cuối hoặc buổi tập demo. DOCX/PPTX cập nhật theo UI thực chạy vẫn chờ kiểm tra.

## Kiểm tra bản SQL nộp

Dùng đúng file tải từ commit cuối đã chọn. Ghi SHA commit và SHA256 bằng Get-FileHash. Import một lần trên schema thử mới theo SETUP; kiểm tra 11 bảng, 9 trigger, 1.144 dòng và cả hai lượt audit đều rỗng. Đối chiếu tháng 10/2026: khám 4.680.000, thuốc 5.820.800, tổng 10.500.800 đồng. Giữ log và hash file thực chạy.

Hồ sơ cũ có hash local Workbench khác blob Git; chưa xác định nguyên nhân. Chưa có kết quả import mới trong lần cập nhật tài liệu này. Không gọi bước này đã đạt chỉ vì CI các file nguồn thành công.

## Trình bày và lịch

16/11–06/12/2026; mỗi nhóm 10 phút trình bày + 5 phút hỏi đáp. Thứ tự theo thứ tự nộp, 10 nhóm/buổi; lịch cụ thể chờ thông báo. Ngày 17/11 thưởng 4%, ngày 24/11 thưởng 2%; đặt câu hỏi cho nhóm khác thưởng 2% theo thông báo. Đi muộn/bỏ lỡ không thuyết trình bù. Nộp sau 15/11 bị trừ 50% điểm BTL; sau khi hết lịch thuyết trình không có điểm BTL.

Trước demo: kiểm tra health/db, tiếp nhận, đơn nhiều thuốc, lịch sử và bốn báo cáo trên laptop Quyền. Nếu HTTP503/MySQL2003 tái diễn, giữ log, thời điểm, route và cấu hình instance để điều tra; không gửi lại thao tác ghi khi chưa xác định kết quả trước. Ghi phân vai và thời lượng tập thật. Tag/release chờ các điều kiện cuối và review nhóm.
