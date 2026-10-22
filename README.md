# Bài tập lớn CSDL — Quản lý phòng khám tư nhân

**Quyết định phạm vi ngày 21/10/2026 của Quyền:** demo và nghiệm thu bản cuối trên laptop Quyền. Bỏ tiêu chí T16/cài trên máy thứ hai khỏi điều kiện hoàn thành và release; không ghi T16 là PASS. Vẫn kiểm tra hướng dẫn chạy, SQL, T01–T15 và các lỗi ảnh hưởng demo. Quyết định này thay các yêu cầu máy thứ hai trong tài liệu cũ; bằng chứng lịch sử giữ nguyên.

Nhóm: **Minh Quyền · Trung · Vương**. Thời gian: **13/10–03/11/2026**, múi giờ Việt Nam.

## Bắt đầu với bản tích hợp tuần 3

Bản tích hợp gồm #12/#13/#14/#15, tài liệu #18 và phần dọn upstream #16. Xem [trạng thái hiện hành và bộ nộp](docs/WEEK3_FINAL_STATUS.md), [cài/chạy Windows](docs/SETUP.md), [sử dụng](docs/USER_GUIDE.md) và [kịch bản demo](docs/VUONG_WEEK3_DEMO.md). Trạng thái merge/CI mới nhất xem [PR #17](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/pull/17); không dùng các phần lịch sử bên dưới làm hướng dẫn phiên bản hiện tại.

Quyền đã kiểm thử source `dd1f41e` trên laptop Windows: **236/236 test đạt**, audit sạch 11 bảng/9 trigger/1.144 dòng và cleanup thành công. Các thay đổi tiếp theo chỉ đồng bộ tài liệu và gỡ 7 file upstream không dùng; CI của bản cuối được xác nhận riêng trước merge. Nguồn và giới hạn bằng chứng được giữ trong hồ sơ.

**W3-RUN-01:** chấp nhận đóng lỗi cleanup theo bằng chứng sửa/source, review và retest thành công/lỗi Windows. **W3-DB-01 (503/MySQL 2003):** vẫn theo dõi, chưa xác định nguyên nhân hoặc nhận đã sửa. **T16:** không thực hiện, không tính PASS. Chưa xác nhận nhóm đã tập demo đủ thời lượng hoặc đã phát hành tag/release.

## Bản bàn giao tuần 2 của Vương (lịch sử)

Bản trên nhánh `vuong/week-2` có UI tiếp nhận/khám/tái khám, hỗ trợ y tá, đơn thuốc, đóng lượt/xác nhận khỏi và bốn báo cáo MySQL thật. Phụ thuộc backend [#5](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/pull/5) tại `10c8082` và oracle [#10](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/pull/10) tại `1bf9f8b`; hai PR chưa merge lúc đóng gói.

Bắt đầu từ [bàn giao](docs/VUONG_WEEK2_HANDOFF.md), [hướng dẫn sử dụng ngắn](docs/VUONG_WEEK2_USER_GUIDE.md), [nghiệm thu T01–T15](docs/VUONG_WEEK2_ACCEPTANCE.md) và [hợp đồng tuần 2](docs/WEEK2_INTEGRATION.md). Local 168 test đạt/0 skipped trên Python 3.12/MySQL 8.0/Chromium; CI của commit sẽ được ghi riêng, không thay nghiệm thu bản cuối trên laptop Quyền.

## Nền tích hợp tuần 1 (lịch sử)

[Hướng dẫn Windows thống nhất](docs/SETUP.md) hiện đã cập nhật cho bản tích hợp. Mốc lịch sử tuần 1: #4/#6/#7/#8/#9 đã merge vào main `20cd47a`. Thứ tự import hiện hành vẫn là schema → seed → audit → constraints → audit → queries; không chạy chồng adapter cũ.

## Trạng thái nền tuần 1 (lịch sử)

- Đã chuyển backend sang lược đồ 11 bảng: CRUD bệnh nhân/bác sĩ/y tá, validation, kết nối theo request, transaction và cấu hình `.env`.
- Có màn hình tra cứu lượt/đợt/lần khám làm nền tuần 2; chưa triển khai ghi nghiệp vụ và bốn báo cáo hoàn chỉnh.
- `database/week1/clinic_seed.sql` là adapter định danh từ dữ liệu giả lập Vũ Đại Vương bàn giao; cần Quyền review. Schema upstream `hospital_db.sql` được lưu trong lịch sử Git, không nhập cho app mới.
- Xem [bàn giao tuần 1](docs/TRUNG_WEEK1_HANDOFF.md), [cách chạy](docs/SETUP.md), và [hợp đồng route/form](docs/INTEGRATION.md).
- Chưa coi nghiệm thu hoàn tất trước khi nhóm review và merge PR theo RULES.md.

## Tài liệu dự án và lịch sử tuần 1

Tài liệu lịch sử UI tuần 1 của Vương: [bàn giao](docs/VUONG_WEEK1_HANDOFF.md), [hướng dẫn sử dụng](docs/VUONG_WEEK1_USER_GUIDE.md), [checklist và ảnh kiểm thử](docs/VUONG_WEEK1_CHECKLIST.md). Mô tả khung báo cáo tuần 1 chỉ áp dụng bản cũ; bản tích hợp hiện hành dùng đủ bốn báo cáo thật.

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
- `database/`: schema, seed, truy vấn, expected_results, audit và `project1_submission.sql` đã đóng gói trong #15/#17; xem SETUP để chọn đúng schema/import.
- `app.py`: entry point; `clinic_app/`: backend và UI tiếng Việt tuần 1–2 đang được Flask sử dụng.
- `clinic_app/templates/`, `clinic_app/static/`: giao diện đang chạy. Template/CSS và schema bệnh viện upstream không còn dùng đã được gỡ khỏi checkout; source gốc vẫn có trong lịch sử Git.
- `tests/`: unit/SQL/backend/Chromium tuần 1–2, oracle và T01–T15.
- `.github/`: mẫu issue/PR, CODEOWNERS và CI Python 3.11 + MySQL 8.4.

## Làm việc nhóm

Nhánh đã chuẩn bị: `quyen/week-1`, `trung/week-1`, `vuong/week-1`. Mở PR về `main`. Tuần sau tạo nhánh mới từ `origin/main`, không tái sử dụng nhánh đã squash merge. Quyền điều phối merge; PR của Quyền phải có Trung hoặc Vương review.

CODEOWNERS không thay thế bảo vệ nhánh; xem trạng thái cấu hình trong RULES.md.

## Nguồn tham khảo

Dựa trên [scmeyer41/hospital-database-management-system](https://github.com/scmeyer41/hospital-database-management-system), commit `711d7b1bdff824901a75e086525d0a9f5ca14701`. Giữ lịch sử upstream và [README gốc](docs/UPSTREAM_README.md). Xem [ghi nhận nguồn](docs/ATTRIBUTION.md). Nhóm tự chịu trách nhiệm giải thích và kiểm thử phần chuyển đổi; không coi tính năng của upstream là phần nhóm đã hoàn thành.
