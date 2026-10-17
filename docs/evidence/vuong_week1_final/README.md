# Kiểm tra cuối trước commit tuần 1 của Vương

Ngày: 17/10/2026. Nền đã đồng bộ: `origin/trung/week-1` tại `5a25395699905cc5f79af4904bd73d95073963a0`. Thay đổi UI nằm trên nhánh `vuong/week-1`; ảnh/log các bước trước vẫn giữ nguyên để đối chiếu lịch sử phiên kiểm tra.

## Kết quả sau đồng bộ

- [automated_results.json](automated_results.json): **33/33 ca checklist đạt** với MySQL thật trên database giả lập riêng `clinic_vuong_week1`, gồm CRUD ba nhóm, validation, dữ liệu trùng, trạng thái rỗng, CSRF và dọn hồ sơ tạm. Toàn bộ 11 bảng được so hash trước/sau, giữ đủ 1.144 dòng và `.env` không đổi.
- [canonical_record_ids.json](canonical_record_ids.json): tạo hồ sơ có mã trộn hoa/thường ở cả ba nhóm, mở URL chữ thường để sửa, giữ mã chuẩn, lưu và xóa qua alias đều đạt; đã dọn các hồ sơ tự tạo.
- [pytest.txt](pytest.txt): **25 passed, 21 skipped**. 18 test MySQL gốc yêu cầu database `_test`; 3 test Playwright chưa bật. Đã cập nhật nhãn nút trong test browser phù hợp UI, nhưng chưa tuyên bố các test tùy chọn chạy đạt trên phiên bản mới.
- Python AST parse 18 file, Jinja parse 15 template, diff check đạt. Không đổi schema, SQL, services hoặc app entry point của nền Trung.
- [security_review.json](security_review.json): rà toàn bộ file khác main và file mới; không có phát hiện secrets chưa xử lý. Các trùng chuỗi số trong ví dụ giả lập đã được phân loại, không đưa giá trị credentials vào báo cáo. `.env`/`.venv` không được theo dõi.

## Điều chỉnh để tương thích nền Trung mới

- Backend đã dùng mã chuẩn DB trong sửa/xóa. Context `record_id` được truyền cho form sửa; UI không lấy mã từ chữ hoa/thường của URL hoặc từ POST bị giả sửa mã.
- Test hồi quy UI kiểm tra cả URL `BN001` và `bn001`. Test browser của Trung được đổi locator sang nhãn `Thêm hồ sơ` / `Lưu thay đổi`.
- Mọi field, CSRF và quy tắc không đổi khóa chính giữ nguyên. Xử lý FK 1217/1451 và GET khung báo cáo vẫn cần Trung review.

## Giới hạn

Máy hiện tại: Windows/Python 3.14.6/MySQL 8.0.46. Chưa có CI Python 3.11/MySQL 8.4 cho commit UI, chưa rà hai PDF, chưa review/merge. Các ca ở [checklist gốc](../../VUONG_WEEK1_CHECKLIST.md) có ngày/nền ghi riêng; không dùng bằng chứng backend Trung để đánh dấu test UI mới chưa chạy là đạt.
