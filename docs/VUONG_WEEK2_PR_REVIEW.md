# Review phụ thuộc và kiểm tra tích hợp tuần 2 — Vương

> Phạm vi hiện hành 21/10/2026: bỏ T16/máy thứ hai theo quyết định Quyền; demo trên laptop Quyền. Các nhận xét T16 bên dưới là lịch sử của phiên trước, không còn là điều kiện nghiệm thu hoặc release. Không sửa kết quả kiểm thử gốc.

## Xác nhận cuối — 20/10/2026

Vương (`Vuong-it`) đã phản hồi và resolve hai thread do mình tạo trên #5: [responsive](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/pull/5#discussion_r4321140559), [title](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/pull/5#discussion_r4321140844). Đã đọc source đúng head `da59e561b187ee693842efd4c6e943c64201a4a1`: form nối `clinical-form`, base nạp `week2.css`, CSS giới hạn fieldset/control; title lịch sử chỉ định danh trang/bệnh nhân, bảng ở content.

Đã đọc `tests/test_week2_review_regressions.py` tại head trên và log [run 39356597220/job 118412695683](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/actions/runs/39356597220/job/118412695683): `test_history_title_does_not_contain_clinical_tables` và `test_prescription_controls_fit_mobile` đều PASSED; ca mobile kiểm tra 320/390/1440px sau thêm dòng thứ tư. Toàn suite 115 passed/0 skipped trong 18,17s; source checkout merge thử `3e905049703dbf368d8bd8ca93a2f4b9d95bce57` của head `da59e56` với main `20cd47a`. Audit cuối sạch, 11 bảng/9 trigger/1.144 dòng. Hai workflow của head #5 success. Phiên này chỉ đọc source và log CI, không chạy lại local/MySQL/browser.

#11 đã được [Trung APPROVE tại e346a9f](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/pull/11#pullrequestreview-5579919269) trong phạm vi backend/context/JSON. Đã đọc log [run 39280384214/job 118153244300](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/actions/runs/39280384214/job/118153244300): merge thử `f3c169009172b7191d88c9783adb5cf4e9bfb048`, head `e346a9f39b6e4fa932cd689dea85c95008cb1687`, 168 passed/0 skipped trong 60,83s, audit sạch 11 bảng/9 trigger/1.144 dòng. Cả ba workflow của head này success. Không dùng kết quả này thay kiểm thử commit tài liệu tiếp theo hoặc tree tích hợp cuối.

#10 giữ head `1bf9f8b` và approval Vương đã đăng; không review/test lại. #5/#10/#11 chưa merge; không sửa nhánh Trung/Quyền hoặc cập nhật nền. Chờ Quyền nghiệm thu UI và điều phối tích hợp/merge; Vương phối hợp kiểm tra UI sau tích hợp. T16 là cổng tuần 3, chưa chạy. Nội dung bên dưới giữ lịch sử phiên 19/10, các trạng thái “chưa review/CI” của phiên cũ đã được cập nhật bởi mục này.

Ngày 19/10/2026, reviewer GitHub `Vuong-it`. Phạm vi: UI/hợp đồng của Trung và SQL/oracle của Quyền ảnh hưởng phần Vương. Không sửa nhánh người khác, không merge PR hoặc đóng issue #2.

## Phiên bản và kết quả riêng biệt

| Đối tượng | Source thực chạy local | Kết quả | Bằng chứng |
|---|---|---|---|
| #5 Trung, source gốc export bằng git archive | `10c808238ef2f8f4f0a1aabcfc59da19079b38f8` | 108 passed, 0 skipped, 14,79s; kiểm tra 18 URL × 3 viewport | [JUnit](evidence/vuong_review_pr5_20261019_224001/junit.xml), [log](evidence/vuong_review_pr5_20261019_224001/pytest.txt), [results](evidence/vuong_review_pr5_20261019_224001/results.json), [manifest](evidence/vuong_review_pr5_20261019_224001/source_sha256.json) |
| #10 Quyền, source gốc export bằng git archive | `1bf9f8b18342eaf6d0097f3693df1bc02addfcfa` | 78 SQL passed, 0 skipped, 2,55s; không bật backend parity trong phiên SQL này | [JUnit](evidence/vuong_review_pr10_20261019_224013/junit.xml), [log](evidence/vuong_review_pr10_20261019_224013/pytest.txt), [results](evidence/vuong_review_pr10_20261019_224013/results.json), [manifest](evidence/vuong_review_pr10_20261019_224013/source_sha256.json) |
| #11 Vương, source tích hợp | `33901998df480d753985127ed7f7e9a791cbc5fd` | 168 passed, 0 skipped, 47,12s | [JUnit](evidence/vuong_week2_prepare_20261019_224053/junit.xml), [log](evidence/vuong_week2_prepare_20261019_224053/pytest.txt), [results](evidence/vuong_week2_prepare_20261019_224053/results.json), [manifest](evidence/vuong_week2_prepare_20261019_224053/source_sha256.json) |

