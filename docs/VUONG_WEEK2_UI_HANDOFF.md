# Bàn giao UI nghiệp vụ tuần 2 — Vương

> Mốc kiểm thử lịch sử. Trạng thái bàn giao hiện tại: [VUONG_WEEK2_HANDOFF.md](VUONG_WEEK2_HANDOFF.md).

Cập nhật sau bước 3: [Bốn báo cáo và bảng đối chiếu](VUONG_WEEK2_REPORTS_HANDOFF.md) đã hoàn thiện; các ghi chú báo cáo còn chờ dưới đây là trạng thái tại thời điểm bàn giao bước 2.

Ngày thực hiện: 19/10/2026. Nhánh `vuong/week-2`, nền tích hợp `f8d80c8ea64ce0843430b5e16eac1538b7eb2d85` (Trung `10c8082` + Quyền `1bf9f8b`). Thay đổi UI trong working tree, chưa commit/push hoặc đăng GitHub.

## Kết quả

| Nghiệp vụ | Hành vi hiện tại |
|---|---|
| Tiếp nhận | Nhóm riêng thông tin bệnh nhân, lần khám đầu, hỗ trợ; có nhãn, giới hạn đầu vào và hướng dẫn mã/tiền/ngày |
| Đợt mới / tái khám | Chọn đợt đang điều trị được lọc theo bệnh nhân; hiển thị tên bệnh/bác sĩ; đổi bệnh nhân xóa lựa chọn đợt cũ; bệnh/bác sĩ không được gửi lại trong chế độ tái khám |
| Chi tiết lượt | Tổng tiền khám chưa gồm thuốc, trạng thái, ngày dd/mm/yyyy, bảng lần khám và hỗ trợ; điều hướng rõ đến khám thêm/kê đơn/khỏi/đóng lượt |
| Hỗ trợ y tá | Liên kết cập nhật theo từng y tá; tự nạp ngày/nội dung hiện có; ngày cũ readonly nếu đúng; đổi y tá giữ bản nháp từng người |
| Đơn thuốc | Thêm/xóa dòng bằng bàn phím, đánh lại số thứ tự và ID/label, chuyển focus phù hợp, tối đa 100 dòng; giữ các giá trị lặp sau lỗi server |
| Xem đơn | Ngày, lần khám/lượt, đơn giá lịch sử, số lượng/liều/thành tiền và tổng; quay lại đúng lượt |
| Đóng lượt / khỏi | Hai form giải thích riêng hệ quả; hiển thị bệnh nhân/ngữ cảnh; lỗi giữ ngày đã nhập và focus tới thông báo; không thay nghiệp vụ server |
| Màn hình nhỏ | Form select/fieldset co theo chiều rộng; bảng dài có vùng cuộn focus được; không tràn ngang toàn trang ở 320/390/1440 px trong khảo sát |

Form có CSRF như trước. Mọi giá trị hồ sơ/thuốc/nội dung được Jinja escape; JSON hỗ trợ dùng `tojson`. JavaScript chỉ hỗ trợ nhập liệu, không thực thi tính tiền hoặc thay kiểm tra backend. Khi JavaScript tắt, các field gốc và ba dòng thuốc vẫn có thể gửi; thao tác thêm/xóa dòng và bộ chọn đợt theo bệnh nhân cần JavaScript. Chưa chạy một bộ browser riêng khi tắt JavaScript.

## Thay đổi backend để Trung review

`clinic_app/clinical_routes.py` chỉ bổ sung đọc dữ liệu phục vụ UI:

- `choices.episodes` giữ các khóa cũ và bổ sung mã/tên bác sĩ, tên bệnh bằng JOIN.
- Form nhận thêm `clinical_context`, `support_rows`, `back_url`. Đọc lượt/đợt/lần khám theo ID trên route để hiện đúng bệnh nhân, trả 404 khi nguồn không tồn tại. Ngày hỗ trợ chuyển ISO trong JSON của form.
- Chi tiết đơn nhận thêm `visit_id` để quay lại đúng lượt.

Không đổi route, tên field, HTTP redirect, JSON báo cáo, schema, seed, trigger, công thức, service ghi hoặc transaction. Giá thuốc vẫn chỉ do server lấy và lưu. Khóa bệnh nhân/rollback cũ tiếp tục được bộ test kiểm chứng.

