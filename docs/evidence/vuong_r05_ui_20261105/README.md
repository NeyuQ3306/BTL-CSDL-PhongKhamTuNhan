# R05 — UI đợt tái mắc, 05/11/2026

Nhánh `feat/vuong-analytics-ui`, parent `e13a9e6612b60b95fc498da14891c582f03ad472`.
Orchestrator đã fetch, main vẫn `a0d6c300`; không sửa backend/SQL/schema/seed/file chung.

- `ui_implementer` triển khai bộ lọc kỳ ngày, bảng đủ 8 cột và SVG offline từ **chart_groups**
  của cùng response API, giữ thứ tự nhóm. Không đếm lại bệnh nhân hoặc lịch sử bằng JS.
- `ui_tester` viết/chạy bộ kiểm độc lập. `contract_reviewer` đối chiếu API/SQL/diff/tests,
  không thấy lỗi chặn. Orchestrator đọc diff, chạy hồi quy liên quan và xem ảnh chart.
  Review subagent không thay review Trung/Quyền hoặc nghiệm thu nhóm.
- Nhãn phân biệt số đợt/số người; thiếu lịch sử không chứng minh chưa từng mắc.
  Bảng/chart cùng xóa khi đổi lọc/lỗi/response cũ; text an toàn, hover/focus/Tab.
  SVG/CSS/JS dự án, không CDN/thư viện biểu đồ/font ngoài hoặc giấy phép bên thứ ba mới.

Windows/Python 3.14.6/pytest 8.4.2/Playwright 1.64.1/Chrome, chỉ desktop 1440/1280.
API Flask/validation/serializer thật, **SQL service stub** bằng oracle seed; không chạy MySQL.

```powershell
$env:RUN_BROWSER_TESTS='1'; $env:BROWSER_CHANNEL='chrome'; $env:RUN_MYSQL_TESTS='0'
& '.venv\Scripts\python.exe' -m pytest tests/test_vuong_r05_ui.py -q -x --junitxml=test-artifacts/vuong-analytics-ui/r05-local.xml
```

**20 passed**, không failed/skipped: đủ 6 dòng/8 cột seed và các nhóm chart; một request,
thứ tự nhóm đảo có chủ đích vẫn giữ, cùng bệnh nhân nhiều đợt, kỳ/ngày nhuận, rỗng,
HTML/tên dài, bàn phím/offline, malformed rows/groups, lỗi HTTP/mạng/timeout và response cũ.
Không kiểm điện thoại. Ảnh/JUnit ở `test-artifacts/vuong-analytics-ui/r05-*` (gitignored).

Hồi quy liên quan do orchestrator chạy: bốn ca seed/switch R01–R04 cùng
`tests/test_report_shells.py tests/test_trung_analytics_backend.py`:
**54 passed, 12 skipped**, JUnit `r05-related.xml`. Không cộng chồng với lượt tập trung;
12 MySQL checks skipped. Node syntax và git diff --check đạt.
SHA256 source đã thử: `source-sha256.json` cạnh tài liệu.

Chưa push/PR/merge hoặc nghiệm thu MySQL/laptop Quyền/nhóm. Tiếp tục R06, R07.
