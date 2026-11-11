# Quản lý phòng khám tư nhân

Website hỗ trợ quản lý hồ sơ và hoạt động khám chữa bệnh tại một phòng khám tư nhân. Người dùng có thể tiếp nhận bệnh nhân, ghi nhận lần khám, theo dõi đợt điều trị, kê đơn và xem báo cáo trên trình duyệt.

Dự án được thực hiện trong học phần **Cơ sở dữ liệu — Project 1**, sử dụng Flask và MySQL. Dữ liệu trong ứng dụng là dữ liệu giả lập phục vụ học tập.

## Chức năng

- **Quản lý hồ sơ:** tìm kiếm, thêm, sửa và xóa hồ sơ bệnh nhân, bác sĩ, y tá theo các ràng buộc dữ liệu.
- **Khám và điều trị:** tiếp nhận lượt khám, mở đợt điều trị, tái khám, ghi hỗ trợ y tá, kê đơn nhiều thuốc, kết thúc lượt và xác nhận khỏi.
- **Báo cáo nghiệp vụ:** thống kê bệnh theo tháng, tính lương bác sĩ/y tá, tra cứu lịch sử bệnh nhân và thống kê doanh thu khám/thuốc.
- **Báo cáo phân tích:** chọn bộ lọc, xem bảng kết quả và biểu đồ cho R01–R07.

| Báo cáo phân tích | Nội dung |
|---|---|
| R01 | Phân bố bệnh theo nhóm tuổi |
| R02 | Lượt tiếp nhận và lần khám theo ngày |
| R03 | Khối lượng khám theo bác sĩ |
| R04 | Thuốc được kê: số đơn và lượng kê theo đơn vị |
| R05 | Đợt tái mắc cùng bệnh có tiền sử đã khỏi |
| R06 | Đợt đang điều trị lâu chưa ghi nhận khám |
| R07 | Chi phí các đợt đã khỏi theo bệnh |

### Chức năng nghiệp vụ R08–R10

| Mã | Chức năng |
|---|---|
| R08 | Sửa và xóa hồ sơ |
| R09 | Tìm kiếm và phân trang |
| R10 | Kê đơn và lưu giá lịch sử |

Danh mục R01–R10, đầu vào/kết quả và vị trí mã nguồn được mô tả tại [FEATURES.md](docs/FEATURES.md). Chức năng thêm hồ sơ và các luồng tiếp nhận/điều trị vẫn có trong ứng dụng; thao tác thêm hồ sơ không nằm trong phạm vi R08.

Bảng và biểu đồ dùng cùng kết quả truy vấn. Biểu đồ được vẽ bằng SVG, không cần tải thư viện từ Internet; lấy dữ liệu mới vẫn cần Flask và MySQL hoạt động.

## Công nghệ và cơ sở dữ liệu

- **Backend:** Python, Flask, PyMySQL.
- **Giao diện:** Jinja, HTML, CSS, JavaScript và SVG.
- **Cơ sở dữ liệu:** MySQL 8.4; 11 bảng, khóa và ràng buộc nghiệp vụ, 9 trigger.
- **Kiểm thử:** pytest và Playwright.

Dữ liệu mẫu gồm 1.144 dòng, với hoạt động khám từ tháng 7 đến ngày 14/10/2026. Các báo cáo mô tả dữ liệu đã lưu; kết quả được dùng để minh họa phân tích, không suy ra mùa vụ hoặc dự báo.

## Cài đặt và sử dụng

1. Chuẩn bị Git, Python 3.11 hoặc 3.12 và MySQL Server 8.4.
2. Clone repo, tạo môi trường Python và cấu hình kết nối theo [hướng dẫn cài đặt](docs/SETUP.md).
3. Nhập [bộ SQL](database/project1_submission.sql) vào một schema mới trống.
4. Chạy ứng dụng và mở `http://127.0.0.1:5000`.

[Hướng dẫn sử dụng](docs/USER_GUIDE.md) mô tả các thao tác hồ sơ, khám, kê đơn và báo cáo. Chi tiết file SQL và cách chạy truy vấn xem [database/README.md](database/README.md).

## Cấu trúc mã nguồn

| Đường dẫn | Nội dung |
|---|---|
| `app.py` | Điểm khởi chạy ứng dụng |
| `clinic_app/` | Route, nghiệp vụ, kết nối DB, giao diện và tài nguyên tĩnh |
| `database/` | Schema, dữ liệu mẫu, ràng buộc, audit và truy vấn SQL |
| `tests/`, `week3_checks/`, `windows_checks/` | Kiểm thử ứng dụng và công cụ chạy thử |
| `tools/` | Công cụ nhập, đối chiếu dữ liệu và chạy kiểm thử |
| `docs/` | Thiết kế CSDL và hướng dẫn kỹ thuật |

## Tài liệu

- [Mô hình ER](docs/design/ER_Phong_kham_Ban_chot.pdf), [lược đồ quan hệ](docs/design/Luoc_do_quan_he_Phong_kham_Ban_chot.pdf) và [từ điển dữ liệu](docs/design/DATA_DICTIONARY.md).
- [Bốn nhóm truy vấn nghiệp vụ](database/queries.sql) và [kết quả mẫu](database/expected_results.md).
- [SQL R01–R07](database/analytics_queries.sql) và [quy ước báo cáo phân tích](docs/ANALYTICS_HANDOFF.md).
- [Hướng dẫn kiểm thử](tests/README.md).
- [Danh mục chức năng R01–R10](docs/FEATURES.md).
- [Mục lục tài liệu](docs/README.md).

## Thành viên

| Thành viên | Phần việc chính |
|---|---|
| Nguyễn Minh Quyền | Thiết kế CSDL, SQL và tích hợp |
| Phan Trọng Trung | Backend và xử lý nghiệp vụ |
| Vũ Đại Vương | Giao diện, biểu đồ và kiểm thử người dùng |

Quy trình gửi thay đổi được mô tả trong [CONTRIBUTING.md](CONTRIBUTING.md).

## Nguồn tham khảo

Dự án tham khảo [hospital-database-management-system](https://github.com/scmeyer41/hospital-database-management-system) của scmeyer41 và Richard Tashjian. Phạm vi phát triển của nhóm và thông tin nguồn được ghi tại [ATTRIBUTION.md](docs/ATTRIBUTION.md).

CSDL đã tạo với cột `cmt` cần được sao lưu và nâng cấp trước khi chạy ứng dụng mới. Xem [hướng dẫn chuyển sang CCCD](docs/CCCD_MIGRATION.md).
