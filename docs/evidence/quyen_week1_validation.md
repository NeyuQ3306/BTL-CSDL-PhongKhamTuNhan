# Bằng chứng kiểm thử Quyền tuần 1

## Cập nhật 18/10/2026

- SQL head 08e4427: [run 39034485323](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/actions/runs/39034485323) đạt 26 SQL test và 58 backend compatibility test (backend pin 26bc627).
- Tích hợp SQL 08e4427 + UI/backend 33d45a0: [run 39092264670](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/actions/runs/39092264670) đạt 72/72 (26 SQL + 46 backend/UI), không skipped. UI sau đồng bộ 8c5be94 giữ nguyên tree.
- Vương chạy lại Windows/Python 3.12.14/MySQL 8.0.46: 72/72 test, 33 ca hồ sơ và 4/4 trang PDF. [Bằng chứng](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/blob/fe9dd4959f4871f1bfcb8eb4c346746f6f20a9a2/docs/evidence/vuong_week1_acceptance_2026-10-18/README.md).
- Quyền ngày 18/10 chạy Windows/Python 3.11.9/MySQL 8.4.11, DB clinic_week1_demo2 với UI 8c5be94 + SQL 08e4427. Output người dùng cung cấp: 11 bảng/1.144 dòng, matches_expected_counts=true, 9 nhóm findings rỗng; xác nhận đủ 9 trigger và thêm/tìm/sửa/tải lại bệnh nhân trên web. Đây là thử thủ công, không phải chạy 72 test hoặc toàn bộ checklist trên máy Quyền.
- Hướng dẫn chuẩn duy nhất: docs/SETUP.md; schema → seed → audit → constraints → audit → queries. tools.quyen_db và tools.import_seed không phải đường cài chuẩn.
- Vuong-it đã review CHANGES_REQUESTED về hướng dẫn/bàn giao. Cập nhật tài liệu này xử lý nội dung phản hồi; còn chờ reviewer xác nhận lại. Chưa xác minh máy Trung hoặc bản main tích hợp. Không tự chốt tuần 1.

## Bằng chứng lịch sử ngày 17/10 (giữ theo snapshot)


Ngày 17/10/2026. CI MySQL 8.4.11 / Python 3.11.

Run: https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/actions/runs/39034289909
Commit: `83bd7fc18e4131ac192616abf74ac6fee1e131ca`

- Import `schema.sql` + `seed.sql` + `constraints.sql`: thành công, 11 bảng/1.144 dòng.
- Job database: 25 passed, 0 failed, 0 skipped. Đối chiếu Q1, Q2 và Q4 bằng oracle Python cho 07–10/2026 và tháng rỗng 12/2025; chạy Q3 hồ sơ/lịch sử; audit 10 nhóm không phát hiện.
- Job backend-compatibility: 58 passed, 0 failed, 0 skipped. Chạy backend snapshot Trung `26bc627b5bd8943f275d369a0d86f2d640aaf06f` trên chính schema/seed/trigger Quyền, gồm CRUD, transaction, rollback, báo cáo tính tay, ràng buộc và ghi đồng thời. Không gồm Playwright/browser test.
- Bổ sung test coverage seed (qua tháng, tái mắc, nhiều bệnh, không đơn, nhiều thuốc) chạy local: 1 passed. Commit kế tiếp chạy lại CI với test này, xem Checks của PR để lấy kết quả mới nhất.

Lần CI đầu `39034092505` phát hiện lỗi MySQL 1442 do FOR UPDATE trên chính bảng đang được trigger ghi. Đã sửa bằng cách bỏ khóa tự tham chiếu không được hỗ trợ; giữ khóa bảng cha/chỉ mục unique và quy trình khóa bệnh nhân của backend. Run ở trên xác nhận sửa thành công.

Giới hạn: chưa demo trình duyệt trên máy của ba thành viên; chưa có review/merge; chưa xác nhận UI của Vương tích hợp. Kiểm thử backend snapshot không chứng minh mọi commit tương lai tương thích. Không tuyên bố MySQL kiểm tra được cận dưới ở COMMIT; xem database/README.md.
