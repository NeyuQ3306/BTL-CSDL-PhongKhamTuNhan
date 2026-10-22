# Bàn giao review cuối tuần 3 — Vương

Ngày 21/10/2026, UTC+07:00. **Bước 7 đang thực hiện, chưa nghiệm thu/merge/release.** Nhánh `vuong/week-3`, base/main đã fetch: `f4869299c25fdfd0b711597e30b60ab277120f44`. Vương xác nhận đã hoàn thành bước 6 trong yêu cầu thực hiện bước 7; chi tiết biên bản tập chung chưa được cung cấp, không tự dựng ngày giờ/thời lượng/người tham gia.

## Bản bàn giao và kết quả

- UI bổ sung thông báo ô số tiếng Việt, giữ ràng buộc native/server và phục hồi sau sửa; bốn test Chromium locale en-US kiểm tra bác sĩ/y tá/phí/số lượng, gồm dòng thuốc động. Không đổi backend, API, schema, seed hoặc công thức báo cáo.
- [Hướng dẫn cài/chạy](SETUP.md), [sử dụng](USER_GUIDE.md), [biên bản tuần 3](VUONG_WEEK3_ACCEPTANCE.md), [demo](VUONG_WEEK3_DEMO.md); tài liệu tuần 2 giữ làm lịch sử.
- Suite local cuối bước 4: **179 passed, 0 failure/error/skipped**, Python 3.11.9 / MySQL 8.4.7 / Chromium 156.0.8078.4. [JUnit](evidence/vuong_week3_final_20261021/runner-output/junit.xml), [log](evidence/vuong_week3_final_20261021/runner-output/pytest.txt), [audit](evidence/vuong_week3_final_20261021/runner-output/results.json).
- T01–T15 đều PASS local ở run `20261021_121231`, bao gồm HTTP/SQL/concurrency/rollback; không gọi tất cả là thao tác tay UI. [Input/expected/actual](evidence/vuong_week3_final_20261021/browser-tests/vuong-acceptance/cases.json), [ma trận](VUONG_WEEK3_ACCEPTANCE.md#2-ma-trận-t01t16). Audit seed sạch 11 bảng/9 trigger/1.144 dòng.
- Kết quả thuộc base **cộng candidate** `sha256:045a7c42b12390bc5a1cb911a1ec648215cf66df679b6576a7b22464bb398894`, không thuộc riêng main. [Đối chiếu bàn giao](evidence/vuong_week3_handoff_20261021/verification.json) so sánh hash source hiện tại với manifest cuối, manifest setup và công cụ demo đã diễn tập. Commit bàn giao được nhận diện bằng head PR; các phiên cũ giữ nguyên SHA/diff/manifest thực chạy, không đổi thành SHA mới.
- [Smoke cài/chạy bước 5](VUONG_WEEK3_STEP5_VERIFICATION.md), [hai lần demo tự động và thử mở/dừng server](VUONG_WEEK3_DEMO.md#6-kết-quả-diễn-tập-kỹ-thuật-và-bằng-chứng) có bằng chứng riêng. Không nhận đã chạy lại suite hoặc buổi tập nhóm bằng việc đọc lại bằng chứng.
- `.gitattributes` giữ nguyên byte của bằng chứng tuần 3 khi commit/clone, tránh đổi CRLF/LF làm sai hash manifest. Không thay nội dung bằng chứng gốc.

## T16 và bằng chứng lịch sử

**T16: Không thực hiện theo quyết định nhóm. Actual: Chưa chạy.** Theo thông báo Vương ngày 21/10/2026, không tính PASS hoặc cổng nghiệm thu còn thiếu; không khẳng định chạy được trên máy khác. Các câu chờ máy thứ hai trong hồ sơ/JSON phiên trước quyết định là lịch sử, được ghi đè về mặt trạng thái bằng mục này và biên bản hiện hành; không sửa bằng chứng gốc.

PR [#12 của Trung](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/pull/12) đang có nội dung chờ T16. Quyền/Trung cần đồng bộ phạm vi khi tích hợp; PR bàn giao này không sửa nhánh hoặc PR của Trung, không lấy 207 test của PR #12 thay kết quả ứng viên Vương.

## Trung review kỹ thuật

Tài khoản `ptt172` được xác minh từ tác giả PR backend [#5](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/pull/5), tiêu đề và nội dung nhận bàn giao Trung, khớp lịch sử commit backend. Nhờ review static validation/base template, bốn test hồi quy, công cụ demo private và cách truy vết source/bằng chứng.

**W3-RUN-01/P2 công cụ vẫn mở cho Trung:** runner `tools/vuong_week2_prepare.py` thoát nhưng còn MySQL con trên Windows. Workaround dừng đúng executable/datadir đã được kiểm tra; không có sửa source runner trong PR này. [Sổ lỗi](VUONG_WEEK3_ISSUES.md), [cleanup cuối](evidence/vuong_week3_final_20261021/cleanup.json). Cần Trung sửa và retest cả đường thành công/lỗi, hoặc Quyền ghi quyết định chấp nhận giới hạn. Không đóng lỗi chỉ vì bỏ T16.

## Quyền nghiệm thu và điều phối merge

Nhờ Quyền (`NeyuQ3306`, CODEOWNERS) xem T01–T15, audit, hướng dẫn/demo, quyết định T16 và W3-RUN-01; quyết định nghiệm thu, phối hợp review Trung và squash merge khi đủ điều kiện. Chưa có lỗi SQL/công thức mới được chứng minh; không tạo thêm việc sửa ngoài bằng chứng. Không dùng `Closes` cho issue chung.

Sau merge, ghi SHA main thực tế, so sánh source thực thi với bản đã nghiệm thu, chạy nhanh demo trên DB riêng. Nếu tree thực thi thay đổi thì chạy lại kiểm tra bị ảnh hưởng và suite cuối; không dùng bằng chứng candidate cho tree khác. Quyền chốt release/tag sau các cổng nghiệm thu.

- [ ] Trung review kỹ thuật và xử lý các nhận xét.
- [ ] Quyền quyết định nghiệm thu, bao gồm lỗi công cụ còn mở.
- [ ] PR được merge theo điều phối của Quyền.
- [ ] Xác minh main sau merge và smoke demo; retest/suite nếu source thay đổi.
- [ ] Quyền chốt release/tag.

Không đánh dấu bước 7 hoàn thành trước khi có kết quả review, merge và kiểm tra sau merge. Trạng thái PR/CI mới được ghi trong PR; kết quả local và CI phải tách riêng.

## Bổ sung sau review cleanup PR #13 — 21/10/2026

Đã sửa đường lỗi demo: dùng riêng helper PR #12 `d566abf` (nguồn Trung, cần psutil) và ghi session/đóng log qua các bước độc lập, phân biệt workload với cleanup. Không merge nhánh Trung, không đổi app/SQL hoặc runner tuần 2. [Bằng chứng và giới hạn mới](evidence/vuong_week3_cleanup_final_20261021/README.md), [sổ lỗi](VUONG_WEEK3_ISSUES.md). 179 test/ảnh/biên bản cũ giữ đúng source cũ; CI head mới báo riêng trong PR.

Còn chờ Trung re-review cleanup/head mới; Quyền nghiệm thu T01–T15 và bản cuối trên laptop Quyền, điều phối tích hợp/merge và xử lý W3-RUN-01. Chưa tự approve, resolve thay Trung, merge, release/tag; T16 không chạy theo quyết định nhóm.
