# Bộ nộp cho giảng viên

Theo thông báo giảng viên do Quyền cung cấp ngày 02/11/2026. Hạn: hết ngày 15/11/2026, giờ Việt Nam. Mốc chốt 03/11 của nhóm là nội bộ.

| Thành phần | Điểm học phần | Vị trí/trạng thái |
|---|---:|---|
| PDF thiết kế | 8% | Hai PDF trong docs/design/ |
| SQL | 6% | database/project1_submission.sql (YC2) và database/analytics_queries.sql (R01–R07 bổ sung) |
| Link GitHub app | 6% | https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan |
| DOCX mô tả chi tiết | 3% | Bản bàn giao nằm ngoài repo; DOCX bổ sung phân quyền đã được tạo riêng, chưa tích hợp ảnh mới trong lần cập nhật này |
| PPTX thuyết trình | 2% | Bản bàn giao nằm ngoài repo; chưa đồng bộ PPTX vào repo trong lần cập nhật này |
| Thuyết trình | 5% | Chưa xác nhận hoàn thành |

Thư mục bộ nộp của nhóm: **Nhóm 02 - Phòng khám bệnh tư**. Bộ bàn giao gồm PDF, SQL, DOCX, PPTX và link GitHub. Link form theo thông báo: https://forms.gle/7zy3YPksCrKtbNqr5 . Trạng thái gửi form/quyền xem và phiên bản file trên Drive cần đối chiếu trực tiếp; lần cập nhật repo này không xác nhận lại các thao tác đó.

## Truy cập GitHub

Repo hiện **public** tại https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan để giảng viên xem source, không cần mời tài khoản GitHub riêng. Website chạy local/tunnel vẫn yêu cầu tài khoản được tạo trong database của máy phục vụ; công khai source không tạo tài khoản website.

## Bản ứng dụng hiện tại

Đã có đăng nhập, quản lý tài khoản và năm vai trò. Bộ SQL/thiết kế ban đầu có 11 bảng nghiệp vụ; CLI `init-auth` bổ sung bảng kỹ thuật `app_user`, tổng 12 bảng. Máy đã có bảng tài khoản bản cũ dùng `upgrade-auth`. Không nhập lại SQL/seed lên DB đang dùng. Xem [SETUP](SETUP.md), [AUTHENTICATION](AUTHENTICATION.md) và [demo hai máy](DEMO_TWO_MACHINES.md).

R01–R07 kết thúc giao dịch đọc xác thực trước khi mở snapshot báo cáo MySQL. Bộ kiểm thử có ca đăng nhập rồi mở từng báo cáo và API tổng hợp. Công cụ `tools/capture_report_images.py` cùng workflow **Report UI images** tạo ảnh từ app xác thực trên MySQL thử; ảnh nằm trong artifact của workflow, không đồng nghĩa đã đưa ảnh vào Word.

## Đối chiếu nội dung báo cáo và slide

Dùng [danh mục R01–R10](FEATURES.md): R01–R07 là báo cáo phân tích; R08 sửa/xóa hồ sơ (không tính thêm), R09 tìm kiếm/phân trang, R10 kê đơn/lưu giá lịch sử. Q1–Q4 giữ tên riêng cho yêu cầu 2. Phụ lục C phải phân biệt SQL Workbench và SQL PyMySQL có `%s`; R08–R10 đối chiếu với mã ứng dụng thay vì đổi bộ analytics thành 10 báo cáo.

DOCX/PPTX chưa được lưu trong repo ở lần cập nhật này. Khi bổ sung, đối chiếu ảnh với giao diện đã đăng nhập, quyền từng vai trò, bảng `app_user`, mục lục và link mã nguồn. Không lấy artifact ảnh làm bằng chứng Word/slide đã được cập nhật.

## Báo cáo mở rộng và bằng chứng laptop

PR #23 đã tích hợp bộ lọc/bảng/biểu đồ offline R01–R07 trên main tại `2c01db2`. Kèm `database/analytics_queries.sql` trong bộ nộp để giảng viên đối chiếu các chức năng bổ sung; chạy sau khi tạo/nạp CSDL bằng file YC2. Không thay bốn truy vấn bắt buộc bằng bảy báo cáo mới. Hợp đồng và ý nghĩa: [ANALYTICS_HANDOFF](ANALYTICS_HANDOFF.md).

[Bằng chứng laptop Quyền ngày06/11](evidence/quyen_laptop_acceptance_20261106/README.md):485test đạt,0lỗi/skip, MySQL8.4.11; nguồn ứng dụng2c01db2 cộng test/runner bổ sung được ghi hash riêng. Đây không thay xác nhận import file SQL gộp cuối hoặc buổi tập demo. DOCX/PPTX cập nhật theo UI thực chạy vẫn chờ kiểm tra.

## Kiểm tra bản SQL nộp

Dùng đúng file tải từ commit cuối đã chọn. Ghi SHA commit và SHA256 bằng Get-FileHash. Import một lần trên schema thử mới theo SETUP; kiểm tra 11 bảng, 9 trigger, 1.144 dòng và cả hai lượt audit đều rỗng. Đối chiếu tháng 10/2026: khám 4.680.000, thuốc 5.820.800, tổng 10.500.800 đồng. Giữ log và hash file thực chạy.

Hồ sơ cũ có hash local Workbench khác blob Git; chưa xác định nguyên nhân. Chưa có kết quả import mới trong lần cập nhật tài liệu này. Không gọi bước này đã đạt chỉ vì CI các file nguồn thành công.

## Trình bày và lịch

16/11–06/12/2026; mỗi nhóm 10 phút trình bày + 5 phút hỏi đáp. Thứ tự theo thứ tự nộp, 10 nhóm/buổi; lịch cụ thể chờ thông báo. Ngày 17/11 thưởng 4%, ngày 24/11 thưởng 2%; đặt câu hỏi cho nhóm khác thưởng 2% theo thông báo. Đi muộn/bỏ lỡ không thuyết trình bù. Nộp sau 15/11 bị trừ 50% điểm BTL; sau khi hết lịch thuyết trình không có điểm BTL.

Trước demo: Trung kiểm tra đăng nhập, health/db, tiếp nhận, đơn nhiều thuốc, lịch sử và các báo cáo trên máy trình chiếu; Vương chạy app/DB riêng cho QR của lớp theo DEMO_TWO_MACHINES. Nếu HTTP503/MySQL2003 tái diễn, giữ log, thời điểm, route và cấu hình instance để điều tra; không gửi lại thao tác ghi khi chưa xác định kết quả trước. Ghi phân vai và thời lượng tập thật. Tag/release chờ các điều kiện cuối và review nhóm.
