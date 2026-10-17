# Vương cần làm gì để tích hợp giao diện tuần 1?

## Phần backend Trung đã sửa

Sửa/xóa hồ sơ lấy mã chuẩn từ bản ghi MySQL, không lấy chữ hoa/thường trong URL làm chuẩn. Ví dụ mở `/patients/bn001/edit` nhưng mã lưu là `BN001`: form vẫn giữ `BN001`, lưu thành công và chuyển đến `/patients/BN001`. Không cho đổi khóa chính khi sửa; xóa vẫn cần nhập đúng mã lưu trong DB. Áp dụng bệnh nhân/bác sĩ/y tá.

Vương không phải sửa logic backend cho lỗi này. Không chuyển mã sang lower()/upper() trong form hoặc JavaScript; giữ mã từ bản ghi.

## Các file UI đang thực sự chạy

Flask factory ở `clinic_app/__init__.py` dùng package `clinic_app`. Vì vậy template đang được nạp từ **clinic_app/templates/** và CSS từ **clinic_app/static/**. Chỉ sửa `templates/` hoặc `static/` gốc của source bệnh viện sẽ không đổi giao diện backend hiện tại.

| File | Phần Vương có thể chỉnh để tích hợp |
|---|---|
| `clinic_app/templates/week1/base.html` | Layout/menu tiếng Việt, điều hướng và thông báo flash |
| `clinic_app/templates/week1/list.html` | Danh sách, tìm kiếm, phân trang, link thêm/xem/sửa |
| `clinic_app/templates/week1/form.html` | Form thêm/sửa, hiển thị lỗi và giữ dữ liệu người dùng |
| `clinic_app/templates/week1/detail.html` | Chi tiết, link lịch sử, xác nhận xóa |
| `clinic_app/templates/week1/history.html` | Lịch sử sơ bộ tuần 1 |
| `clinic_app/templates/week1/visits.html`, `treatments.html` | Tra cứu lượt và đợt |
| `clinic_app/static/week1.css` | Màu, font, bố cục, responsive |

Đây là các file bản chạy thử Trung đang bàn giao cho Vương. Báo trên PR trước khi cùng sửa các file này. Nếu muốn dùng lại template trong thư mục gốc, cần thống nhất với Trung để cấu hình loader/đường dẫn; không sao chép form gốc rồi kỳ vọng tự nối DB.

## Hợp đồng phải giữ

| Đối tượng | Đường dẫn gốc | Field riêng |
|---|---|---|
| Bệnh nhân | `/patients` | `ma_benh_nhan`, `so_dien_thoai` |
| Bác sĩ | `/doctors` | `ma_bac_si`, `bac_nghe`, `tham_nien`, `chuyen_mon`, `trinh_do_dao_tao` |
| Y tá | `/nurses` | `ma_y_ta`, `so_dien_thoai`, `trinh_do`, `tham_nien` |

Field chung: `cmt`, `ho_ten`, `ngay_sinh`, `dia_chi`. Ngày `YYYY-MM-DD`; CMT/điện thoại dùng chuỗi giữ số 0 đầu; thâm niên số nguyên. Tất cả trường theo form hiện tại bắt buộc.

- GET/POST `/<slug>/new`: thêm hồ sơ.
- GET `/<slug>/<id>`: chi tiết.
- GET/POST `/<slug>/<id>/edit`: sửa hồ sơ; mã input **readonly**, không dùng disabled vì disabled không gửi giá trị.
- POST `/<slug>/<id>/delete`: cần `confirm_delete` bằng đúng mã từ `record[entity.pk]`.
- Mọi POST có `<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">`.
- Tạo link và action bằng `url_for` như template đang có; dùng mã bản ghi DB.
- Không dùng GET để ghi/xóa, không thêm `|safe` vào dữ liệu hồ sơ.
- Giữ `values`, `errors[field.name]`, `form_error` để hiện dữ liệu và lỗi từ server.
- HTTP 303: thành công; 422: đầu vào sai; 409: trùng mã/CMT hoặc hồ sơ có lịch sử; 400: CSRF/xác nhận sai; 404: hồ sơ không tồn tại; 503: DB không sẵn sàng.

Context chi tiết và route đã có tại [INTEGRATION.md](INTEGRATION.md). Tuần 2 bổ sung menu/luồng trong cùng base và lịch sử, nên tránh ghi đè bản tuần 2 bằng file tuần 1 cũ; khi tích hợp tuần 2 đọc thêm [WEEK2_INTEGRATION.md](WEEK2_INTEGRATION.md) trên nhánh `trung/week-2`.

## Checklist Vương xác nhận

- [ ] Chạy theo SETUP.md trên máy mình với MySQL thật và seed snake_case.
- [ ] Thêm → xem → sửa → xóa hồ sơ thử ở cả ba mục; CMT/số điện thoại giữ số 0 đầu.
- [ ] Mở URL mã khác chữ hoa/thường rồi sửa thành công, mã lưu không bị đổi.
- [ ] Trùng mã/CMT có lỗi dễ hiểu; xóa BN001 có lịch sử bị chặn và hồ sơ vẫn còn.
- [ ] Lỗi form giữ dữ liệu, hiện đúng trường lỗi; CSRF hoạt động; không lỗi layout khi xem trên màn hình nhỏ.
- [ ] Ghi commit đã chạy, môi trường, kết quả và ảnh; chỉ đánh dấu đạt sau khi tự chạy.
- [ ] Xác nhận trên PR #4 rằng tên route/field/context đã thống nhất, hoặc nêu chính xác tên cần đổi để Trung sửa cùng.

Ảnh Chromium tự động trong Actions là bằng chứng backend đã chạy UI với DB thật, không thay lời xác nhận đã chạy trên máy Vương. Quyền review/merge theo RULES.md. Không đánh dấu nghiệm thu thay người khác.

## Bằng chứng Trung đã chạy

Tuần 1: 32/32 test đạt, gồm ba luồng CRUD bằng Chromium với MySQL thật. Xem [CI](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/actions/runs/39035269920) và ảnh trong [evidence/week1](evidence/week1/). Đây là kết quả backend/UI thử của Trung, các ô checklist của Vương phía trên vẫn chờ Vương tự xác nhận.
