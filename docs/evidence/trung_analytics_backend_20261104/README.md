# Bằng chứng backend R01–R07 — Trung, 04/11/2026

## Nguồn và phạm vi

Nền main `98bd2675bfffc64be09c87dd2897148f8b02b440`, phụ thuộc SQL Quyền
`e65d05893e073f05c8d2efa256abc82125f5b3bf` (#21).
Chỉ thêm API JSON, service, đăng ký blueprint và bộ kiểm thử; không sửa SQL chuẩn,
seed/schema, bốn báo cáo cũ, templates hoặc static.
Không nhận đây là nghiệm thu giao diện, máy Trung/Vương hoặc toàn nhóm.

## Local

- Linux, Python 3.12. Thử `python -m pytest tests/test_trung_analytics_backend.py -q`:
  **41 passed, 12 skipped**. 12 ca cần MySQL được skip đúng cờ RUN_MYSQL_TESTS.
  JUnit: [local-unit.xml](local-unit.xml). Compile app và test mới đạt.
- Đã tải binary MySQL 8.4.13 để thử instance riêng; môi trường chặn UNIX socket,
  server báo `Can't start server: UNIX Socket : Operation not permitted`.
  Không chạy được import/đối chiếu MySQL local, không nhận skip là PASS.
  Lỗi môi trường này không được dùng làm kết luận cho lỗi 503/MySQL2003 lịch sử.
- Lệnh toàn bộ test chạy trước khi có DB chưa đủ điều kiện DB_PASSWORD/DB_NAME;
  không lấy phiên đó làm kết quả hồi quy. Kiểm chứng MySQL/hồi quy phải đọc CI thật.

## Kỳ vọng kiểm chứng MySQL

- Bảy tập mặc định có số dòng **29 / 83 / 10 / 29 / 6 / 19 / 15**,
  nhưng kiểm thử đối chiếu **mọi cột và thứ tự**, không chỉ đếm dòng.
- API toàn bộ và từng API khớp cùng oracle seed độc lập qua bảy kỳ, gồm kỳ rỗng
  và biên 14/10. R03 rỗng hoạt động vẫn giữ 10 bác sĩ với số 0.
- R01 lọc đủ nhóm tuổi, R06 đúng ngày đối chiếu; SQL bind trên dữ liệu biên
  sinh nhật/ngày nhuận, nhiều bệnh/thuốc/y tá, tái mắc/lịch sử trước kỳ,
  chưa khám, giá lịch sử và đợt thiếu dữ liệu khớp contract của Quyền.
- Ngày, mã báo cáo, nhóm tuổi, ngưỡng, tham số lạ/lặp sai trả JSON 400/404
  trước truy cập MySQL. Tiền lớn/NULL được giữ, lỗi DB không lộ nội dung riêng.
- Một read-only snapshot; rollback khi thành công và khi SELECT lỗi;
  không commit, không ảnh hưởng 1.144 dòng seed hoặc ràng buộc hiện có.

## CI

Kết quả được đối chiếu trên PR backend mới liên kết issue #3.
Các workflow `Backend and MySQL`, `Trung week 3 integrated backend` và
`Quyen analytics MySQL 8.4` dùng MySQL 8.4, kèm audit trước/sau và JUnit artifact.
Chỉ xác nhận đạt sau khi run của đúng head hoàn tất và đã đọc log; bảng này
chưa nhận đã chạy CI tại thời điểm commit ban đầu. Kết quả cuối cập nhật vào
mô tả PR sau khi có log. Không cộng chồng số test của các workflow.

## Phụ thuộc còn lại

Review SQL #21 và backend bởi người khác, Vương nối bảng/biểu đồ offline và DOCX,
nghiệm thu tích hợp rồi cập nhật ảnh slide. Không tự merge/approve/release/đóng #3.
