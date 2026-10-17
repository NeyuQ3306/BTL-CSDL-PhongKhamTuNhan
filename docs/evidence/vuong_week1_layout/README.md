# Kiểm tra layout và điều hướng tuần 1 của Vương

Ngày kiểm tra: 17/10/2026. Nhánh: `vuong/week-1`, nền Trung `c442384` cùng thay đổi UI chưa commit.

Môi trường: Windows, Python 3.14.6, MySQL 8.0.46, database demo `clinic_vuong_week1`. Đây là kiểm tra cục bộ, không thay thế CI Python 3.11/MySQL 8.4.

## Kết quả

- Trình duyệt Chromium trong ứng dụng: kiểm tra trực quan ở 1440px, 390px và 320px. Đo bố cục danh sách bệnh nhân/bác sĩ/y tá, form bệnh nhân, trang báo cáo và trang chờ lịch sử ở 320px, 768px, 1440px: không tràn ngang toàn trang. Bảng cuộn ngang trong vùng riêng; menu chọn đúng mục; form và thẻ báo cáo về một cột trên màn hình hẹp.
- Kiểm tra 11 trang GET với Flask test client kết nối MySQL thật: danh sách ba loại hồ sơ, lượt/đợt khám, tổng hợp báo cáo, bốn trang chờ báo cáo và lịch sử BN001 đều trả 200, có đúng một mục menu đang chọn, không có đường dẫn nội trú/phẫu thuật.
- Ba form giữ hidden CSRF. POST thiếu token trả 400; POST có token hợp lệ nhưng thiếu dữ liệu trả 422 và hiển thị lỗi trường/thông báo. Không ghi hồ sơ trong đợt kiểm tra này.
- Trang báo cáo không tồn tại trả 404. Các trang chờ không truy vấn hoặc hiển thị số liệu thống kê giả.
- Parse Python/Jinja và `git diff --check` đạt.
- Audit sau kiểm tra: 11 bảng, 1.144 dòng, đúng số lượng mẫu, không có phát hiện. Hash `.env` không đổi.

## Ảnh minh chứng

- `desktop.png`: danh sách bệnh nhân ở 1440px.
- `patients-mobile.png`: bảng bệnh nhân với vùng cuộn riêng ở 390px.
- `form-mobile.png`: form bệnh nhân một cột ở 390px.
- `reports-desktop.png`: tổng hợp báo cáo ở 1440px.
- `reports-mobile.png`, `reports-320.png`: báo cáo ở 390px và 320px.

## Phạm vi còn lại

Các route báo cáo hiện chỉ phục vụ điều hướng và hiển thị trạng thái chờ. Bộ lọc, bảng kết quả và SQL báo cáo chưa triển khai. Chưa thực hiện kiểm thử toàn bộ CRUD hoặc nghiệm thu UI tuần 1 trong bước layout này.
