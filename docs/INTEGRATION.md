# Hợp đồng tích hợp ban đầu

**Hiện trạng tuần 2 (19/10/2026):** nhánh Vương đã tích hợp backend Trung #5 và oracle Quyền #10 để hoàn thiện UI nghiệp vụ/báo cáo; hai PR phụ thuộc chưa merge. Dùng [hợp đồng tuần 2](WEEK2_INTEGRATION.md) và [bàn giao Vương](VUONG_WEEK2_HANDOFF.md) cho bản này. Các trạng thái chờ tích hợp/PR tuần 1 phía dưới là lịch sử, không mô tả hành vi hiện tại.

Phần đầu là mục tiêu tích hợp toàn dự án. Các route đã triển khai và hợp đồng form tuần 1 được ghi rõ ở phần cuối. Cập nhật trạng thái ngày 18/10/2026: backend #4 đã merge, UI #7 đã đồng bộ main và có CI; xác nhận bằng bình luận của Vương trên PR #4 vẫn còn thiếu.

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

Đây là hợp đồng backend tuần 1 đã được UI Vương sử dụng và kiểm thử theo bằng chứng bàn giao; chưa đăng xác nhận của Vương trên PR #4. Thuốc/đơn và SQL của ba trang thống kê trên UI chưa được triển khai trong tuần 1; phần khung báo cáo được ghi riêng bên dưới.

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

UI hồ sơ của Vương hiển thị ngày ở danh sách/chi tiết theo `dd/mm/yyyy`; giá trị gửi từ input date vẫn là `YYYY-MM-DD`. Lỗi xóa tham chiếu xử lý cả mã MySQL 1217 và 1451 để cùng trả 409, giữ nguyên quy tắc FK. Form sửa dùng mã trên route cho điều hướng hủy và input readonly; backend vẫn kiểm tra chống sửa mã trong POST.

Các template chạy thử nằm ở `clinic_app/templates/week1`, CSS ở `clinic_app/static/week1.css`, để Vương có bản có thể chạy ngay. Các file `templates/`, `static/` upstream chưa bị sửa. Khi thay UI, giữ hợp đồng và CSRF, kiểm thử lại POST và hiển thị lỗi.

### Bổ sung điều hướng UI tuần 1 của Vương

- GET `/reports`: trang tổng hợp bốn nhóm báo cáo.
- GET `/reports/diseases`, `/reports/salaries`, `/reports/revenue` nhận `month=YYYY-MM`, mặc định tháng hiện tại theo giờ Việt Nam. Bộ lọc chỉ ghi nhận lựa chọn và dựng khung kết quả, không truy vấn SQL báo cáo. Tháng không hợp lệ trả 400 ngay trên trang, có lỗi ở trường tháng. Khóa báo cáo khác trả 404.
- GET `/reports/history` có bộ lọc `patient_id` và liên kết tìm bệnh nhân. Mã hợp lệ được redirect 302 tới `/patients/<record_id>/history`, tái sử dụng toàn bộ service/query hiện có; mã sai định dạng trả 400 trên form chọn. Hồ sơ không tồn tại do route lịch sử hiện có xử lý 404.
- Trang lịch sử trình bày lại bệnh đang điều trị, các lần khám và lượt đến khám, có bộ lọc đổi bệnh nhân; không thêm service, SQL hoặc nghiệp vụ mới.
- Ba báo cáo thống kê ghi rõ chưa tích hợp dữ liệu, dùng dấu “—” thay cho kết quả chưa có; không hiển thị giá trị 0 hoặc số mẫu như kết quả thật.
- Chỉ bổ sung route GET hiển thị; hợp đồng CRUD, field, template context hiện có, CSRF và nghiệp vụ dữ liệu giữ nguyên.
- Layout sử dụng `clinic_app/templates/week1/base.html`, CSS ở `clinic_app/static/week1.css`; các template upstream ở root không nằm trong luồng ứng dụng mới.

### Điểm cần Quyền/Vương review

Tên vật lý đã theo snake_case; adapter không thay giá trị nguồn. Importer adapter trên nhánh UI không cài trigger Quyền. Bộ SQL/trigger PR #6 đã được kiểm thử cùng UI bằng CI tích hợp bên dưới, nhưng chưa được nhập vào nhánh UI và không bảo vệ toàn bộ nghiệp vụ tại COMMIT; phải giữ các giới hạn trong tài liệu SQL. Các route tạo lượt/đợt/lần khám chưa mở POST, cần triển khai giao dịch và ràng buộc trong tuần 2. Không đánh dấu bốn báo cáo nghiệp vụ hoàn tất từ các màn hình tra cứu nền.

