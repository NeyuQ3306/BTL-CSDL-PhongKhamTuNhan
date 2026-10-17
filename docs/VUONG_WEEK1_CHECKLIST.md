# Checklist nghiệm thu UI tuần 1 — Vương

**Cập nhật trước commit:** đã đồng bộ backend Trung `5a25395`, chạy lại checklist 33/33 đạt và kiểm tra URL khác hoa/thường cho cả ba nhóm. Pytest mới nhất **25 passed, 21 skipped**; xem [bằng chứng cuối](evidence/vuong_week1_final/README.md). Các bảng và log bên dưới giữ nguyên kết quả phiên kiểm tra trước đó để đối chiếu, không thay thế kết quả mới.

## Trạng thái và căn cứ

**Kết quả: 33/33 ca kiểm tra bằng script đạt; 14/14 ca kiểm tra trình duyệt đạt.** Trong đó responsive gồm 36 lượt ở 320, 390, 768 và 1440px. Một lỗi vùng bấm UI được phát hiện, sửa và kiểm tra lại đạt. Chưa coi đây là nghiệm thu hoàn tất toàn bộ tuần 1 của nhóm: còn review/merge và các phụ thuộc ghi bên dưới.

- Ngày chạy: 17/10/2026, giờ Việt Nam. Người thực hiện: Codex theo yêu cầu Vương.
- Nhánh: `vuong/week-1`. HEAD nền: `c44238498d11971fd101a02982b2e98054b2e225` cùng thay đổi UI chưa commit. Mã chính xác được lưu hash trong [source_sha256.json](evidence/vuong_week1_checklist/source_sha256.json).
- Môi trường thực chạy: Windows, Python 3.14.6, MySQL 8.0.46; Flask tại `http://127.0.0.1:5000`. Chưa xác nhận chạy bản UI hiện tại trên môi trường mục tiêu Python 3.11/MySQL 8.4.
- Chỉ dùng database giả lập riêng `clinic_vuong_week1`. Không nhập hoặc sửa `hospital_db`, không ghi đè `.env`, không tắt CSRF hoặc FK.
- Mã hồ sơ thử bằng script: patients: `VW97bbc1d2a`, doctors: `VW92f87c633`, nurses: `VWab3183926`. Mã thử qua trình duyệt: `VP242715504`. Tất cả đã được xóa sau khi kiểm tra.

## Luồng ưu tiên: thêm bệnh nhân → lưu MySQL → tải lại → xem danh sách

1. Mở `/patients/new`, điền dữ liệu hoàn toàn giả. [Ảnh form](evidence/vuong_week1_checklist/01-patient-filled.png).
2. Bấm **Thêm hồ sơ**: chuyển sang chi tiết, hiện thông báo thành công. [Ảnh thành công](evidence/vuong_week1_checklist/02-patient-created.png).
3. SELECT độc lập theo mã trong MySQL: dữ liệu lưu đúng, CCCD/điện thoại giữ số 0 đầu. [Log MySQL](evidence/vuong_week1_checklist/03-mysql-confirmation.json).
4. Tải lại trang: hồ sơ vẫn hiển thị; không cần gửi lại form. [Ảnh sau reload](evidence/vuong_week1_checklist/04-patient-after-reload.png).
5. Quay về danh sách, tìm mã: hiện đúng hồ sơ vừa lưu. [Ảnh danh sách](evidence/vuong_week1_checklist/05-patient-in-list.png).
6. Cuối đợt thử, xóa đúng hồ sơ tạm qua UI và đối chiếu hash toàn bộ dữ liệu nền. [Audit cuối](evidence/vuong_week1_checklist/final_audit.json).

## Checklist bằng script trên MySQL thật

Chạy từ thư mục repository: `.venv/Scripts/python.exe -m tools.check_vuong_week1`. Script chỉ dùng database demo có tên cố định nêu trên, không import SQL; sinh mã tạm, dọn trong `finally`, so hash trước/sau. Các bước sửa/xóa chỉ tác động hồ sơ tự tạo; ca chặn xóa thử trên seed phải bị FK từ chối.

[Log máy đọc được, có bước chạy/expected/actual](evidence/vuong_week1_checklist/automated_results.json).

