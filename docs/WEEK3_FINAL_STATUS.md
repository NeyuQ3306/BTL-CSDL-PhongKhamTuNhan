# Bàn giao kỹ thuật tuần 3 và bộ nộp

Cập nhật chuẩn bị nộp 02/11/2026: xem [SUBMISSION](SUBMISSION.md) cho hạn chính thức 15/11, điểm và trạng thái DOCX/PPTX/quyền truy cập. Phần dưới là hồ sơ kỹ thuật ngày 22/10; PR #17 đã merge vào main 98bd267. Những cập nhật này không xác nhận một phiên kiểm thử mới.

Cập nhật 22/10/2026, giờ Việt Nam. Quyền đã yêu cầu tự động kiểm tra và hoàn thiện phần còn lại. Bản này ghi quyết định tích hợp; không tạo bằng chứng tập nhóm, không nhận giảng viên đã duyệt. Trạng thái merge/CI mới nhất: [PR #17](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/pull/17).

## Phạm vi và source

- #12 backend/cleanup, #13 UI/demo, #14 bỏ T16 và #15 SQL gộp nằm trong source Windows `dd1f41e4b1459bb82b5d288eb2a02d85de0d81b3`.
- `1964a4a` chỉ thêm 12 file bằng chứng. Trung đã review/APPROVE #17; không đổi executable source sau Windows acceptance.
- #18 được Trung APPROVE và squash vào nhánh tích hợp tại `179ef27`.
- #16 được Vương APPROVE. Đã đồng bộ nền, giải quyết hai dòng README giữ hướng dẫn #18; compare chỉ README và đúng 7 file upstream bị xóa. Squash vào nhánh tích hợp tại `3c5fa8759967484fad61c59db54fb07584a56c86`. Không đổi clinic_app, SQL, tests, workflow, PDF hoặc bằng chứng.
- Cập nhật hồ sơ sau đó chỉ Markdown. Không gán số test của snapshot trước cho SHA mới; CI bản cuối được kiểm tra trước merge.

## Kiểm chứng

| Nguồn | Kết quả | Giới hạn |
|---|---|---|
| Windows Quyền phiên 073906 | 194 đạt / 1 lỗi; HTTP503/MySQL2003 | Giữ nguyên hồ sơ thất bại |
| Windows Quyền phiên 074813 | 195 đạt, không lỗi/bỏ qua | Đã xác nhận trực tiếp health/db, lịch sử BN001 và doanh thu mẫu |
| Windows Quyền phiên 075907 | 236 đạt, không lỗi/bỏ qua, gồm tests và week3_checks | Source dd1f41e, Python3.11.9/MySQL8.4.11/Chromium156 |
| Audit phiên 075907 | 11 bảng, 9 trigger, 1.144 dòng; 10 tập SQL rỗng, findings rỗng; seed không đổi | Đọc results/JUnit/log; không nhận đã xem ảnh local chưa upload |
| Cleanup phiên 075907 | success/port_closed/launcher_exited/env_unchanged=true; remaining_pids/errors/cleanup_errors rỗng | Kết thúc instance private, không tác động MySQL hệ thống |
| CI #17 tại head1964a4a | Linux236 đạt và Windows cleanup2 đạt; 4 workflow success | Log run39703489223 đã được đối chiếu; checkout merge thử1dcd4b7 |

Bằng chứng Windows ở docs/evidence/vuong_week2_prepare_20261022_{073906_519771,074813_773699,075907_328633}/. Mỗi thư mục có results.json, pytest.txt, junit.xml và source_sha256.json. Ảnh được JSON tham chiếu vẫn giữ trên máy Quyền.

## Quyết định lỗi

- **W3-RUN-01: đóng về kỹ thuật trên bản tích hợp.** Bản sửa #12 xác minh instance/datadir/port, fallback chỉ tiến trình đúng phạm vi; đã review độc lập và có Windows CI success/error, cùng cleanup phiên lỗi đầu và hai phiên đạt trên laptop Quyền. Quyết định dựa trên bằng chứng, không dựa vào việc bỏ T16. Tái mở nếu bản cuối còn PID/cổng private.
- **W3-DEMO-02:** đã sửa/retest và được Trung duyệt tại #13; giữ hồ sơ lịch sử.
- **W3-DB-01: tiếp tục theo dõi, chưa đóng.** Phiên đầu có 503/code2003; server không crash theo log Quyền cung cấp. Hai phiên sau và CI không tái hiện. Chấp nhận tích hợp để tiếp tục chuẩn bị bộ nộp, không tuyên bố đã sửa hoặc bỏ ca kiểm tra. Nếu tái diễn, giữ app/MySQL log, route, thời điểm, source và instance; điều tra trước buổi demo, không retry mù request ghi.
- T16 không thực hiện/không PASS theo quyết định Quyền. Máy demo chính là laptop Quyền.

## Đối chiếu yêu cầu đề bài và bộ nộp

Đã đọc Project1 trong đề BTL được cung cấp, trích xuất cả4trang của hai PDF, render/xem hai sơ đồ và trang ràng buộc. Đối chiếu schema/constraints, queries.sql và clinic_app/reports.py/workflows.py. Đây là review nguồn/tài liệu, không phải lượt chạy app/MySQL mới của trợ lý.

| Yêu cầu | File/đường dẫn nộp | Đối chiếu |
|---|---|---|
| YC1 PDF mô tả thực thể, thuộc tính, quan hệ/EER | [ER](design/ER_Phong_kham_Ban_chot.pdf), [lược đồ quan hệ](design/Luoc_do_quan_he_Phong_kham_Ban_chot.pdf) | 9 thực thể +2liên kết N-N ánh xạ11bảng, PK/FK/UQ, min/max và ràng buộc trang2 |
| YC2 MySQL tạo bảng, seed,4nhóm truy vấn | [project1_submission.sql](../database/project1_submission.sql) | Đủ11CREATE TABLE/9CREATE TRIGGER, sáu phần đúng thứ tự; giữ DELIMITER; chọn schema mới trống và chạy1lần |
| YC3 app có giao diện | [GitHub](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan), [SETUP](SETUP.md), [USER_GUIDE](USER_GUIDE.md) | Bốn báo cáo diseases/salaries/history/revenue; CRUD và luồng khám/hỗ trợ/kê đơn/đóng lượt/khỏi |
| Kết quả đối chiếu | [expected_results](../database/expected_results.md) và bằng chứng nêu trên | 10/2026: khám4.680.000,thuốc5.820.800,tổng10.500.800đ |

Khớp thiết kế: MaBacSi đặt ở DOT_DIEU_TRI; PK ghép HO_TRO/CHI_TIET_DON_THUOC; một đơn tối đa/lần khám; UQ(lượt,đợt) và UQ(đợt,STT); cận dưới và quy tắc liên bảng do transaction/trigger/audit phối hợp. Q1 đếm DISTINCT đợt trong kỳ; Q2 thưởng bác sĩ theo ngày khỏi, y tá theo hỗ trợ; Q3 toàn lịch sử; Q4 cộng riêng khám và thuốc theo giá bán lưu. Không thấy lệch khóa/ánh xạ/công thức chặn bộ nộp trong phạm vi đã rà.

SQL gộp trên Git khớp từng phần nguồn sau chuẩn hóa xuống dòng/khoảng trắng cuối phần. SHA256 blob LF: `2e7a6fdc20fcd937cd3743f683791af269e48d8b60908e892d09e4eb2142a55b`. Hash local Workbench trong hồ sơ #15 khác; thử LF/CRLF và biến thể USE đơn giản không khớp hash local, nên **không kết luận chỉ do xuống dòng** hoặc giống byte. Giữ nghiệm thu Workbench là xác nhận người chạy; CI nguồn không tự chứng minh import file gộp. Hai reviewer đã chấp nhận nội dung chuẩn hóa tại #15.

## Phần cần người thật xác nhận trước phát hành

- Nhóm xác nhận phân vai và tập demo có lời nói/chuyển phần, bấm giờ; hồ sơ hiện chưa đủ thành phần/thời lượng để tự điền.
- Nếu W3-DB-01 tái diễn, giữ log và điều tra, không tự đánh dấu PASS.
- Tag/release v1.0.0 chỉ tạo sau khi xác nhận các điều kiện cuối. Không nhận đã nộp bài hoặc đã diễn tập thay nhóm.

Phần chuẩn bị vấn đáp chuyên môn vẫn để sau theo yêu cầu Quyền; tài liệu backend/SQL đã có trong repo.
