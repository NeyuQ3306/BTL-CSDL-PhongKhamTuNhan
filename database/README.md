# CSDL chuẩn — Quyền tuần 1

Bộ SQL kế thừa schema/1.144 dòng dữ liệu giả Vũ Đại Vương qua adapter Trung `c44238498d11971fd101a02982b2e98054b2e225`; Quyền rà soát thiết kế, tách file, bổ sung ràng buộc và truy vấn. Không sửa file `database/week1/clinic_seed.sql` trên nhánh Trung và không đổi giá trị seed.

## Import trên MySQL 8.4

Tạo **database mới, trống** (ví dụ `clinic_quyen_week1`) với utf8mb4/utf8mb4_0900_ai_ci. Trong MySQL Workbench mở và chạy lần lượt:

1. Chọn database vừa tạo bằng `USE clinic_quyen_week1;`.
2. `schema.sql`: 11 bảng, PK/FK/UQ/CHECK.
3. `seed.sql`: dữ liệu mẫu lịch sử, gồm cả đợt đã khỏi/lượt đã đóng.
4. `audit.sql`: tất cả truy vấn phải trả **0 dòng**; có phát hiện thì dừng.
5. `constraints.sql`: chỉ mục bổ sung và trigger cho nghiệp vụ mới.
6. `queries.sql`: đặt `@thang`, `@ma_benh_nhan` rồi chạy báo cáo; đối chiếu `expected_results.md`.

Không import thêm `hospital_db.sql` hoặc `database/week1/clinic_seed.sql` vào cùng DB. Không chạy seed sau trigger: seed có lịch sử đã hoàn tất còn trigger yêu cầu tạo đợt đang điều trị trước, đóng sau. Không chạy lại schema/constraints trên DB có sẵn. DDL implicit commit nên import lỗi có thể còn bảng; tạo DB thử mới để chạy lại, không tự xóa dữ liệu.

Python CLI trên PowerShell (dùng mật khẩu DB thử của bạn, không commit):

```powershell
python -m pip install PyMySQL cryptography pytest
$env:DB_HOST = '127.0.0.1'
$env:DB_PORT = '3306'
$env:DB_USER = 'root'
$env:DB_PASSWORD = '<mat-khau-local>'
$env:DB_NAME = 'clinic_quyen_week1'
python -m tools.quyen_db
python -m pytest tests/test_quyen_database.py -v
```

CLI này dùng biến môi trường, không tự đọc `.env`. Importer từ chối DB có bảng, không DROP/tắt FK. Sau khi ghép PR Trung, đặt DB_NAME trong `.env` backend trỏ đến DB mới; hướng dẫn `tools.import_seed` của Trung vẫn dùng adapter cũ, chưa cài trigger Quyền. Cần thống nhất một đường import khi tích hợp.

## Phạm vi ràng buộc

- PK/FK/UQ/CHECK: toàn bộ khóa theo sơ đồ, số tiền không âm, số lượng dương, trạng thái/ngày khỏi nhất quán.
- Chỉ mục hàm: tối đa một đợt đang điều trị cho mỗi bệnh nhân/bệnh, kể cả ghi đồng thời.
- Trigger: cùng bệnh nhân lượt/đợt, thứ tự khám liên tiếp khi INSERT, không thêm khám vào đợt đã khỏi/lượt đã đóng; không thay bác sĩ/khóa/ngày lịch sử; hỗ trợ đúng lượt/ngày; ngày lập đơn bằng ngày khám; ngày kết thúc không trước dữ liệu con; đóng lượt phải có khám và y tá.
- Transaction/backend + audit: đơn hoàn tất phải có chi tiết, đợt/lượt hoàn tất phải đủ bản ghi con; không commit nghiệp vụ dang dở. MySQL không có deferred constraint để kiểm tra số con vào thời điểm COMMIT. Truy cập SQL quản trị trực tiếp vẫn có thể xóa hết chi tiết hoặc commit đợt rỗng; **không tuyên bố trigger bảo vệ mọi cận dưới**. Không mở API xóa lịch sử; sửa dữ liệu lịch sử cần audit lại.
- Quy trình ghi: khóa bệnh nhân `FOR UPDATE` trước các bản ghi nghiệp vụ, đồng nhất backend Trung; xử lý rollback/retry toàn giao dịch nếu deadlock. Các test đồng thời của backend được chạy trong CI tương thích.

Q1/Q2/Q4 đã có truy vấn độc lập; Q3 trả nhiều tập kết quả cho hồ sơ, lượt, đợt/tình trạng, khám, thuốc, y tá để tránh nhân bản JOIN. Đây là bàn giao tuần 1, chưa là script nộp cuối YC2 hay nghiệm thu UI.