| ID | Ca kiểm tra | Thao tác/input | Mong đợi | Thực tế | Trạng thái |
|---|---|---|---|---|---|
| ENV01 | Ứng dụng và dữ liệu nền | GET /health, /health/db; audit read-only | 200, đúng seed | Flask/MySQL 200; 11 bảng/1.144 dòng; audit không có phát hiện | ĐẠT |
| PAT01 | Thêm bệnh nhân và lưu MySQL | POST /patients/new; GET chi tiết; SELECT theo mã | 303, thông báo thành công, lưu đúng dữ liệu | POST 303; thông báo thành công; MySQL lưu đúng mã VW97bbc1d2a, họ tên và số 0 đầu CMT | ĐẠT |
| PAT02 | Tải lại trang và xem trong danh sách | Client mới GET chi tiết hai lần; tìm mã trong danh sách | Hồ sơ còn sau tải lại | Hai GET bằng client mới và tìm theo mã đều thấy hồ sơ từ MySQL | ĐẠT |
| PAT03 | Sửa hồ sơ | POST sửa tên; GET lại; SELECT MySQL | 303, thông báo cập nhật, dữ liệu mới được lưu | Đúng kết quả mong đợi | ĐẠT |
| PAT04 | Lỗi nhập liệu và giữ giá trị | Thử thiếu tên, sai CCCD/ngày/điện thoại/thâm niên tùy nhóm | 422, lỗi từng trường, giữ dữ liệu | 5 đầu vào sai: 422, lỗi đúng trường, giữ dữ liệu hợp lệ | ĐẠT |
| PAT05 | Trùng mã và trùng CCCD | Gửi lại mã đã tạo; gửi mã mới cùng CCCD | 409, thông báo dễ hiểu, không tạo thêm | Đúng kết quả mong đợi | ĐẠT |
| PAT06 | CSRF và mã hồ sơ không đổi | POST thiếu/sai token; giả sửa mã trong POST | 400/422, giữ mã và liên kết gốc | Đúng kết quả mong đợi | ĐẠT |
| PAT07 | Ba trạng thái danh sách rỗng | Tìm mã không có; page=999; render danh sách trống | Thông báo và đường quay lại phù hợp | Tìm không có kết quả/trang vượt: dữ liệu thật; danh sách trống: render context giả lập, không xóa seed | ĐẠT |
| PAT08 | Chặn xóa hồ sơ đã có lịch sử | POST xóa hồ sơ seed có tham chiếu | 409, hồ sơ vẫn tồn tại | Đúng kết quả mong đợi | ĐẠT |
| DOC01 | Thêm bác sĩ và lưu MySQL | POST /doctors/new; GET chi tiết; SELECT theo mã | 303, thông báo thành công, lưu đúng dữ liệu | POST 303; thông báo thành công; MySQL lưu đúng mã VW92f87c633, họ tên và số 0 đầu CMT | ĐẠT |
| DOC02 | Tải lại trang và xem trong danh sách | Client mới GET chi tiết hai lần; tìm mã trong danh sách | Hồ sơ còn sau tải lại | Hai GET bằng client mới và tìm theo mã đều thấy hồ sơ từ MySQL | ĐẠT |
| DOC03 | Sửa hồ sơ | POST sửa tên; GET lại; SELECT MySQL | 303, thông báo cập nhật, dữ liệu mới được lưu | Đúng kết quả mong đợi | ĐẠT |
| DOC04 | Lỗi nhập liệu và giữ giá trị | Thử thiếu tên, sai CCCD/ngày/điện thoại/thâm niên tùy nhóm | 422, lỗi từng trường, giữ dữ liệu | 6 đầu vào sai: 422, lỗi đúng trường, giữ dữ liệu hợp lệ | ĐẠT |
| DOC05 | Trùng mã và trùng CCCD | Gửi lại mã đã tạo; gửi mã mới cùng CCCD | 409, thông báo dễ hiểu, không tạo thêm | Đúng kết quả mong đợi | ĐẠT |
| DOC06 | CSRF và mã hồ sơ không đổi | POST thiếu/sai token; giả sửa mã trong POST | 400/422, giữ mã và liên kết gốc | Đúng kết quả mong đợi | ĐẠT |
| DOC07 | Ba trạng thái danh sách rỗng | Tìm mã không có; page=999; render danh sách trống | Thông báo và đường quay lại phù hợp | Tìm không có kết quả/trang vượt: dữ liệu thật; danh sách trống: render context giả lập, không xóa seed | ĐẠT |
| DOC08 | Chặn xóa hồ sơ đã có lịch sử | POST xóa hồ sơ seed có tham chiếu | 409, hồ sơ vẫn tồn tại | Đúng kết quả mong đợi | ĐẠT |
| NUR01 | Thêm y tá và lưu MySQL | POST /nurses/new; GET chi tiết; SELECT theo mã | 303, thông báo thành công, lưu đúng dữ liệu | POST 303; thông báo thành công; MySQL lưu đúng mã VWab3183926, họ tên và số 0 đầu CMT | ĐẠT |
| NUR02 | Tải lại trang và xem trong danh sách | Client mới GET chi tiết hai lần; tìm mã trong danh sách | Hồ sơ còn sau tải lại | Hai GET bằng client mới và tìm theo mã đều thấy hồ sơ từ MySQL | ĐẠT |
| NUR03 | Sửa hồ sơ | POST sửa tên; GET lại; SELECT MySQL | 303, thông báo cập nhật, dữ liệu mới được lưu | Đúng kết quả mong đợi | ĐẠT |
| NUR04 | Lỗi nhập liệu và giữ giá trị | Thử thiếu tên, sai CCCD/ngày/điện thoại/thâm niên tùy nhóm | 422, lỗi từng trường, giữ dữ liệu | 7 đầu vào sai: 422, lỗi đúng trường, giữ dữ liệu hợp lệ | ĐẠT |
| NUR05 | Trùng mã và trùng CCCD | Gửi lại mã đã tạo; gửi mã mới cùng CCCD | 409, thông báo dễ hiểu, không tạo thêm | Đúng kết quả mong đợi | ĐẠT |
| NUR06 | CSRF và mã hồ sơ không đổi | POST thiếu/sai token; giả sửa mã trong POST | 400/422, giữ mã và liên kết gốc | Đúng kết quả mong đợi | ĐẠT |
| NUR07 | Ba trạng thái danh sách rỗng | Tìm mã không có; page=999; render danh sách trống | Thông báo và đường quay lại phù hợp | Tìm không có kết quả/trang vượt: dữ liệu thật; danh sách trống: render context giả lập, không xóa seed | ĐẠT |
| NUR08 | Chặn xóa hồ sơ đã có lịch sử | POST xóa hồ sơ seed có tham chiếu | 409, hồ sơ vẫn tồn tại | Đúng kết quả mong đợi | ĐẠT |
| NAV01 | Điều hướng và menu đang chọn | Mở bảy đường dẫn chính | 200, đúng menu, không có nội trú/phẫu thuật | Đúng kết quả mong đợi | ĐẠT |
| REP01 | Ba khung thống kê không giả kết quả | Chọn tháng; chặn kết nối DB; thử tháng sai | 200/400, không SQL, không tiền giả | Đúng kết quả mong đợi | ĐẠT |
| REP02 | Lịch sử đã lưu và lịch sử rỗng | Chọn BN001; mở hồ sơ tạm chưa khám | Dữ liệu thật/ba trạng thái rỗng đúng | Đúng kết quả mong đợi | ĐẠT |
| NAV02 | Đường dẫn và tham số không hợp lệ | Hồ sơ không có, page=0, báo cáo không có | 404/400 với thông báo | Đúng kết quả mong đợi | ĐẠT |
| CLEAN_PATIENTS | Dọn hồ sơ thử patients | Xóa duy nhất mã tự sinh VW97bbc1d2a | 303/404, seed không bị xóa | Đúng kết quả mong đợi | ĐẠT |
| CLEAN_DOCTORS | Dọn hồ sơ thử doctors | Xóa duy nhất mã tự sinh VW92f87c633 | 303/404, seed không bị xóa | Đúng kết quả mong đợi | ĐẠT |
| CLEAN_NURSES | Dọn hồ sơ thử nurses | Xóa duy nhất mã tự sinh VWab3183926 | 303/404, seed không bị xóa | Đúng kết quả mong đợi | ĐẠT |
| DATA01 | Bảo toàn dữ liệu và cấu hình | So hash tất cả bản ghi 11 bảng; audit; hash .env | Không đổi dữ liệu nền hoặc cấu hình | Hash toàn bộ 11 bảng khớp trước chạy; 1.144 dòng; .env không đổi | ĐẠT |

