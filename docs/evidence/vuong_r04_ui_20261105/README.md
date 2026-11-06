# Vương — UI R04 và rút gọn kế hoạch, 05/11/2026

Nhánh `feat/vuong-analytics-ui`, parent `0b11ad751e70db695c41bb3565036500dc668c4a`.
Đã fetch; origin/main vẫn `a0d6c300be631cea404672ade548a67c20fea1c1`, nằm trong lịch sử nhánh.

## Thay đổi

- R04 tại `/reports`: bộ lọc kỳ ngày, bảng đủ `ma_thuoc/ten_thuoc/don_vi_tinh/so_don/tong_so_luong`
  và biểu đồ thanh ngang cùng một response. Chỉ gửi start/end, không gửi tuổi.
- Thanh vẽ **số đơn có thuốc**; tổng lượng kê và đơn vị giữ riêng từng thuốc trong bảng/chi tiết.
  Không cộng lượng khác đơn vị, không suy ra lượng cần nhập, không coi lượng kê là đã bán/đã uống.
- Giữ mã/thứ tự API, hai thuốc trùng tên vẫn riêng. Rỗng, zero và dữ liệu lỗi khác nhau;
  đổi bộ lọc/báo cáo hoặc lỗi/response cũ đều xóa/ẩn cả hai view. Có hover/focus/Tab.
- R03/R04 dùng chung renderer thanh ngang; R03 vẫn giữ bác sĩ zero và đúng đơn vị lần khám.
- SVG/CSS/JS của dự án, không CDN/thư viện/font/asset ngoài hoặc giấy phép bên thứ ba mới.
  Không sửa backend, SQL/schema/seed, README, requirements, workflow hay tài liệu tích hợp chung.
- Theo yêu cầu người dùng: các ca UI R01–R04 chỉ dùng desktop **1440/1280 px**;
  không chạy kiểm điện thoại. Không xóa CSS responsive cũ.
- `D:\BTL\CSDL\plan_vuong.md` được viết lại từ 219 còn 54 dòng: bỏ lịch sử review,
  trạng thái/việc tiếp theo cũ, log và câu lệnh lặp; giữ trạng thái hiện hành, hợp đồng cần dùng,
  R05–R07, kiểm DB/review/nghiệm thu, DOCX/demo/hạn nộp và liên kết bằng chứng.

## Kiểm chứng thực chạy

Windows/Python 3.14.6, pytest 8.4.2, Playwright 1.64.1, Chrome cài trên máy.
API Flask/validation/serializer thật, SQL service stub bằng oracle; R04 fixture sắp theo hợp đồng.
Không kết nối/ghi MySQL, không nghiệm thu UI/API/SQL trên DB thật hoặc laptop Quyền.

```powershell
$env:RUN_BROWSER_TESTS='1'
$env:BROWSER_CHANNEL='chrome'
$env:RUN_MYSQL_TESTS='0'
& '.venv\Scripts\python.exe' -m pytest tests/test_vuong_analytics_ui.py tests/test_vuong_r02_ui.py tests/test_vuong_r03_ui.py tests/test_vuong_r04_ui.py tests/test_report_shells.py tests/test_trung_analytics_backend.py -q -x --junitxml=test-artifacts/vuong-analytics-ui/r04-local.xml
```

**118 passed, 12 skipped**: 68 desktop browser checks (19 R01 + 17 R02 + 15 R03 + 17 R04),
9 hub/dispatch, 41 backend unit; 12 MySQL skipped. Chrome/Flask loopback chạy ngoài sandbox.

- Đối chiếu mọi ô 29 dòng/29 thanh R04; một request đúng endpoint và chỉ start/end.
  Đổi kỳ ngày nhuận, rows rỗng, chuyển R04/R03/R01/R02/R04 đúng cột/description/chart/tuổi.
- Fixture 6 đơn/12 Viên và 3 đơn/999 Chai cho chiều dài thanh 2:1 theo **đơn**,
  không theo lượng. Giữ khác đơn vị, thuốc trùng tên khác mã, thứ tự hòa, zero/all-zero.
  Tên dài/HTML không tạo markup thực thi; chi tiết chuột/bàn phím giữ lượng và đơn vị.
- HTTP 400/404/500/503, mất mạng, timeout 20 giây bằng đồng hồ giả lập, response đến muộn;
  null/âm/chuỗi ở count hoặc lượng, đơn vị/tên null, mã trùng, kỳ/report sai đều xử lý đúng.
- Chặn request ngoài loopback, reload/render tại 1440/1280 px đạt, không có request ngoài;
  offline sau tải vẫn xem chi tiết. API cục bộ vẫn cần để lấy dữ liệu mới.
- Không tràn trang ở hai độ rộng desktop; đã xem ảnh `r04-chart.png`.
  JUnit và ảnh `r04-desktop.png/r04-chart.png/r04-1440.png/r04-1280.png` ở
  `test-artifacts/vuong-analytics-ui/` (gitignored). Không chụp/kiểm điện thoại trong phiên.

Hồi quy không DB, không cộng chồng với lượt tập trung:

```powershell
$env:RUN_BROWSER_TESTS='0'
$env:RUN_MYSQL_TESTS='0'
& '.venv\Scripts\python.exe' -m pytest tests week3_checks --ignore=tests/test_quyen_database.py --ignore=tests/test_quyen_week2_reports.py --basetemp=.codex-qa/vuong-r04-final-pytest -q --junitxml=test-artifacts/vuong-analytics-ui/r04-regression.xml
```

**153 passed, 151 skipped**; hai module SQL cũ bị loại rõ ràng vì luôn mở DB.
Không nhận Q1–Q4/MySQL end-to-end đã đạt. Node syntax và git diff --check đạt.
SHA256 source đã thử ở `source-sha256.json` cạnh tài liệu này.

R01–R04 có UI cục bộ; chưa push/PR/review/merge, chưa nghiệm thu MySQL hoặc nhóm.
Tiếp theo R05: bảng hồ sơ và biểu đồ theo `chart_groups` cùng response;
phân biệt số đợt tái mắc với số bệnh nhân, không suy từ thiếu lịch sử thành chưa từng mắc.
