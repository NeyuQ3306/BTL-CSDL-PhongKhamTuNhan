# Bổ sung nghiệm thu phần Quyền — 19/10/2026

Bản nền tích hợp: `a813ac76ed925c3a127f2989c8195605ff80f1eb`. Không đổi SQL, seed, backend hay UI; bổ sung cách thu bằng chứng tái lập. Kết quả chạy phải lấy từ Checks/Artifacts của đúng SHA, không xem cấu hình workflow là kết quả đạt.

## Phạm vi bằng chứng

- Cài trên MySQL 8.4 cách ly: schema → seed → audit → constraints → audit → queries. Mỗi audit kiểm tra toàn bộ 10 truy vấn và dừng nếu có findings; xác nhận 11 bảng/9 trigger.
- Chạy toàn bộ pytest hiện có, gồm test_crud (trùng mã/CMT), test_validation/test_bad_form_and_queries (ca sai), test_history_prevents_delete (FK thật) và browser CRUD ba nhóm. Không thêm test lặp triển khai.
- test_reports_python_oracle đối chiếu SQL Q1/Q2/Q4 với phép tính Python độc lập cho 07–10/2026 và tháng rỗng 12/2025; kiểm tra hồ sơ và số lần khám Q3. Đây là phạm vi đối chiếu Q3 hiện có, chưa khẳng định mọi trường của mọi tập kết quả Q3 được đối chiếu độc lập.
- Lưu canonical-import.json, final-audit-queries.json (đúng SHA, môi trường, mọi tập kết quả queries.sql), pytest.xml và ảnh browser.
- Tiện ích chỉ chấp nhận DB có tên kết thúc _test; --install từ chối DB không trống. Không DROP, không tắt FK, không in credentials.

## Chạy lại

Cấu hình biến DB_* cho DB thử trống riêng có hậu tố _test, quyền tạo trigger. Không dùng DB làm việc. Dùng môi trường Python đã cài requirements-dev.txt và Playwright Chromium, bật RUN_MYSQL_TESTS=1, RUN_BROWSER_TESTS=1.

```text
python -m tools.quyen_week1_evidence --install
python -m pytest -v --junitxml=test-artifacts/quyen-week1/pytest.xml
python -m tools.quyen_week1_evidence
python -m tools.audit_seed
```

Công cụ đọc biến môi trường, không tự đọc .env. Hướng dẫn Windows/Workbench hiện hành vẫn là SETUP.md. Sau test phải kiểm tra 72 ca đạt, không skipped, đủ 1.144 dòng và findings rỗng; nếu thất bại giữ log, không import chồng.

## Giới hạn

Đây là bằng chứng tự động trên máy CI, không đánh dấu chạy trên máy Windows của Quyền hoặc Trung. Những xác nhận máy Quyền ngày 18/10 vẫn giữ nguyên giá trị theo snapshot. Nghiệm thu cùng hướng dẫn trên máy Trung còn cần thành viên cung cấp. PR bổ sung này cần Trung/Vương review theo RULES trước merge; không tự approve.