Danh sách hoàn toàn trống được kiểm tra bằng context render giả lập, ghi rõ trong các ca PAT07/DOC07/NUR07; không xóa dữ liệu seed để tạo tình huống này. Tìm không có kết quả, trang vượt và lịch sử rỗng dùng database thật.

## Checklist trình duyệt và ảnh minh chứng

| ID | Thao tác/input | Mong đợi | Thực tế | Trạng thái | Bằng chứng |
|---|---|---|---|---|---|
| UI01 | Điền form bệnh nhân giả | Đủ trường, giữ số 0 đầu CCCD/điện thoại | Điền đủ, sẵn sàng gửi | ĐẠT | [Ảnh/log](evidence/vuong_week1_checklist/01-patient-filled.png) |
| UI02 | Gửi thêm bệnh nhân qua trình duyệt | Mở chi tiết, có thông báo thành công | Hiển thị đúng tên và mã VP242715504 | ĐẠT | [Ảnh/log](evidence/vuong_week1_checklist/02-patient-created.png) |
| UI03 | Kiểm tra lưu MySQL độc lập | SELECT thấy đúng bản ghi vừa nhập | Đúng mã, tên, ngày sinh, CCCD và điện thoại | ĐẠT | [Ảnh/log](evidence/vuong_week1_checklist/03-mysql-confirmation.json) |
| UI04 | Tải lại trang chi tiết | Dữ liệu vẫn còn; không gửi lại POST | Hồ sơ còn sau reload; flash thành công đã biến mất đúng vòng đời | ĐẠT | [Ảnh/log](evidence/vuong_week1_checklist/04-patient-after-reload.png) |
| UI05 | Tìm mã trong danh sách | Hiện đúng một hồ sơ | Tìm VP242715504 có một kết quả từ MySQL | ĐẠT | [Ảnh/log](evidence/vuong_week1_checklist/05-patient-in-list.png) |
| UI06 | Thêm trùng hồ sơ qua trình duyệt | Thông báo xung đột, giữ thông tin nhập | Không tạo thêm; thông báo trùng mã/CCCD rõ ràng | ĐẠT | [Ảnh/log](evidence/vuong_week1_checklist/06-duplicate-patient.png) |
| UI07 | Form bác sĩ với CCCD abc | Lỗi đúng CCCD, giữ trường còn lại và thâm niên 0 | Đúng lỗi, dữ liệu còn lại được giữ | ĐẠT | [Ảnh/log](evidence/vuong_week1_checklist/07-doctor-validation.png) |
| UI08 | Form y tá với điện thoại 12 ở 390px | Lỗi đúng điện thoại, giữ dữ liệu | Đúng lỗi và không tràn ngang toàn trang | ĐẠT | [Ảnh/log](evidence/vuong_week1_checklist/08-nurse-validation-mobile.png) |
| UI09 | Tìm không có kết quả trên điện thoại | Có hướng dẫn đổi từ khóa/xóa bộ lọc | Có trạng thái rỗng và đường quay lại | ĐẠT | [Ảnh/log](evidence/vuong_week1_checklist/09-empty-search-mobile.png) |
| UI10 | Lịch sử bệnh nhân vừa tạo chưa khám | Ba vùng đều báo chưa có dữ liệu thật | Không giả số liệu hoặc trạng thái bệnh | ĐẠT | [Ảnh/log](evidence/vuong_week1_checklist/10-empty-history-mobile.png) |
| UI11 | Bấm liên kết lỗi nhiều dòng trên 390px | Chuyển focus đúng ô lỗi | Sau sửa CSS: focus so_dien_thoai, hash #so_dien_thoai | ĐẠT | [Ảnh/log](evidence/vuong_week1_checklist/11-error-link-focus-fixed.png) |
| UI12 | Xóa hồ sơ trình duyệt vừa tạo | Chỉ xóa hồ sơ tạm, thông báo thành công | Đã xóa; SELECT và hash cuối xác nhận không còn | ĐẠT | [Ảnh/log](evidence/vuong_week1_checklist/12-temporary-patient-cleaned.png) |
| UI13 | Responsive và menu đang chọn | Không tràn trang, có tiêu đề và đúng một menu đang chọn | 36/36 tổ hợp màn hình/kích thước đạt | ĐẠT | [Ảnh/log](evidence/vuong_week1_checklist/browser_results.json) |
| UI14 | Bốn đường dẫn báo cáo từ menu | Có bốn nhóm, phân biệt khung thống kê và lịch sử | Đủ đường dẫn, không có nội trú/phẫu thuật | ĐẠT | [Ảnh/log](evidence/vuong_week1_checklist/13-reports-navigation.png) |

