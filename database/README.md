# Cơ sở dữ liệu phòng khám

Bộ SQL MySQL 8.4 gồm 11 bảng, 9 trigger và 1.144 dòng dữ liệu giả. Thiết kế: [ER](../docs/design/ER_Phong_kham_Ban_chot.pdf), [lược đồ quan hệ](../docs/design/Luoc_do_quan_he_Phong_kham_Ban_chot.pdf) và [từ điển dữ liệu](../docs/design/DATA_DICTIONARY.md).

## Các file chính

| File | Nội dung |
|---|---|
| `project1_submission.sql` | File gộp: schema → seed → audit → constraints → audit → bốn nhóm truy vấn nghiệp vụ |
| `schema.sql`, `seed.sql` | Tạo bảng và nạp dữ liệu mẫu |
| `constraints.sql` | Chỉ mục và trigger bảo vệ quy tắc nghiệp vụ |
| `audit.sql` | Đối chiếu tính nhất quán dữ liệu |
| `queries.sql` | Q1 thống kê bệnh, Q2 lương, Q3 lịch sử bệnh nhân, Q4 doanh thu |
| `expected_results.md` | Tham số và kết quả mẫu Q1–Q4 |
| `analytics_queries.sql` | Bảy báo cáo phân tích R01–R07 |
| `analytics_expected.json` | Đáp án độc lập dùng đối chiếu seed trong kiểm thử |

## Nhập và chạy truy vấn

Theo [SETUP](../docs/SETUP.md), tạo schema mới trống, chọn làm default schema trong MySQL Workbench rồi chạy toàn bộ `project1_submission.sql` một lần. File không tự tạo/chọn database; giữ nguyên các khối `DELIMITER`.

Nếu dùng bộ file rời, chạy đúng thứ tự **schema → seed → audit → constraints → audit → queries**. Chọn một trong hai cách nhập. Mỗi lần audit SQL phải có 10 tập kết quả rỗng; sau import có 11 bảng và 9 trigger. Seed chứa lịch sử đã hoàn tất nên được nạp trước trigger.

Sau khi nhập CSDL, có thể chạy `analytics_queries.sql` trên cùng schema. Phạm vi mặc định: từ 01/07 đến hết 14/10/2026; R06 đối chiếu 14/10, ngưỡng 14 ngày. Quy ước cột, bộ lọc, đơn vị và NULL ở [ANALYTICS_HANDOFF](../docs/ANALYTICS_HANDOFF.md).

R08–R10 là sửa/xóa hồ sơ, tìm kiếm/phân trang và kê đơn/lưu giá lịch sử, dùng SQL trong ứng dụng. Xem [danh mục và vị trí code](../docs/FEATURES.md) để đối chiếu Phụ lục C; `analytics_queries.sql` chỉ trả bảy báo cáo R01–R07. SQL có `%s` phải đi qua PyMySQL cùng tham số, không chạy nguyên dạng đó trong Workbench.

## Quy tắc dữ liệu

- Khóa chính, khóa ngoại, UNIQUE và CHECK bảo vệ liên kết, số tiền/số lượng và trạng thái/ngày.
- Chỉ mục hàm giới hạn một đợt đang điều trị cho mỗi bệnh nhân/bệnh.
- Trigger kiểm ngày, bệnh nhân của lượt/đợt, thứ tự lần khám, hỗ trợ và đơn thuốc.
- Backend dùng transaction và khóa bản ghi cho các thao tác nhiều bước; audit kiểm dữ liệu sau nhập/kiểm thử. MySQL không có deferred constraint để kiểm mọi điều kiện về số bản ghi con lúc COMMIT.
- Doanh thu cộng tiền khám và thuốc riêng để tránh nhân tiền khi JOIN. Chi tiết đơn lưu giá bán lịch sử bằng DECIMAL.

`week1/clinic_seed.sql` và `tools/normalize_vuong.py` giữ nguồn chuyển đổi dữ liệu giai đoạn đầu; `tools/import_seed.py` còn cung cấp bộ tách câu SQL cho công cụ kiểm thử. Dùng quy trình SETUP để cài ứng dụng.

CSDL đã tạo với cột `cmt` cần được sao lưu và nâng cấp trước khi chạy ứng dụng mới. Xem [hướng dẫn chuyển sang CCCD](../docs/CCCD_MIGRATION.md).
