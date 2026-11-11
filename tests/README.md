# Kiểm thử

Các test dùng pytest; test giao diện dùng Playwright Chromium. Chạy từ gốc repo.

## Chuẩn bị

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt "playwright>=1.50,<2"
.\.venv\Scripts\python.exe -m playwright install chromium
```

Chạy `python -m pytest tests -q` sẽ chạy các ca không cần DB; các ca tích hợp cần cờ môi trường tương ứng. Đọc cả passed, failed và skipped.

## MySQL và trình duyệt

Fixture trong `conftest.py` yêu cầu `RUN_MYSQL_TESTS=1` và `DB_NAME` kết thúc bằng `_test`. Các test cần canonical seed và có fixture ghi dữ liệu, vì vậy chuẩn bị DB thử riêng. `RUN_BROWSER_TESTS=1` bật browser.

Trên Windows, [runner nghiệm thu](../docs/evidence/quyen_laptop_acceptance_20261106/README.md) tạo instance MySQL với datadir/cổng riêng, nạp seed, chạy SQL/oracle, hồi quy, browser và cleanup. Dùng output mới và đường dẫn mysqld thực tế; giữ log để kiểm tra sau chạy.

CI dựng MySQL thử riêng theo từng workflow. Hai fixture R07 zero/NULL chỉ ghi khi DB đúng tên `clinic_vuong_analytics_test`; trên DB khác chúng được skip có giải thích. Skip không được tính thành ca đạt.

## Phạm vi

| Vị trí | Nội dung |
|---|---|
| `tests/` | SQL, API, validation, transaction, giao diện và báo cáo |
| `week3_checks/` | Hồi quy tích hợp và kiểm tra công cụ chạy thử |
| `windows_checks/` | Cleanup instance MySQL trên Windows |
| `tools/analytics_oracle.py` | Đáp án tính độc lập từ seed |
| `tools/analytics_evidence.py` | So sánh bảy truy vấn với oracle và kiểm seed |

Bằng chứng đã chọn lưu ở `docs/evidence/`; output tạm ở `test-artifacts/` hoặc `local-evidence/`. Xem [nghiệm thu laptop](../docs/evidence/quyen_laptop_acceptance_20261106/README.md) và [ma trận nghiệp vụ](../docs/ACCEPTANCE.md) khi cần truy lại phiên chạy.
