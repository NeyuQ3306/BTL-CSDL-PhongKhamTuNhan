# Báo cáo review tuần 1 — 18/10/2026

## Kết luận

Backend Trung đã được review và squash merge qua PR #4. Chưa chốt toàn bộ tuần 1: PR #6 cần Trung/Vương review, PR #7 còn draft, chưa có bằng chứng cả ba thành viên chạy cùng bộ tích hợp từ hướng dẫn thống nhất. Không chấm phần trăm từ số commit hoặc CI.

Đối chiếu RULES.md, PHAN_CONG_3_TUAN.md, ACCEPTANCE.md, các bàn giao Quyền/Trung/Vương, dictionary và manifest thiết kế. Phạm vi yêu cầu lấy từ tài liệu hiện hành trong repo; chưa có bản đề gốc tách riêng được xác minh. Chưa rà trực quan hai PDF; không kết luận PDF đã đạt.

## Trạng thái và đóng góp

| Người | Đã có và có bằng chứng | Chưa đủ điều kiện hoàn tất |
|---|---|---|
| Minh Quyền | SQL 11 bảng, tách seed 1.144 dòng, audit/trigger, bốn nhóm truy vấn nháp, oracle kết quả, dictionary và manifest YC1. PR #6 tại 08e4427. | Cần Trung hoặc Vương review. Chưa ghép SQL mới với UI mới nhất thành bản nghiệm thu; chưa xác minh cả ba máy/PDF cuối. Từ điển bàn giao 17/10, muộn mốc 15/10. |
| Trung | Backend CRUD ba nhóm, DB theo request, validation, CSRF, mã chuẩn, rollback, lịch sử nền; PR #4 tại 5a25395, 32 test CI đạt. Đã review và merge. | Source upstream đầy đủ chưa có bằng chứng chạy; hợp đồng cần Vương xác nhận trên PR; setup chuẩn SQL cần thống nhất. Chưa coi nghiệp vụ tuần 2 đã merge. |
| Vương | Seed giả bàn giao qua adapter Trung, được Quyền kế thừa nguyên 1.144 dòng; UI tiếng Việt, CRUD/form/khung bốn báo cáo, checklist, công cụ, ảnh/log. PR #7 tại 33d45a0, 46 test CI đạt. | PR draft; bàn giao vẫn ghi CI chưa chạy dù run mới đã đạt. Chưa rà PDF, chưa xác minh máy thành viên khác. Ba khung thống kê chưa tích hợp SQL, đúng phạm vi tuần 1. |

Không gán dữ liệu mẫu cho Trung/Quyền chỉ vì commit nằm trên nhánh hai bạn. Compare 5a25395...33d45a0 cho thấy một commit UI Vương trên nền sáu commit Trung; tránh đếm trùng backend.

## Bằng chứng kiểm thử

| Snapshot | Kiểm chứng đọc từ log GitHub | Chạy lại trong lần review |
|---|---|---|
| Trung 5a25395699905cc5f79af4904bd73d95073963a0 | [Run 39035653555](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/actions/runs/39035653555), job 117404788765: 32 passed, MySQL 8.4 + Chromium, audit 11 bảng/1.144 dòng sạch. | Python 3.12: 11 passed, 21 skipped; compile đạt. |
| Quyền 08e4427f6ac8e9ba55eaba859ddab4067330ec04 | [Run 39034485323](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/actions/runs/39034485323), jobs 117401448906/117401449097: 26 SQL + 58 backend compatibility passed. Backend compatibility pin 26bc627, không phải UI mới nhất. | Đọc code/SQL/tests, không chạy MySQL local. |
| Vương 33d45a06eb7e237796d3d240fd6d419fabd00bd1 | [Run 39037430772](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/actions/runs/39037430772), job 117409980090: 46 passed, MySQL 8.4 + Chromium, audit sạch. | Python 3.12: 25 passed, 21 skipped; compile/Jinja đạt. |

Không tính skipped là đạt. Không có MySQL hoặc Chromium local; không nhận các run cũ là kiểm thử được chạy lại trong lần review này. Workflow week1-review.yml bổ sung kiểm thử tích hợp hai SHA Quyền/Vương kể trên vào cùng DB thử; kết quả sẽ cập nhật sau CI. Nó không đưa code tuần 2 vào main.

