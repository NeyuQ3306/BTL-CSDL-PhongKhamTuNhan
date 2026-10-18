# Hướng dẫn sử dụng ngắn — giao diện tuần 1

## Mở ứng dụng

Phiên kiểm thử trên máy Vương dùng `http://127.0.0.1:5000`, database giả lập riêng `clinic_vuong_week1`. `.env` hiện vẫn trỏ tới database bệnh viện cũ; không chạy trực tiếp với cấu hình đó cho backend 11 bảng.

Nếu cần chạy lại, mở PowerShell tại gốc repository, dùng `.venv` đã cài và database demo đã có seed:

```powershell
$savedClinicDatabase = [Environment]::GetEnvironmentVariable('DB_NAME', 'Process')
try {
    $env:DB_NAME = 'clinic_vuong_week1'
    .\.venv\Scripts\python.exe -m flask --app app run --host 127.0.0.1 --port 5000 --no-reload
}
finally {
    [Environment]::SetEnvironmentVariable('DB_NAME', $savedClinicDatabase, 'Process')
}
```

Giữ cửa sổ chạy, dừng bằng Ctrl+C. Chỉ chạy một phiên ở cổng 5000. Lựa chọn database áp dụng cho tiến trình và được khôi phục khi dừng; không ghi đè `.env`. Không import lại seed vào database đang có dữ liệu. Cài mới trên máy khác xem [SETUP.md](SETUP.md).

## Quản lý hồ sơ

1. Chọn **Bệnh nhân**, **Bác sĩ** hoặc **Y tá** từ menu.
2. Tìm bằng một phần mã hoặc họ tên; dùng **Xóa bộ lọc** để về danh sách đầy đủ. Bảng có phân trang; trên màn hình hẹp cuộn ngang bảng.
3. Chọn **Thêm**, nhập các trường có dấu *. Mã tối đa 12 ký tự chữ không dấu/số/gạch ngang/gạch dưới, không dùng `new`. CCCD là 9–20 chữ số; điện thoại 9–15 chữ số, có thể bắt đầu bằng +; giữ số 0 đầu. Ngày sinh từ 1900 đến hôm nay; thâm niên từ 0 đến 100.
4. Bấm **Thêm hồ sơ**. Khi thành công, trang chi tiết hiện thông báo; tải lại vẫn thấy dữ liệu đã lưu MySQL. Dùng hoàn toàn dữ liệu giả cho demo.
5. Chọn **Sửa hồ sơ**, chỉnh thông tin rồi **Lưu thay đổi**. Mã không đổi. URL khác hoa/thường vẫn dùng mã chuẩn đã lưu trong database.
6. Nếu có lỗi, đọc thông báo đầu form và dưới từng ô. Bấm liên kết trong tóm tắt lỗi để tới ô cần sửa. Các giá trị còn lại được giữ. Trùng mã/CCCD cần đổi dữ liệu; không bấm gửi lặp liên tục.
7. **Xóa hồ sơ chưa phát sinh nghiệp vụ** nằm trong trang chi tiết. Mở mục này, nhập đúng mã và xác nhận. Chỉ dùng để dọn hồ sơ demo vừa tạo; hồ sơ đã có lịch sử bị chặn xóa. Không có thao tác hoàn tác trên giao diện.

## Bốn báo cáo và tra cứu

- Mở **Báo cáo** để chọn nhóm thống kê bệnh, lương bác sĩ/y tá, lịch sử và tình trạng bệnh nhân, doanh thu.
- Thống kê bệnh/lương/doanh thu: chọn tháng. Đây là **khung tuần 1**, chưa có SQL thống kê; dấu “—” nghĩa là chưa có kết quả, không phải số 0.
- Lịch sử: nhập mã bệnh nhân, hoặc tìm bệnh nhân theo tên rồi mở hồ sơ → **Xem lịch sử khám**. Có thể dùng `BN001` trong seed demo. Trang hiển thị bệnh đang điều trị, các lần khám và lượt đến khám từ dữ liệu đã lưu; hồ sơ chưa khám có thông báo rỗng.
- **Lượt khám**, **Đợt điều trị** hiện chỉ tra cứu. Form ghi nghiệp vụ khám/đơn thuốc thuộc tuần 2.

## Khi gặp vấn đề

- Lỗi nhập liệu: sửa trường được đánh dấu. Trùng dữ liệu hoặc xóa hồ sơ có tham chiếu: kiểm tra mã/CCCD và lịch sử.
- Phiên biểu mẫu không hợp lệ: tải lại trang rồi nhập lại. Hồ sơ không tồn tại: quay về danh sách để tìm.
- Lỗi kết nối MySQL: kiểm tra phiên chạy đang dùng đúng database 11 bảng và tài khoản có quyền; tham khảo SETUP.md. Không gửi `.env` hoặc mật khẩu vào issue/PR.

Kết quả và ảnh minh chứng: [checklist tuần 1](VUONG_WEEK1_CHECKLIST.md), [kiểm tra sau đồng bộ backend](evidence/vuong_week1_final/README.md).
