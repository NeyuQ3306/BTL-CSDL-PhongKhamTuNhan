# Tiêu đề PR

[Vương][Tuần 1] Hoàn thiện UI hồ sơ, khung bốn báo cáo và kiểm thử MySQL

# Nội dung PR

## Mục tiêu và phụ thuộc

Hoàn thiện giao diện tiếng Việt tuần 1 trên backend Trung: quản lý bệnh nhân/bác sĩ/y tá, thêm và xem lại hồ sơ từ MySQL thật, cùng khung bốn báo cáo. Các trang thống kê chưa tích hợp SQL luôn hiển thị trạng thái chờ, không trình bày số liệu giả như kết quả thật.

**Phụ thuộc #4** — nền `trung/week-1` tại `5a25395` chưa merge. Nhánh này chứa 6 commit Trung trước commit UI Vương; diff về main hiện bao gồm backend đó. Phần Vương xem riêng bằng `git diff 5a25395..vuong/week-1`. Quyền phối hợp merge backend trước và đồng bộ nhánh sau squash merge nếu cần; chưa tự merge PR này.

## Thay đổi

- Layout/menu và responsive; danh sách, thêm/sửa/chi tiết ba nhóm, lỗi từng trường, hướng dẫn và trạng thái rỗng; giữ field/CSRF và mã chuẩn DB khi URL khác hoa/thường.
- GET khung thống kê bệnh/lương/doanh thu có tháng và vùng kết quả chờ; bộ lọc bệnh nhân dùng lại route lịch sử. Không thêm SQL, schema hoặc nghiệp vụ tuần 2.
- Xử lý FK 1217/1451 thành thông báo chặn xóa; mở rộng vùng bấm liên kết lỗi nhiều dòng trên điện thoại.
- Checklist, ảnh/log, hướng dẫn sử dụng, công cụ chạy lại và test hồi quy; cập nhật test browser theo nhãn nút mới.

## Cách kiểm thử và bằng chứng

- `.venv/Scripts/python.exe -m pytest -q` với `RUN_MYSQL_TESTS=0`, `RUN_BROWSER_TESTS=0`: **25 passed, 21 skipped**. Test tùy chọn chưa chạy không được tính đạt.
- `python -m tools.check_vuong_week1`: **33/33 ca đạt** trên database giả lập riêng `clinic_vuong_week1`; thử MySQL thật cho ba nhóm và dọn bản ghi tự sinh.
- Kiểm tra thêm URL khác hoa/thường cho sửa/xóa: cả ba nhóm đạt. Máy thực chạy Windows/Python 3.14.6/MySQL 8.0.46.
- Trình duyệt: thêm bệnh nhân → SELECT xác nhận MySQL → reload → tìm danh sách; lỗi trùng/nhập liệu, form bác sĩ/y tá, lịch sử rỗng và điều hướng. 14 ca đạt, 36 lượt responsive ở 320/390/768/1440px.
- Sau dọn: dữ liệu nền 11 bảng/1.144 dòng và hash không đổi; `.env` giữ nguyên. Parse Python/Jinja và diff check đạt.
- [Bàn giao](VUONG_WEEK1_HANDOFF.md), [hướng dẫn](VUONG_WEEK1_USER_GUIDE.md), [checklist/ảnh](VUONG_WEEK1_CHECKLIST.md), [kiểm tra cuối](evidence/vuong_week1_final/README.md).

## Cần review và phần chưa hoàn thành

- Trung review routes/context mã chuẩn, CSRF/field, xử lý FK và test browser. Quyền review adapter/schema/seed và điều phối merge. Chưa gửi bình luận xác nhận hợp đồng lên #4.
- Chưa rà hai PDF YC1, chưa thử máy thành viên khác/thiết bị thật; chưa chạy CI Python 3.11/MySQL 8.4 cho bản UI mới hoặc 21 test tùy chọn.
- Ba SQL báo cáo và nghiệp vụ khám/đơn nhiều bước thuộc tuần 2. Chưa đánh dấu toàn bộ tuần 1 của nhóm hoàn tất.

## Checklist

- [x] Không đổi schema/nghiệp vụ ngoài phạm vi
- [x] Đã kiểm tra ca đúng/sai/biên liên quan và lưu bằng chứng
- [x] Không chứa `.env`, credentials thật hoặc dữ liệu bệnh nhân thật trong phần bàn giao Vương
- [x] Tài liệu UI/hợp đồng liên quan đã cập nhật
- [ ] CI môi trường mục tiêu cho commit UI mới đạt
- [ ] Trung/Quyền review và resolve nhận xét trước merge

Chưa có issue riêng được xác nhận cho phần Vương nên không điền `Closes #` giả. Người mở PR bổ sung issue thật nếu có.