## Lỗi UI phát hiện và đã sửa

**UI-B01 — Vùng bấm liên kết lỗi nhiều dòng trên màn hình hẹp.**

- Tái hiện: ở 390px, gửi form y tá với điện thoại `12`, bấm giữa vùng chữ của liên kết điện thoại trong tóm tắt lỗi. Liên kết inline xuống dòng có khoảng trống giữa các dòng nằm trong bounding box; vị trí bấm có thể trúng `li` thay vì `a`, không chuyển tới input.
- Mong đợi: vùng bấm liên kết đưa focus tới ô điện thoại.
- Sửa: `.error-summary a` thành block, chiều cao tối thiểu 44px và padding trong `clinic_app/static/week1.css`; không thay field, route hoặc CSRF.
- Kiểm tra lại: focus `so_dien_thoai`, URL có `#so_dien_thoai`, không tràn ngang. Ca UI11 đạt, có ảnh minh chứng.
- Trạng thái: **ĐÃ SỬA**, chưa commit/review/merge.

Không phát hiện lỗi UI còn mở trong các ca đã chạy. Sửa riêng mã hóa stdout của công cụ checklist sang UTF-8 để chạy được log tiếng Việt trên Windows; đây là lỗi công cụ kiểm tra, không phải ứng dụng.

