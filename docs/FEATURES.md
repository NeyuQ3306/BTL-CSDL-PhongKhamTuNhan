# Danh mục chức năng R01–R10

Quy ước dùng chung khi đối chiếu website, báo cáo Word và slide. R01–R07 là các báo cáo phân tích; R08–R10 là ba chức năng nghiệp vụ của ứng dụng.

Bốn nhóm truy vấn bắt buộc của yêu cầu 2 tiếp tục mang mã **Q1–Q4**. Chúng độc lập với cách đánh số mười chức năng bổ sung dưới đây. Thêm hồ sơ, tiếp nhận và theo dõi điều trị vẫn thuộc luồng ứng dụng, nhưng thao tác thêm hồ sơ không được gộp vào R08.

## Đầu vào, kết quả và xử lý

| Mã | Chức năng | Đầu vào | Kết quả và cách xử lý |
|---|---|---|---|
| R01 | Bệnh theo nhóm tuổi | Khoảng ngày, nhóm tuổi tùy chọn | Bảng số đợt/số bệnh nhân từng bệnh–nhóm tuổi và cột chồng số đợt; tuổi tại lần khám đầu của đợt trong kỳ |
| R02 | Tiếp nhận và khám theo ngày | Khoảng ngày | Bảng và hai cột riêng cho số lượt tiếp nhận/số lần khám; giữ số bệnh nhân tiếp nhận từng ngày riêng |
| R03 | Khối lượng khám theo bác sĩ | Khoảng ngày | Bảng lần khám/đợt/bệnh nhân và thanh số lần khám; giữ bác sĩ có 0 hoạt động |
| R04 | Thuốc được kê | Khoảng ngày lập đơn | Bảng số đơn có thuốc/lượng kê theo đơn vị và thanh số đơn |
| R05 | Đợt tái mắc có tiền sử ghi nhận | Khoảng ngày bắt đầu đợt mới | Hồ sơ đợt cùng bệnh sau đợt đã khỏi trước đó; biểu đồ số đợt theo bệnh |
| R06 | Lâu chưa ghi nhận khám | Ngày đối chiếu, ngưỡng ngày | Hồ sơ đợt đang điều trị tại cuối ngày và nhóm số ngày; chưa có khám thì lấy ngày bắt đầu làm mốc |
| R07 | Chi phí đợt đã khỏi theo bệnh | Khoảng ngày khỏi | Bảng số mẫu/đợt loại/trung bình/min/max và cột chồng khám–thuốc; chi phí tính toàn đợt, giữ NULL khác 0 |
| R08 | Sửa và xóa hồ sơ | Loại hồ sơ bệnh nhân/bác sĩ/y tá, mã và trường được sửa; mã xác nhận xóa | Cập nhật hồ sơ qua validation/transaction; xóa bị FK chặn nếu hồ sơ đang được lịch sử tham chiếu |
| R09 | Tìm kiếm và phân trang | Loại hồ sơ, từ khóa q, trang page | Tìm theo họ tên hoặc mã, đếm tổng kết quả và trả tối đa 20 dòng/trang theo thứ tự ổn định; escape ký tự LIKE |
| R10 | Kê đơn và lưu giá lịch sử | Lần khám, mã/ngày đơn, thuốc, số lượng, liều dùng | Ghi đơn và các dòng trong một transaction; lấy giá danh mục tại lúc ghi vào don_gia_ban, dùng giá đó khi xem đơn/tính tiền |

Các diễn giải chi tiết về dữ liệu giả, đơn vị đếm, phạm vi ngày và giới hạn kết luận của R01–R07 ở [ANALYTICS_HANDOFF](ANALYTICS_HANDOFF.md). Danh mục chức năng là cách tổ chức nội dung báo cáo; việc chấm điểm tuân theo tiêu chí giảng viên, không tự quy đổi mỗi mã thành điểm chắc chắn.

## Mở code khi hỏi đáp

