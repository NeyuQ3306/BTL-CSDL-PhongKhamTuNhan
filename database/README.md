# CSDL chuẩn — Quyền tuần 1

Bộ SQL kế thừa schema/1.144 dòng dữ liệu giả Vũ Đại Vương qua adapter Trung `c44238498d11971fd101a02982b2e98054b2e225`; Quyền rà soát thiết kế, tách file, bổ sung ràng buộc và truy vấn. Không sửa file `database/week1/clinic_seed.sql` trên nhánh Trung và không đổi giá trị seed.

## Import trên MySQL 8.4

Hướng dẫn hiện hành duy nhất: [docs/SETUP.md](../docs/SETUP.md).

Thứ tự chuẩn cho DB mới trống: **schema.sql → seed.sql → audit.sql → constraints.sql → audit.sql → queries.sql**. Mọi truy vấn audit phải trả 0 dòng; đối chiếu queries.sql với expected_results.md. Seed phải nhập trước trigger.

Không dùng tools.import_seed, database/week1/clinic_seed.sql hoặc hospital_db.sql cho quy trình này. tools.quyen_db là tiện ích kiểm thử cũ, không đọc .env và chưa audit trước constraints; không dùng làm đường cài chuẩn. Không import chồng hoặc tự DROP dữ liệu. Xem SETUP về Windows, cổng 3306/3307 và cấu hình DB_NAME.

## Phạm vi ràng buộc

- PK/FK/UQ/CHECK: toàn bộ khóa theo sơ đồ, số tiền không âm, số lượng dương, trạng thái/ngày khỏi nhất quán.
- Chỉ mục hàm: tối đa một đợt đang điều trị cho mỗi bệnh nhân/bệnh, kể cả ghi đồng thời.
- Trigger: cùng bệnh nhân lượt/đợt, thứ tự khám liên tiếp khi INSERT, không thêm khám vào đợt đã khỏi/lượt đã đóng; không thay bác sĩ/khóa/ngày lịch sử; hỗ trợ đúng lượt/ngày; ngày lập đơn bằng ngày khám; ngày kết thúc không trước dữ liệu con; đóng lượt phải có khám và y tá.
- Transaction/backend + audit: đơn hoàn tất phải có chi tiết, đợt/lượt hoàn tất phải đủ bản ghi con; không commit nghiệp vụ dang dở. MySQL không có deferred constraint để kiểm tra số con vào thời điểm COMMIT. Truy cập SQL quản trị trực tiếp vẫn có thể xóa hết chi tiết hoặc commit đợt rỗng; **không tuyên bố trigger bảo vệ mọi cận dưới**. Không mở API xóa lịch sử; sửa dữ liệu lịch sử cần audit lại.
- Quy trình ghi: khóa bệnh nhân `FOR UPDATE` trước các bản ghi nghiệp vụ, đồng nhất backend Trung; xử lý rollback/retry toàn giao dịch nếu deadlock. Các test đồng thời của backend được chạy trong CI tương thích.

Q1/Q2/Q4 đã có truy vấn độc lập; Q3 trả nhiều tập kết quả cho hồ sơ, lượt, đợt/tình trạng, khám, thuốc, y tá để tránh nhân bản JOIN. Đây là bàn giao tuần 1, chưa là script nộp cuối YC2 hay nghiệm thu UI.