## Bổ sung 17/10: mã hồ sơ và bàn giao UI

Edit/delete sử dụng mã chuẩn lấy từ DB khi URL khác hoa/thường. Form vẫn gửi mã chuẩn, giữ readonly và không đổi PK. Xác nhận xóa so với mã chuẩn. File UI đang được Flask dùng và checklist cho Vương: [VUONG_WEEK1_UI_HANDOFF.md](VUONG_WEEK1_UI_HANDOFF.md).

Form sửa của Vương nhận thêm context `record_id` là mã chuẩn vừa đọc từ DB, dùng cho input readonly và liên kết hủy cả khi POST mã sai. Không lấy chữ hoa/thường từ URL làm giá trị input. Kiểm tra bổ sung cho URL alias ở [bằng chứng cuối](evidence/vuong_week1_final/README.md).

## Trạng thái tích hợp và bằng chứng ngày 18/10

- Backend Trung `5a25395` đã squash merge qua [#4](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/pull/4) thành main `b51b0afb3b0d03f6fa30a255b1efc614b89a9bbd`. Nhánh UI đã đồng bộ bằng `8c5be9469976333195eb67c9d2689638d02c045f`, giữ tree UI `33d45a0`. [PR #7](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/pull/7) đang mở, hết Draft, chưa merge.
- [CI 39092326435](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/actions/runs/39092326435), head `8c5be94`: **46 passed**, không skipped, Python 3.11.17/MySQL 8.4.11/Chromium; dùng seed adapter. [CI tích hợp 39092264670](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/actions/runs/39092264670): **72 passed**, không skipped, SQL `08e4427` + UI/backend `33d45a0` cùng DB có trigger. Cả hai audit sạch 11 bảng/1.144 dòng. [SHA đầy đủ, job và phạm vi log](evidence/vuong_week1_final/README.md#doi-chieu-ci-18102026).
- Kết quả local Vương 17/10 vẫn là **25 passed, 21 skipped** cùng checklist MySQL riêng 33/33; không dùng kết quả CI để đổi trạng thái các test chưa bật trong phiên local.
- [Hướng dẫn setup đề xuất tại PR #8](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/blob/3b59effd4bb86fca1f8d239af8349e73ac09e9e6/docs/SETUP.md) quy định DB mới, schema → seed → audit → constraints → audit → queries. Không chạy chồng `tools.import_seed`/seed adapter với bộ SQL này. Bản SETUP trên nhánh UI/main cũ chưa phản ánh hướng dẫn tích hợp đó; cần nhóm review, thống nhất tài liệu khi merge và thử trên cả ba máy.
- Đợt cập nhật tài liệu `ea556ca` chỉ đối chiếu log CI; phiên nghiệm thu local tiếp theo được ghi riêng bên dưới. Vẫn cần xác nhận hợp đồng trên PR #4, review route/context/FK của UI, hoàn tất review SQL/setup và nghiệm thu máy thành viên.

### Bổ sung kiểm thử local sau cập nhật bàn giao

Ngày 18/10, UI `8c5be94` + SQL `08e4427` đã được import và kiểm thử thật trên instance riêng Windows/Python 3.12.14/MySQL 8.0.46/Chromium. Đúng thứ tự SETUP: schema → seed → audit → constraints → audit → queries; đủ 11 bảng, 9 trigger, audit 1.144 dòng sạch. **72 pytest đạt, không skipped**, 33 ca hồ sơ qua browser/SELECT cùng health/lịch sử đạt; hash seed trước/sau khớp, `.env` không đổi. Hai PDF đã rà đủ 4 trang, không sửa thiết kế.

[Bằng chứng và giới hạn](evidence/vuong_week1_acceptance_2026-10-18/README.md): xuất snapshot bằng git archive, thực thi SQL qua PyMySQL thay Workbench; chưa nghiệm thu clone mạng mới, máy Trung/Quyền hoặc môi trường mục tiêu local Python 3.11/MySQL 8.4. Không đăng xác nhận hợp đồng, approve hoặc merge trong đợt này. Route/field/CSRF/nghiệp vụ giữ nguyên.
