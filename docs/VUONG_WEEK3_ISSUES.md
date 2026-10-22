# Sổ lỗi tuần 3 của Vương

> **Cập nhật tích hợp 22/10/2026:** trạng thái hiện hành, danh sách file nộp và quyết định lỗi được ghi tại [WEEK3_FINAL_STATUS.md](WEEK3_FINAL_STATUS.md). Các đoạn mô tả #17 chưa merge, #16 chưa tích hợp hoặc W3-RUN-01 chờ đóng bên dưới là snapshot bàn giao trước cập nhật này; giữ để truy vết, không dùng làm checklist hiện hành.

Cập nhật **22/10/2026 theo #17 head1964a4a**: #13 đã được Trung approve/resolve cleanup; W3-UX-01 và W3-DEMO-02 đã sửa/retest, W3-RUN-01 đã có sửa tích hợp nhưng vẫn mở chờ Trung/Quyền quyết định đóng. **W3-DB-01 (HTTP503/MySQL2003) còn theo dõi**, chưa kết luận nguyên nhân/đã sửa. [Bàn giao hiện hành](VUONG_WEEK3_HANDOFF.md) phân biệt Windows của Quyền, CI và các phiên lịch sử. T16 không thực hiện, actual chưa chạy, không tính PASS. Các câu chưa commit/gửi/chờ sửa ở mốc21/10 bên dưới chỉ áp dụng phiên cũ.

Liên kết [hồ sơ nghiệm thu](VUONG_WEEK3_ACCEPTANCE.md). Chỉ ghi lỗi/quan sát có bằng chứng Bước 2–3; ưu tiên cài/chạy, dữ liệu, tiền/báo cáo và demo trước hiển thị/câu chữ. Người thực hiện công cụ: trợ lý Codex thay mặt Vương.

## W3-UX-01 — Thông báo kiểm tra ô số phụ thuộc ngôn ngữ trình duyệt

- Mức ảnh hưởng: **P3**, thông báo tiếng Anh, vẫn chặn dữ liệu sai; không có mất dữ liệu hoặc sai tiền.
- Phụ trách: **Vương — UI**, không chuyển quy tắc validation backend sang frontend.
- Source phát hiện: `f4869299c25fdfd0b711597e30b60ab277120f44`; Python3.11.9/MySQL8.4.7, Codex IAB trên Windows (phiên bản IAB chưa xác minh).
- Input/tái hiện: mở thêm bác sĩ/y tá, điền các trường hợp lệ và nhập thâm niên `-1`; hoặc form khám nhập phí `-1`; hoặc kê đơn nhập số lượng `0/-1`. Bấm lưu, xem `validationMessage` và việc trình duyệt ngăn POST.
- Expected: thông báo tiếng Việt, giữ input; sửa về số hợp lệ tiếp tục được; min/max/số nguyên, validation server và trường thuốc trống tùy chọn giữ nguyên.
- Actual trước sửa: `Value must be greater than or equal to 0/1.`; dữ liệu sai bị chặn. [Ghi nhận gốc](evidence/vuong_week3_ui_20261021/findings.json), [actual các ô số](evidence/vuong_week3_ui_20261021/ui-observations.json).
- Sửa: script UI `number-validation.js` xử lý sự kiện invalid/input/change, dùng customValidity tiếng Việt và xóa trạng thái lỗi khi người dùng sửa. Dùng event delegation cho dòng thuốc thêm mới; không tắt native validation hoặc thay giới hạn/API/server. Base template của UI nạp script.
- Định danh bản sửa: SHA nền trên + diff/manifest phiên Bước 4 (chưa commit); không nhận commit nền tự chứa sửa đổi.
- **Trạng thái: đã sửa và đã kiểm tra lại ngày21/10/2026.** IAB trực tiếp: -1/101/1.5 báo tiếng Việt, sửa5 hết custom error và giữ input. Bốn regression Chromium en-US doctor/nurse/fee/quantity đạt; full suite179/179,0failure/error/skip. Xem [ảnh](evidence/vuong_week3_step4_retest_20261021/doctor-vietnamese.jpg), [IAB actual](evidence/vuong_week3_step4_retest_20261021/interactive-retest.json), [JUnit cuối](evidence/vuong_week3_final_20261021/runner-output/junit.xml). Định danh bản kiểm tra lại: SHA nền + [candidate045a7c42/diff/manifest124](evidence/vuong_week3_final_20261021/candidate.json). Chưa commit/review nhóm; enhancement cần JavaScript, không nhận đã Việt hóa native khi JS tắt.

