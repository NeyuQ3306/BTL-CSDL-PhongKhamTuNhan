# Bằng chứng đối chiếu hướng dẫn Bước 5 — 21/10/2026

- [setup-results.json](setup-results.json): phiên đạt mới, Python3.11.9/MySQL8.4.7; tạo DB/datadir mới, sáu bước import, 11bảng/9trigger; app.py thật đọc .env riêng; 11route HTTP200; app/DB shutdown, cổng đóng, source/.env/bằng chứng cũ giữ nguyên.
- [audit.json](audit.json): 1.144 dòng, counts đúng,9 nhóm findings rỗng.
- [queries-default.json](queries-default.json): 11 tập kết quả SQL, tham số mặc định10/2026 và BN001; đối chiếu expected trong document-checks.
- [execution_source_sha256.json](execution_source_sha256.json): 66file thực thi/config/dependencies trùng candidate bước4; không gán candidate cho riêng SHA nền.
- [verify_setup.py](verify_setup.py): script thực chạy, dùng runtime và MySQL sẵn có; không phải installer thay hướng dẫn. Chạy lại cần thư mục evidence mới và OUT đúng vị trí, không ghi đè phiên này.
- [attempt1-sandbox.json](attempt1-sandbox.json): lần đầu không kết nối được private MySQL, success=false; giữ để truy vết, không tính đạt.
- [process-check.json](process-check.json): kiểm tra có quyền sau cùng, số tiến trình MySQL thuộc datadir step5 bằng0.
- [remote-main.txt](remote-main.txt): SHA main remote xác minh trực tiếp, không dùng trạng thái nhánh local để suy đoán.
- [check_docs.py](check_docs.py): lệnh kiểm tra link, hash, JUnit và expected SQL; không chạy lại suite.
- [document-checks.json](document-checks.json): kiểm tra link tài liệu hiện hành, source, JUnit/cases, expected SQL và bảo toàn file.

Phạm vi là kiểm chứng local trên cùng máy; không phải cài lại dependencies từ mạng, Workbench GUI, CI, nghiệm thu nhóm hoặc T16. Không chạy lại CRUD/luồng ghi/bốn báo cáo bằng browser trong bước5: phần đó dẫn suite179/179 đúng candidate bước4 ở [biên bản](../../VUONG_WEEK3_STEP5_VERIFICATION.md).