## Findings, rủi ro và hành động

| Mức | Vị trí | Nhận định và việc cần làm | Chủ trì / hạn đề xuất |
|---|---|---|---|
| P2 tích hợp | tools/import_seed.py:38; database/README.md (PR #6); docs/SETUP.md | Hai đường import: adapter Trung chưa cài trigger, SQL Quyền có trigger. Chọn hướng dẫn chuẩn từ DB mới, không chạy chồng seed; hiện chưa phải lỗi SQL đã tái hiện. | Quyền + Trung, trước PR chốt 19/10 20:00 |
| P2 tài liệu | docs/VUONG_WEEK1_HANDOFF.md, phần kiểm thử/chưa hoàn thành | Các câu CI chưa chạy đã cũ so với run 46/46. Cập nhật mốc log, giữ giới hạn PDF/máy khác. | Vương, trước chuyển ready |
| Gate review | PR #6, RULES mục 4 | Chưa có Trung/Vương review. Tài khoản Quyền không tự approve. | Trung hoặc Vương, trước 19/10 20:00 |
| Gate trạng thái | PR #7 | Vẫn draft. Kiểm tra diff/CI với main sau squash #4; chuyển ready khi tài liệu và hợp đồng sẵn sàng. | Vương phối hợp Trung |
| Gate nghiệm thu | PHAN_CONG tuần 1; ACCEPTANCE T16 | Chưa chứng minh cả ba chạy theo cùng hướng dẫn. PDF chưa được rà trực quan. Không đánh dấu chốt tuần 1. | Cả nhóm; Vương rà PDF, trước 20/10 20:00 |
| Rủi ro Git | PR #5 base trung/week-1 | Stacked tuần 2; sau squash #4 cần đồng bộ có kiểm soát trước xử lý tuần 2. Không đổi base/merge nội dung tuần 2 trong lần này. | Trung, trước review tuần 2 |
| Giới hạn đã công bố | constraints.sql; database/README.md | Không có deferred constraint kiểm tra mọi cận dưới ở COMMIT; truy cập SQL quản trị vẫn cần audit. Không mở API xóa lịch sử. | Quyền/Trung, hoàn thiện khi triển khai tuần 2 |

Chưa phát hiện lỗi code P0/P1 trong phần tuần 1 đã rà. Đây không phải cam kết không còn lỗi. Review tập trung diff/routes/services/validation/CSRF, SQL và dữ liệu/tests liên quan; bằng chứng ảnh/log của tác giả được đọc theo mốc, chưa tái nghiệm thu mọi ảnh/máy.

## Thao tác đã thực hiện

- Review APPROVE #4 tại SHA mới nhất, kiểm tra lại head/base, CI thành công, không conflict, không có unresolved review thread; squash merge thành công, xác minh main tại b51b0afb3b0d03f6fa30a255b1efc614b89a9bbd.
- Review COMMENT có file/vị trí và mức độ trên [#6](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/pull/6) và [#7](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/pull/7). Không tự approve #6.
- Không tạo PR trùng: cả ba nhánh tuần 1 đều đã có PR. Không merge #5, không force push, không xóa nhánh, không ghi thẳng main.
- Nhánh main protected=false; API rulesets trả 403 yêu cầu nâng gói cho repo private, khớp giới hạn trong RULES. Không sửa/bỏ qua quy tắc.
- Báo cáo và ghi chú học chung đưa qua nhánh/PR riêng; không tự approve hoặc merge PR tài liệu của Quyền. Ghi chú chưa phải tài liệu ôn cuối.
- Không thay đổi lịch báo cáo tuần.

## Việc tiếp theo theo thứ tự

1. Trung/Vương review SQL #6, giải quyết phản hồi; Quyền/Trung thống nhất đường import chuẩn.
2. Vương cập nhật bàn giao, xác nhận hợp đồng trên #4, đồng bộ main sau squash rồi chuyển #7 ready; chạy CI trên SHA thay đổi mới.
3. Dùng kết quả tích hợp SQL + backend/UI mới và review hợp lệ để quyết định merge #6/#7, xác minh SHA ngay trước merge.
4. Cả ba chạy clone mới theo hướng dẫn; Vương ghi expected/actual, ảnh/log và rà PDF. Chốt tuần 1 ngày 20/10 lúc 20:00 khi đủ bằng chứng.
