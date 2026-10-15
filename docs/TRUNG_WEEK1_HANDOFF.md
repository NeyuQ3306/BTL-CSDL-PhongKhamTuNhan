# Bàn giao tuần 1 — Phan Trọng Trung

Đề tài: CSDL quản lý phòng khám tư nhân. Ngày thực hiện: 15/10/2026.

## Căn cứ và phạm vi

Căn cứ yêu cầu bài tập, hai PDF thiết kế bản chốt trong `docs/design`, phân công nhóm và SQL `phong_kham_full_mysql.sql` của Vũ Đại Vương. Bộ dữ liệu là giả lập; Vương là người chuẩn bị dữ liệu. Backend sử dụng mô hình lượt đến khám → lần khám theo bệnh → đợt điều trị; bác sĩ phụ trách nằm tại đợt điều trị.

Tài liệu CSDL và hai slide SQL người dùng cung cấp được dùng để đối chiếu khóa, liên kết bảng, JOIN/tổng hợp, transaction. File SQL_Cheat_Sheet chưa nhận được nội dung nên không được ghi là nguồn đã đọc.

## Kết quả theo đầu việc

| Đầu việc | Sản phẩm | Trạng thái |
|---|---|---|
| Khảo sát source gốc và môi trường | Log bên dưới, requirements, Compose MySQL8.4 | Đã khảo sát; giới hạn chạy cục bộ được ghi rõ |
| Tách DB / cấu hình / app | clinic_app/config.py, db.py, factory và app.py | Đã triển khai |
| Chuẩn hóa định danh | Adapter seed, công cụ normalize và audit | Đã làm; chờ Quyền review schema |
| CRUD bệnh nhân, bác sĩ, y tá | Route/service, validation, form và thông báo lỗi | Đã qua kiểm thử tích hợp MySQL8.4 |
| Nền lượt/đợt/lần khám | Màn hình tra cứu và lịch sử sơ bộ | Đã triển khai đọc; ghi nghiệp vụ thuộc tuần 2 |
| Route/form/template thống nhất | docs/INTEGRATION.md, entities.py | Đã bàn giao hợp đồng; chưa có xác nhận Vương |
| Tài liệu chạy và tích hợp | docs/SETUP.md, README, test | Đã viết |

## Cấu trúc và lựa chọn triển khai

- `app.py` chỉ tạo/chạy ứng dụng; `clinic_app` tách config, kết nối, services, routes, validation và CSRF.
- Mỗi Flask context dùng một kết nối, đóng ở teardown. Ghi có commit/rollback; không dùng kết nối toàn cục của upstream. Tham số đi qua placeholder PyMySQL, tên bảng lấy từ danh sách cố định.
- Số CMT/điện thoại giữ kiểu chuỗi; tiền Decimal; múi giờ ngày ứng dụng là Việt Nam. PK không thay đổi khi sửa. Hồ sơ có lịch sử được FK chặn xóa.
- Các form chạy thử nằm trong package backend, giữ nguyên templates/static gốc để Vương tích hợp sau. Đây là UI phục vụ nghiệm thu backend tuần 1.
- Seed trong `database/week1` chỉ đổi định danh, không sửa giá trị nguồn. SHA256 nguồn được ghi đầu file. Import vào DB trống, giữ nguyên PK/FK/UNIQUE/CHECK gốc.

## Nhật ký môi trường và source gốc

1. Snapshot khảo sát: commit `f8165de29c939104d3f126dee548a25b0b2340f8` của repository nhóm. Source tham khảo nằm trong lịch sử Git, giữ ghi nhận tác giả trong docs/ATTRIBUTION.md.
2. Source cũ mở MySQL ngay khi import `app.py`; chạy thử khi DB không có trả `OperationalError 2003` trước khi Flask khởi động. Bản mới khởi động không cần DB; `/health` trả200, lỗi DB được xử lý503. Unit test xác nhận.
3. Đọc source thấy truy vấn `Patient`, `Physician`, `Illness` trong khi SQL gốc tạo bảng chữ thường, và mô hình bệnh viện không trùng 11 bảng nhóm. Đây là phát hiện khi đọc mã; chưa tuyên bố đã chạy UI upstream với database gốc.
4. Môi trường cục bộ là Python3.12. Đã cài Flask, PyMySQL, python-dotenv, pytest, cryptography. Unit tests: 9 passed; 9 integration tests skipped khi chưa bật DB. Compileall và parse Jinja đã qua.
5. Thử MySQL8.0.46 trong vùng tạm: tải gói lần đầu bị thiếu, tải lại và initialize thành công. Server dừng với `Can't start server: UNIX Socket: Operation not permitted`. Vì vậy không dùng môi trường cục bộ này làm bằng chứng MySQL đã chạy.
6. CI cấu hình môi trường mục tiêu Python3.11/MySQL8.4, import seed, chạy đủ unit/integration và in báo cáo audit. Run [38764280374](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/actions/runs/38764280374) đã thành công: **18/18 test passed**, MySQL8.4.11, Python3.11.17; nhập đủ 11 bảng/1.144 dòng. Các truy vấn audit đã chạy không có phát hiện. Chi tiết lưu tại [bằng chứng kiểm thử](evidence/trung_week1_results.txt).

## Kiểm thử đã chuẩn bị

CRUD đủ ba đối tượng; trùng mã/CMT; giữ số 0 đầu; ngày không hợp lệ; PK bị sửa; FK chặn xóa lịch sử; không ghi bằng GET; CSRF; escape HTML; tìm kiếm với dấu nháy và ký tự wildcard; transaction rollback; đóng kết nối; đọc lịch sử; tổng tiền không bị nhân bản JOIN; đếm 1.144 dòng; từ chối import lại.

`tools.audit_seed` kiểm tra số dòng, cùng bệnh nhân giữa lượt/đợt, ngày khám, đợt đang điều trị trùng, thứ tự tái khám, lượt/đơn rỗng, ngày hỗ trợ/đơn và đợt cùng bệnh chồng nhau. Công cụ chỉ báo cáo; không tự sửa dữ liệu Vương. Kết quả audit có vấn đề phải bàn với Quyền/Vương trước nghiệm thu dữ liệu.

## Phần chưa thuộc nghiệm thu tuần 1

Chưa có các luồng ghi lượt/đợt/lần khám/đơn đa bước, trigger đầy đủ, bốn báo cáo nghiệp vụ hoàn chỉnh hoặc UI cuối của Vương. Bản backend dùng demo localhost, chưa có đăng nhập/phân quyền triển khai thực tế. Chưa có xác nhận chốt contract của Vương và review/merge của Quyền. Không tự đánh dấu toàn bộ tuần 1 của nhóm hoàn tất.

## Hướng dẫn demo

Theo SETUP.md, import seed và chạy app. Mở Bệnh nhân, tìm BN001, xem hồ sơ/lịch sử. Thêm hồ sơ mã DEMO001 với CMT mới hợp lệ, sửa họ tên, rồi xóa hồ sơ vừa thêm. Thử thêm trùng CMT và xóa BN001 có lịch sử để thấy thông báo409. Mở Bác sĩ/Y tá để thực hiện cùng luồng; mở Lượt khám/Đợt điều trị để xem dữ liệu liên kết. Khi kết thúc, không để hồ sơ DEMO còn lại nếu đối chiếu số lượng seed.
