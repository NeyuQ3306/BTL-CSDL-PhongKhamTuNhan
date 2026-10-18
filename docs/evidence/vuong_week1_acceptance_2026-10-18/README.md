# Nghiệm thu bổ sung tuần 1 — Vương, 18/10/2026

**Kết quả:** rà trực quan đủ 4 trang của hai PDF; import chuẩn thành công; **72/72 pytest đạt, không skipped**; 33 ca hồ sơ qua trình duyệt/SELECT độc lập đạt (11 ca × 3 nhóm), cùng health và lịch sử đạt. Không phát hiện lỗi UI cần sửa trong phạm vi đã chạy. Đây là bằng chứng local bổ sung, không thay cho review/merge hoặc xác nhận trên máy Trung/Quyền.

## Phiên bản và môi trường

| Thành phần | Thực tế |
|---|---|
| UI/backend | `8c5be9469976333195eb67c9d2689638d02c045f`, snapshot được SETUP chỉ định |
| Nhánh Vương lúc bắt đầu | `ea556ca149019119a4f3c9063e6f0b3b4e9f4e88`; chỉ thêm tài liệu so với `8c5be94`, không đổi code/tests/tools/dependencies |
| SQL | `08e4427f6ac8e9ba55eaba859ddab4067330ec04`, sáu file SQL/expected_results từ PR #6 |
| Hướng dẫn | [SETUP tại PR #8](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/blob/3b59effd4bb86fca1f8d239af8349e73ac09e9e6/docs/SETUP.md), SHA `3b59effd4bb86fca1f8d239af8349e73ac09e9e6` |
| Hệ điều hành/runtime | Windows, Python **3.12.14**, MySQL **8.0.46**, Playwright 1.64.0/Chromium **156.0.8078.4** |
| Trình duyệt | Chromium headless, viewport 1440×1000, locale vi-VN; ảnh full page |
| MySQL cách ly | Instance mới với `--no-defaults`, datadir riêng trong `.venv/week1_acceptance_20261018/mysql-data`, bind `127.0.0.1`, cổng ngẫu nhiên riêng; schema `clinic_vuong_w1_acceptance_test` |

Source xuất bằng `git archive` từ hai commit đã fetch, tương đương nội dung snapshot; không clone mạng mới. Chỉ ghép sáu file SQL của SETUP; thêm `tools/quyen_db.py` để tách statement có DELIMITER và `tests/test_quyen_database.py` để chạy 26 test SQL. Không gọi importer adapter hoặc hàm install tự động. [Manifest](source_manifest.json) xác minh blob tám file và code UI không đổi so với nhánh Vương lúc bắt đầu.

Tài khoản ứng dụng trên dịch vụ MySQL đang làm việc đã được kiểm tra quyền; CREATE database mới bị từ chối mã 1044, không tạo database nào ở đó. Vì vậy chuyển sang instance riêng từ binary MySQL có sẵn. Không đổi service, cấu hình, quyền hoặc dữ liệu của dịch vụ cũ. Mật khẩu root của instance mới được sinh trong bộ nhớ, không đưa vào log/commit; instance đã dừng sau chạy.

## Rà trực quan PDF

Render bằng Poppler: `pdftoppm -scale-to 2600 -png <PDF> <prefix>`. Đã xem toàn bộ từng trang; trang sơ đồ được đối chiếu cả tiêu đề, các vùng thực thể/bảng, đường nối, khóa/lực lượng kết hợp và chú thích cuối trang. [Manifest PDF](pdf_review.json) ghi SHA-256, kích thước trang và ảnh; hai PDF gốc không thay đổi.

| File / trang | Mong đợi | Thực tế | Kết quả / ảnh |
|---|---|---|---|
| ER, trang 1 | Đủ 9 thực thể, quan hệ và thuộc tính; nhãn, ký hiệu khóa và (min,max) đọc được; không bị cắt | Chữ tiếng Việt rõ; đường nối và ký hiệu phân biệt được; chú thích nằm trong trang; không thấy chồng chữ/cắt nội dung | ĐẠT — [er-1.png](pdf/er-1.png) |
| ER, trang 2 | Đọc đủ các đoạn ràng buộc, không mất chữ cuối dòng/trang | Đủ các đoạn từ phạm vi đến nguồn/quy ước, không thấy lỗi glyph/chồng lấn | ĐẠT — [er-2.png](pdf/er-2.png) |
| Quan hệ, trang 1 | Đủ 11 bảng; PK/FK/UQ, tên cột, nhãn đường nối và chú thích rõ | Tên bảng/cột, màu nhãn khóa, đường nối và chú thích dưới cùng đọc được, không cắt trang | ĐẠT — [relational-1.png](pdf/relational-1.png) |
| Quan hệ, trang 2 | Nội dung ràng buộc chung đọc rõ và đủ | Cùng nội dung ràng buộc trang 2 của ER; không thấy lỗi hiển thị | ĐẠT — [relational-2.png](pdf/relational-2.png) |

Chỉ nghiệm thu hiển thị trên màn hình. Không thay thiết kế/ý nghĩa quan hệ, không xác nhận đã in thử A4 hoặc review đầy đủ tính đúng nghiệp vụ ER–SQL.

## Import theo SETUP và audit

Các file chạy nguyên nội dung, bằng PyMySQL thay thao tác click Workbench. Mỗi statement lỗi sẽ dừng; kiểm tra audit trước/sau constraints, không bỏ qua trigger.

| Bước | Mong đợi | Thực tế |
|---|---|---|
| schema.sql | Database trống, tạo đủ 11 bảng | ĐẠT, 11 bảng |
| seed.sql | Nhập đủ dữ liệu giả | ĐẠT, 1.144 dòng |
| audit.sql lần 1 | Cả 10 truy vấn trả 0 dòng | ĐẠT, cả 10 rỗng |
| constraints.sql | Tạo chỉ mục/trigger không lỗi | ĐẠT, 9 trigger |
| audit.sql lần 2 | Cả 10 truy vấn vẫn trả 0 dòng | ĐẠT, cả 10 rỗng |
| queries.sql | Chạy đủ tập kết quả; so expected_results.md | ĐẠT, 11 tập kết quả; doanh thu tháng 10 = 10.500.800, lương bác sĩ = 78.000.000, lương y tá = 65.600.000 |

[integration_results.json](integration_results.json) lưu các tập kết quả SQL và audit. Bộ pytest đối chiếu độc lập Q1/Q2/Q4 bằng oracle từ seed cho tháng 07–10/2026 và tháng không phát sinh 12/2025, kiểm tra lịch sử, ràng buộc ghi và rollback. [pytest.txt](pytest.txt): **72 passed in 11.80s**, gồm 26 test SQL + 46 backend/UI, không skipped, exit code 0.

## Các ca hồ sơ chạy trên cùng DB có trigger

Mỗi nhóm `patients`, `doctors`, `nurses` dùng mã tự sinh mới, CMT giả có số 0 đầu. Cột ảnh dưới đây dẫn một ví dụ; [JSON](integration_results.json) ghi expected/actual của từng nhóm và toàn bộ đường dẫn ảnh. 33 ca hồ sơ đều đạt; thêm health/lịch sử đạt. JSON có 36 entry gồm 33 ca hồ sơ + health + lịch sử + summary pytest; không cộng các entry này vào 72 test pytest.

| Ca, chạy cho cả ba nhóm | Mong đợi | Thực tế / ví dụ bằng chứng |
|---|---|---|
| Thêm | Lưu thành công, mở chi tiết | ĐẠT — [bệnh nhân vừa tạo](browser/patients-created.png) |
| SELECT độc lập | Mã/tên/CMT khớp; giữ số 0 đầu | ĐẠT — dòng SELECT trong JSON cho từng nhóm |
| Reload | Hồ sơ vẫn tồn tại sau tải lại | ĐẠT — [bệnh nhân reload](browser/patients-reloaded.png) |
| Tìm danh sách | Tìm đúng hồ sơ vừa lưu | ĐẠT, kiểm tra link chi tiết theo đúng mã |
| Sửa qua URL chữ thường | Giữ mã chuẩn; sửa địa chỉ lưu được sau reload và SELECT | ĐẠT — [bác sĩ đã sửa](browser/doctors-edited.png) |
| Trùng mã | HTTP 409; thông báo rõ, giữ thông tin nhập | ĐẠT — [trùng mã](browser/patients-duplicate-code.png) |
| Trùng CMT, mã khác | HTTP 409; không tạo bản sao | ĐẠT — [trùng CMT](browser/doctors-duplicate-cmt.png) |
| CMT = abc | HTTP 422; lỗi đúng trường, giữ tên đã nhập | ĐẠT — [lỗi CMT y tá](browser/nurses-invalid-cmt.png) |
| Ngày sinh = 2999-01-01 | HTTP 422; từ chối ngày tương lai | ĐẠT — [ngày sinh sai](browser/patients-future-birth.png) |
| Xóa hồ sơ có lịch sử | BN001/BS001/YT001 đều trả 409, mở lại vẫn 200 | ĐẠT — [bác sĩ bị chặn xóa](browser/doctors-protected.png) |
| Dọn hồ sơ thử | Chỉ xóa mã tự tạo; mở lại 404 | ĐẠT — [dọn hồ sơ y tá](browser/nurses-cleaned.png) |

`/health` và `/health/db` đều 200; [lịch sử BN001](browser/patient-history.png) có các lần khám. Có **37 ảnh browser**: 28 ảnh của đợt thao tác bổ sung (9 × 3 nhóm + lịch sử) và 9 ảnh từ ba test browser pytest. Tất cả là seed giả hoặc hồ sơ giả mới; không lấy dữ liệu bệnh nhân thật.

## Bảo toàn và giới hạn

- Dọn hồ sơ thử qua UI; hash toàn bộ bản ghi của 11 bảng trước/sau giống nhau. Cả audit trước/sau đạt `total=1144`, `matches_expected_counts=true`, mọi findings rỗng.
- `.env` hiện tại được so hash trước/sau, không đổi; app thử nhận cấu hình qua biến môi trường và `PYTHON_DOTENV_DISABLED=1`. Không lưu mật khẩu hoặc nội dung `.env` vào bằng chứng.
- Instance thử và HTTP server đã dừng. Không DROP database, không xóa seed hay thư mục dữ liệu có sẵn. Datadir thử do phiên này tạo được giữ trong `.venv` bị Git bỏ qua, không commit.
- Chưa xác minh UI thao tác Workbench/cài đặt từ clone mạng mới; quy trình import SQL và web đã chạy thật theo cùng thứ tự SETUP. Không gọi đây là nghiệm thu nguyên văn mọi thao tác của hướng dẫn.
- Python 3.11/MySQL 8.4 chưa chạy lại local: môi trường mục tiêu đã có CI riêng được dẫn trong [bàn giao](../../VUONG_WEEK1_HANDOFF.md). Không đổi phiên bản của bằng chứng local thành phiên bản CI.
- Chưa nghiệm thu trên máy Trung/Quyền, điện thoại thật, Firefox/Safari hoặc bản main sau merge. Responsive không chạy lại trong đợt này; bằng chứng viewport cũ giữ nguyên mốc.
- Chưa đăng xác nhận hợp đồng PR #4 hoặc approve/merge PR. Ba trang thống kê vẫn là khung tuần 1; kết quả SQL không có nghĩa UI thống kê đã tích hợp.

## Phản hồi ngoài phạm vi Vương

Không phát hiện lỗi SQL/backend mới trong các ca đã chạy. Quyền/Trung cần review [báo cáo setup](SETUP_FINDINGS.md): cập nhật dòng Draft đã cũ trong SETUP, giữ rõ hai đường importer và điều kiện quyền tạo DB. Báo cáo được chuẩn bị trong PR #7, chưa đăng nhận xét thay thành viên.

## Chạy lại

[run_isolated_acceptance.py](run_isolated_acceptance.py) là script phiên này. Cần source đúng snapshot, dependencies/Chromium trong runtime riêng và **datadir mới** đã khởi tạo bằng binary MySQL với `--no-defaults --initialize-insecure`. Không tái dùng datadir của dịch vụ hoặc datadir phiên cũ; script từ chối thư mục đã có `acceptance-used.json`.

Lệnh phiên đã chạy (từ repo, các đường dẫn `.venv` đều bị Git bỏ qua):

```powershell
$env:PLAYWRIGHT_BROWSERS_PATH = Join-Path (Get-Location) '.venv/week1_acceptance_20261018/browsers'
$env:PYTHONIOENCODING = 'utf-8'
.\.venv\week1_acceptance_20261018\runtime\Scripts\python.exe docs/evidence/vuong_week1_acceptance_2026-10-18/run_isolated_acceptance.py --source .venv/week1_acceptance_20261018/source --datadir .venv/week1_acceptance_20261018/mysql-data --mysqld 'C:/Program Files/MySQL/MySQL Server 8.0/bin/mysqld.exe' --repo . --output docs/evidence/vuong_week1_acceptance_2026-10-18
```

Khi chạy lại phải đổi sang thư mục datadir mới được khởi tạo riêng và thư mục output mới để giữ nguyên bằng chứng phiên này. Không chạy lại lệnh trên nguyên trạng.
