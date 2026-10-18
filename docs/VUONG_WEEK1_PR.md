# Tiêu đề PR

[Vương][Tuần 1] Hoàn thiện UI hồ sơ, khung bốn báo cáo và kiểm thử MySQL

# Nội dung PR

## Mục tiêu và phụ thuộc

Hoàn thiện giao diện tiếng Việt tuần 1 trên backend Trung: quản lý bệnh nhân/bác sĩ/y tá, thêm và xem lại hồ sơ từ MySQL thật, cùng khung bốn báo cáo. Các trang thống kê chưa tích hợp SQL luôn hiển thị trạng thái chờ, không trình bày số liệu giả như kết quả thật.

Backend Trung `5a25395699905cc5f79af4904bd73d95073963a0` đã squash merge qua #4 thành main `b51b0afb3b0d03f6fa30a255b1efc614b89a9bbd`. Nhánh Vương đã đồng bộ main bằng `8c5be9469976333195eb67c9d2689638d02c045f`, giữ nguyên tree của commit UI `33d45a06eb7e237796d3d240fd6d419fabd00bd1`. PR #7 hiện mở, đã hết Draft, chưa merge. Sáu commit nền Trung không tính thành đóng góp UI Vương. Bộ SQL/trigger #6 và hướng dẫn setup #8 còn cần hoàn tất review/tích hợp; seed giả Vương bàn giao qua Trung được SQL Quyền kế thừa 1.144 dòng.

## Thay đổi

- Layout/menu và responsive; danh sách, thêm/sửa/chi tiết ba nhóm, lỗi từng trường, hướng dẫn và trạng thái rỗng; giữ field/CSRF và mã chuẩn DB khi URL khác hoa/thường.
- GET khung thống kê bệnh/lương/doanh thu có tháng và vùng kết quả chờ; bộ lọc bệnh nhân dùng lại route lịch sử. Không thêm SQL, schema hoặc nghiệp vụ tuần 2.
- Xử lý FK 1217/1451 thành thông báo chặn xóa; mở rộng vùng bấm liên kết lỗi nhiều dòng trên điện thoại.
- Checklist, ảnh/log, hướng dẫn sử dụng, công cụ chạy lại và test hồi quy; cập nhật test browser theo nhãn nút mới.

## Cách kiểm thử và bằng chứng

**CI đã xác minh trực tiếp metadata, steps và log ngày 18/10/2026:**

- [Backend and MySQL — run 39092326435](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/actions/runs/39092326435), job `117571499620`, head `8c5be9469976333195eb67c9d2689638d02c045f`: **46 passed**, không skipped; compile/Jinja đạt; dùng seed adapter.
- [Week 1 integration review — run 39092264670](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/actions/runs/39092264670), job `117571317667`: **72 passed** (26 SQL + 46 backend/UI), không skipped; ghép SQL/trigger `08e4427f6ac8e9ba55eaba859ddab4067330ec04` và UI/backend `33d45a06eb7e237796d3d240fd6d419fabd00bd1` cùng DB. Workflow thuộc #8 tại `89539428d4b522a44938bc21115114c595cc207b`; không phải 72 test chạy trên head #7.
- Cả hai job chạy Ubuntu/Python 3.11.17/MySQL 8.4.11/Chromium; audit sau test đủ 11 bảng/1.144 dòng, `matches_expected_counts=true`, findings rỗng. Không xem CI là bằng chứng cả ba máy đã nghiệm thu hoặc #6/#7 đã merge.

**Local ngày 17/10, giữ nguyên kết quả lịch sử:**

- `.venv/Scripts/python.exe -m pytest -q` với `RUN_MYSQL_TESTS=0`, `RUN_BROWSER_TESTS=0`: **25 passed, 21 skipped**. Test tùy chọn chưa chạy không được tính đạt.
- `python -m tools.check_vuong_week1`: **33/33 ca đạt** trên database MySQL thật riêng `clinic_vuong_week1` dùng dữ liệu giả lập; kiểm tra ba nhóm và dọn bản ghi tự sinh.
- Kiểm tra thêm URL khác hoa/thường cho sửa/xóa: cả ba nhóm đạt. Máy thực chạy Windows/Python 3.14.6/MySQL 8.0.46.
- Trình duyệt: thêm bệnh nhân → SELECT xác nhận MySQL → reload → tìm danh sách; lỗi trùng/nhập liệu, form bác sĩ/y tá, lịch sử rỗng và điều hướng. 14 ca đạt, 36 lượt responsive ở 320/390/768/1440px.
- Sau dọn: dữ liệu nền 11 bảng/1.144 dòng và hash không đổi; `.env` giữ nguyên. Parse Python/Jinja và diff check đạt.
- [Bàn giao](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/blob/vuong/week-1/docs/VUONG_WEEK1_HANDOFF.md), [hướng dẫn](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/blob/vuong/week-1/docs/VUONG_WEEK1_USER_GUIDE.md), [checklist/ảnh](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/blob/vuong/week-1/docs/VUONG_WEEK1_CHECKLIST.md), [kiểm tra cuối và đối chiếu CI](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/blob/vuong/week-1/docs/evidence/vuong_week1_final/README.md).

Đợt cập nhật 18/10 chỉ sửa tài liệu bàn giao/PR/hợp đồng và đọc lại log CI; không chạy lại MySQL/browser local. Các run trên gắn với SHA đã ghi; xem Checks theo head mới cho commit tài liệu tiếp theo, không gán run cũ cho SHA mới.

## Cần review và phần chưa hoàn thành

- Trung review routes/context mã chuẩn, CSRF/field, xử lý FK và test browser; Quyền điều phối merge. Review COMMENT hiện có trên #7 chưa phải approval cuối. Chưa gửi bình luận xác nhận hợp đồng lên #4.
- Hai PDF YC1 chưa rà trong đợt cập nhật này; chưa xác minh cả ba thành viên chạy cùng bộ tích hợp hoặc thử điện thoại thật. 21 ca skipped chỉ thuộc lần chạy local đã ghi; CI môi trường mục tiêu đã chạy đủ 46 test trên snapshot nêu trên.
- Nhóm cần review SQL #6 và [hướng dẫn setup #8](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/blob/3b59effd4bb86fca1f8d239af8349e73ac09e9e6/docs/SETUP.md): DB mới, schema → seed → audit → constraints → audit → queries; không chạy chồng importer adapter. Không nhập bộ SQL đó vào nhánh UI trong đợt sửa tài liệu.
- Ba trang thống kê còn là khung; tích hợp SQL báo cáo và nghiệp vụ khám/đơn nhiều bước thuộc tuần 2. Chưa đánh dấu toàn bộ tuần 1 của nhóm hoàn tất.

## Checklist

- [x] Không đổi schema/nghiệp vụ ngoài phạm vi
- [x] Đã kiểm tra ca đúng/sai/biên liên quan và lưu bằng chứng
- [x] Không chứa `.env`, credentials thật hoặc dữ liệu bệnh nhân thật trong phần bàn giao Vương
- [x] Tài liệu UI/hợp đồng liên quan đã cập nhật
- [x] CI môi trường mục tiêu tại `8c5be94` đạt 46/46; CI tích hợp hai snapshot đạt 72/72
- [ ] Trung/Quyền review và resolve nhận xét trước merge

Chưa có issue riêng được xác nhận cho phần Vương; không tự đóng issue của backend Trung.
