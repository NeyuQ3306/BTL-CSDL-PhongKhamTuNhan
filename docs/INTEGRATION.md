# Hợp đồng tích hợp ban đầu

Phần đầu là mục tiêu tích hợp toàn dự án. Các route đã triển khai và hợp đồng form tuần 1 được ghi rõ ở phần cuối; cần Vương xác nhận trước khi thay UI.

## Tên vật lý

11 bảng: benh_nhan, benh, dot_dieu_tri, luot_den_kham, bac_si, lan_kham_benh, y_ta, ho_tro, don_thuoc, chi_tiet_don_thuoc, thuoc. Cột snake_case tương ứng thuộc tính PDF (MaBenhNhan -> ma_benh_nhan). Dùng một tên thống nhất trên mọi OS.

## Màn hình và route mục tiêu

| Màn hình | GET mục tiêu | Dữ liệu chính |
|---|---|---|
| Bệnh nhân | /patients | Danh sách và bộ lọc tên/mã |
| Hồ sơ | /patients/<id>/history | Lượt, đợt, lần khám, đơn, bệnh đang điều trị |
| Lượt khám | /visits | Lượt và các lần khám theo bệnh |
| Đợt điều trị | /treatments | Bệnh nhân, bệnh, bác sĩ phụ trách, trạng thái |
| Thuốc | /medicines | Danh mục, đơn vị, giá hiện tại |
| Đơn thuốc | /prescriptions | Lần khám, ngày lập, các dòng thuốc |
| Thống kê bệnh | /reports/diseases?month=2026-10 | Bệnh, số đợt có lần khám trong tháng, giảm dần |
| Lương | /reports/salaries?month=2026-10 | Nhân viên, lương cơ bản, thưởng, tổng |
| Doanh thu | /reports/revenue?month=2026-10 | Tiền khám, tiền thuốc, tổng |

POST dùng cho thay đổi dữ liệu, không GET. Jinja server-rendered để giảm khối lượng API/frontend. Field và template context cần ghi rõ trong PR backend đầu tiên; không tự đổi khi frontend đã dùng.

## Quy ước báo cáo

Tháng lọc dạng YYYY-MM; khoảng thời gian là từ đầu tháng (bao gồm) đến đầu tháng tiếp theo (không bao gồm). Tháng hiện tại chỉ lấy sự kiện đến thời điểm hiện tại; ngày lưu theo giờ Việt Nam. Bác sĩ thưởng theo ngày khỏi; y tá theo ngày bắt đầu hỗ trợ của lượt. Doanh thu theo ngày khám và ngày lập đơn, là doanh thu ghi nhận từ dữ liệu khám/kê đơn, chưa phải quản lý thu tiền thực tế.

Không JOIN thẳng lần khám với nhiều dòng thuốc rồi SUM tiền khám. Aggregate từng nguồn trước. Không có dữ liệu: báo cáo rỗng/tổng 0; lương vẫn gồm lương cơ bản cho nhân viên trong phạm vi mô hình.

## Ràng buộc bắt buộc

Một bác sĩ/đợt; một lần khám tối đa một đơn; một y tá/lượt có một khoản thưởng; cùng bệnh nhân giữa lượt và đợt; không trùng đợt đang điều trị cho một bệnh; UNIQUE(lượt,đợt), UNIQUE(đợt,STT). Ngày hợp lệ, số lượng dương, tiền không âm. Không cho xóa danh mục đang được lịch sử tham chiếu. Tạo các bản ghi phụ thuộc trong cùng giao dịch; chỉ nghiệm thu trạng thái hoàn tất đủ bản ghi con theo PDF.

## Hợp đồng backend được triển khai trên nhánh Trung tuần 1

Đây là giao diện bàn giao để Vương tích hợp; chưa có xác nhận đồng thuận của Vương trong PR. Các route mục tiêu thuốc/đơn/báo cáo ở trên chưa được triển khai trong tuần 1.

Với `slug` thuộc `patients`, `doctors`, `nurses`:

| Route | Method | Kết quả / template context |
|---|---|---|
| `/<slug>?q=...&page=1` | GET | `week1/list.html`: entity, rows, total, q, page, pages; 20 dòng/trang |
| `/<slug>/new` | GET, POST | `week1/form.html`: entity, values, errors, form_error, editing=False |
| `/<slug>/<record_id>` | GET | `week1/detail.html`: entity, record, form_error |
| `/<slug>/<record_id>/edit` | GET, POST | form như trên; editing=True; mã không đổi |
| `/<slug>/<record_id>/delete` | POST | phải có confirm_delete bằng mã hồ sơ |
| `/visits` | GET | `week1/visits.html`: rows; chỉ tra cứu |
| `/treatments` | GET | `week1/treatments.html`: rows; chỉ tra cứu |
| `/patients/<record_id>/history` | GET | patient, visits, treatments, examinations; lịch sử nền, chưa có chi tiết từng thuốc/hỗ trợ |
| `/health`, `/health/db` | GET | JSON status; DB lỗi trả 503 |

### Form field

- Chung: `cmt`, `ho_ten`, `ngay_sinh`, `dia_chi`.
- Bệnh nhân: `ma_benh_nhan`, `so_dien_thoai`.
- Bác sĩ: `ma_bac_si`, `bac_nghe`, `tham_nien`, `chuyen_mon`, `trinh_do_dao_tao`.
- Y tá: `ma_y_ta`, `so_dien_thoai`, `trinh_do`, `tham_nien`.
- Mọi POST: hidden `csrf_token` bằng `{{ csrf_token() }}`. Dùng url_for endpoint trong `clinic_app/routes.py`; không đổi tên field riêng ở HTML.

Ngày nhập `YYYY-MM-DD`; CMT/điện thoại là chuỗi giữ số 0 đầu. Tiền đọc từ DB là Decimal, hiển thị `{{ value|money }}`; không dùng float. Lỗi validation trả HTTP422, giữ values và errors[field]. Trùng PK/CMT hoặc xóa hồ sơ có tham chiếu trả409. Thành công POST redirect303. Hồ sơ không tồn tại404, token thiếu/sai400. Không có JSON CRUD API trong tuần 1.

Các template chạy thử nằm ở `clinic_app/templates/week1`, CSS ở `clinic_app/static/week1.css`, để Vương có bản có thể chạy ngay. Các file `templates/`, `static/` upstream chưa bị sửa. Khi thay UI, giữ hợp đồng và CSRF, kiểm thử lại POST và hiển thị lỗi.

### Điểm cần Quyền/Vương review

Tên vật lý đã theo snake_case; adapter không thay giá trị nguồn. Những quy tắc liên bảng trong mục trước mới được audit, **chưa có trigger bảo vệ toàn bộ nghiệp vụ**. Các route tạo lượt/đợt/lần khám chưa mở POST, cần triển khai giao dịch và ràng buộc trong tuần 2. Không đánh dấu bốn báo cáo nghiệp vụ hoàn tất từ các màn hình tra cứu nền.
