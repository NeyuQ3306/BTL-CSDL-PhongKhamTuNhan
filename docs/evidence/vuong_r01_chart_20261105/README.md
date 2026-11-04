# Vương — biểu đồ offline R01, 05/11/2026

Nhánh `feat/vuong-analytics-ui`, bắt đầu từ commit UI `20190467219a2d94e3ce0d5c47d5f116c3b97fba`,
nền tích hợp main `a0d6c300be631cea404672ade548a67c20fea1c1`.
Đã fetch: origin/main vẫn tại a0d6c30, không cần đồng bộ thêm.
Phạm vi phiên này: biểu đồ R01, kiểm thử và bằng chứng riêng của Vương.

## Kết quả triển khai

- Cột chồng theo mã bệnh; series nhóm tuổi, chiều cao `so_dot`.
  Giữ thứ tự bệnh theo lần xuất hiện trong response, không gộp theo tên bệnh.
- Bảng và biểu đồ dùng cùng payload đã validate sau **một** request R01;
  không gọi endpoint hoặc bộ số khác. Không cộng DISTINCT bệnh nhân.
- Chú giải màu ổn định, chỉ liệt kê nhóm có mặt. Nhóm -1 có nhãn riêng
  “Ngày sinh không hợp lệ (nhóm riêng)”, không đưa vào nhóm trẻ em.
- Trục ghi Bệnh/Số đợt, hiển thị kỳ thực trả về, số dòng nguồn và đơn vị.
  Chi tiết có mã/tên bệnh, nhóm, số đợt và bệnh nhân của đúng dòng;
  xem bằng hover hoặc focus/Tab, có nội dung text tương đương trong bảng.
- Không tạo nhóm thiếu thành hàng 0; số 0 có chiều cao 0. Tập rỗng có thông báo riêng.
  Đổi lọc/loading/error/stale response xóa/ẩn cả bảng và biểu đồ.
- Từ chối response có count null/âm/chuỗi, trùng mã bệnh–nhóm tuổi hoặc dòng lệch nhóm đã chọn.
- SVG/CSS/JavaScript tự viết trong source dự án; không dùng thư viện biểu đồ,
  CDN, font hay asset bên ngoài. Không phát sinh giấy phép thư viện bên thứ ba cần đính kèm;
  không tự gán giấy phép mới cho repository.
- Không sửa backend, SQL/schema/seed, README, requirements, workflow hay tài liệu tích hợp chung.

## Kiểm chứng thực chạy

Windows/Python 3.14.6, pytest 8.4.2, Playwright 1.64.1, Chrome cài trên máy.
API Flask và serializer/validation thật; SQL service được stub bằng oracle seed.
Không kết nối/ghi MySQL. Không phải nghiệm thu UI/API/SQL trên DB thật hoặc laptop Quyền.

```powershell
$env:RUN_BROWSER_TESTS='1'
$env:BROWSER_CHANNEL='chrome'
$env:RUN_MYSQL_TESTS='0'
& '.venv\Scripts\python.exe' -m pytest tests/test_vuong_analytics_ui.py tests/test_report_shells.py tests/test_trung_analytics_backend.py -q -x --junitxml=test-artifacts/vuong-analytics-ui/chart-local.xml
```

**69 passed, 12 skipped**: 19 browser checks, 9 report hub/dispatch và 41 backend unit.
12 MySQL checks skipped. Chrome/Flask loopback chạy ngoài sandbox để mở browser/server.

- Đối chiếu mọi segment với số đợt/bệnh nhân/mã bệnh/nhóm tuổi của 29 dòng seed;
  bảng vẫn khớp đủ sáu cột/thứ tự. Xác nhận một request cho mỗi submit và cả hai view
  cập nhật theo mọi nhóm tuổi; submit lặp không cộng ngày lần hai.
- Kiểm hình học cột chồng 3:2; hai mã bệnh có cùng tên không bị gộp.
  Fixture riêng cho nhóm -1, tên dài, HTML an toàn, hàng 0/all-zero;
  focus được cả segment chiều cao 0 và xem đúng chi tiết. Thiếu/NULL không biến thành 0.
- Kiểm lỗi 400/404/500/503/mạng, response sai/trùng/lệch nhóm và đến muộn;
  không còn segment cũ sau lỗi/đổi lọc. Ca ngày biên của adapter tiếp tục đạt.
- Chặn mọi request ngoài loopback, reload và render cả chart/bảng thành công;
  sau đó đặt browser offline và vẫn focus/xem chi tiết được. Không có request ngoài.
  Điều này chứng minh tài nguyên biểu đồ dùng offline; tải dữ liệu mới vẫn cần API cục bộ.
- Ảnh 1440/390/320 px đã xem: trang không tràn, chart/bảng cuộn trong vùng riêng.
  Ảnh nằm ở `test-artifacts/vuong-analytics-ui/r01-desktop.png`, `r01-390.png`,
  `r01-320.png`, `r01-chart.png` (gitignored).

Hồi quy không DB sau thay đổi cuối:

```powershell
$env:RUN_BROWSER_TESTS='0'
$env:RUN_MYSQL_TESTS='0'
& '.venv\Scripts\python.exe' -m pytest tests week3_checks --ignore=tests/test_quyen_database.py --ignore=tests/test_quyen_week2_reports.py --basetemp=.codex-qa/vuong-r01-chart-final-pytest -q --junitxml=test-artifacts/vuong-analytics-ui/chart-regression.xml
```

**153 passed, 102 skipped**. Loại rõ hai module SQL cũ luôn mở DB, không theo cờ tắt MySQL.
Không cộng chồng với lượt kiểm tập trung; không nhận hồi quy Q1–Q4/MySQL end-to-end đạt.
`node --check clinic_app/static/analytics.js` và `git diff --check` đạt.
SHA256 source đã thử ở `source-sha256.json` cạnh tài liệu này.

Subagent rà diff đọc-only không thấy lỗi chặn; hai đề nghị bổ sung test (focus zero,
response lệch nhóm) đã được kiểm đạt. Đây không thay thế review của Trung/Quyền theo RULES.

## Còn lại

R01 đã có bảng/biểu đồ trong source cục bộ; chưa push/PR/review/merge hoặc nghiệm thu nhóm.
Giao diện R02–R07, đối chiếu UI/API/SQL trên DB thử riêng, DOCX/PPTX và demo còn tiếp tục.
Bước tiếp theo đề xuất: UI R02 gồm kỳ ngày, bảng và biểu đồ cột lượt/lần khám từ cùng response;
giữ số bệnh nhân tiếp nhận trong bảng/chi tiết, không chèn ngày thiếu thành số 0.
