# Bàn giao tuần 3 theo ứng viên tích hợp #17 — Vương

Cập nhật **22/10/2026**, UTC+07:00, dựa trên trạng thái GitHub và hồ sơ đã có. **Chưa merge vào main, chưa chốt nghiệm thu toàn nhóm hoặc release.** Trợ lý cập nhật tài liệu thay mặt Vương; không chạy lại suite/app/MySQL hoặc xác nhận buổi tập chung trong lần này.

## 1. Source và phạm vi hiện hành

| Mốc | Định danh | Ý nghĩa |
|---|---|---|
| Main ở lần kiểm tra 22/10 | `f4869299c25fdfd0b711597e30b60ab277120f44` | Nền trước tích hợp tuần 3 |
| [PR #17](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/pull/17), `quyen/week3-integration` | `1964a4a10e8634384ce2ebf5951bc66e5525f755` | Ứng viên tích hợp #12/#13/#14/#15 |
| Source Windows Quyền thực chạy | `dd1f41e4b1459bb82b5d288eb2a02d85de0d81b3` | Head trên chỉ thêm 12 file evidence, không đổi code/SQL/test theo đối chiếu của Trung |
| Checkout CI thử merge #17 | `1dcd4b76babffe8aa5070a345a18d357e94eab78` | Head `1964a4a` ghép với main `f486929`, không phải đã merge main |
| [PR #13](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/pull/13), `vuong/week-3` | `4f68099054fcce6fec252a74b0e36484c31ab4e7` | Phần UI/demo/tài liệu Vương đã được review, nằm trong #17 |
| [PR #16](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/pull/16) | `870df424d252763b6a331c2e26c44debb1654e34` | Dọn upstream riêng, **chưa nằm trong #17** |

Các SHA trên định danh bản tích hợp và các phiên trước cập nhật tài liệu này; không nhận commit tài liệu mới đã được chạy Windows. [SETUP](SETUP.md) pin snapshot #17, cài Python3.11/MySQL8.4, nhập SQL trên DB mới, audit rồi chạy app; [USER_GUIDE](USER_GUIDE.md) hướng dẫn UI; [DEMO](VUONG_WEEK3_DEMO.md) mở seed trên instance private cho nhóm.

## 2. Review và việc đã bàn giao

- #13: Trung [APPROVED tại head4f68099](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/pull/13#pullrequestreview-5602549788), [resolve thread P2 cleanup](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/pull/13#discussion_r4339014574). Không còn chờ re-review bản sửa này. Demo luôn thử các bước cleanup tiếp theo và ghi session cuối khi SHUTDOWN/close/wait lỗi, phân biệt workload/cleanup; giữ helper có nguồn Trung và dependency psutil.
- #17: Trung [APPROVED tích hợp tại1964a4a](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/pull/17#pullrequestreview-5608460590). Approval xác nhận phạm vi ghép nhánh đã review, chưa thay quyết định nghiệm thu/release của Quyền.
- #16: Vương [APPROVED cleanup](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/pull/16#pullrequestreview-5608581327); Quyền chọn thời điểm tích hợp. 7 file upstream vẫn hiện diện trong snapshot #17, không được hướng dẫn như đã xóa.
- SQL gộp `database/project1_submission.sql` từ #15 nằm trong #17: chọn default schema mới trống trong tab Workbench rồi chạy toàn bộ một lần. Không có CREATE DATABASE/USE trong file; không nhập chồng bộ nguồn và file gộp. [Review SQL của Vương](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/pull/15#pullrequestreview-5602203513) ghi rõ phạm vi và chênh hash local/Git chưa kết luận cùng byte.
- Thông báo ô số tiếng Việt, CRUD/luồng khám/bốn báo cáo, T01–T15, hướng dẫn và kịch bản đã bàn giao; kết quả mỗi phiên vẫn giữ source và người thực thi riêng.

## 3. Bằng chứng Windows của Quyền trong #17

Môi trường được Quyền báo cáo: Python3.11.9/MySQL8.4.11/Chromium156.0.8078.4, source `dd1f41e`, MySQL datadir/instance riêng. Trợ lý đọc hồ sơ, không trực tiếp chạy trên laptop Quyền.

| Phiên 22/10/2026 | Kết quả | Hồ sơ |
|---|---|---|
| `073906_519771` | 194 pass/1 fail; acceptance browser HTTP503, lượt chụp BN001 có503; PR ghi MySQL2003, nguyên nhân chưa xác định | [results](evidence/vuong_week2_prepare_20261022_073906_519771/results.json), [JUnit](evidence/vuong_week2_prepare_20261022_073906_519771/junit.xml), [log](evidence/vuong_week2_prepare_20261022_073906_519771/pytest.txt) |
| `074813_773699` | 195 tests/0 failure/error/skipped; không tái hiện503 | [results](evidence/vuong_week2_prepare_20261022_074813_773699/results.json), [JUnit](evidence/vuong_week2_prepare_20261022_074813_773699/junit.xml) |
| `075907_328633` | `PYTEST_ADDOPTS="tests week3_checks"`; 236 tests/0 failure/error/skipped, preparation_success=true | [results](evidence/vuong_week2_prepare_20261022_075907_328633/results.json), [JUnit](evidence/vuong_week2_prepare_20261022_075907_328633/junit.xml), [manifest](evidence/vuong_week2_prepare_20261022_075907_328633/source_sha256.json), [log](evidence/vuong_week2_prepare_20261022_075907_328633/pytest.txt) |

Phiên236: seed giữ nguyên, 11 bảng/9 trigger/1.144 dòng, 10 tập audit SQL/9 nhóm findings rỗng; cleanup success, port_closed/launcher_exited=true, remaining_pids/errors/cleanup_errors rỗng; .env giữ nguyên. Quyền xác nhận /health/db, BN001 và doanh thu10/2026: khám4.680.000 + thuốc5.820.800 = **10.500.800đ**. Không lấy kết quả hai phiên sau để xóa phiên lỗi hoặc nhận lỗi2003 đã sửa.

12 file mới chỉ gồm results/pytest/JUnit/manifest của ba phiên. Ảnh JSON tham chiếu còn trên máy Quyền, không có trong 12 file; không nhận đã xem ảnh đó. Metadata scope/dependencies mang tên tuần2 là lịch sử của runner, không thay source_sha/tập test thực chạy.

## 4. CI của bản tích hợp

Bốn workflow head `1964a4a` đã completed/success ở lần kiểm tra 22/10:

- [Trung integrated39703489223](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/actions/runs/39703489223): theo review Trung đã đọc log, Linux236passed/0skip (63,06s), Windows cleanup2passed/0skip (28,63s); checkout thử merge `1dcd4b7`, audit sạch.
- [Backend39703489090](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/actions/runs/39703489090), [Database39703489202](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/actions/runs/39703489202), [Independent reports39703489281](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/actions/runs/39703489281): success. Backend candidate pin riêng trong workflow độc lập không được gán thành source backend của #17.

Lần cập nhật tài liệu này xác minh trạng thái workflow qua GitHub; số test và chi tiết log ở gạch đầu dòng đầu được dẫn từ [review Trung](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/pull/17#pullrequestreview-5608460590), không nhận trợ lý chạy lại hoặc đọc lại mọi log. CI này không thay nghiệm thu file SQL gộp Workbench hoặc buổi demo nhóm.

## 5. Lỗi còn theo dõi và việc chờ xác nhận

- **W3-RUN-01 còn mở trong sổ lỗi:** #12 đã sửa runner; source được ghép vào #17 và Trung review tích hợp cùng bằng chứng Windows success/error. Trung/Quyền chưa ghi quyết định đóng sổ lỗi; không còn ghi “runner #17 chưa sửa”. Không dùng resolve cleanup demo #13 hoặc bỏ T16 để tự đóng lỗi runner.
- **HTTP503/MySQL2003:** giữ trạng thái theo dõi, chưa rõ nguyên nhân, chưa chứng minh đã sửa. Nếu tái diễn, giữ app/MySQLconsole, URL/cổng/instance và bước/input/thời điểm để Trung điều tra; Quyền ghi quyết định chấp nhận/hoãn chốt. Không retry mù thao tác ghi.
- **T16 không thực hiện theo quyết định Quyền**, actual chưa chạy, không tính PASS và không phải điều kiện còn thiếu. Giữ [issue#3](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/issues/3) và #14 làm nguồn quyết định.
- Vương đã xác nhận bước6 ngày21/10; chưa có chi tiết ngày giờ/thành phần/thời lượng/vướng mắc của buổi tập chung. Giữ phân vai/checklist dự kiến trong DEMO, không tự ghi nhóm đã tập hoặc đạt13phút.
- Quyền chọn phạm vi #16, cả nhóm rà PDF–SQL–app/README/bộ nộp. Chưa có xác nhận hoàn tất toàn bộ bộ nộp.

## 6. Sau review tài liệu và merge

- [x] Trung review/approve #13 và resolve P2 cleanup demo.
- [x] Trung review/approve #17 tại1964a4a; CI head này xanh.
- [x] Vương review/approve #16 tại870df42; chưa tích hợp vào #17.
- [ ] Trung/Quyền quyết định đóng W3-RUN-01 và Quyền ghi quyết định về lỗi2003 còn theo dõi.
- [ ] Nhóm xác nhận tài liệu/bộ nộp, chi tiết tập demo và phạm vi cuối; Quyền điều phối squash merge.
- [ ] Ghi SHA main sau merge, so source thực thi với ứng viên đã thử, smoke kết nối/luồng demo trên DB riêng. Chỉ retest phần ảnh hưởng khi hành vi/source đổi hoặc có dấu hiệu lỗi; không chạy lặp toàn suite chỉ vì đổi SHA/tài liệu.
- [ ] Quyền chốt release/tag khi đủ điều kiện.

Không tự đóng #12–#15 hoặc issue#3. Chưa đánh dấu bước7 hoàn thành.

## 7. Hồ sơ lịch sử của Vương ngày21/10

Giữ nguyên [ma trận T01–T15](VUONG_WEEK3_ACCEPTANCE.md#2-ma-trận-t01t16), [suite179 và candidate/diff](evidence/vuong_week3_final_20261021/README.md), [đối chiếu bàn giao](evidence/vuong_week3_handoff_20261021/verification.json), [smoke hướng dẫn bước5](VUONG_WEEK3_STEP5_VERIFICATION.md), [diễn tập kỹ thuật](VUONG_WEEK3_DEMO.md#6-kết-quả-diễn-tập-kỹ-thuật-và-bằng-chứng) và [hồ sơ sửa cleanup](evidence/vuong_week3_cleanup_final_20261021/README.md). Candidate045a7c42/179tests thuộc SHA nền cộng source sửa chưa commit lúc chạy; CI195tests thuộc head#13/merge checkout ghi riêng trong PR. Không gán các phiên này cho SHA#17, main sau merge hoặc commit tài liệu mới. Bằng chứng gốc không sửa.
