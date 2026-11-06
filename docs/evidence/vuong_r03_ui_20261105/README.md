# Vương — bộ lọc, bảng và biểu đồ offline R03, 05/11/2026

Nhánh `feat/vuong-analytics-ui`, parent `555db90d22cce764780e9f4125639952df6cf48b`.
Đã fetch: origin/main vẫn `a0d6c300be631cea404672ade548a67c20fea1c1`, nằm trong lịch sử nhánh.
Phạm vi: UI R03, kiểm thử và bằng chứng riêng; không sửa backend/SQL/schema/seed hoặc file chung.

## Triển khai

- Chọn R03 tại `/reports`: dùng kỳ ngày bao gồm ngày cuối và adapter lịch hiện có.
  Ẩn/vô hiệu hóa bộ lọc tuổi, chỉ gửi start/end vào endpoint R03.
- Một response API cấp bảng sáu cột `ma_bac_si`, `ho_ten`, `chuyen_mon`,
  `so_lan_kham`, `so_dot`, `so_benh_nhan` và biểu đồ thanh ngang.
- Chiều dài thanh là số lần khám, không dùng số đợt hoặc bệnh nhân để vẽ thay.
  Giữ nguyên thứ tự API, nhận diện theo mã bác sĩ, không gộp hai người trùng tên.
  Hợp đồng SQL sắp lần khám giảm, mã tăng khi bằng nhau; UI không tự tính/sắp lại nghiệp vụ.
- Giữ bác sĩ có 0 hoạt động: hàng, nhãn, số 0 và chi tiết vẫn có; thanh có chiều dài 0.
  Kỳ toàn zero khác tập không có bác sĩ trả về. Không biến null/lỗi thành zero.
- Nhãn kỳ thực trả về, số bác sĩ/dòng nguồn, đơn vị, trục và chi tiết lần khám/đợt/bệnh nhân riêng.
  Không cộng bệnh nhân giữa bác sĩ thành tổng người duy nhất và không xếp hạng chất lượng.
- Hover/focus/Tab xem tên đầy đủ, chuyên môn và ba số đếm; tên dài rút gọn ở nhãn SVG,
  giữ nguyên trong title/chi tiết/bảng, dùng text an toàn. Bảng giữ đầy đủ dữ liệu đối chiếu.
- Đổi kỳ hoặc báo cáo xóa/ẩn cả bảng/chart và hủy request cũ; xử lý rỗng/lỗi HTTP/mạng/timeout.
- SVG/CSS/JS của dự án, không thư viện/CDN/font/asset ngoài;
  không phát sinh giấy phép thư viện bên thứ ba hoặc tự gán giấy phép mới cho repository.

## Kiểm chứng thực chạy

Windows/Python 3.14.6, pytest 8.4.2, Playwright 1.64.1, Chrome cài trên máy.
API Flask/validation/serializer thật; SQL service stub bằng oracle seed.
Fixture R03 sắp oracle theo thứ tự hợp đồng, kỳ ngoài mặc định dùng dữ liệu zero mô phỏng;
đây không phải kết quả truy vấn MySQL thực. Không kết nối/ghi DB trong phiên.

```powershell
$env:RUN_BROWSER_TESTS='1'
$env:BROWSER_CHANNEL='chrome'
$env:RUN_MYSQL_TESTS='0'
& '.venv\Scripts\python.exe' -m pytest tests/test_vuong_analytics_ui.py tests/test_vuong_r02_ui.py tests/test_vuong_r03_ui.py tests/test_report_shells.py tests/test_trung_analytics_backend.py -q -x --junitxml=test-artifacts/vuong-analytics-ui/r03-local.xml
```

**101 passed, 12 skipped**: 51 browser checks (19 R01 + 17 R02 + 15 R03),
9 hub/dispatch, 41 backend unit; 12 MySQL checks skipped.
Chrome/Flask loopback chạy ngoài sandbox để mở browser/server.

- Đối chiếu mọi ô 10 dòng R03 và 10 thanh với fixture oracle; một request đúng endpoint,
  chỉ start/end dù R01 trước đó có chọn tuổi. Đổi kỳ ngày nhuận chuyển end đúng một lần.
- Kỳ mô phỏng không hoạt động giữ đủ 10 bác sĩ với ba count zero, có chart thay vì empty;
  fixture trả rows=[] hiển thị empty riêng, không tạo bác sĩ giả.
- Fixture hai bác sĩ cùng tên, bằng số lần khám giữ hai mã và thứ tự; tên rất dài/HTML
  không tạo markup thực thi. Chi tiết phân biệt 6 lần/3 đợt/2 người.
- Tỷ lệ chiều dài thanh 6:3 = 2:1, cùng gốc x, các thanh nằm ngang riêng hàng.
  Zero có chiều dài 0 và vẫn focus được; Tab đến bác sĩ kế tiếp.
- Chuyển R03/R02/R01/R03 thay đúng bảng/description/chart, giữ tuổi R01,
  xóa thanh cũ và không gửi tuổi vào R02/R03. Hồi quy R01/R02 trong cùng lượt đạt.
- 400/404/500/503, lỗi mạng, timeout 20 giây bằng đồng hồ giả lập và response đến muộn
  sau đổi báo cáo không hiển thị số cũ. Count null/âm/chuỗi, mã trùng, tên null,
  kỳ sai và report_id sai bị từ chối, không trở thành dữ liệu zero.
- Chặn mọi request ngoài loopback, reload/tải ở 1440/390/320 px thành công;
  không request ngoài. Browser offline sau tải vẫn focus/xem chi tiết được;
  API cục bộ vẫn cần hoạt động để tải dữ liệu mới.
- Đã xem ảnh `r03-chart.png` và `r03-320.png`; layout tự động cả 1440/390/320 đạt,
  không tràn trang; chart/bảng cuộn ngang trong vùng riêng trên màn hình hẹp.

Hồi quy không DB:

```powershell
$env:RUN_BROWSER_TESTS='0'
$env:RUN_MYSQL_TESTS='0'
& '.venv\Scripts\python.exe' -m pytest tests week3_checks --ignore=tests/test_quyen_database.py --ignore=tests/test_quyen_week2_reports.py --basetemp=.codex-qa/vuong-r03-final-pytest -q --junitxml=test-artifacts/vuong-analytics-ui/r03-regression.xml
```

**153 passed, 134 skipped**; loại rõ hai module SQL cũ luôn mở DB, không theo cờ tắt MySQL.
Không cộng chồng với lượt tập trung, không nhận hồi quy Q1–Q4/MySQL end-to-end đã đạt.
`node --check clinic_app/static/analytics.js` và `git diff --check` đạt.
JUnit và ảnh ở `test-artifacts/vuong-analytics-ui/` (gitignored);
SHA256 source đã thử ở `source-sha256.json` cạnh tài liệu này.

## Còn lại

R01–R03 có UI cục bộ, chưa push/PR/review/merge, chưa nghiệm thu MySQL hoặc nhóm/laptop Quyền.
R04–R07, đối chiếu DB thử riêng, DOCX/PPTX/demo còn theo kế hoạch.
Tiếp theo: R04 với kỳ ngày, bảng và biểu đồ thanh ngang số đơn có thuốc;
giữ lượng kê/đơn vị riêng từng thuốc, không gộp khác đơn vị hoặc suy ra lượng cần nhập.
