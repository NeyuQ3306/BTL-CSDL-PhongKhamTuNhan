# Bằng chứng tuần 3 — Bước 2, ngày 21/10/2026

**Đạt hồi quy tự động local: 175 passed / 0 failures / 0 errors / 0 skipped**, 55,74 giây theo pytest. SHA source `f4869299c25fdfd0b711597e30b60ab277120f44`, nhánh `vuong/week-3`. Người thực hiện: trợ lý Codex thay mặt Vương. Không phải xác nhận Vương/Trung/Quyền tự thao tác, CI hoặc kiểm tra thủ công Bước 3.

## Môi trường và cách ly

- Python **3.11.9** trong `.venv/week3-runtime`; MySQL Server **8.4.7** từ ZIP riêng trong `.venv/week3-tools/mysql84`; Chromium **156.0.8078.4**, Playwright và thư viện trong [dependencies.txt](dependencies.txt).
- Đúng dòng Python 3.11/MySQL 8.4 mục tiêu; không có khác biệt major/minor cần miễn trừ. [installation.json](installation.json) ghi nguồn tải, SHA256 gói tải, khảo sát ban đầu và lệnh cài. Không cài dịch vụ hoặc sửa runtime hệ thống.
- Runner nguyên bản `tools/vuong_week2_prepare.py` chạy trên bản sao **122 file tracked khớp byte với checkout** tại `.venv/week3-regression-20261021-run2/source`. Không copy `.env`; source và runner không sửa. Cách này giữ nguyên cả `test-artifacts` cũ trong checkout.
- Git trong bản sao tra SHA/nhánh từ repo cha; SHA không phải định danh duy nhất: phải đối chiếu [execution_source_sha256.json](execution_source_sha256.json) và [session.json](session.json). Manifest bao gồm app, templates/static, tests, tools, SQL/oracle, dependencies và cấu hình tracked. Diff source rỗng: [source.diff](source.diff), [ghi chú diff](source.diff.json). Các tài liệu tuần 3 untracked không phải source thực thi.
- Runner tạo datadir mới, chỉ bind `127.0.0.1:56310`, DB `clinic_vuong_week2_prepare_test`. Tên DB giống tuần cũ nhưng thuộc **instance/datadir mới**, không dùng DB cũ. Credential sinh ngẫu nhiên chỉ tồn tại trong bộ nhớ.
- MySQL, browser và oracle Quyền đều bật qua `RUN_MYSQL_TESTS=1`, `RUN_BROWSER_TESTS=1`, `QUYEN_CHECK_WEEK2=1`; thiết lập được xác nhận từ runner nguyên bản và các module tương ứng thực thi trong JUnit.

## Chỉ mục bằng chứng

| File/thư mục | Nội dung |
|---|---|
| [session.json](session.json) | Giờ bắt đầu/kết thúc, executable, source, lệnh thực chạy, thống kê XML, bảo toàn dữ liệu/file |
| [runner-output/junit.xml](runner-output/junit.xml) | 175 testcase, không failure/error/skipped |
| [runner-output/pytest.txt](runner-output/pytest.txt) | Danh sách từng test và kết quả; 175 passed in 55.74s |
| [runner-console.txt](runner-console.txt) | Stdout/stderr của runner, gồm HTTP và kết quả khởi chạy |
| [runner-output/results.json](runner-output/results.json) | Phiên bản server/browser thực chạy, import, audit, bảo toàn seed, 54 khảo sát trang |
| [review.json](review.json) | Đối chiếu độc lập XML, JSON ca và nguồn; điều kiện đạt Bước 2 |
| [acceptance-matrix.csv](acceptance-matrix.csv) | T01–T15 với input/expected/actual, phương thức, người/ngày/SHA và bằng chứng; T16 còn chờ |
| [browser-tests/vuong-acceptance/cases.json](browser-tests/vuong-acceptance/cases.json) | Kết quả T01–T15 và CSRF của đúng run_id `20261021_112820` |
| [browser-tests/vuong-reports/seed-parity.json](browser-tests/vuong-reports/seed-parity.json) | UI/JSON/SQL/oracle qua 5 tháng và 40 bệnh nhân |
| [browser-tests/vuong-reports/edge-parity.json](browser-tests/vuong-reports/edge-parity.json) | Ca biên báo cáo |
| [protected_files_before.json](protected_files_before.json) | Hash bằng chứng untracked tuần 2 và test-artifacts cũ trước chạy |
| [cleanup.json](cleanup.json) | Kết quả dừng MySQL con còn sót, không còn tiến trình riêng/cổng app hoặc DB |
| [setup-attempt1.json](setup-attempt1.json), [setup-issues.json](setup-issues.json) | Lần khởi động Playwright bị kẹt trong sandbox trước khi runner/test bắt đầu; retry đã thành công |
| [run_regression.py](run_regression.py) | Script điều phối đã dùng; bảo vệ source/bằng chứng cũ, xuất kết quả mới |

