# Kiểm tra cuối trước commit tuần 1 của Vương

Đây là bằng chứng local 17/10 và lần đối chiếu CI đầu ngày 18/10. **Cập nhật tiếp theo:** [nghiệm thu PDF và tích hợp local 18/10](../vuong_week1_acceptance_2026-10-18/README.md) đã rà đủ 4 trang PDF, chạy 72 pytest và 33 ca hồ sơ browser/SELECT đạt trên instance riêng. Giữ nguyên log/JSON của các phiên cũ để đối chiếu lịch sử.

Ngày: 17/10/2026. Nền đã đồng bộ: `origin/trung/week-1` tại `5a25395699905cc5f79af4904bd73d95073963a0`. Thay đổi UI nằm trên nhánh `vuong/week-1`; ảnh/log các bước trước vẫn giữ nguyên để đối chiếu lịch sử phiên kiểm tra.

## Kết quả sau đồng bộ

- [automated_results.json](automated_results.json): **33/33 ca checklist đạt** với MySQL thật trên database giả lập riêng `clinic_vuong_week1`, gồm CRUD ba nhóm, validation, dữ liệu trùng, trạng thái rỗng, CSRF và dọn hồ sơ tạm. Toàn bộ 11 bảng được so hash trước/sau, giữ đủ 1.144 dòng và `.env` không đổi.
- [canonical_record_ids.json](canonical_record_ids.json): tạo hồ sơ có mã trộn hoa/thường ở cả ba nhóm, mở URL chữ thường để sửa, giữ mã chuẩn, lưu và xóa qua alias đều đạt; đã dọn các hồ sơ tự tạo.
- [pytest.txt](pytest.txt): **25 passed, 21 skipped** trong phiên local 17/10. 18 test MySQL gốc yêu cầu database `_test`; 3 test Playwright chưa bật. Giữ nguyên kết quả local; CI chạy đủ trên các snapshot riêng được bổ sung bên dưới.
- Python AST parse 18 file, Jinja parse 15 template, diff check đạt. Không đổi schema, SQL, services hoặc app entry point của nền Trung.
- [security_review.json](security_review.json): rà toàn bộ file khác main và file mới; không có phát hiện secrets chưa xử lý. Các trùng chuỗi số trong ví dụ giả lập đã được phân loại, không đưa giá trị credentials vào báo cáo. `.env`/`.venv` không được theo dõi.

## Điều chỉnh để tương thích nền Trung mới

- Backend đã dùng mã chuẩn DB trong sửa/xóa. Context `record_id` được truyền cho form sửa; UI không lấy mã từ chữ hoa/thường của URL hoặc từ POST bị giả sửa mã.
- Test hồi quy UI kiểm tra cả URL `BN001` và `bn001`. Test browser của Trung được đổi locator sang nhãn `Thêm hồ sơ` / `Lưu thay đổi`.
- Mọi field, CSRF và quy tắc không đổi khóa chính giữ nguyên. Xử lý FK 1217/1451 và GET khung báo cáo vẫn cần Trung review.

## Giới hạn

Phiên local 17/10 dùng Windows/Python 3.14.6/MySQL 8.0.46. Hai PDF chưa rà; chưa nghiệm thu cùng hướng dẫn trên cả ba máy, chưa thử điện thoại thật, PR #7 chưa merge. Các ca ở [checklist gốc](../../VUONG_WEEK1_CHECKLIST.md) có ngày/nền ghi riêng. Không sửa log/JSON lịch sử để thay kết quả local bằng CI.

<a id="doi-chieu-ci-18102026"></a>

## Đối chiếu CI 18/10/2026

Đã đọc metadata run, steps và log hai job GitHub dưới đây; đây là xác minh bằng chứng CI có sẵn, không phải chạy lại MySQL/Chromium local trong lần cập nhật tài liệu. Cả hai run `completed/success`, dùng Ubuntu/Python 3.11.17/MySQL 8.4.11/Chromium.

| Run / job | Phiên bản được kiểm thử | Kết quả log |
|---|---|---|
| [39092326435](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/actions/runs/39092326435) / `117571499620` | PR #7, head `8c5be9469976333195eb67c9d2689638d02c045f`; workflow `.github/workflows/ci.yml`, import bằng `tools.import_seed` (adapter) | `46 passed in 11.62s`; compile và parse Jinja đạt |
| [39092264670](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/actions/runs/39092264670) / `117571317667` | PR #8, workflow head `89539428d4b522a44938bc21115114c595cc207b`; SQL `08e4427f6ac8e9ba55eaba859ddab4067330ec04` + UI/backend `33d45a06eb7e237796d3d240fd6d419fabd00bd1` | `Imported schema + 1144 rows + constraints successfully`; `72 passed in 9.59s` (26 SQL + 46 backend/UI) |

Không có ca skipped trong hai summary CI. Audit sau test của cả hai job: `mysql_version = 8.4.11`, 11 bảng, `total = 1144`, `matches_expected_counts = true`; toàn bộ mảng `findings` rỗng. Audit sạch không thay thế bảo vệ mọi lần ghi tương lai hoặc review nghiệp vụ.

PR #4 đã squash merge tại `b51b0afb3b0d03f6fa30a255b1efc614b89a9bbd`. Commit đồng bộ `8c5be94` có hai parent UI/main và cùng tree `5489ec161273bcc0daf8349ceb762dc04e4f6952` với `33d45a0`; `git diff 33d45a0 8c5be94` rỗng. Local fast-forward an toàn từ `33d45a0` tới `8c5be94` ngày 18/10, working tree sạch trước đồng bộ. Không nhập code tuần 2.

PR #7 đang mở, hết Draft khi kiểm tra ngày 18/10. Nhận xét cũ về chưa có CI/Draft được thay bằng trạng thái này; vẫn cần review hợp lệ và xử lý phản hồi trước merge. Run 72 ca chỉ chứng minh hai snapshot được ghép trong CI, không chứng minh #6/#7 đã merge hoặc cả ba máy đã chạy. Với commit tài liệu mới, kiểm tra Checks theo SHA mới; không đổi SHA của bằng chứng cũ.
