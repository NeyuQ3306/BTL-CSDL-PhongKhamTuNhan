# Trung — bàn giao tuần 3

## Trạng thái ngày 21/10/2026

#5, #10, #11 đã merge. Nền hiện tại là main f4869299c25fdfd0b711597e30b60ab277120f44. Nhánh trung/week-3 đồng bộ nền bằng merge thường; chỉ bổ sung bộ kiểm tra, công cụ audit và tài liệu của Trung. Code nghiệp vụ/UI/SQL đã tích hợp được giữ từ main.

Theo PHAN_CONG_3_TUAN.md: kiểm tra/sửa backend và transaction, NULL/số tiền/dữ liệu không tồn tại/rollback; chạy MySQL thống nhất; phối hợp clone mới máy thứ hai; chuẩn bị giải thích route/kết nối/ràng buộc.

## Đã triển khai

- week3_checks/test_backend_release.py: validation tiền ở 0 và trần DECIMAL(12,0); lỗi body/commit rồi request tiếp theo; teardown khi mất kết nối; MySQL thật kiểm tra lịch sử rỗng, ngày NULL, không kê đơn, tiền lớn chính xác, rollback lượt lỗi, rollback thuốc thứ hai rồi thử lại cùng mã đơn, dữ liệu thiếu trả 404.
- week3_checks/test_preflight.py: kiểm tra receipt sạch và các trường hợp phải thất bại (sai SHA, số dòng/trigger/audit/findings, không ghi đè receipt).
- tools/trung_week3_preflight.py: chỉ đọc; xác nhận source SHA khi được yêu cầu; 11 bảng/1.144 dòng, 9 trigger, 10 audit SQL và 9 nhóm findings. Failed audit trả exit 1. Không import/drop/xóa hoặc ghi đè receipt cũ. Chỉ kiểm tra chuẩn số dòng khi DB đã dọn về seed.
- docs/TRUNG_WEEK3_SECOND_MACHINE.md: clone/cấu hình/import và mẫu ghi nhận máy thứ hai.
- docs/TRUNG_WEEK3_BACKEND_EXPLAIN.md: route, DB, transaction, NULL/tiền, ràng buộc và vấn đáp.

Fixture MySQL lấy tên DB từ cấu hình app sau khi nạp .env, đồng thời vẫn bắt buộc RUN_MYSQL_TESTS=1 và tên DB kết thúc _test. Chạy riêng các ca MySQL không còn phụ thuộc test unit trước đó có nạp .env hay chưa.

## Kiểm chứng hiện tại

Workflow trung-week3.yml kiểm tra trực tiếp checkout hiện tại, không checkout candidate tuần 2 cũ. CI Python 3.11/MySQL 8.4/Chromium bật QUYEN_CHECK_WEEK2=1; chạy chung tests và week3_checks, có audit trước/sau, JUnit/ảnh/JSON.

PR event chạy SHA merge thử; push event chạy head nhánh. Receipt source_sha phải bằng github.sha của event. Kết quả từng commit lấy từ Checks PR #12, không gán CI cũ cho commit mới.

## Kết quả lịch sử

Commit chuẩn bị 2ac0d2f: run 39360946626 đạt 24/24 trên từng candidate Trung da59e56 và Vương e346a9f, audit sạch. Đây là hai snapshot trước tích hợp, không thay kết quả workflow hiện tại. Local cũ 16 passed/8 skipped không phải nghiệm thu MySQL.

## Còn chờ thực tế

- Trung/Vương thực sự clone mới trên máy thứ hai, ghi OS/Python/MySQL/browser/SHA, import/audit và thao tác UI. T16 CHƯA XÁC NHẬN; CI Linux không thay bằng chứng máy thứ hai.
- Reviewer khác kiểm tra PR #12. Giữ Draft đến khi đủ nghiệm thu; không tự approve/merge/tag.
- Sau mọi sửa code hoặc thay nền release, chạy lại trên SHA cuối. Quyền phụ trách SQL nộp/tag, Vương phụ trách UI/demo.
- Khi đóng gói SQL, Quyền cần giữ thứ tự import thực tế schema → seed → audit → constraints → audit → queries theo SETUP; không áp dụng máy móc mô tả thứ tự cũ nếu seed bị trigger từ chối.

Chưa thấy lỗi nghiệp vụ cần sửa từ bộ ca đã chạy trước đây. Mọi lỗi phát hiện trong lần kiểm tra hiện tại cần xử lý hoặc ghi rõ trước chốt.