## Backend/schema cần phối hợp

- Không phát hiện lỗi backend/schema mới cần chặn bàn giao UI trong đợt chạy này.
- Trung cần review thay đổi xử lý lỗi FK `1217` cùng `1451` ở route xóa đã sửa trong bước trước; ca PAT08/DOC08/NUR08 và test hồi quy xác nhận hành vi chặn xóa đúng trên MySQL máy này.
- Quyền vẫn cần review adapter seed/schema 11 bảng; audit dữ liệu đạt không đồng nghĩa đã bảo vệ đầy đủ mọi ràng buộc cho lần ghi tương lai.
- Ba báo cáo thống kê chỉ nghiệm thu khung, bộ lọc và trạng thái chờ. Không đánh dấu SQL/tính lương/doanh thu/thống kê bệnh là đã hoàn thành.

## Ca chưa chạy / giới hạn

| Hạng mục | Trạng thái | Lý do và phạm vi |
|---|---|---|
| 12 test tích hợp gốc của pytest | BỎ QUA | Chưa cấu hình database riêng hậu tố `_test`; không vượt guard để chạy trên database làm việc. Checklist MySQL thật ở trên được chạy độc lập, không ghi là 12 test này đã đạt. |
| Mã UI hiện tại trên Python 3.11 + MySQL 8.4 | CHƯA CHẠY | Máy này thực tế dùng Python 3.14.6/MySQL 8.0.46. CI của nền Trung là bằng chứng phiên bản trước, không thay cho CI thay đổi UI hiện tại. |
| Trình duyệt Firefox/Safari, thiết bị điện thoại thật | CHƯA CHẠY | Đã dùng Chromium với viewport mô phỏng; chưa có bằng chứng trên thiết bị thật. |
| Rà hiển thị hai PDF YC1 | CHƯA CHẠY | Thuộc bước rà PDF riêng chưa được giao; không đánh dấu hoàn tất tuần 1 toàn phần. |
| SQL báo cáo và nghiệp vụ khám/đơn nhiều bước | NGOÀI PHẠM VI | Thuộc tuần 2; không dùng khung UI làm bằng chứng nghiệp vụ đạt. |
| Review/merge PR và chạy theo hướng dẫn trên máy thành viên khác | CHƯA THỰC HIỆN | Chưa tạo/push PR trong bước checklist; cần nhóm review và xác nhận phối hợp. |

Pytest hiện tại: **24 passed, 12 skipped**, chạy với `RUN_MYSQL_TESTS=0`; xem [log](evidence/vuong_week1_checklist/pytest.txt). Không có test thất bại trong lần chạy cuối. `git diff --check` đạt.

## Bảo toàn sau chạy

- Đã xóa toàn bộ hồ sơ thử của script và trình duyệt; các form lỗi bác sĩ/y tá không tạo hồ sơ.
- Tổng dữ liệu về **1.144 dòng/11 bảng**; audit không có phát hiện.
- Hash tất cả bản ghi của từng bảng khớp trước/sau, mạnh hơn chỉ đối chiếu số lượng.
- `.env` không đổi; không chỉnh database bệnh viện cũ.
- [Audit và xác nhận cleanup](evidence/vuong_week1_checklist/final_audit.json), [log trình duyệt](evidence/vuong_week1_checklist/browser_results.json).
