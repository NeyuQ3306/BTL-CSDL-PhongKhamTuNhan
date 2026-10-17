# Hợp đồng backend tuần 2

Các route dưới đây đã triển khai. GET mở form/tra cứu; POST thay đổi DB và yêu cầu `csrf_token`. Chưa có JSON mutation API. GET báo cáo hỗ trợ `format=json` để UI khác dùng. Mọi tên bảng/cột là snake_case như seed chuẩn hóa tuần 1.

## Route và form

| Route | Method | Field / chức năng |
|---|---|---|
| `/visits/new` | GET, POST | Tạo lượt, khám đầu tiên và y tá hỗ trợ nguyên tử |
| `/visits/<visit_id>` | GET | visit, examinations, support |
| `/visits/<visit_id>/examinations/new` | GET, POST | Thêm một bệnh vào lượt đang mở |
| `/visits/<visit_id>/support` | GET, POST | Ghi/cập nhật hỗ trợ y tá |
| `/visits/<visit_id>/close` | GET, POST | `ngay_ra_vien` |
| `/treatments/<episode_id>/cure` | GET, POST | `ngay_khoi` |
| `/examinations/<exam_id>/prescription` | GET, POST | `ma_don`, `ngay_lap_don`; lặp field `ma_thuoc`, `so_luong`, `lieu_dung` |
| `/prescriptions/<order_id>` | GET | order, rows, total |

Tạo lượt cần `ma_luot`, `ma_benh_nhan`, `ngay_vao_vien` + nhóm khám + nhóm hỗ trợ.

Nhóm khám: `ma_lan_kham`, `ngay_kham`, `tien_kham_chua`, `ket_luan`, `che_do_dot` (`new` hoặc `existing`), `ma_dot`. Với `new` cần thêm `ma_benh`, `ma_bac_si`; server đặt ngày bắt đầu đợt bằng ngày khám. Với `existing`, bệnh và bác sĩ lấy từ đợt, không thay theo form. STT do server tính; không gửi.

Nhóm hỗ trợ: `ma_y_ta`, `ngay_ho_tro`, `noi_dung_ho_tro`. Lưu lại cùng cặp y tá/lượt cập nhật nội dung; đổi ngày cũ trả 409. Để nhiều y tá hỗ trợ, tạo lượt với một y tá rồi thêm từng người.

Đơn thuốc: các field lặp phải có cùng số phần tử; tối đa 100 dòng, bỏ dòng trống hoàn toàn. Không gửi đơn giá/tổng tiền: server lấy giá DB. Một thuốc một dòng, số lượng nguyên dương, liều dùng bắt buộc. Mã dài tối đa 12; ngày YYYY-MM-DD; tiền nguyên đồng không âm tối đa 999999999999.

Form template `week2/form.html`: action, title, values (MultiDict giữ giá trị khi lỗi), error, choices, today. Các nhóm choices: patients/doctors/nurses/diseases/episodes/medicines. Tên endpoint nằm trong blueprint `clinical`. Phần UI đây là bản tích hợp thử; Vương có thể thay trình bày nhưng giữ field và CSRF.

POST thành công: redirect 303. Token sai 400; validation 422; trùng mã, trạng thái hoặc xung đột nghiệp vụ 409; tham chiếu không tồn tại 404; lỗi vận hành MySQL 503 theo xử lý chung. Lỗi nghiệp vụ hiển thị lại form; các lỗi khác dùng trang lỗi tuần 1. Không có ghi một phần khi lỗi.

## Báo cáo

| Route | Bộ lọc | Context / JSON |
|---|---|---|
| `/reports/diseases` | `month=YYYY-MM` | month, rows(ma_benh, ten_benh, so_dot_mac), total |
| `/reports/salaries` | month | month, doctors, nurses, total; mỗi dòng: ma_nhan_vien, ho_ten, luong_co_ban, so_lan_thuong, tien_thuong, tong_luong |
| `/reports/revenue` | month | month, consultation, medicine, total |
| `/reports/history` | `patient_id` | patient, visits, treatments, current, examinations, medicines, support |
| `/patients/<record_id>/history` | mã trên đường dẫn | Cùng nội dung lịch sử, HTML |

Thêm `&format=json` vào báo cáo để lấy JSON. Decimal là chuỗi để giữ chính xác tiền; số đếm là số; ngày ISO YYYY-MM-DD, ngày chưa có là null. Không truyền month: tháng hiện tại; month sai: 400. Lịch sử thiếu patient_id mở màn hình chọn bệnh nhân; mã không tồn tại 404. Dữ liệu bệnh nhân không bị lọc theo tháng: trả toàn bộ lịch sử.

Báo cáo tiền dùng `money` filter của app khi render HTML. Tháng không phát sinh: danh sách bệnh rỗng, doanh thu 0; lương cơ bản vẫn có. Tính trạng thái hiện tại theo đợt Đang điều trị. Không suy diễn số lần mắc bằng số lần khám.

## Điểm review

Hợp đồng này cần Vương xác nhận trước khi nghiệm thu tích hợp. Quyền review SQL báo cáo trong reports.py và khóa/transaction trong workflows.py; backend không thay thế constraints khi ghi trực tiếp bằng SQL.
