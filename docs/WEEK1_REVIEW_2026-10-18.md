# Báo cáo review tuần 1 — 18/10/2026

## Cập nhật hiện trạng — 18/10/2026, 19:51 (Asia/Ho_Chi_Minh)

Phần bên dưới mục “Lịch sử review đầu ngày” là ghi nhận theo thời điểm cũ, không dùng làm trạng thái hiện tại.

- #4 đã merge. Vương đã xác nhận hợp đồng trên [#4](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/pull/4#issuecomment-6246625492).
- #6 head 08e4427 đã được Vuong-it review; còn CHANGES_REQUESTED về hướng dẫn import và bằng chứng bàn giao. Không tự approve hoặc bỏ yêu cầu sửa.
- #7 đã hết Draft, head fe9dd4959f4871f1bfcb8eb4c346746f6f20a9a2. Bàn giao đã cập nhật; CI Backend and MySQL [39104330959](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/actions/runs/39104330959) thành công trên head này. Đã review APPROVE và squash merge thành e174f626da01f88f9d6b5d34c7e744941b536ecf trong phiên chốt.
- Vương đã rà 4/4 trang hai PDF và chạy local 72/72 test tích hợp, 33 ca hồ sơ; xem [bằng chứng](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/blob/fe9dd4959f4871f1bfcb8eb4c346746f6f20a9a2/docs/evidence/vuong_week1_acceptance_2026-10-18/README.md). Đây là Windows/Python 3.12.14/MySQL 8.0.46, không phải CI MySQL 8.4 hoặc nghiệm thu máy khác.
- Quyền chạy Windows/Python 3.11.9/MySQL 8.4.11, UI/backend 8c5be94 + SQL 08e4427, DB clinic_week1_demo2. Output audit do Quyền cung cấp xác nhận 11 bảng/1.144 dòng, matches_expected_counts=true, 9 nhóm findings rỗng. Quyền xác nhận đủ 9 trigger sau khi chạy riêng phần trigger qua PyMySQL; Workbench trước đó báo 1064. Ảnh web hiển thị 40 bệnh nhân trước thử; Quyền xác nhận thêm/tìm/sửa/tải lại bệnh nhân mẫu thành công. Không coi đây là 72 test chạy trên máy Quyền, cũng chưa xác minh xóa/ca lỗi/SQL SELECT độc lập trên máy này.
- Hồ sơ thử BNTESTQ1 có thể còn trong DB Quyền; số lượng audit sau thử có thể khác nền. Không import lại seed để xử lý.
- #8 đang có CHANGES_REQUESTED về trạng thái tài liệu. Cập nhật này xử lý thông tin cũ; cần reviewer xác nhận lại.
- Chưa có bằng chứng nghiệm thu máy Trung trong phiên này. Chưa chốt toàn bộ tuần 1; không nhập PR #5 tuần 2.

### Việc còn lại

1. Hoàn thiện hướng dẫn chuẩn và bằng chứng #6/#8; Trung/Vương xác nhận lại các yêu cầu sửa.
2. #7 đã được review kết luận và squash merge. #6/#8 chờ reviewer xác nhận lại; giữ nhánh thành viên.
3. Kiểm thử bản main sau tích hợp, ghi đúng SHA và kết quả; không gán CI snapshot cũ cho main mới.
4. Bổ sung nghiệm thu máy Trung và các mục còn thiếu trong ACCEPTANCE trước chốt toàn nhóm.

## Lịch sử review đầu ngày


## Kết luận

Backend Trung đã được review và squash merge qua PR #4. Chưa chốt toàn bộ tuần 1: PR #6 cần Trung/Vương review, PR #7 còn draft (đã đồng bộ main bằng merge commit giữ nguyên nội dung UI), chưa có bằng chứng cả ba thành viên chạy cùng bộ tích hợp từ hướng dẫn thống nhất. Không chấm phần trăm từ số commit hoặc CI.

Đối chiếu RULES.md, PHAN_CONG_3_TUAN.md, ACCEPTANCE.md, các bàn giao Quyền/Trung/Vương, dictionary và manifest thiết kế. Phạm vi yêu cầu lấy từ tài liệu hiện hành trong repo; chưa có bản đề gốc tách riêng được xác minh. Chưa rà trực quan hai PDF; không kết luận PDF đã đạt.

## Trạng thái và đóng góp