## W3-RUN-01 — Runner còn MySQL con sau khi kết thúc trên Windows

- Mức ảnh hưởng: **P2 đối với công cụ kiểm thử**: chiếm cổng/tài nguyên sau suite; không có bằng chứng mất dữ liệu, sai báo cáo hoặc chặn demo của ứng dụng.
- Phụ trách: **Trung** xem xét runtime/cleanup; Vương bàn giao bằng chứng. Không tự sửa `tools/vuong_week2_prepare.py` khi chưa phối hợp.
- Source/môi trường: SHA `f4869299c25fdfd0b711597e30b60ab277120f44`, Python3.11.9/MySQL8.4.7 trên Windows, không dùng `--serve`.
- Input/tái hiện: chạy runner bằng Python test và mysqld private; sau khi runner exit0 kiểm tra cổng DB và process có executable/datadir của phiên đó.
- Expected: app/DB private đóng cổng, không còn MySQL con thuộc datadir phiên chạy.
- Actual Bước2: suite175/175 đạt nhưng DB private còn PID27944, cổng56310; runner terminate parent chưa đảm bảo hết cây tiến trình. Đã dừng riêng đúng executable/datadir và xác nhận đóng cổng.
- Bằng chứng: [session trước cleanup](evidence/vuong_week3_regression_20261021/session.json), [cleanup cuối](evidence/vuong_week3_regression_20261021/cleanup.json), [runner/log](evidence/vuong_week3_regression_20261021/README.md).
- Đề xuất: gửi SHUTDOWN qua kết nối private còn sống, chờ process/cổng thoát; có fallback chỉ dọn cây process đúng datadir nếu lỗi. Thử cả suite thành công và đường thoát lỗi; không dừng MySQL hệ thống hoặc ghi credentials vào log.
- **Lịch sử trước bản sửa #12:** chờ Trung xử lý source runner; workaround đã thực hiện và kiểm tra ở phiên Bước2. Tại mốc này chưa sửa source. Phiên ứng viên cuối đã tái hiện: runner exit0 nhưng còn MySQL con PID13296/cổng57136. Đã xác minh executable/datadir, dừng riêng, chờ và kiểm tra0 process/các cổng đóng; [cleanup mới](evidence/vuong_week3_final_20261021/cleanup.json). Bản thử: SHA nền + candidate045a7c42 nêu trên. **Đã kiểm tra lại workaround, chưa sửa/đóng lỗi source runner**; cần Trung xử lý theo hồ sơ.

**Trạng thái hiện hành 22/10: vẫn mở, chờ quyết định đóng của Trung/Quyền.** #12 head`d566abf` đã sửa runner với helper xác minh datadir/port và fallback đúng executable/datadir, kiểm tra PID/cổng/launcher. #17 đã tích hợp bản sửa; Trung [approve tích hợp](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/pull/17#pullrequestreview-5608460590), dẫn Windows CI success/error2passed cùng phiên Windows236tests của Quyền [cleanup đạt](evidence/vuong_week2_prepare_20261022_075907_328633/results.json). Đây là xác nhận sửa/tích hợp và bằng chứng, chưa có quyết định đóng sổ lỗi. Không dùng bỏ T16 hoặc resolve cleanup demo#13 để đóng W3-RUN-01.

## W3-ENV-01 — Playwright bị kẹt trước khi runner bắt đầu trong sandbox

- Mức ảnh hưởng: **P2 môi trường ở thời điểm phát hiện**, không phải failure sản phẩm.
- Phụ trách xử lý phiên: trợ lý thay mặt Vương; không cần đổi backend/SQL.
- Source/môi trường: SHA nền nêu trên, Python3.11.9/Playwright trong sandbox; runner chưa chạy, chưa thu thập test.
- Input/tái hiện: khởi động driver Playwright từ script điều phối trong execution bị hạn chế.
- Expected/actual: driver sẵn sàng / không hoàn thành khởi động trước suite.
- Xử lý: dừng đúng hai Python của tác vụ, chạy lại qua cơ chế cấp quyền thực thi; suite Bước2 đạt175/175.
- Bằng chứng: [metadata lần đầu](evidence/vuong_week3_regression_20261021/setup-attempt1.json), [sự cố và xử lý](evidence/vuong_week3_regression_20261021/setup-issues.json), [JUnit sau retry](evidence/vuong_week3_regression_20261021/runner-output/junit.xml).
- **Trạng thái: đã kiểm tra lại bằng retry thành công**, không coi là sửa source hoặc lỗi backend cần bàn giao.

## Trạng thái bàn giao ở mốc Bước4 ngày21/10 (lịch sử)

