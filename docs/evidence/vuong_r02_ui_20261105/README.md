# Vương — bộ lọc, bảng và biểu đồ offline R02, 05/11/2026

Nhánh `feat/vuong-analytics-ui`, parent `0bf291687b8e80674531363aa1ea6b32b4dad388`.
Đã fetch: origin/main vẫn `a0d6c300be631cea404672ade548a67c20fea1c1`, nằm trong lịch sử nhánh.
Phạm vi: UI R02 và hồi quy UI R01, không sửa backend/SQL/schema/seed hoặc file chung.

## Triển khai

- Chọn R02 tại `/reports`: kỳ ngày bao gồm ngày cuối dùng adapter lịch hiện có;
  không gửi age_group, ẩn và vô hiệu hóa bộ lọc tuổi. Chuyển lại R01 khôi phục lựa chọn tuổi.
- Một request `/api/analytics/R02?start=...&end=...` cấp cùng payload cho bảng và chart.
  Bảng giữ đủ `ngay`, `so_luot`, `so_benh_nhan_tiep_nhan`, `so_lan_kham` theo thứ tự API.
- Hai cột cạnh nhau theo ngày: lượt tiếp nhận (ngày vào) và lần khám (ngày khám),
  không chồng/cộng hai loại. Số bệnh nhân tiếp nhận là người khác nhau trong ngày,
  giữ ở bảng và chi tiết từng cột, không cộng thành tổng người duy nhất cả kỳ.
- Chỉ vẽ ngày API trả về; không tạo hàng/cột cho ngày thiếu và không nối đường qua khoảng thiếu.
  Trục ngày là danh mục, khoảng cách các cột không biểu diễn độ dài khoảng ngày thiếu;
  ghi rõ giới hạn này trong hướng dẫn cạnh biểu đồ.
- Kỳ thực trả về, số dòng/ngày có bản ghi, đơn vị trục/chú giải và chi tiết ba số đếm có nhãn.
  Chi tiết hỗ trợ hover/focus/Tab; zero vẫn focus được. Bảng là bản đối chiếu đầy đủ.
- Kiểm ngày hợp lệ, trong kỳ, tăng và không trùng; ba số đếm nguyên không âm, không null/chuỗi.
  Không biến response sai thành bảng rỗng hoặc count 0. Giữ hàng all-zero thật từ payload.
- Đổi bộ lọc/báo cáo xóa cả chart/bảng và hủy request cũ; lỗi và response đến muộn không hiện số cũ.
  Có thông báo tải, rỗng, lỗi HTTP/mạng/timeout.
- SVG/CSS/JS là mã dự án, không có thư viện biểu đồ/CDN/font/asset ngoài;
  không phát sinh giấy phép thư viện bên thứ ba hoặc tự gán giấy phép mới cho repo.

## Kiểm chứng thực chạy

Windows/Python 3.14.6, pytest 8.4.2, Playwright 1.64.1 với Chrome cài trên máy.
API Flask/validation/serializer thật; SQL service stub bằng oracle seed cho R01 và R02.
Không chạy hoặc ghi MySQL, không nghiệm thu UI/API/SQL tích hợp hoặc laptop Quyền.

```powershell
$env:RUN_BROWSER_TESTS='1'
$env:BROWSER_CHANNEL='chrome'
$env:RUN_MYSQL_TESTS='0'
& '.venv\Scripts\python.exe' -m pytest tests/test_vuong_analytics_ui.py tests/test_vuong_r02_ui.py tests/test_report_shells.py tests/test_trung_analytics_backend.py -q -x --junitxml=test-artifacts/vuong-analytics-ui/r02-local.xml
```

**86 passed, 12 skipped**: 36 browser checks (19 R01 + 17 R02),
9 report hub/dispatch, 41 backend unit; 12 MySQL checks skipped.
Chrome và Flask loopback chạy ngoài sandbox để mở browser/server.

- R02 đối chiếu mọi ô của 83 dòng và 166 cột biểu đồ với oracle payload;
  request đúng endpoint/chỉ start/end và duy nhất một request cho bảng/chart.
- Fixture 01/07 và 03/07 không sinh ngày 02/07; đếm 2 lượt/5 lần khám/1 người
  hiển thị tách biệt. Kiểm tỷ lệ chiều cao 2:5, cột cạnh nhau cùng baseline,
  zero/all-zero không có chiều cao nhưng có chi tiết qua bàn phím.
- Kỳ một ngày nhuận đổi end đúng một lần; kỳ rỗng không trở thành zero.
  Đổi ngày và chuyển R01/R02 xóa view cũ, R01 giữ tuổi/đủ sáu cột và chart cũ vẫn đúng.
- Lỗi 400/404/500/503, mất mạng, timeout 20 giây (đồng hồ browser giả lập),
  response đến muộn sau đổi báo cáo đều xử lý đúng.
- Response null/âm/chuỗi ở count, ngày trùng/đảo thứ tự/sai lịch/ngoài kỳ,
  kỳ sai và report_id sai bị từ chối; không có bảng/chart gây hiểu nhầm.
- Chặn mọi request ngoài loopback, reload và render thành công ở 1440/390/320 px;
  không có request ngoài. Browser offline sau khi tải vẫn focus/xem chi tiết được.
  API cục bộ vẫn cần hoạt động để tải dữ liệu mới.
- Đã xem ảnh `r02-chart.png` và mobile `r02-320.png`; kiểm layout tự động cả 1440/390/320,
  không tràn trang, chart và bảng dài cuộn ngang trong vùng riêng.

Hồi quy không DB:

```powershell
$env:RUN_BROWSER_TESTS='0'
$env:RUN_MYSQL_TESTS='0'
& '.venv\Scripts\python.exe' -m pytest tests week3_checks --ignore=tests/test_quyen_database.py --ignore=tests/test_quyen_week2_reports.py --basetemp=.codex-qa/vuong-r02-final-pytest -q --junitxml=test-artifacts/vuong-analytics-ui/r02-regression.xml
```

**153 passed, 119 skipped**. Hai module SQL cũ bị loại rõ ràng vì luôn mở DB,
không theo cờ tắt MySQL. Không cộng chồng test với lượt tập trung;
không nhận Q1–Q4/MySQL end-to-end đã đạt.
`node --check clinic_app/static/analytics.js` và `git diff --check` đạt.
JUnit và ảnh ở `test-artifacts/vuong-analytics-ui/` (gitignored).
Source đã thử được định danh SHA256 ở `source-sha256.json` cạnh tài liệu này.

## Còn lại

UI R01/R02 đã có bản cục bộ; chưa push/PR/review/merge, chưa nghiệm thu MySQL/nhóm.
R03–R07, đối chiếu DB thử riêng, DOCX/PPTX và demo vẫn còn theo kế hoạch.
Bước tiếp theo: R03 với kỳ ngày, bảng và biểu đồ thanh ngang số lần khám;
giữ bác sĩ 0 hoạt động và số đợt/bệnh nhân riêng, không diễn giải thành chất lượng bác sĩ.
