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

Đây là bằng chứng tự động trên máy CI, không đánh dấu chạy trên máy Windows của Quyền hoặc Trung. Những xác nhận máy Quyền ngày 18/10 vẫn giữ nguyên giá trị theo snapshot. Trung đã xác nhận nghiệm thu cá nhân ngày 19/10/2026 trên main a813ac7, Windows/Python 3.11.9/MySQL 8.4.11: import chuẩn, 11 bảng/9 trigger, CRUD ba nhóm, trùng/sai/chặn xóa và audit sau dọn sạch 1.144 dòng. [Xác nhận và giới hạn bằng chứng](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/pull/9#issuecomment-6260786763). Đây là xác nhận thao tác trực tiếp do Trung cung cấp qua trợ lý; ảnh gốc chưa đính kèm GitHub, không phải local 72 pytest. PR bổ sung này cần Trung/Vương review theo RULES trước merge; không tự approve.

## Kết quả đã xác minh và SHA thực chạy

- Main tích hợp `a813ac76ed925c3a127f2989c8195605ff80f1eb`: [run 39202562894](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/actions/runs/39202562894), job 117898447330: 72 passed, audit 1.144 dòng, matches_expected_counts=true, findings rỗng.
- Head PR #9 là `538a451dde20cc8541ab883c7a95dfedb4ee8df1`; **SHA thực được checkout và chạy** trong [acceptance run 39203057488](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/actions/runs/39203057488) là merge thử `607253ce1f0961c61dbb6cb04111909df787a5e8` (head trên + main a813ac7), không phải trực tiếp head PR. JSON source_sha và log checkout xác nhận điều này.
- Job 117899939130: 72 passed, không skipped; 10 truy vấn audit sạch, 11 bảng/9 trigger; audit_seed 1.144 dòng đúng. Artifact 12164836512 chứa JSON/JUnit/ảnh. Các kết quả này thuộc snapshot trên; commit cập nhật tài liệu sau đó phải xem Checks riêng.
- Phản hồi review Trung ngày 19/10 đã được cập nhật vào tài liệu; vẫn chờ approval cuối, không tự đánh dấu PR đã duyệt.
