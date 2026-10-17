# Bằng chứng kiểm thử Quyền tuần 1

Ngày 17/10/2026. CI MySQL 8.4.11 / Python 3.11.

Run: https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/actions/runs/39034289909
Commit: `83bd7fc18e4131ac192616abf74ac6fee1e131ca`

- Import `schema.sql` + `seed.sql` + `constraints.sql`: thành công, 11 bảng/1.144 dòng.
- Job database: 25 passed, 0 failed, 0 skipped. Đối chiếu Q1, Q2 và Q4 bằng oracle Python cho 07–10/2026 và tháng rỗng 12/2025; chạy Q3 hồ sơ/lịch sử; audit 10 nhóm không phát hiện.
- Job backend-compatibility: 58 passed, 0 failed, 0 skipped. Chạy backend snapshot Trung `26bc627b5bd8943f275d369a0d86f2d640aaf06f` trên chính schema/seed/trigger Quyền, gồm CRUD, transaction, rollback, báo cáo tính tay, ràng buộc và ghi đồng thời. Không gồm Playwright/browser test.
- Bổ sung test coverage seed (qua tháng, tái mắc, nhiều bệnh, không đơn, nhiều thuốc) chạy local: 1 passed. Commit kế tiếp chạy lại CI với test này, xem Checks của PR để lấy kết quả mới nhất.

Lần CI đầu `39034092505` phát hiện lỗi MySQL 1442 do FOR UPDATE trên chính bảng đang được trigger ghi. Đã sửa bằng cách bỏ khóa tự tham chiếu không được hỗ trợ; giữ khóa bảng cha/chỉ mục unique và quy trình khóa bệnh nhân của backend. Run ở trên xác nhận sửa thành công.

Giới hạn: chưa demo trình duyệt trên máy của ba thành viên; chưa có review/merge; chưa xác nhận UI của Vương tích hợp. Kiểm thử backend snapshot không chứng minh mọi commit tương lai tương thích. Không tuyên bố MySQL kiểm tra được cận dưới ở COMMIT; xem database/README.md.
