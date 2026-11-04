# Bộ nộp cho giảng viên

Theo thông báo giảng viên do Quyền cung cấp ngày 02/11/2026. Hạn: hết ngày 15/11/2026, giờ Việt Nam. Mốc chốt 03/11 của nhóm là nội bộ.

| Thành phần | Điểm học phần | Vị trí/trạng thái |
|---|---:|---|
| PDF thiết kế | 8% | Hai PDF trong docs/design/ |
| SQL | 6% | database/project1_submission.sql |
| Link GitHub app | 6% | https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan |
| DOCX mô tả chi tiết | 3% | Vương chỉnh sửa; chờ kiểm tra bản cuối |
| PPTX thuyết trình | 2% | Trung chỉnh sửa; chờ kiểm tra bản cuối |
| Thuyết trình | 5% | Chưa xác nhận hoàn thành |

Tạo thư mục Google Drive mang đúng số hiệu nhóm (chưa xác nhận; không tự lấy nhóm lớp 05 làm số hiệu). Đặt PDF, SQL, DOCX, PPTX và một tệp ghi link GitHub trong thư mục. Kiểm tra quyền xem/tải rồi gửi link tại https://forms.gle/7zy3YPksCrKtbNqr5 . Chưa xác nhận đã tạo Drive hoặc gửi form.

## Truy cập GitHub

Repo giữ private. Quyền chưa có tài khoản GitHub của giảng viên. Khi có tài khoản, cấp quyền và xác nhận giảng viên mở được repo. Nếu chưa có trước hạn, trao đổi với giảng viên về cách nhận source; có thể chuẩn bị ZIP source kèm Drive theo hướng dẫn của thầy, nhưng ZIP không tự thay yêu cầu link GitHub. Không tự chuyển repo public.

## Kiểm tra bản SQL nộp

Dùng đúng file tải từ commit cuối đã chọn. Ghi SHA commit và SHA256 bằng Get-FileHash. Import một lần trên schema thử mới theo SETUP; kiểm tra 11 bảng, 9 trigger, 1.144 dòng và cả hai lượt audit đều rỗng. Đối chiếu tháng 10/2026: khám 4.680.000, thuốc 5.820.800, tổng 10.500.800 đồng. Giữ log và hash file thực chạy.

Hồ sơ cũ có hash local Workbench khác blob Git; chưa xác định nguyên nhân. Chưa có kết quả import mới trong lần cập nhật tài liệu này. Không gọi bước này đã đạt chỉ vì CI các file nguồn thành công.

## Trình bày và lịch

16/11–06/12/2026; mỗi nhóm 10 phút trình bày + 5 phút hỏi đáp. Thứ tự theo thứ tự nộp, 10 nhóm/buổi; lịch cụ thể chờ thông báo. Ngày 17/11 thưởng 4%, ngày 24/11 thưởng 2%; đặt câu hỏi cho nhóm khác thưởng 2% theo thông báo. Đi muộn/bỏ lỡ không thuyết trình bù. Nộp sau 15/11 bị trừ 50% điểm BTL; sau khi hết lịch thuyết trình không có điểm BTL.

Trước demo: kiểm tra health/db, tiếp nhận, đơn nhiều thuốc, lịch sử và bốn báo cáo trên laptop Quyền. Nếu HTTP503/MySQL2003 tái diễn, giữ log, thời điểm, route và cấu hình instance để điều tra; không gửi lại thao tác ghi khi chưa xác định kết quả trước. Ghi phân vai và thời lượng tập thật. Tag/release chờ các điều kiện cuối và review nhóm.
