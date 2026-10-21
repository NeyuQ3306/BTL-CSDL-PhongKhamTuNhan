# Hướng dẫn sử dụng tuần 2 — Vương

## Chạy bản review trên Windows

Cần Python, MySQL Server đã cài và Git. Chọn nhánh `vuong/week-2`; không trộn file từ snapshot khác. Bộ chạy private dưới đây không dùng DB trong `.env`, tự tạo instance và DB mới kết thúc `_test`.

```powershell
python -m venv .venv/week2-review
.venv/week2-review/Scripts/python.exe -m pip install -r requirements-dev.txt "playwright>=1.50,<2"
.venv/week2-review/Scripts/python.exe -m playwright install chromium
.venv/week2-review/Scripts/python.exe tools/vuong_week2_prepare.py --serve
```

Runner tự tìm `mysqld.exe` bản 8.4/8.0 trong Program Files hoặc PATH. Nếu cài nơi khác, thêm `--mysqld "D:/duong-dan/bin/mysqld.exe"`. Có thể dùng `--browsers-path` khi đã có cache Chromium; không bắt buộc cache từ các tuần trước. Mỗi lần chạy dùng datadir mới, không import chồng DB cũ.

Sau test/audit, runner in URL dạng `http://127.0.0.1:<cổng>/visits/new`; mở URL đó, cổng mỗi lần khác nhau. **Giữ cửa sổ chạy mở**, Ctrl+C dừng app/instance của runner. Không dùng `python app.py` với `.env` cũ để nghiệm thu private. Nếu dùng DB đã cấu hình riêng thay runner, theo SETUP.md với DB thử trống và thứ tự schema → seed → audit → constraints → audit → queries.

## Tiếp nhận và khám

1. Vào **Tiếp nhận / khám**. Điền mã lượt, bệnh nhân, ngày vào; chọn đợt mới hoặc tái khám. Mã tối đa 12 ký tự: chữ không dấu, số, gạch ngang/gạch dưới; không dùng `new`.
2. Đợt mới: đặt mã chưa dùng, chọn bệnh/bác sĩ. Tái khám: chọn đợt đang điều trị của đúng bệnh nhân; bệnh và bác sĩ giữ nguyên, hệ thống tự cấp STT.
3. Điền mã lần khám, ngày, tiền nguyên đồng chưa gồm thuốc, kết luận và y tá hỗ trợ rồi **Lưu**. Một lượt có thể khám nhiều bệnh: chọn **Khám thêm bệnh** trong chi tiết lượt.

## Y tá, đơn thuốc và kết thúc

- **Ghi hỗ trợ y tá** để thêm người; chọn liên kết cập nhật của một y tá để sửa nội dung và giữ ngày bắt đầu đã ghi.
- **Kê đơn**: nhập mã đơn, giữ ngày bằng ngày khám, chọn thuốc/số lượng/liều dùng. Dùng **Thêm dòng thuốc** hoặc **Xóa dòng**; mỗi thuốc một dòng. Giá/tổng do server tính; xem lại đơn sau lưu để kiểm tra giá lịch sử.
- **Kết thúc lượt** khóa việc thêm lần khám/sửa hỗ trợ của lượt, không tự xác nhận khỏi đợt. **Xác nhận khỏi** kết thúc đợt, không tự đóng các lượt; tái mắc sau ngày khỏi phải dùng mã đợt mới.
- Khi lỗi, đọc thông báo đầu form; dữ liệu nhập được giữ lại. Lưu lại sau sửa; không tạo mã mới chỉ để né lỗi nghiệp vụ.

## Bốn báo cáo

Vào **Báo cáo**. Q1/Q2/Q4 chọn tháng/năm, **Xem báo cáo**. Q3 nhập/chọn gợi ý mã bệnh nhân, **Xem lịch sử**; toàn bộ lịch sử không giới hạn tháng. Tìm theo tên từ liên kết **Tìm bệnh nhân** nếu chưa biết mã.

Q1 đếm đợt có khám trong kỳ; Q2 thưởng theo ngày khỏi/ngày hỗ trợ; Q4 dùng giá bán đã lưu, không dùng giá danh mục hiện tại. Tháng rỗng có doanh thu 0 và lương cơ bản. Trên màn hình nhỏ, bảng rộng cuộn ngang trong vùng riêng; có thể Tab tới vùng bảng rồi dùng phím mũi tên. Enter kích hoạt nút thêm/xóa dòng thuốc.

[Bàn giao và giới hạn](VUONG_WEEK2_HANDOFF.md) · [Kết quả T01–T15](VUONG_WEEK2_ACCEPTANCE.md).
