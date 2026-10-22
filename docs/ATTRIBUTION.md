# Ghi nhận nguồn

Source tham khảo: https://github.com/scmeyer41/hospital-database-management-system

Commit nhập: 711d7b1bdff824901a75e086525d0a9f5ca14701. Tác giả theo README upstream: scmeyer41 và Richard Tashjian. Repo nhóm giữ lịch sử 3 commit gốc; README gốc được lưu nguyên văn tại UPSTREAM_README.md.

Tại thời điểm nhập, chưa thấy file LICENSE của toàn repo. Không tự gán MIT/ISC cho source này. Giữ repo nhóm private trong giai đoạn làm bài; trước khi phát hành công khai cần làm rõ quyền sử dụng và quy định môn học. Việc ghi nguồn không tự thay thế quyền sử dụng.

Phần nhóm phát triển: ER/lược đồ 11 bảng và ràng buộc phòng khám tư; SQL, seed và truy vấn theo đề; chuyển đổi Flask/UI; báo cáo, kiểm thử và hướng dẫn. Danh sách này là phạm vi dự kiến, không khẳng định mọi phần đã hoàn tất.

## Helper cleanup private MySQL

`tools/private_mysql_cleanup.py` được lấy riêng, giữ nguyên byte từ PR #12 của Trung (`ptt172`), commit `d566abf5545d5c5f77caaea7deeab42fddb7f5b5`. Chỉ thêm helper và dependency dev `psutil>=6,<8`; không merge nhánh Trung hoặc lấy runner/backend của PR đó. Tích hợp cho demo và test mới của Vương ở PR #13.
