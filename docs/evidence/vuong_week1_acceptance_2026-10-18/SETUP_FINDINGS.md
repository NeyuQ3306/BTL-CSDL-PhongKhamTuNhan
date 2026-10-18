# Phản hồi SETUP cho Quyền/Trung — 18/10/2026

Đối chiếu `docs/SETUP.md` của PR #8 tại `3b59effd4bb86fca1f8d239af8349e73ac09e9e6`. Các mục dưới là tài liệu/môi trường, không phải lỗi UI hoặc lỗi SQL đã tái hiện.

| ID / người phụ trách | Vị trí và bước tái hiện | Expected | Actual / đề nghị |
|---|---|---|---|
| DOC-01 — Quyền, P3 | Đoạn cuối mục 7: câu PR #7 còn Draft; đối chiếu trạng thái GitHub | Trạng thái tài liệu khớp PR | #7 đã hết Draft từ trước phiên này; sửa câu này khi cập nhật PR #8. Không tự sửa nhánh Quyền trong PR Vương. |
| ENV-01 — Quyền/Trung | Dùng tài khoản DB_USER hiện tại trên máy Vương, thử CREATE database mới | Hướng dẫn chỉ rõ cần tài khoản có quyền tạo DB hoặc nhờ quản trị viên cấp một DB trống | Server 8.0.46 kết nối được nhưng CREATE DATABASE trả 1044; không tạo DB ở dịch vụ cũ. Tài liệu đã cho phép root/admin, đề nghị thêm mã 1044 và hướng xử lý vào bảng lỗi. Phiên này đã khắc phục bằng instance riêng, không phải blocker của code. |
| DOC-02 — Quyền/Trung | Sau merge #6/#7/#8, kiểm tra README, database/README và SETUP | Một quy trình import chuẩn có audit trước/sau trigger | SETUP mới đã ghi schema → seed → audit → constraints → audit → queries; nhánh UI/main cũ vẫn có importer adapter. Giữ hướng dẫn chuẩn khi giải quyết tài liệu lúc merge. Đây là phụ thuộc đã biết, không phát hiện lỗi SQL mới. |

Kết quả kiểm tra thực tế: import đúng thứ tự đạt; 72 test đạt, 33 ca hồ sơ qua browser/SELECT đạt, audit sạch. Môi trường local Python 3.12.14/MySQL 8.0.46; chưa xác nhận thao tác Workbench và Python 3.11/MySQL 8.4 trên máy thành viên. [Báo cáo và bằng chứng](README.md).
