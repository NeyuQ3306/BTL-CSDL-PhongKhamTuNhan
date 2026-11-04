# R06 — UI rà soát đợt điều trị, 05/11/2026

Nhánh `feat/vuong-analytics-ui`, parent `eeb7dbca476a1404f044b6e9efa789a09f9de175`.
`ui_implementer` triển khai; `ui_tester` viết/chạy kiểm độc lập; `contract_reviewer` đối chiếu
API/SQL/source/tests, không thấy blocker. Góp ý nhãn cờ đã làm rõ 1=chưa khám/0=đã có khám.
Orchestrator đọc diff, xem chart, chạy hồi quy liên quan và commit. Không thay review nhóm.

- Bộ lọc riêng as_of/threshold; chỉ gửi hai tham số, không cộng ngày. Kỳ/tuổi ẩn và disabled.
- Bảng đủ 13 cột, last-exam NULL là “Chưa có lần khám”, giữ cờ đi kèm và thứ tự API.
- Biểu đồ từ cùng response.chart_groups, luôn đủ bốn nhóm kể cả zero và rows=[];
  dùng chung renderer với R05, không tự tổng hợp nghiệp vụ hoặc đưa điện thoại lên biểu đồ.
- Không diễn giải trễ hẹn/bỏ điều trị. SVG/CSS/JS dự án, offline, không asset/CDN/thư viện ngoài.
  Không sửa backend/SQL/schema/seed/file chung. Chỉ desktop 1440/1280, không điện thoại.

Windows/Python 3.14.6/pytest 8.4.2/Playwright 1.64.1/Chrome. API Flask/serializer/validation thật,
SQL service stub; fixture ngoài mặc định là emptyrows/fourzeros mô phỏng, không phải SQL thực.

```powershell
$env:RUN_BROWSER_TESTS='1'; $env:BROWSER_CHANNEL='chrome'; $env:RUN_MYSQL_TESTS='0'
& '.venv\Scripts\python.exe' -m pytest tests/test_vuong_r06_ui.py -q -x --junitxml=test-artifacts/vuong-analytics-ui/r06-local.xml
```

**26 passed**, không skipped/failed: 19 dòng/13 cột, NULL/flag/phone-only-table, đủ4groups,
rows rỗng vẫn4zero, as_of9999-12-31 trực tiếp, threshold0/36500 và sai/ngày sai, đổi bộ lọc/báo cáo,
không bị native validation của kỳ ẩn chặn, malformed response, HTTP/mạng/timeout/stale/offline/bàn phím.
Lượt đầu dừng do test helper gọi inner_text trên SVG; đã sửa thành text_content rồi chạy lại đạt.

Hồi quy root chạy R05 đầy đủ + bốn seed/switch R01–R04 + hub/backend unit:
**74 passed, 12 skipped** (MySQL), JUnit `test-artifacts/vuong-analytics-ui/r06-related.xml`.
Không cộng chồng với lượt tập trung. Ảnh/JUnit R06 ở cùng thư mục gitignored; chart đã xem.
Node syntax và git diff --check đạt. Source SHA256 ở `source-sha256.json`.

Chưa push/PR/merge, chưa chạy/ghi hoặc nghiệm thu MySQL/laptop Quyền/nhóm. Tiếp tục R07.