| Phạm vi | File và điểm bắt đầu |
|---|---|
| SQL phân tích R01–R07 | [analytics_queries.sql](../database/analytics_queries.sql), các marker R01-BEGIN đến R07-END |
| API R01–R07 | [analytics_routes.py](../clinic_app/analytics_routes.py), [analytics.py](../clinic_app/analytics.py) |
| Bảng, bộ lọc và biểu đồ | [panel.html](../clinic_app/templates/analytics/panel.html), [analytics.js](../clinic_app/static/analytics.js) |
| R08: route sửa/xóa | [routes.py](../clinic_app/routes.py), hàm edit và delete |
| R08: SQL/transaction | [services.py](../clinic_app/services.py), nhánh record_id khác None trong save_record; delete_record |
| R09: nhận bộ lọc/trang | [routes.py](../clinic_app/routes.py), hàm listing |
| R09: COUNT, LIKE, LIMIT/OFFSET | [services.py](../clinic_app/services.py), hàm list_records |
| R10: form và ghi đơn | [clinical_routes.py](../clinic_app/clinical_routes.py), hàm prescription; [workflows.py](../clinic_app/workflows.py), hàm prescribe |
| R10: xem giá đã lưu | [clinical_routes.py](../clinic_app/clinical_routes.py), hàm prescription_detail; [reports.py](../clinic_app/reports.py), truy vấn doanh thu |
| Ràng buộc dữ liệu | [schema.sql](../database/schema.sql), [constraints.sql](../database/constraints.sql) |

R08–R10 không phải endpoint /api/analytics/R08–R10 và không có marker tương ứng trong analytics_queries.sql. Khi mở code R08, phân biệt nhánh UPDATE với nhánh INSERT dùng cho thêm hồ sơ trong cùng hàm save_record.

## Phân biệt SQL Workbench và SQL trong Python

- **Workbench:** chạy project1_submission.sql để tạo/nạp CSDL và đối chiếu Q1–Q4; sau đó chạy analytics_queries.sql để xem R01–R07. File analytics dùng biến phiên MySQL @tu, @den, @ngay_doi_chieu và @nguong_ngay.
- **Python/PyMySQL:** placeholder %s đại diện cho giá trị; chương trình truyền tuple/list tham số qua execute(sql, params). Dán nguyên câu có %s vào Workbench sẽ không hoạt động như chạy qua ứng dụng.
- **R08–R10 trong Phụ lục C:** đối chiếu với các hàm ở bảng trên. UPDATE/DELETE/INSERT là SQL thay đổi dữ liệu trong transaction, không được mô tả như ba SELECT phân tích bổ sung. Nếu minh họa bằng Workbench, dùng schema thử và giá trị mẫu rõ ràng; bản minh họa không thay quy trình kiểm tra nghiệp vụ của ứng dụng.
- Tên bảng/cột động của CRUD lấy từ danh sách Entity cố định ở [entities.py](../clinic_app/entities.py); không truyền tên bảng tùy ý từ người dùng. Placeholder dùng cho giá trị.

Phụ lục có thể gom SQL theo R01–R10, nhưng không cần đổi tên file SQL hoặc route hiện có để khớp cách đánh số trong tài liệu.

## Số liệu và thuật ngữ thống nhất

- Seed tháng 10/2026: tổng lương bác sĩ **78.000.000 đồng**, y tá **65.600.000 đồng**, cộng **143.600.000 đồng**; xem [expected_results](../database/expected_results.md). Đây là hai tổng theo nhóm nhân viên, không phải lương một người.
- **Kết thúc lượt khám:** cập nhật ngay_ra_vien của luot_den_kham, kiểm điều kiện khám/hỗ trợ; không tự chuyển đợt sang đã khỏi.
- **Xác nhận khỏi đợt điều trị:** cập nhật ngay_khoi và trang_thai của dot_dieu_tri; không tự đóng các lượt. Hai thao tác ở close_visit và cure trong [workflows.py](../clinic_app/workflows.py).
- **Giá lịch sử R10:** copy gia_hien_tai vào chi_tiet_don_thuoc.don_gia_ban khi kê đơn. Tiền đơn cũ được tính theo don_gia_ban; không khẳng định app có chức năng sửa danh mục giá nếu chưa có giao diện đó.

## Nguồn ảnh và mã đối chiếu

Khi dùng ảnh trong Word/slide, ghi đúng nguồn: ảnh demo do thành viên cung cấp hoặc ảnh từ phiên kiểm thử cụ thể. Ảnh đơn thuốc demo của Trung không được đổi nguồn thành CI.

Đường dẫn file phía trên mở trên nhánh đang xem. Khi chốt tài liệu nộp, ghi commit nguồn ứng dụng đã dùng để tạo kết quả/ảnh; phân biệt với commit chỉ cập nhật tài liệu. Số slide, nội dung ghi chú và nguồn từng ảnh cần kiểm trực tiếp trên bản DOCX/PPTX cuối.
