# Sổ lỗi tuần 3 của Vương

Cập nhật bước 7 ngày 21/10/2026: W3-RUN-01 vẫn mở cho Trung; W3-UX-01 đã sửa/retest. [Bàn giao review cuối](VUONG_WEEK3_HANDOFF.md) cập nhật trạng thái PR/nhóm; các câu chưa gửi/chưa commit ở mốc bước 4 bên dưới là lịch sử. T16 **Không thực hiện theo quyết định nhóm**, actual **Chưa chạy**, không tính PASS hoặc việc chờ.

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
- **Trạng thái: chờ Trung xử lý source runner; workaround đã thực hiện và kiểm tra ở phiên Bước2.** Không nhận lỗi source đã sửa. Phiên ứng viên cuối đã tái hiện: runner exit0 nhưng còn MySQL con PID13296/cổng57136. Đã xác minh executable/datadir, dừng riêng, chờ và kiểm tra0 process/các cổng đóng; [cleanup mới](evidence/vuong_week3_final_20261021/cleanup.json). Bản thử: SHA nền + candidate045a7c42 nêu trên. **Đã kiểm tra lại workaround, chưa sửa/đóng lỗi source runner**; cần Trung xử lý theo hồ sơ.

## W3-ENV-01 — Playwright bị kẹt trước khi runner bắt đầu trong sandbox

- Mức ảnh hưởng: **P2 môi trường ở thời điểm phát hiện**, không phải failure sản phẩm.
- Phụ trách xử lý phiên: trợ lý thay mặt Vương; không cần đổi backend/SQL.
- Source/môi trường: SHA nền nêu trên, Python3.11.9/Playwright trong sandbox; runner chưa chạy, chưa thu thập test.
- Input/tái hiện: khởi động driver Playwright từ script điều phối trong execution bị hạn chế.
- Expected/actual: driver sẵn sàng / không hoàn thành khởi động trước suite.
- Xử lý: dừng đúng hai Python của tác vụ, chạy lại qua cơ chế cấp quyền thực thi; suite Bước2 đạt175/175.
- Bằng chứng: [metadata lần đầu](evidence/vuong_week3_regression_20261021/setup-attempt1.json), [sự cố và xử lý](evidence/vuong_week3_regression_20261021/setup-issues.json), [JUnit sau retry](evidence/vuong_week3_regression_20261021/runner-output/junit.xml).
- **Trạng thái: đã kiểm tra lại bằng retry thành công**, không coi là sửa source hoặc lỗi backend cần bàn giao.

## Trạng thái bàn giao

Không có lỗi backend/SQL/nghiệp vụ chặn nào được chứng minh trong Bước2–3. UI đã có retest trực tiếp và suite cuối179/179 đạt, audit sạch. **Tiêu chí local Bước4 đạt**, không có lỗi chặn demo/sai nghiệp vụ còn được chứng minh; lỗi công cụ W3-RUN-01 vẫn mở cho Trung, có workaround và chưa tự đóng. T16 **không thực hiện theo quyết định Quyền và cả nhóm**, do Vương thông báo ngày 21/10/2026; chưa chạy, không tính đạt và không còn cổng nghiệm thu. Quyết định này không đóng W3-RUN-01. Chưa gửi tin nhắn, đăng bình luận, push, PR hoặc merge.

Bản nháp trao đổi từng người: [VUONG_WEEK3_STEP4_HANDOFF.md](VUONG_WEEK3_STEP4_HANDOFF.md). Người dùng chưa cần tự chạy lệnh để xác minh lại phần local đã có bằng chứng.