Không có lỗi backend/SQL/nghiệp vụ chặn nào được chứng minh trong Bước2–3. UI đã có retest trực tiếp và suite cuối179/179 đạt, audit sạch. **Tiêu chí local Bước4 đạt**, không có lỗi chặn demo/sai nghiệp vụ còn được chứng minh; lỗi công cụ W3-RUN-01 vẫn mở cho Trung, có workaround và chưa tự đóng. T16 **không thực hiện theo quyết định Quyền và cả nhóm**, do Vương thông báo ngày 21/10/2026; chưa chạy, không tính đạt và không còn cổng nghiệm thu. Quyết định này không đóng W3-RUN-01. Chưa gửi tin nhắn, đăng bình luận, push, PR hoặc merge.

Bản nháp trao đổi từng người: [VUONG_WEEK3_STEP4_HANDOFF.md](VUONG_WEEK3_STEP4_HANDOFF.md). Người dùng chưa cần tự chạy lệnh để xác minh lại phần local đã có bằng chứng.

## W3-DEMO-02 — Cleanup demo bị ngắt khi SHUTDOWN/close/wait lỗi

- Mức P2 công cụ; Trung yêu cầu sửa tại [thread PR #13](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/pull/13#discussion_r4336604656), head phát hiện `0a8aecc`. Phụ trách sửa: Vương.
- Trước sửa: exception trong finally có thể bỏ qua proc.wait/log.close/session cuối. Sau sửa: các bước app/MySQL/log/check độc lập, session phân biệt workload và cleanup; giữ lỗi workload gốc, không ghi message có thể chứa credentials.
- Lấy riêng helper của Trung từ PR #12 `d566abf` với dependency psutil; không merge nhánh Trung. [Kiểm thử và bằng chứng mới](evidence/vuong_week3_cleanup_final_20261021/README.md). Trạng thái hiện hành: đã sửa/retest, Trung [APPROVED head4f68099](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/pull/13#pullrequestreview-5602549788) và [resolve thread](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/pull/13#discussion_r4339014574). Bản sửa nằm trong #17; không còn chờ re-review cleanup này.
- **W3-RUN-01 vẫn mở** chờ Trung/Quyền quyết định đóng; runner/helper #12 đã nằm trong #17 và được Trung review, xem mục W3-RUN-01. T16 không thực hiện, không ghi PASS.

## W3-DB-01 — HTTP503/MySQL2003 gián đoạn trong phiên tích hợp Windows

- Trạng thái: **theo dõi, chưa rõ nguyên nhân, chưa chứng minh đã sửa**. Trung phụ trách điều tra backend/kết nối; Quyền là người chạy và quyết định chốt bản cuối; Vương ghi nhận bước/ảnh/log nếu tái diễn.
- Source thực chạy `dd1f41e4b1459bb82b5d288eb2a02d85de0d81b3`, Windows/Python3.11.9/MySQL8.4.11/Chromium156.0.8078.4 trên laptop Quyền. #17 head1964a4a chỉ thêm12file evidence. Không đồng nhất với lỗi cleanup W3-RUN-01.
- Phiên `20261022_073906_519771`: acceptance browser tải báo cáo bệnh bị503; lượt chụp lịch sử BN001 cũng503. Expected route phản hồi thành công với DB private đang hoạt động; actual194pass/1fail. [results](evidence/vuong_week2_prepare_20261022_073906_519771/results.json), [pytest](evidence/vuong_week2_prepare_20261022_073906_519771/pytest.txt), [JUnit](evidence/vuong_week2_prepare_20261022_073906_519771/junit.xml). MySQLcode2003 và server không crash/cleanup shutdown bình thường là thông tin Quyền báo trong [PR#17](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/pull/17), không nhận đã trực tiếp xem console chưa đưa vào repo.
- Hai phiên sau: [195tests](evidence/vuong_week2_prepare_20261022_074813_773699/results.json) và [236tests](evidence/vuong_week2_prepare_20261022_075907_328633/results.json) đều0failure/error/skip; CI#17 xanh. Chưa tái hiện không chứng minh lỗi đã sửa; giữ nguyên phiên thất bại.
- Nếu tái diễn: ghi thời điểm, route/input/thao tác, SHA, instance/cổng/datadir; giữ app console/MySQLconsole và log trước cleanup, không đưa credentials vào hồ sơ. Không retry mù thao tác ghi; Trung điều tra bằng chứng, Quyền ghi quyết định chấp nhận hoặc hoãn chốt. Không tự đánh dấu lỗi đã đóng hoặc nghiệm thu/release đạt.
