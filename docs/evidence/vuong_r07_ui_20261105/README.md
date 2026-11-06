# R07 và kiểm tổng thể UI R01–R07, 05/11/2026

Nhánh `feat/vuong-analytics-ui`, parent `34406f5c3ad63239cea58fc88237cc3fefc21f07`.
Main đã fetch vẫn `a0d6c300`. R05 commit `eeb7dbc`, R06 commit `34406f5`.

## Điều phối và review

- `ui_implementer`: sở hữu ba tệp UI; triển khai tuần tự R05, R06, R07, giữ R01–R04.
- `ui_tester`: sở hữu fixture và ba bộ test mới; viết và chạy độc lập song song với UI.
- `contract_reviewer`: chỉ đọc; đối chiếu API/SQL/diff/tests của từng báo cáo, không còn blocker.
  Đề nghị làm rõ nhãn cờ R06 đã áp dụng. R07 thêm thông báo không có mẫu và guard scale/tick;
  đây là cải thiện/hardening, không nhận lỗi overflow đã tái hiện (nghi vấn ban đầu đã rút lại).
- Orchestrator kiểm Git/RULES/hợp đồng, chia quyền tệp để không xung đột, đọc diff/xem ảnh,
  chạy hồi quy/tổng kiểm, ghi bằng chứng/kế hoạch và commit từng báo cáo. Không có push/PR/merge.
  Review subagent không thay review Trung/Quyền hay nghiệm thu nhóm.

## R07 thực hiện

- Kỳ ngày, bảng đủ 9 cột và cột chồng trung bình tiền khám/thuốc từ cùng response.rows.
- Giữ nguyên 5 chuỗi tiền hai chữ số thập phân/NULL trong bảng, title, chi tiết và data-money;
  không đi qua Number/Intl khi hiển thị bảng. Number chỉ phục vụ hình học hữu hạn.
- Không tính lại tb_tong hoặc đòi tổng thành phần bằng tb_tong: chênh làm tròn 0,01 hợp lệ.
- Nhóm so_dot_tinh=0 giữ hàng/NULL/nhãn, không có money segment; mẫu dương với tiền0 thật
  vẫn có hai segment cao0 có thể focus. Không có mẫu và rows rỗng có thông báo phù hợp.
- Chi tiết giữ số mẫu/đợt loại/tb_tong/min/max; kỳ chọn theo ngày khỏi, chi phí toàn đợt,
  không coi là báo giá hoặc doanh thu Q4. Text an toàn, hover/focus/Tab, asset cục bộ.
- Không đổi backend/SQL/schema/seed/README/requirements/workflow; không thêm thư viện/CDN
  hoặc giấy phép bên thứ ba. Chỉ desktop 1440/1280, không kiểm điện thoại.

## Kiểm chứng thực chạy

Windows/Python 3.14.6, pytest 8.4.2, Playwright 1.64.1, Chrome cài trên máy.
API Flask/validation/serializer thật, **SQL service stub** bằng oracle và fixture biên.
Không chạy/ghi MySQL; không nhận CI hoặc stub thành nghiệm thu DB/laptop Quyền/nhóm.

Kiểm riêng độc lập: R05 **20 passed**, R06 **26 passed**, R07 **21 passed** (không skipped/failed).
Các lượt riêng không cộng vào lượt tổng thể. JUnit `r05-local.xml/r06-local.xml/r07-local.xml`.
R06 từng sửa helper inner_text trên SVG; R07 từng sửa kỳ vọng selector/thông báo quá cụ thể;
đã chạy lại đạt, không ghi các lỗi helper đó thành lỗi sản phẩm.

```powershell
$env:RUN_BROWSER_TESTS='1'; $env:BROWSER_CHANNEL='chrome'; $env:RUN_MYSQL_TESTS='0'
& '.venv\Scripts\python.exe' -m pytest tests/test_vuong_analytics_ui.py tests/test_vuong_r02_ui.py tests/test_vuong_r03_ui.py tests/test_vuong_r04_ui.py tests/test_vuong_r05_ui.py tests/test_vuong_r06_ui.py tests/test_vuong_r07_ui.py tests/test_report_shells.py tests/test_trung_analytics_backend.py -q -x --junitxml=test-artifacts/vuong-analytics-ui/r01-r07-final.xml
```

**185 passed, 12 skipped**, 0 failed/errors, 179,32 giây: 135 desktop browser checks
(R01–R07), 9 hub/dispatch và 41 backend unit; 12 MySQL skipped.

Kiểm gồm mọi ô/thứ tự và segment với oracle payload; một request cấp hai view,
đổi bộ lọc/báo cáo, ngày biên, threshold, nhóm0/NULL/rỗng, lỗi HTTP/mạng/timeout/stale,
chuột/bàn phím, text an toàn, chặn mọi request ngoài loopback và offline sau tải.
R07 kiểm tiền lớn hơn giới hạn integer chính xác JS, component-rounding0,01,
tiền thật0, không có mẫu, 400 chữ số không thể vẽ và biên gần Number.MAX_VALUE hữu hạn.
Nguồn chart R05/R06 là chart_groups; R06 giữ4groups kể cả emptyrows, phone chỉ ở bảng.
Đã xem ảnh chart R05/R06/R07; layout desktop tự động1440/1280 đạt.
Ảnh/JUnit cục bộ ở `test-artifacts/vuong-analytics-ui/` (gitignored).

```powershell
$env:RUN_BROWSER_TESTS='0'; $env:RUN_MYSQL_TESTS='0'
& '.venv\Scripts\python.exe' -m pytest tests week3_checks --ignore=tests/test_quyen_database.py --ignore=tests/test_quyen_week2_reports.py --basetemp=.codex-qa/vuong-r01-r07-final-pytest -q --junitxml=test-artifacts/vuong-analytics-ui/r01-r07-regression.xml
```

**153 passed, 218 skipped**, 0 failed/errors. Loại rõ hai module SQL cũ luôn mở DB,
không theo cờ tắt MySQL. Không cộng chồng với kiểm tổng thể và không nhận Q1–Q4/MySQL
end-to-end đã đạt. Node syntax/diff checks đạt; source SHA256 ở `source-sha256.json`.

R01–R07 có UI cục bộ; còn đối chiếu UI/API/SQL trên DB thử riêng, review Trung/Quyền,
tích hợp, DOCX/PPTX/demo và nghiệm thu nhóm. Không đóng issue #3, không push/tạo PR/merge.
