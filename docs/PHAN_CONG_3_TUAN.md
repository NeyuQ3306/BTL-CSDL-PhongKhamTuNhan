# Phân công Project 1 phòng khám tư nhân

**Nhóm:** Minh Quyền (trưởng nhóm), Trung, Vương. **Thời gian:** 13/10–03/11/2026, đúng 3 tuần. **Múi giờ:** Việt Nam. Yêu cầu 1 đã chốt thiết kế; công việc còn lại tập trung yêu cầu 2 và 3, đồng thời đóng gói bản nộp yêu cầu 1.

**Quyết định phạm vi ngày 21/10/2026 của Quyền:** demo và nghiệm thu bản cuối trên laptop Quyền. Bỏ tiêu chí T16/cài trên máy thứ hai khỏi điều kiện hoàn thành và release; không ghi T16 là PASS. Vẫn kiểm tra hướng dẫn chạy, SQL, T01–T15 và các lỗi ảnh hưởng demo. Quyết định này thay các yêu cầu máy thứ hai trong tài liệu cũ; bằng chứng lịch sử giữ nguyên.

## Mục tiêu và người chịu trách nhiệm

| Hạng mục | Chủ trì | Người phối hợp/review | Sản phẩm cuối |
|---|---|---|---|
| YC1: thiết kế PDF | Quyền | Trung kiểm tra khả năng triển khai, Vương rà trình bày | PDF ER, quan hệ, mô tả và ràng buộc |
| YC2: tạo MySQL và seed | Quyền | Trung review FK/transaction; Vương kiểm tra dữ liệu | schema.sql, seed.sql, constraints.sql |
| YC2: bốn nhóm truy vấn | Quyền | Trung tích hợp backend; Vương đối chiếu kết quả | queries.sql, expected_results.md |
| YC3: backend | Trung | Quyền review nghiệp vụ | Kết nối MySQL, CRUD, báo cáo và validation |
| YC3: giao diện | Vương | Trung thống nhất dữ liệu form; Quyền nghiệm thu | Giao diện tiếng Việt, lỗi dễ hiểu, lọc tháng/bệnh nhân |
| Kiểm thử và demo | Vương điều phối test | Cả ba sửa lỗi phần mình; Quyền duyệt cuối | Test log, dữ liệu demo, hướng dẫn, release |

## Tuần 1 từ 13/10 đến mốc 20/10

**Mục tiêu:** CSDL 11 bảng được dựng từ đầu và nhóm có một luồng nhập/xem bệnh nhân chạy thật.

### Minh Quyền

- 13–15/10: chuyển ER thành từ điển dữ liệu (tên cột, kiểu, NULL, PK/FK/UQ); chốt tên snake_case với Trung và Vương.
- Viết `database/schema.sql`, `database/constraints.sql` và `database/seed.sql`; tạo dữ liệu giả có tái khám, tái mắc, nhiều bệnh, đợt qua hai tháng, đơn nhiều thuốc và y tá hỗ trợ.
- Viết truy vấn nháp cho bốn nhóm yêu cầu; chuẩn bị đáp án thủ công của dữ liệu mẫu.
- Đóng gói tài liệu YC1 từ thiết kế đã chốt; không thiết kế lại theo schema upstream.
- Bàn giao: SQL import được trên DB trống; từ điển dữ liệu; bản nháp báo cáo và test dữ liệu.

### Trung

- Dựng môi trường Python/MySQL, chạy source gốc để xác định lỗi; ghi log cài đặt.
- Tách kết nối DB, cấu hình .env và dần tách `app.py` thành các module; chuẩn hóa tên bảng chữ thường.
- Chốt tên route, form field, biến template và định dạng kết quả cùng Vương trước 15/10.
- Chuyển CRUD bệnh nhân, bác sĩ/y tá sang schema nhóm; tạo nền cho luồng lượt/đợt/lần khám.
- Bàn giao: kết nối DB thật, CRUD bệnh nhân chạy được, validation cơ bản và tài liệu tích hợp.

### Vương

- Khởi chạy giao diện, chọn phần dùng lại; bỏ menu giường bệnh/phẫu thuật khỏi phạm vi nhóm.
- Việt hóa layout/menu; làm danh sách và form bệnh nhân, bác sĩ/y tá; tạo khung bốn trang báo cáo.
- Phối hợp Trung nối ít nhất luồng thêm và xem bệnh nhân với MySQL thật.
- Viết checklist test và ảnh minh chứng; kiểm tra hai PDF YC1 hiển thị rõ.
- Bàn giao: UI khung và một luồng chạy thật, danh sách ca kiểm thử.

**Nghiệm thu 20/10 lúc 20:00:** import 11 bảng không lỗi; dữ liệu mẫu có các tình huống cần thiết; thêm/xem bệnh nhân qua UI; cả ba chạy được cùng hướng dẫn. Các báo cáo có SQL nháp, chưa bắt buộc hoàn tất UI. PR trước 20:00 ngày 19/10.

## Tuần 2 sau mốc 20/10 đến mốc 27/10

**Mục tiêu:** hoàn tất yêu cầu 2 và bốn chức năng bắt buộc của yêu cầu 3.

### Minh Quyền

