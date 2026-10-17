# Bàn giao tuần 1 — Vương

Ngày tổng hợp: 17/10/2026. Nhánh `vuong/week-1`. **Phần UI và kiểm thử đã sẵn sàng review; chưa xác nhận hoàn tất toàn bộ tuần 1 hoặc tự merge.**

## Sản phẩm

| Đầu việc | Kết quả |
|---|---|
| Layout/menu | Tiếng Việt; bệnh nhân, bác sĩ, y tá, lượt/đợt khám và bốn nhóm báo cáo; không có menu giường/phẫu thuật |
| Hồ sơ ba nhóm | Danh sách/thêm/sửa/chi tiết, hướng dẫn nhập, lỗi đúng trường, thông báo, trạng thái rỗng, phân trang |
| Tích hợp MySQL | Thêm bệnh nhân qua trình duyệt, SELECT độc lập, tải lại và tìm trong danh sách đạt; CRUD cả ba nhóm được kiểm tra |
| Khung báo cáo | Ba bộ lọc tháng và vùng kết quả chưa tích hợp; lịch sử dùng service/query có sẵn, không thêm SQL tuần 2 |
| Responsive | Kiểm tra ở 320/390/768/1440px; bảng cuộn trong vùng riêng, menu/form không tràn trang |
| Bằng chứng | Checklist expected/actual, ảnh PNG, JSON/log, công cụ chạy lại, hướng dẫn sử dụng |

Backend nền là nhánh Trung tuần 1 tại `5a25395`, đã đồng bộ bằng fast-forward trên nhánh Vương. Giữ nguyên schema, SQL, `app.py`, field và CSRF. Thay đổi nhỏ ở routes gồm GET khung báo cáo, context mã chuẩn cho form sửa và xử lý lỗi FK 1217/1451.

## Tài liệu và kiểm thử

- [Hướng dẫn sử dụng](VUONG_WEEK1_USER_GUIDE.md).
- [Checklist và 12 ảnh kiểm thử chính](VUONG_WEEK1_CHECKLIST.md).
- [Bằng chứng sau đồng bộ backend](evidence/vuong_week1_final/README.md).
- [Hợp đồng tích hợp](INTEGRATION.md).
- [Nội dung PR đã chuẩn bị](VUONG_WEEK1_PR.md).

Sau đồng bộ: **33/33 ca checklist MySQL đạt**, thêm/sửa/xóa qua URL khác hoa/thường của cả ba nhóm đạt; pytest **25 passed, 21 skipped**. 21 ca bỏ qua gồm 18 test MySQL gốc cần database `_test` và 3 test Playwright chưa bật. Không ghi những ca đó là đã đạt trên bản UI mới.

Ảnh trình duyệt trước khi đồng bộ backend vẫn là bằng chứng của phiên bản tương ứng đã ghi trong checklist. Kiểm tra bổ sung sau đồng bộ được lưu riêng. Dữ liệu nền giữ 11 bảng/1.144 dòng, hash không đổi sau dọn các hồ sơ tạm. Máy Vương thực tế dùng Windows/Python 3.14.6/MySQL 8.0.46; CI mục tiêu Python 3.11/MySQL 8.4 của thay đổi UI hiện tại chưa chạy.

## Phụ thuộc review

- **Trung:** review các route GET báo cáo, context `record_id` lấy mã chuẩn DB, CSRF/field, xử lý FK và cập nhật nhãn nút trong test browser. Hợp đồng đã chạy trên máy Vương; chưa đăng lời xác nhận lên PR của Trung.
- **Quyền:** review adapter/schema/seed và tính nhất quán thiết kế; duyệt UI/phạm vi; điều phối merge theo RULES.md.
- Backend Trung [PR #4](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/pull/4) còn mở khi tổng hợp. `main` vẫn ở bản khởi tạo `f8165de`; PR Vương về main sẽ bao gồm 6 commit nền Trung. Reviewer có thể xem riêng phần Vương bằng `git diff 5a25395..vuong/week-1`. Cần phối hợp thứ tự merge và đồng bộ nhánh nếu PR #4 được squash merge, tránh tính lại phần backend như công việc Vương.

## Phần chưa hoàn thành

- Chưa rà trực quan hai PDF YC1 trong `docs/design/`.
- Chưa chạy bản UI mới trên Python 3.11/MySQL 8.4, trên máy thành viên khác hoặc điện thoại thật.
- Chưa chạy 21 test tùy chọn nêu trên; chưa có CI mới cho commit Vương.
- Chưa review/merge; chưa xác nhận nghiệm thu chung 11 bảng và SQL của nhóm. SQL báo cáo/luồng khám/đơn đa bước thuộc tuần 2, không tính đã hoàn thành từ khung giao diện.

## Rà nội dung trước commit

Không đưa `.env`, `.venv`, file cấu hình cá nhân, database dump hoặc credentials thật vào commit. Ảnh/log của Vương chứa hồ sơ tự sinh hoặc seed được nhóm xác định là giả lập; hồ sơ thử đã được dọn. Kết quả quét cụ thể được lưu trong thư mục bằng chứng cuối. Không đổi giấy phép/nguồn upstream.
