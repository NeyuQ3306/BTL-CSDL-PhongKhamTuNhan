# Kiểm tra bàn giao bước 7 — 21/10/2026

[verification.json](verification.json) được tạo bằng [verify_handoff.py](verify_handoff.py). Đây là kiểm tra tính toàn vẹn source/bằng chứng, cú pháp và liên kết; không phải phiên chạy mới của suite MySQL/Chromium hoặc T16.

Đối chiếu manifest cuối 124 file, manifest thực thi bước 5 và hash công cụ demo với phiên diễn tập thành công. Những file tài liệu thay đổi được liệt kê riêng; source đã kiểm thử phải giữ nguyên hash. Đọc lại XML để đếm actual 179 test và JSON T01–T15; kiểm tra audit cuối cùng, cleanup và trạng thái diễn tập. Không thay bằng chứng cũ.

[preserved_evidence_sha256.json](preserved_evidence_sha256.json) ghi hash toàn bộ bằng chứng tuần 3 trước bàn giao và thư mục tuần 2 untracked được giữ nguyên, không stage thư mục tuần 2 đó. Script chạy lại sẽ đối chiếu với snapshot này, không ghi đè snapshot. Bằng chứng lịch sử còn nhắc chờ T16 phải đọc cùng quyết định hiện hành trong [bàn giao](../../VUONG_WEEK3_HANDOFF.md).

Kiểm tra secrets chỉ xuất tên file/dòng nghi vấn, không in giá trị. Mật khẩu test sinh ngẫu nhiên trong công cụ không được ghi log/commit; datadir/venv/cache/.env và dump cá nhân không thuộc phạm vi stage. Các chuỗi ví dụ rõ ràng trong hướng dẫn được rà riêng.
