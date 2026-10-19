# Bài tập lớn CSDL — Quản lý phòng khám tư nhân

Nhóm: **Minh Quyền · Trung · Vương**. Thời gian: **13/10–03/11/2026**, múi giờ Việt Nam.

## Chạy thử tích hợp tuần 1

Dùng [hướng dẫn Windows thống nhất](docs/SETUP.md). Backend #4 và UI #7 đã merge; SQL #6 còn chờ xác nhận review. Khi #6 chưa merge, dùng snapshot theo SETUP; không coi main đã có trigger chuẩn. Import schema → seed → audit → constraints → audit → queries; không chạy chồng adapter cũ.

## Trạng thái backend tuần 1

- Đã chuyển backend sang lược đồ 11 bảng: CRUD bệnh nhân/bác sĩ/y tá, validation, kết nối theo request, transaction và cấu hình `.env`.
- Có màn hình tra cứu lượt/đợt/lần khám làm nền tuần 2; chưa triển khai ghi nghiệp vụ và bốn báo cáo hoàn chỉnh.
- `database/week1/clinic_seed.sql` là adapter định danh từ dữ liệu giả lập Vũ Đại Vương bàn giao; cần Quyền review. `hospital_db.sql` vẫn là schema tham khảo, không nhập cho app mới.
- Xem [bàn giao tuần 1](docs/TRUNG_WEEK1_HANDOFF.md), [cách chạy](docs/SETUP.md), và [hợp đồng route/form](docs/INTEGRATION.md).
- Chưa coi nghiệm thu hoàn tất trước khi nhóm review và merge PR theo RULES.md.

## Bắt đầu từ đây

Phần UI tuần 1 của Vương: [bàn giao](docs/VUONG_WEEK1_HANDOFF.md), [hướng dẫn sử dụng](docs/VUONG_WEEK1_USER_GUIDE.md), [checklist và ảnh kiểm thử](docs/VUONG_WEEK1_CHECKLIST.md). Bốn báo cáo hiện gồm ba khung thống kê chờ SQL và một luồng lịch sử dùng dữ liệu đã lưu; chưa nghiệm thu nghiệp vụ tuần 2.

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
- `app.py`: entry point; `clinic_app/`: backend module và UI kiểm thử tuần 1.
- `templates/`, `static/`: UI upstream giữ nguyên để tránh xung đột phần Vương.
- `tests/`: unit test và integration test MySQL cho tuần 1.
- `.github/`: mẫu issue/PR, CODEOWNERS và CI Python 3.11 + MySQL 8.4.

## Làm việc nhóm

Nhánh đã chuẩn bị: `quyen/week-1`, `trung/week-1`, `vuong/week-1`. Mở PR về `main`. Tuần sau tạo nhánh mới từ `origin/main`, không tái sử dụng nhánh đã squash merge. Quyền điều phối merge; PR của Quyền phải có Trung hoặc Vương review.

CODEOWNERS không thay thế bảo vệ nhánh; xem trạng thái cấu hình trong RULES.md.

## Nguồn tham khảo

Dựa trên [scmeyer41/hospital-database-management-system](https://github.com/scmeyer41/hospital-database-management-system), commit `711d7b1bdff824901a75e086525d0a9f5ca14701`. Giữ lịch sử upstream và [README gốc](docs/UPSTREAM_README.md). Xem [ghi nhận nguồn](docs/ATTRIBUTION.md). Nhóm tự chịu trách nhiệm giải thích và kiểm thử phần chuyển đổi; không coi tính năng của upstream là phần nhóm đã hoàn thành.