| Người | Đã có và có bằng chứng | Chưa đủ điều kiện hoàn tất |
|---|---|---|
| Minh Quyền | SQL 11 bảng, tách seed 1.144 dòng, audit/trigger, bốn nhóm truy vấn nháp, oracle kết quả, dictionary và manifest YC1. PR #6 tại 08e4427. | Cần Trung hoặc Vương review. Test tích hợp SQL/UI mới đã đạt 72/72, nhưng chưa merge/nghiệm thu; chưa xác minh cả ba máy/PDF cuối. Từ điển bàn giao 17/10, muộn mốc 15/10. |
| Trung | Backend CRUD ba nhóm, DB theo request, validation, CSRF, mã chuẩn, rollback, lịch sử nền; PR #4 tại 5a25395, 32 test CI đạt. Đã review và merge. | Source upstream đầy đủ chưa có bằng chứng chạy; hợp đồng cần Vương xác nhận trên PR; setup chuẩn SQL cần thống nhất. Chưa coi nghiệp vụ tuần 2 đã merge. |
| Vương | Seed giả bàn giao qua adapter Trung, được Quyền kế thừa nguyên 1.144 dòng; UI tiếng Việt, CRUD/form/khung bốn báo cáo, checklist, công cụ, ảnh/log. PR #7 tại 33d45a0, 46 test CI đạt. | PR draft; bàn giao vẫn ghi CI chưa chạy dù run mới đã đạt. Chưa rà PDF, chưa xác minh máy thành viên khác. Ba khung thống kê chưa tích hợp SQL, đúng phạm vi tuần 1. |

Không gán dữ liệu mẫu cho Trung/Quyền chỉ vì commit nằm trên nhánh hai bạn. Compare 5a25395...33d45a0 cho thấy một commit UI Vương trên nền sáu commit Trung; tránh đếm trùng backend.

## Bằng chứng kiểm thử

| Snapshot | Kiểm chứng đọc từ log GitHub | Chạy lại trong lần review |
|---|---|---|
| Trung 5a25395699905cc5f79af4904bd73d95073963a0 | [Run 39035653555](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/actions/runs/39035653555), job 117404788765: 32 passed, MySQL 8.4 + Chromium, audit 11 bảng/1.144 dòng sạch. | Python 3.12: 11 passed, 21 skipped; compile đạt. |
| Quyền 08e4427f6ac8e9ba55eaba859ddab4067330ec04 | [Run 39034485323](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/actions/runs/39034485323), jobs 117401448906/117401449097: 26 SQL + 58 backend compatibility passed. Backend compatibility pin 26bc627, không phải UI mới nhất. | Đọc code/SQL/tests, không chạy MySQL local. |
| Vương 33d45a06eb7e237796d3d240fd6d419fabd00bd1 | [Run 39037430772](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/actions/runs/39037430772), job 117409980090: 46 passed, MySQL 8.4 + Chromium, audit sạch. | Python 3.12: 25 passed, 21 skipped; compile/Jinja đạt. |

Không tính skipped là đạt. Không có MySQL hoặc Chromium local; không nhận các run cũ là kiểm thử được chạy lại trong lần review này. **Kiểm thử mới chạy trong lần review này:** [Week 1 integration review — run 39092264670](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/actions/runs/39092264670), job 117571317667: **72/72 passed, không skipped**, Python 3.11/MySQL 8.4/Chromium. Cài schema + 1.144 dòng + trigger Quyền, chạy 26 test SQL và 46 test backend/UI Vương cùng DB; audit sau test đủ 11 bảng/1.144 dòng và không phát hiện. Đây là test hai snapshot pin 08e4427/33d45a0, không phải xác nhận đã merge hai PR. Nội dung UI mới sau đồng bộ có cùng tree 5489ec1 nên không đổi code được test. Workflow không đưa tuần 2 vào main.

## Findings, rủi ro và hành động