`runner-output` giữ nguyên tên file/nội dung runner sinh ra. Trường `scope` còn chữ “week-2” và `dependencies` chứa SHA Trung/Quyền cũ là **metadata lịch sử hard-code của runner**, không phải bằng chứng checkout các SHA đó. Source thực chạy là SHA/manifest tuần 3 nêu trên. Đường dẫn/url tạm trong log là nơi chạy lúc đó, hiện app/DB đã dừng. Bằng chứng đã copy sang hồ sơ này để không phụ thuộc venv/datadir.

## Audit và đọc kết quả

- Import: schema → seed → audit → constraints → audit → queries. Hai lượt audit import trả 10 tập kết quả rỗng/lượt (helper yêu cầu rỗng), queries trả 11 tập.
- Audit cuối: **11 bảng, 9 trigger, 1.144 dòng**, `matches_expected_counts=true`, cả **9 nhóm findings rỗng**; `audit.sql` cuối có 10 tập rỗng.
- Runner so sánh SHA256 nội dung từng bảng seed trước/sau suite và sau khảo sát browser: cả hai bằng nhau. Không chỉ so số dòng.
- Cả 54 URL/viewport trả status mong đợi và không tràn ngang toàn trang theo phép đo tự động; gồm 1440/390/320 px. Có tổng 130 ảnh PNG mới từ suite và khảo sát. **Chưa rà ảnh bằng mắt và chưa thực hiện kiểm tra tay Bước 3**.
- `test_quyen_database`: 26 testcase, `test_quyen_week2_reports`: 52 testcase; tất cả đạt. Các module browser, rollback, concurrency, CRUD và regression khác đều có trong JUnit; không lấy con số tuần 2 làm số lượng bắt buộc.
- T01–T15 được ghi “Đạt local — tự động” chỉ theo phạm vi assertions hiện có. T05/T06/T07/T13 có HTTP sửa payload, SQL trực tiếp hoặc yêu cầu đồng thời, không gọi là thao tác tay UI. T08 dùng dữ liệu tháng 9/10 năm 2001; đây là dữ liệu giả mới của suite, không phải tái sử dụng kết quả cũ.

## Sự cố và phần còn chờ

1. Khởi động Playwright bị kẹt trong sandbox trước khi chạy runner: đã lưu metadata, dừng đúng hai Python của phiên và retry bằng quyền thực thi; không phải test sản phẩm thất bại. Các URL tải ban đầu có 403/404 đã được thay bằng endpoint thành công, ghi trong installation.json.
2. Runner kết thúc nhưng còn MySQL con trên Windows: `session.json` ghi đúng `mysql_port_closed_after_run=false` tại thời điểm kiểm tra đầu. Đã xác minh executable/datadir rồi dừng riêng PID 27944 và chờ thoát hoàn toàn; **trạng thái cuối theo cleanup.json** là MySQL/app đóng cổng, 0 MySQL riêng và 0 browser riêng. Không sửa runner trong Bước 2. Đề nghị Bước 4 xem xét cải thiện cleanup cây tiến trình của runner; workaround phiên này đã hoàn tất, không ảnh hưởng kết quả suite.
3. Không có failure/error/skip sản phẩm trong lần chạy hoàn tất. Không khẳng định sản phẩm không còn lỗi ngoài phạm vi kiểm thử.
4. CI **chưa chạy/chưa xác minh**; Bước 3 và Bước 4 chưa thực hiện. T16 **Chờ nhóm chốt máy thứ hai**, chưa chạy.

## Tái hiện

Lệnh điều phối đã dùng (PowerShell, từ gốc repo):

```powershell
& '.venv/week3-runtime/Scripts/python.exe' 'docs/evidence/vuong_week3_regression_20261021/run_regression.py'
```

Lệnh runner/executable/path chính xác có trong `session.json`. Để chạy phiên mới, dùng thư mục evidence và source mirror **mới**, cập nhật `WORK` trong bản sao script cho phiên mới; không chạy đè bằng chứng này. Script chủ động từ chối nếu source mirror đã tồn tại. Không dùng `--serve` trong hồi quy; kiểm tra/dừng cây tiến trình private theo ghi chú cleanup trên Windows. Venv, gói tải và datadir nằm trong `.venv` bị Git bỏ qua; không bàn giao chúng thay cho bằng chứng hoặc dùng chúng làm T16.

[Hồ sơ tuần 3](../../VUONG_WEEK3_ACCEPTANCE.md).