Local: Windows, Python 3.12.14, MySQL 8.0.46, Chromium 156.0.8078.4; DB mỗi phiên là instance/datadir/port riêng, tên `clinic_vuong_week2_prepare_test`. Không đọc thông tin kết nối DB làm việc. Cả ba phiên thành công có hash seed giữ nguyên, audit SQL cuối 10 tập rỗng, 11 bảng/9 trigger/1.144 dòng, 9 nhóm findings rỗng. Private server được dừng khi runner kết thúc. Bốn phiên trước gặp lỗi hạ tầng/harness trước pytest, không tính đạt; metadata lưu trong archive local Git bỏ qua.

Harness review sao chép từ công cụ chuẩn bị, chỉ đổi ROOT sang snapshot export, gắn SHA thật và thêm đo title/control bounds/JSON/CSRF. Không thay file source/test của PR. `dependencies` trong results là nhãn pin của harness tích hợp; PR5 snapshot không chứa code PR10. Manifest từng snapshot mới là danh sách file thực chạy. Các runner/tập lệnh dựng snapshot được lưu cùng [bằng chứng harness](evidence/vuong_pr_review_harness/README.md).

## #5: nhận xét và trách nhiệm xử lý

[Review COMMENT, commit 10c8082](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/pull/5#pullrequestreview-5574078036). Chưa approve UI gốc.

| Phát hiện | Input / expected | Actual tại head #5 | Sửa trong phần Vương |
|---|---|---|---|
| P2: select thuốc tràn màn hình | GET `/examinations/K0001/prescription`, 320px; form phải nằm trong viewport | document width 376px; cả 3 select có mép phải 376; [ảnh](evidence/vuong_review_pr5_20261019_224001/320-07.png) | CSS giới hạn form/label/fieldset/select tại `fa699a6`; browser regression 320px đạt |
| P2: bảng trong title lịch sử | GET `/reports/history?patient_id=BN001`; title chỉ định danh trang | `page.title()` dài 1.552 ký tự, chứa literal `<h2>/<table>`, thuốc/liều dùng/y tá | Đã đưa bảng vào content, title ngắn tại `fa699a6`; không coi số 108 test là bằng chứng bắt được lỗi này |
| Khoảng trống JSON lỗi | `month=2026-13&format=json`, hoặc patient MISSING | HTTP400/404 đúng nhưng `Content-Type: text/html`; parser JSON không dùng được | Vương thêm `{error:message}` HTTP400/404/422 và cập nhật hợp đồng; success không đổi |

Đã đọc route/field/context/CSRF, redirect 303, `MultiDict` giữ giá trị và field thuốc lặp; STT/giá phía server; điều hướng từ lượt tới thêm bệnh/hỗ trợ/đơn/đóng lượt/khỏi. Suite gốc có browser workflow và rollback/concurrency/validation. Thử thiếu CSRF thực qua HTTP trả 400; thành công Q4 JSON trả consultation/medicine/month/total và Decimal chuỗi. Bản gốc không có context/prefill/đường quay lại đầy đủ; Vương đã bổ sung trong #11, backend ghi nghiệp vụ và schema giữ nguyên.

Các sửa UI/JSON đã tồn tại trong PR #11 trước review, nên không chép ngược vào nhánh Trung. Trung cần review phần adapter/context của Vương; Quyền điều phối phương án nhập các sửa trước nghiệm thu cuối. Review là COMMENT có hai nhận xét inline, không ngầm approve PR #5. Bình luận Trung xác nhận nghiệm thu Windows được ghi nhận là thông tin người chạy cung cấp, không phải phiên này thực hiện.

## #10: sử dụng oracle để nghiệm thu UI

[Review APPROVE, commit 1bf9f8b](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/pull/10#pullrequestreview-5574079099). Tác giả `NeyuQ3306`, khác reviewer. Không phát hiện lỗi chặn trong 5 file thay đổi và phạm vi SQL/oracle/tích hợp.

- Oracle Python dựng từ INSERT seed độc lập; Q3 so đủ 40 bệnh nhân, 7 tập và thuộc tính gốc. So theo tập, không bắt UI theo thứ tự SQL; UI có thể xếp mới trước. Q3 giữ cả đợt khỏi/đang điều trị, không lấy bộ lọc tháng Q1/Q2/Q4 áp vào lịch sử.
- Q1 đếm đợt; Q2 ngày khỏi/cặp lượt-y tá; Q4 tổng riêng phí và thuốc theo đơn giá lịch sử. Đối chiếu 5 tháng và bộ tính tay 2004-02/03: năm nhuận, hôm nay/ngày mai, qua tháng/tái mắc, rỗng, nhiều thuốc/y tá, giá danh mục thay đổi. Fixture biên rollback trên `_test`, đồng hồ MySQL chỉ theo session; expected không lấy từ output backend.
- Workflow riêng #10 chạy SQL, sau đó checkout candidate Trung pin `10c8082`, chép test/seed/queries rồi bật `QUYEN_CHECK_WEEK2=1`. Kết quả candidate không chứng minh UI #11 hay head mới khác. Nhánh Vương đã bật cờ trong CI tích hợp và các test browser/JSON đối chiếu cùng oracle, DB và kỳ tính.
- `queries.sql` chỉ thêm hướng dẫn kỳ nửa mở và cấu trúc 11 tập; không đổi schema/seed/công thức. Các kết quả cần được ghép với kiểm thử UI và lỗi đầu vào của Vương; oracle SQL không kiểm chứng responsive/CSRF/điều hướng.

## CI được xác minh theo SHA

Đã đọc log job, không chỉ nhìn badge hoặc body PR:

| PR / run / job | Source checkout | Kết quả được chứng minh |
|---|---|---|
| [#5 run 39250586251](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/actions/runs/39250586251/job/118053119985) | Merge thử `699edf928a40526dd2f374a0eb6eca3b232c961e`, head `10c8082`, base `20cd47a` | 108 passed; Python 3.11.17/MySQL 8.4.11 |
| [#10 run 39267979479](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/actions/runs/39267979479/job/118112471019) | Merge thử `a6bff3755d6e6c104045e38338fba376523fede9`, head `1bf9f8b` | 78 SQL passed; sau checkout candidate `10c8082`, 52 backend parity passed; Python 3.11.17/MySQL 8.4.11 |
| #11 tại lần kiểm tra review | Head `3390199`, merge thử `832e43a695c2227c8f2910af0f885ed0cb6286ef` | Ba workflow vẫn queued; không đánh dấu CI đạt |

[Trích log và trạng thái](evidence/vuong_pr_review_ci.json). Không lấy 71/45 test của head Quyền cũ hay local 168 của Vương gán cho PR5/10.

Ở lần kiểm tra tiếp theo trước đóng gói, Backend and MySQL run `39278635690`/job `118148774920` đã chuyển `in_progress`; hai workflow Quyền vẫn chờ. Đây chưa phải kết quả đạt. Commit tài liệu sau đó sẽ có CI riêng; không gán run của `3390199` cho head tài liệu mới.

## Tích hợp và phần còn phụ thuộc

Sau fetch và kiểm tra API, #5/#10 vẫn open/chưa merge, main vẫn `20cd47a`; nhánh Vương đã chứa đúng cả hai head qua nền `f8d80c8`. Không cần tạo merge/rebase giả hoặc sửa nhánh khác. #11 chưa có review/thread yêu cầu sửa; các lỗi UI thuộc Vương đã sửa và được chạy lại tại `3390199`. Commit sau phiên này chỉ bổ sung tài liệu/bằng chứng, không đổi source đã test.

Vương hoàn thành UI nghiệp vụ/bốn báo cáo/local T01–T15 và review phụ thuộc trong phạm vi trên. Còn Trung review adapter/context/backend tối thiểu trong #11; reviewer khác review #11 (Vương không self-approve); Quyền điều phối sửa nền sau squash và merge theo RULES. CI #11 chưa được xác nhận thành công, T16 và giới hạn thiết bị/trình duyệt trong bàn giao vẫn giữ nguyên. Không chốt toàn nhóm, không merge/đóng issue.