| Mức | Vị trí | Nhận định và việc cần làm | Chủ trì / hạn đề xuất |
|---|---|---|---|
| P2 tích hợp | tools/import_seed.py:38; database/README.md (PR #6); docs/SETUP.md | Hai đường import: adapter Trung chưa cài trigger, SQL Quyền có trigger. Chọn hướng dẫn chuẩn từ DB mới, không chạy chồng seed; hiện chưa phải lỗi SQL đã tái hiện. | Quyền + Trung, trước PR chốt 19/10 20:00 |
| P2 tài liệu | docs/VUONG_WEEK1_HANDOFF.md, phần kiểm thử/chưa hoàn thành | Các câu CI chưa chạy đã cũ so với run 46/46. Cập nhật mốc log, giữ giới hạn PDF/máy khác. | Vương, trước chuyển ready |
| Gate review | PR #6, RULES mục 4 | Chưa có Trung/Vương review. Tài khoản Quyền không tự approve. | Trung hoặc Vương, trước 19/10 20:00 |
| Gate trạng thái | PR #7 | Vẫn draft. Đã giải quyết xung đột add/add sau squash #4 bằng merge commit 8c5be94, giữ nguyên tree UI; diff còn 67 file của Vương, không có tuần 2. CI head mới đã đạt 46/46 tại run 39092326435; chuyển ready khi tài liệu và hợp đồng sẵn sàng. | Vương phối hợp Trung |
| Gate nghiệm thu | PHAN_CONG tuần 1; ACCEPTANCE T16 | Chưa chứng minh cả ba chạy theo cùng hướng dẫn. PDF chưa được rà trực quan. Không đánh dấu chốt tuần 1. | Cả nhóm; Vương rà PDF, trước 20/10 20:00 |
| Rủi ro Git | PR #5 base trung/week-1 | Stacked tuần 2; sau squash #4 cần đồng bộ có kiểm soát trước xử lý tuần 2. Không đổi base/merge nội dung tuần 2 trong lần này. | Trung, trước review tuần 2 |
| Giới hạn đã công bố | constraints.sql; database/README.md | Không có deferred constraint kiểm tra mọi cận dưới ở COMMIT; truy cập SQL quản trị vẫn cần audit. Không mở API xóa lịch sử. | Quyền/Trung, hoàn thiện khi triển khai tuần 2 |

Chưa phát hiện lỗi code P0/P1 trong phần tuần 1 đã rà. Đây không phải cam kết không còn lỗi. Review tập trung diff/routes/services/validation/CSRF, SQL và dữ liệu/tests liên quan; bằng chứng ảnh/log của tác giả được đọc theo mốc, chưa tái nghiệm thu mọi ảnh/máy.

## Thao tác đã thực hiện

- Review APPROVE #4 tại SHA mới nhất, kiểm tra lại head/base, CI thành công, không conflict, không có unresolved review thread; squash merge thành công, xác minh main tại b51b0afb3b0d03f6fa30a255b1efc614b89a9bbd.
- Review COMMENT có file/vị trí và mức độ trên [#6](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/pull/6) và [#7](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/pull/7). Không tự approve #6.
- Sau squash #4, GitHub báo #7 dirty. Đã xác minh main b51b0af và Trung 5a25395 có cùng tree dde6019; UI Vương là hậu duệ Trung. Tạo merge commit 8c5be9469976333195eb67c9d2689638d02c045f với hai parent Vương/main, giữ tree UI 5489ec1, cập nhật ref fast-forward có expected SHA. #7 trở lại mergeable; vẫn draft. [CI head 8c5be94 — run 39092326435](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/actions/runs/39092326435) đã đạt 46/46, audit sạch. Không sửa code hoặc nhập tuần 2.
- Mở [PR #8](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/pull/8) cho báo cáo, ghi chú và workflow kiểm thử tích hợp. CI snapshot đầu 8953942 đạt 72/72 tích hợp; backend 32/32 cũng xanh. Cập nhật báo cáo chỉ đổi tài liệu; xem tab Checks cho trạng thái CI sau cập nhật.
- Không tạo PR trùng: cả ba nhánh tuần 1 đều đã có PR. Không merge #5, không force push, không xóa nhánh, không ghi thẳng main.
- Nhánh main protected=false; API rulesets trả 403 yêu cầu nâng gói cho repo private, khớp giới hạn trong RULES. Không sửa/bỏ qua quy tắc.
- Báo cáo và ghi chú học chung đưa qua nhánh/PR riêng; không tự approve hoặc merge PR tài liệu của Quyền. Ghi chú chưa phải tài liệu ôn cuối.
- Không thay đổi lịch báo cáo tuần.

## Việc tiếp theo theo thứ tự

1. Trung/Vương review SQL #6, giải quyết phản hồi; Quyền/Trung thống nhất đường import chuẩn.
2. Vương cập nhật bàn giao, xác nhận hợp đồng trên #4, kiểm tra CI ở merge commit đồng bộ, rồi chuyển #7 ready; chạy CI trên SHA thay đổi mới.
3. Dùng kết quả tích hợp SQL + backend/UI mới và review hợp lệ để quyết định merge #6/#7, xác minh SHA ngay trước merge.
4. Cả ba chạy clone mới theo hướng dẫn; Vương ghi expected/actual, ảnh/log và rà PDF. Chốt tuần 1 ngày 20/10 lúc 20:00 khi đủ bằng chứng.
