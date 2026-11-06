# Vương — khung UI và bảng R01, 05/11/2026

Nhánh `feat/vuong-analytics-ui`, nền main `a0d6c300be631cea404672ade548a67c20fea1c1`.
Phạm vi: trang `/reports`, mục Báo cáo mở rộng, bộ lọc R01 và bảng sáu cột.
Chưa có biểu đồ hoặc giao diện R02–R07. Chưa push/PR/review/merge hay nghiệm thu nhóm.

## Hợp đồng đã xác nhận

- #21 đã merge tại `cf516dcc0585c353f7b80ee349a7e3477900ae51`.
- #22 đã merge tại `a0d6c300be631cea404672ade548a67c20fea1c1`, head cuối `82e3a78`.
- Trung xác nhận trong commit `960af1611ae6fceacd476fcf06509e7975e8775d`,
  mục “Trung xác nhận với review UI của Vương” trong `docs/TRUNG_ANALYTICS_BACKEND.md`.
  Đây là phản hồi bằng tài liệu trong PR; công cụ đọc comments không trả bình luận riêng của Trung.
- Adapter UI chuyển ngày cuối bao gồm đúng một lần, API nhận `[start,end)`.
  Ngày cuối tối đa 9999-12-30; tuổi -1/0/1/2/3; bỏ age_group khi xem tất cả.
  Tham chiếu: [PR #22](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/pull/22),
  [xác nhận Trung](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/blob/960af1611ae6fceacd476fcf06509e7975e8775d/docs/TRUNG_ANALYTICS_BACKEND.md).

## Thay đổi

- Include `templates/analytics/panel.html` trong hub báo cáo hiện có; không thêm route backend.
- JS gọi duy nhất endpoint R01, giữ thứ tự API và sáu cột, không tính lại nghiệp vụ.
- Kiểm ngày theo lịch, ngày nhuận, chuyển năm và giới hạn năm bốn chữ số.
- Ẩn bảng và hủy request cũ khi đổi bộ lọc; bỏ response đến muộn.
- Hiển thị loading, lỗi validation/HTTP/network, kết quả rỗng và kỳ API thực trả về.
  Có timeout 20 giây; nhánh timeout chưa có kiểm thử riêng.
- Tất cả asset phục vụ cục bộ, không thêm thư viện/CDN. Chưa kiểm chứng biểu đồ offline vì chưa triển khai biểu đồ.
- Không sửa SQL/schema/seed, backend, requirements, README hay workflow.

## Kiểm chứng thực chạy

Windows, Python 3.14.6, pytest 8.4.2, Playwright 1.64.1 với Chrome cài trên máy.
Đã bổ sung Playwright và dependency dev còn thiếu vào `.venv`; không sửa file requirements.

```powershell
$env:RUN_BROWSER_TESTS='1'
$env:BROWSER_CHANNEL='chrome'
$env:RUN_MYSQL_TESTS='0'
& '.venv\Scripts\python.exe' -m pytest tests/test_vuong_analytics_ui.py tests/test_report_shells.py tests/test_trung_analytics_backend.py -q --junitxml=test-artifacts/vuong-analytics-ui/local.xml
```

**63 passed, 12 skipped**: 13 browser checks, 9 report dispatch/hub checks và
41 backend unit checks; 12 MySQL checks skipped. Trình duyệt chạy với quyền ngoài sandbox
để mở Chrome/máy chủ Flask loopback. API Flask thật dùng serializer/validation thật,
nhưng `analytics.build` được stub bằng oracle seed: không chạy SQL/MySQL.

Đã kiểm đủ ô/thứ tự 29 dòng mặc định; mọi nhóm tuổi; lặp gửi không cộng ngày lần hai;
29/02/2004, 31/12, năm 0001/9999; đảo kỳ/ngày tối đa bị chặn;
400/404/500/503, lỗi mạng; hợp đồng response sai; text chứa HTML không chạy;
response cũ sau đổi lọc không hiện; bảng rỗng; không gọi tài nguyên ngoài.
Ảnh desktop/390/320 px đã xem, không tràn trang, bảng cuộn ngang.

Hồi quy không DB:

```powershell
$env:RUN_BROWSER_TESTS='0'
$env:RUN_MYSQL_TESTS='0'
& '.venv\Scripts\python.exe' -m pytest tests week3_checks --ignore=tests/test_quyen_database.py --ignore=tests/test_quyen_week2_reports.py --basetemp=.codex-qa/vuong-analytics-ui-pytest -q --junitxml=test-artifacts/vuong-analytics-ui/regression-scoped.xml
```

**153 passed, 96 skipped**. Hai module SQL cũ bị loại rõ ràng vì luôn mở DB,
không theo cờ RUN_MYSQL_TESTS. Không cộng chồng với lượt kiểm tập trung.
Lần thử suite toàn bộ trước đó: 141 passed, 96 skipped, 45 failed và 45 errors
do kết nối DB bị sandbox chặn và quyền thư mục tạm; không coi là suite xanh.
Ban đầu còn thiếu psutil gây 2 collection errors; đã cài đủ requirements-dev và khắc phục.
Không kết nối/ghi DB thành công trong phiên này. Không kết luận Q1–Q4/MySQL đạt end-to-end.

`node --check clinic_app/static/analytics.js` và `git diff --check` đạt.
JUnit/ảnh cục bộ ở `test-artifacts/vuong-analytics-ui/` (gitignored).
Manifest SHA256 cạnh tài liệu này định danh source đã thử, không cần commit ảnh/log tạm.

## Bước tiếp theo

Vương bổ sung biểu đồ offline R01 từ cùng response; mở rộng UI các báo cáo tiếp theo,
đối chiếu UI/API/SQL trên DB thử riêng, rồi chuẩn bị PR để Trung/Quyền review.
Chưa đánh dấu mục cả bảy báo cáo, nghiệm thu laptop Quyền hoặc issue #3 hoàn tất.
