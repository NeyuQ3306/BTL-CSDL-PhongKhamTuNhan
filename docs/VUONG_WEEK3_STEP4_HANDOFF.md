# Bàn giao Bước 4 tuần 3 — bản nháp chưa gửi

Ngày21/10/2026, UTC+07:00. Người chuẩn bị: trợ lý Codex thay mặt Vương. Nội dung dưới đây **chưa gửi cho ai, chưa đăng issue/PR/bình luận**.

Ứng viên: SHA nền `f4869299c25fdfd0b711597e30b60ab277120f44` + sửa UI/test chưa commit, [candidate và manifest124](evidence/vuong_week3_final_20261021/candidate.json). **179 pass / 0 failure/error/skip**, audit sạch; [bằng chứng cuối](evidence/vuong_week3_final_20261021/README.md). [Sổ lỗi và trạng thái](VUONG_WEEK3_ISSUES.md).

## Việc tối thiểu cần chuyển

Vẫn cần chuyển Trung phần W3-RUN-01 nếu chưa gửi: lỗi cleanup runner còn mở và không liên quan quyết định bỏ T16. Không cần chuyển nguyên bản dài hoặc gửi lại đề nghị chốt máy. Quyền chỉ cần nhận tóm tắt kết quả local và lỗi còn lại nếu chưa có thông tin; không có lỗi SQL/công thức mới cần bàn giao sửa. Các đoạn dưới là bản nháp, trợ lý chưa gửi.

## Gửi Trung

> Trung ơi, bản UI tuần3 đã sửa W3-UX-01 và chạy lại179/179 test, không có failure/error/skip, audit sạch. Còn W3-RUN-01/P2 ở công cụ kiểm thử Windows: chạy tools/vuong_week2_prepare.py không có --serve, sau exit0 MySQL con vẫn giữ cổng. Phiên cuối ghi PID13296/cổng57136; mình đã dừng đúng instance và xác nhận sạch, chưa sửa source runner. Nhờ bạn xem phần finally: ưu tiên SHUTDOWN trên kết nối private còn sống, chờ process/cổng thoát, fallback chỉ xử lý cây đúng datadir; kiểm tra cả đường thành công/lỗi. Bằng chứng và bước tái hiện xem sổ lỗi/bản ghi cleanup liên kết bên dưới. Không có lỗi validation/transaction backend mới đã được chứng minh cần bạn sửa trong suite hiện tại.

- [W3-RUN-01 và đề xuất](VUONG_WEEK3_ISSUES.md).
- [Source cuối, lệnh và môi trường](evidence/vuong_week3_final_20261021/session.json).
- [Cleanup — runner_issue_reproduced=true](evidence/vuong_week3_final_20261021/cleanup.json).
- Khi Trung có thay đổi runner: chạy lại ca cleanup theo executable/datadir/cổng và suite nếu bản ứng viên thay đổi. Không tự nhận đã sửa chỉ vì có commit.

## Gửi Quyền

> Quyền ơi, phần local Bước4 của Vương đã sửa và kiểm tra lại thông báo ô số tiếng Việt; full suite179/179 đạt trên Python3.11.9/MySQL8.4.7/Chromium156, audit sạch, T01–T15 có kết quả mới đúng candidate/manifest. Không thay API, schema hoặc công thức; không có lỗi SQL/nghiệp vụ chặn còn được chứng minh trong suite. Còn W3-RUN-01/P2 công cụ đã có workaround dừng riêng instance, bàn giao Trung sửa source; nhờ bạn xem giới hạn này khi quyết định nghiệm thu. Theo quyết định bạn và cả nhóm đã chốt, hồ sơ ghi T16 không thực hiện, actual chưa chạy, không tính đạt; không còn yêu cầu chốt máy hoặc lịch T16. Đây chưa phải nghiệm thu nhóm/CI/release.

- [Bảng T01–T16 hiện hành](VUONG_WEEK3_ACCEPTANCE.md).
- [JUnit cuối](evidence/vuong_week3_final_20261021/runner-output/junit.xml), [audit/source](evidence/vuong_week3_final_20261021/README.md).
- Chưa có đề nghị đổi schema/SQL/công thức; không tạo thêm việc sửa SQL khi không có bằng chứng lỗi.

## Ghi chú bàn giao cho Vương

> W3-UX-01 đã sửa trong static/base UI; bốn regression mới kiểm tra locale en-US, số âm/0/vượt max/số lẻ, giữ dữ liệu, phục hồi và dòng thuốc động. Đã xem ảnh tooltip IAB tiếng Việt. Source chưa commit, cần giữ manifest124 và diff cùng kết quả179/179; nếu sửa tiếp code thì xác định retest cần chạy lại. Chưa stage bằng chứng tuần2 cũ, chưa gửi thông báo ra ngoài hoặc làm Bước5–7.

- [Ảnh tooltip sau sửa](evidence/vuong_week3_step4_retest_20261021/doctor-vietnamese.jpg).
- [Actual regression](evidence/vuong_week3_final_20261021/browser-tests/vuong-week3/quantity.json), [IAB phục hồi](evidence/vuong_week3_step4_retest_20261021/interactive-retest.json).
- Việc tối thiểu người dùng: chuyển Trung đoạn W3-RUN-01 kèm liên kết sổ lỗi/bằng chứng nếu chưa gửi. Nếu Quyền chưa nhận kết quả Bước 4, chuyển thêm đoạn tóm tắt dành cho Quyền; không cần xin chốt T16 nữa hoặc tự chạy lại các lệnh local đã có bằng chứng.