Template chạy: `clinic_app/templates/week2/{form,visit,prescription}.html`, layout/menu và danh sách lượt ở `week1/`. CSS/JS mới ở `clinic_app/static/week2.{css,js}`. CSS giới hạn vào các lớp clinical để không thay bố cục báo cáo/hồ sơ tuần 1.

## Kiểm chứng thực chạy

Phiên thành công `20261019_215400`: Windows / Python 3.12.14 / MySQL 8.0.46 / Chromium 156.0.8078.4. Dùng instance MySQL private mới, DB `clinic_vuong_week2_prepare_test`, cổng 56348. Không dùng DB trong `.env`.

- **161 passed, 0 skipped**, 24,02 giây. Bật `RUN_MYSQL_TESTS`, `RUN_BROWSER_TESTS`, `QUYEN_CHECK_WEEK2`.
- Test mới `tests/test_browser_vuong_week2.py` chạy browser thật: tạo lượt → thêm bệnh → sửa hỗ trợ → thêm y tá → đơn hai thuốc → lỗi thuốc trùng/giữ dữ liệu → thêm/xóa bằng Enter → lưu/reload đơn 8.000 đồng → ngày đóng sai/đúng → tái khám STT 2 → ngày khỏi sai/đúng → đóng lượt thứ hai → tái mắc đợt mới. Kiểm tra lựa chọn đợt không rò sang bệnh nhân khác, ID không trùng và không có lỗi JavaScript.
- SQL sau browser xác nhận hai người hỗ trợ, STT tái khám 2, đợt cũ đã khỏi. Fixture dọn riêng dữ liệu giả W2 của test, không xóa seed.
- Khảo sát bổ sung 18 route × 3 viewport = 54 trang: HTTP đúng kỳ vọng, **0 trang tràn ngang**. Trong bước chuẩn bị trước đây, form kê đơn 320 px có tràn ngang.
- Audit cuối 10 tập SQL rỗng; 11 bảng/9 trigger/1.144 dòng; 9 nhóm findings rỗng. Hash mỗi bảng trước/sau test và khảo sát browser giống nhau; `.env` không đổi.

Bằng chứng: [pytest](evidence/vuong_week2_prepare_20261019_215400/pytest.txt), [kết quả/audit](evidence/vuong_week2_prepare_20261019_215400/results.json), [hash source](evidence/vuong_week2_prepare_20261019_215400/source_sha256.json), [ảnh test nghiệp vụ](evidence/vuong_week2_prepare_20261019_215400/browser-tests/vuong-week2/03-prescription-320.png).

`source_sha` trong results là HEAD nền; source UI đang sửa chưa commit được xác định thêm bằng manifest SHA256. Sau phiên thành công chỉ bổ sung tài liệu, manifest và cải tiến helper thu manifest tự động, không thay code ứng dụng/test đã chạy.

Ảnh đã rà trực tiếp: tiếp nhận 390 px, form kê đơn 320 px, chi tiết lượt 1440 px và lỗi ngày đóng 320 px. Không nhận là đã xem bằng mắt toàn bộ ảnh khảo sát.

Phiên `215312` có 160 test đạt/1 test mới lỗi do selector đòi text ô bệnh phải bằng tên bệnh dù ô còn có trạng thái. Đã sửa selector để kiểm tra nội dung trong vùng bảng. Helper phiên đó còn gặp lỗi in log tiếng Việt trên stdout cp1252; đã sửa UTF-8. Kết quả phiên lỗi không được tính đạt.

## Phạm vi còn lại

- Bốn báo cáo và trang tổng hợp sẽ hoàn thiện ở bước 3; badge chờ tích hợp trên trang tổng hợp vẫn chưa sửa trong bước nghiệp vụ này.
- Chưa kết luận nghiệm thu toàn bộ tuần 2 hoặc T01–T15 chỉ từ một test luồng mới; còn checklist tổng thể bước 4.
- Môi trường mục tiêu Python 3.11/MySQL 8.4 và review Trung/Quyền vẫn cần trước chốt nhóm.
- Chưa đăng bình luận/xác nhận hợp đồng/review/PR lên GitHub.

App private của phiên này tại `http://127.0.0.1:64129/visits/new`, chỉ khả dụng khi tiến trình còn chạy. Chạy lại bằng helper trong tài liệu chuẩn bị sẽ tạo instance/DB private mới và in URL mới.