- Hoàn thiện Q1 thống kê bệnh theo đợt có lần khám trong tháng; Q2 lương bác sĩ/y tá; Q3 lịch sử và tình trạng hiện tại; Q4 doanh thu.
- Hoàn thiện ràng buộc liên bảng, cùng bệnh nhân, một đợt đang điều trị cho mỗi bệnh, thứ tự lần khám và trạng thái khỏi.
- Đối chiếu kết quả thật với đáp án thủ công; lập `expected_results.md`.
- Bàn giao: script SQL hoàn chỉnh và kiểm chứng được độc lập với giao diện.

### Trung

- Hoàn thiện nghiệp vụ tạo lượt/đợt/lần khám, ghi hỗ trợ y tá, xác nhận khỏi, kê đơn và chi tiết đơn.
- Dùng transaction cho thao tác nhiều bảng; trả lỗi đúng khi vi phạm, không để dữ liệu dang dở.
- Nối bốn báo cáo vào route/service; mọi bộ lọc tháng và bệnh nhân dùng tham số SQL.
- Bàn giao: bốn báo cáo và luồng khám chạy thật, có test ca lỗi trọng yếu.

### Vương

- Hoàn thiện form lượt/đợt/lần khám, hỗ trợ y tá, đơn thuốc và xác nhận khỏi.
- Hoàn thiện bốn trang báo cáo: bộ lọc, bảng kết quả, tổng tiền và trạng thái không có dữ liệu.
- Chạy luồng đầy đủ cùng Trung; ghi lỗi có input, bước tái hiện, expected/actual.
- Bàn giao: UI dùng được không cần viết SQL, kết quả khớp đáp án Quyền.

**Nghiệm thu 27/10 lúc 20:00:** bốn nhóm báo cáo chạy xuyên suốt; tiền thuốc không bị cộng trùng; thưởng bác sĩ/y tá đúng tháng; ca tái mắc và đợt qua tháng được tính đúng; đầu vào sai bị từ chối. PR trước 20:00 ngày 26/10.

## Tuần 3 sau mốc 27/10 đến mốc 03/11

**Mục tiêu:** bản nộp và demo ổn định; không mở rộng tính năng nếu bốn chức năng bắt buộc còn lỗi.

### Minh Quyền

- Review cuối schema/query và tính nhất quán ER–SQL–app; gộp `database/project1_submission.sql` theo thứ tự schema, ràng buộc, seed, truy vấn.
- Rà báo cáo PDF YC1, README và nguồn tham khảo; chốt tag `v1.0.0` khi nghiệm thu đạt.
- Chuẩn bị trình bày thiết kế, khóa, ánh xạ và giải thích truy vấn.

### Trung

- Sửa lỗi backend/transaction; hoàn thiện xử lý NULL, số tiền, dữ liệu không tồn tại và rollback.
- Kiểm tra chạy trên bản MySQL đã thống nhất; phối hợp Vương kiểm tra cấu hình và chạy bản cuối trên laptop Quyền để demo.
- Chuẩn bị giải thích route, kết nối DB và ràng buộc thực thi ở ứng dụng.

### Vương

- Regression toàn bộ ca kiểm thử; kiểm tra hiển thị, thông báo lỗi, lọc tháng và thao tác người dùng.
- Hoàn thiện hướng dẫn sử dụng, ảnh demo và kịch bản demo; tập demo với cả nhóm.
- Tính năng phụ chỉ làm sau nghiệm thu lõi: tìm kiếm/lọc, xuất CSV, in đơn. Ghi rõ đây là mục tiêu bổ sung, điểm phụ do giảng viên đánh giá, không tự cam kết đạt tối đa.

**Nghiệm thu 03/11 lúc 20:00:** cấu hình, import SQL trên DB thử trống và chạy bản cuối theo README trên laptop Quyền; không còn lỗi chặn demo; đủ PDF YC1, SQL YC2, link repo/app YC3 và hướng dẫn chạy. PR cuối trước 20:00 ngày 02/11; 03/11 chỉ sửa lỗi và đóng gói.

## Phụ thuộc và cách phối hợp

Quyền chốt schema/tên cột trước 15/10 để Trung viết truy vấn và Vương nối form. Trong lúc chờ, Vương dùng dữ liệu giả nhưng phải đánh dấu; không dùng dữ liệu giả để nghiệm thu. Trung cập nhật hợp đồng tích hợp khi thay route/field. Mỗi thành viên chịu trách nhiệm test phần mình; Vương điều phối test không có nghĩa gánh toàn bộ sửa lỗi.

Quyền duyệt thay đổi thiết kế và điều phối merge; một thành viên khác review PR của Quyền. Nếu chậm mốc, ghi phần thiếu và hạn bù trong issue, cắt tính năng phụ trước. Mỗi người phải hiểu luồng dữ liệu tổng thể để vấn đáp, không chỉ biết file của mình.

## Bộ nộp và định nghĩa hoàn thành

- YC1: PDF mô tả, ER, quan hệ và ràng buộc, nhất quán với SQL cuối.
- YC2: file .sql chạy trên MySQL trống, dữ liệu giả và toàn bộ truy vấn bắt buộc; có kết quả mẫu đối chiếu.
- YC3: repo có source, hướng dẫn cài đặt, UI trả lời bốn nhóm câu hỏi; quản lý nhập liệu để demo.
- Không tính một nhiệm vụ hoàn thành chỉ vì đã push; phải review, test, merge và có bằng chứng.
- Source upstream chưa phải sản phẩm hoàn chỉnh của nhóm. Giữ ghi nhận nguồn và kiểm tra điều kiện sử dụng trước khi phát hành công khai.
