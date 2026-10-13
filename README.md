# Bài tập lớn CSDL — Quản lý phòng khám tư nhân

Nhóm: **Minh Quyền · Trung · Vương**. Thời gian: **13/10–03/11/2026**, múi giờ Việt Nam.

## Trạng thái ban đầu

- Yêu cầu 1: đã chốt thiết kế ER và lược đồ 11 bảng, kèm ràng buộc. Xem [tài liệu thiết kế](docs/design/).
- Yêu cầu 2: **chưa triển khai** SQL theo thiết kế nhóm; là đầu việc tuần 1 và tuần 2.
- Yêu cầu 3: đã nhập source tham khảo Flask + MySQL; **chưa chuyển đổi nghiệp vụ và chưa nghiệm thu ứng dụng**.
- `app.py`, `hospital_db.sql`, `templates/`, `static/` hiện là source bệnh viện gốc. `hospital_db.sql` KHÔNG phải lược đồ 11 bảng và KHÔNG phải file SQL để nộp.

## Bắt đầu từ đây

1. Đọc [phân công 3 tuần](docs/PHAN_CONG_3_TUAN.md) hoặc [bản PDF](docs/Phan_cong_Project1_3_tuan.pdf).
2. Đọc [RULES.md](RULES.md) trước khi push; mọi thay đổi sau khởi tạo đi qua PR.
3. Xem [cài đặt môi trường](docs/SETUP.md), [hợp đồng tích hợp](docs/INTEGRATION.md) và [kiểm thử nghiệm thu](docs/ACCEPTANCE.md).

## Mốc chốt

| Tuần | Khoảng làm việc | Chốt thứ Ba lúc 20:00 | Sản phẩm |
|---|---|---|---|
| 1 | 13/10 đến trước mốc 20/10 | 20/10/2026 | 11 bảng, dữ liệu mẫu, khung backend và giao diện |
| 2 | Sau mốc 20/10 đến 27/10 | 27/10/2026 | Bốn báo cáo bắt buộc chạy xuyên suốt từ UI tới MySQL |
| 3 | Sau mốc 27/10 đến 03/11 | 03/11/2026 | Sửa lỗi, kiểm thử máy sạch, demo và bộ nộp cuối |

Đẩy PR trước **20:00 thứ Hai** để có 24 giờ review. 20:00 là giờ làm việc nhóm đề xuất, không phải hạn do giảng viên công bố.

## Công nghệ và phạm vi

Python 3.11; Flask 3; PyMySQL; MySQL 8.4; HTML/CSS/Jinja. Giữ MySQL làm nguồn dữ liệu duy nhất; không chuyển sang SQLite/MongoDB. Dữ liệu demo hoàn toàn giả lập.

Ứng dụng phải cung cấp: thống kê bệnh theo đợt/tháng; lương bác sĩ và y tá; lịch sử và tình trạng bệnh nhân; doanh thu khám và thuốc. CRUD bệnh nhân, bác sĩ/y tá, lượt khám, thuốc và đơn thuốc phục vụ luồng demo. Phòng nội trú, phẫu thuật và quản lý giường của upstream nằm ngoài phạm vi.

## Cấu trúc

- `docs/design/`: hai PDF thiết kế đã chốt.
- `docs/`: phân công, setup, hợp đồng tích hợp, test và nguồn tham khảo.
- `database/`: nơi nhóm sẽ viết schema, seed, query, kiểm tra ràng buộc và script nộp.
- `app.py`, `templates/`, `static/`: nền source cần chuyển đổi.
- `tests/`: bộ kiểm thử sẽ triển khai tuần 1–3.
- `.github/`: mẫu issue/PR, CODEOWNERS và CI kiểm tra cú pháp cơ bản.

## Làm việc nhóm

Nhánh đã chuẩn bị: `quyen/week-1`, `trung/week-1`, `vuong/week-1`. Mở PR về `main`. Tuần sau tạo nhánh mới từ `origin/main`, không tái sử dụng nhánh đã squash merge. Quyền điều phối merge; PR của Quyền phải có Trung hoặc Vương review.

Tài khoản GitHub của Trung và Vương chưa được cung cấp nên **chưa mời cộng tác viên**. CODEOWNERS không thay thế bảo vệ nhánh; xem trạng thái cấu hình trong RULES.md.

## Nguồn tham khảo

Dựa trên [scmeyer41/hospital-database-management-system](https://github.com/scmeyer41/hospital-database-management-system), commit `711d7b1bdff824901a75e086525d0a9f5ca14701`. Giữ lịch sử upstream và [README gốc](docs/UPSTREAM_README.md). Xem [ghi nhận nguồn](docs/ATTRIBUTION.md). Nhóm tự chịu trách nhiệm giải thích và kiểm thử phần chuyển đổi; không coi tính năng của upstream là phần nhóm đã hoàn thành.
