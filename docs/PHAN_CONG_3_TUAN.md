# Phân công Project 1 phòng khám tư nhân

**Nhóm:** Minh Quyền (trưởng nhóm), Trung, Vương. **Kế hoạch gốc:** 13/10–03/11/2026; bổ sung công việc tuần 3 theo quyết định 03/11, triển khai dự kiến đến 09/11 và đóng gói trước hạn 15/11. **Múi giờ:** Việt Nam. Yêu cầu 1 đã chốt thiết kế; công việc còn lại tập trung yêu cầu 2 và 3, đồng thời đóng gói bản nộp yêu cầu 1.

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

## Bổ sung tuần 3 ngày 03/11/2026 — SQL phân tích và biểu đồ

Quyền yêu cầu bổ sung 7 chức năng R01–R07 để thể hiện giá trị khai thác CSDL trong YC3. Đây là công việc mới, chưa triển khai/nghiệm thu. Mốc 03/11 là mốc nội bộ cũ; lịch mở rộng dự kiến 03–09/11, rà soát/đóng gói 10–14/11, hạn chính thức hết ngày 15/11/2026 (giờ Việt Nam). Không cam kết điểm cho từng chức năng.

### Phạm vi và giá trị sử dụng

Mỗi chức năng trình bày theo: cần biết điều gì → lấy dữ liệu nào → kết quả cho thấy gì → có thể làm gì.

| Mã | Cần biết | Dữ liệu và kết quả | Biểu đồ / sử dụng |
|---|---|---|---|
| R01 | Bệnh nào tập trung ở nhóm tuổi nào trong kỳ? | benh, dot_dieu_tri, lan_kham_benh, benh_nhan; số đợt DISTINCT theo bệnh/tuổi, số bệnh nhân riêng biệt | Cột chồng nhóm tuổi; hỗ trợ chọn đối tượng/nội dung truyền thông |
| R02 | Ngày nào có nhiều lượt tiếp nhận? | luot_den_kham, lan_kham_benh; lượt, bệnh nhân và lần khám theo ngày | Cột/đường theo ngày; hỗ trợ bố trí tiếp nhận và y tá |
| R03 | Khối lượng khám phân bố giữa bác sĩ thế nào? | bac_si, dot_dieu_tri, lan_kham_benh; số lần khám, DISTINCT bệnh nhân/đợt | Thanh ngang số lần khám; rà soát lịch và phân công đợt mới theo chuyên môn |
| R04 | Thuốc nào thường được kê, số lượng bao nhiêu? | thuoc, don_thuoc, chi_tiet_don_thuoc; số đơn DISTINCT, lượng kê theo thuốc/đơn vị | Thanh ngang số đơn có thuốc; hỗ trợ rà soát nguồn cung/dự trù |
| R05 | Ai có nhiều đợt tái mắc cùng bệnh trong lịch sử lưu? | benh_nhan, benh, dot_dieu_tri; đợt bắt đầu trong kỳ có đợt cùng bệnh đã khỏi trước đó | Bảng hồ sơ và cột số đợt tái mắc theo bệnh; hỗ trợ rà soát/tư vấn theo dõi |
| R06 | Đợt đang điều trị nào lâu chưa ghi nhận khám mới? | dot_dieu_tri, lan_kham_benh, benh_nhan, bac_si, benh; ngày đối chiếu/ngưỡng ngày | Bảng ưu tiên và cột nhóm số ngày; hỗ trợ rà soát/liên hệ, không gọi trễ hẹn |
| R07 | Chi phí đợt điều trị hoàn tất khác nhau ra sao theo bệnh? | benh, dot_dieu_tri, lan_kham_benh, don_thuoc, chi_tiet_don_thuoc; đợt khỏi trong kỳ, tính toàn bộ chi phí của đợt | Cột chồng khám/thuốc trung bình, số mẫu/min/max; hỗ trợ giải thích chi phí tham khảo |

### Quyền — SQL, đáp án và tích hợp

- [ ] Chốt hợp đồng R01–R07: bộ lọc, tên cột/kiểu dữ liệu, đơn vị đếm, thứ tự, quy tắc rỗng và phạm vi ngày trước khi Trung/Vương nối phần việc.
- [ ] Viết SQL mở rộng riêng (dự kiến database/analytics_queries.sql), giữ bốn truy vấn bắt buộc; chuẩn bị đáp án độc lập cho seed và dữ liệu biên.
- [ ] R01 chốt nhóm tuổi và tuổi tại lần khám đầu của đợt trong kỳ. R05 kiểm tra lịch sử trước đầu kỳ, tránh JOIN nhân số đợt. R06 chốt trạng thái tại ngày đối chiếu, không lấy trạng thái hiện tại thay lịch sử. R07 chỉ sử dụng đợt có đủ dữ liệu; tính khám/thuốc riêng theo đợt.
- [ ] Review SQL/backend, đối chiếu bảng/biểu đồ và tích hợp qua PR; cập nhật danh sách file SQL nộp và hướng dẫn chạy theo bộ cuối.
- [ ] Chuẩn bị phần giải thích truy vấn, tránh cộng trùng và giá trị sử dụng kết quả cho tài liệu học/thuyết trình.

### Trung — backend và slide

- [ ] Xây route/service cho R01–R07; tham số SQL an toàn, kiểm tra ngày/nhóm tuổi/ngưỡng, kiểu số và dữ liệu rỗng.
- [ ] Trả một bộ dữ liệu tổng hợp thống nhất cho bảng/biểu đồ; thống nhất hợp đồng với Vương trước khi triển khai UI. Không tạo công thức riêng ở JavaScript.
- [ ] Bổ sung kiểm thử backend đối chiếu đáp án Quyền, ca ngày biên/rỗng/mã sai; chạy hồi quy phần ảnh hưởng và bốn báo cáo bắt buộc.
- [ ] Cập nhật PPTX bằng kết quả thực chạy: câu hỏi → SQL → bảng/biểu đồ → hành động/giới hạn; sửa lỗi code/đánh số slide đã review. Phần chính nằm trong 10 phút, code chi tiết làm phụ lục.

### Vương — giao diện, biểu đồ, kiểm thử và DOCX

- [ ] Bổ sung mục báo cáo mở rộng, bộ lọc và bảng cho R01–R07; một biểu đồ chính mỗi mục, R06 ưu tiên bảng và biểu đồ tổng hợp nhóm ngày.
- [ ] Hiển thị khoảng dữ liệu, đơn vị, nhãn trục, số mẫu, trạng thái rỗng; giữ bảng để đối chiếu. Tài nguyên biểu đồ chạy khi demo không có Internet; ghi nguồn/giấy phép thư viện.
- [ ] Kiểm tra đổi bộ lọc cập nhật đồng thời bảng/biểu đồ, responsive, số 0/NULL và không có dữ liệu; chụp bằng chứng trên source xác định.
- [ ] Cập nhật DOCX theo chức năng thực hoàn thành, ảnh kết quả và mục đích sử dụng; phối hợp Trung thống nhất slide/demo.

### Lịch dự kiến và phối hợp

| Ngày | Mốc bàn giao |
|---|---|
| 03/11 | Quyền chốt công thức/bộ lọc/đáp án mẫu; Trung và Vương chốt dữ liệu trả về và bố cục |
| 04–06/11 | Quyền SQL/kiểm chứng; Trung backend; Vương UI/bảng/biểu đồ, tích hợp cuốn chiếu |
| 07/11 | Đủ luồng R01–R07 từ MySQL đến giao diện để review |
| 08–09/11 | Hồi quy, sửa lỗi, nghiệm thu và review/merge theo RULES |
| 10–14/11 | Hoàn thiện DOCX/PPTX/bộ SQL, tập demo 10 phút + 5 phút hỏi đáp, chuẩn bị Drive và quyền truy cập |
| 15/11 | Hạn nộp chính thức; chủ động nộp sớm sau khi đủ điều kiện |

Tạo nhánh mới từ main đã cập nhật; không tái sử dụng nhánh tuần 3 đã squash. Người khác review PR của Quyền. Chốt file chung trước khi sửa để tránh xung đột. Nếu trễ, báo phần thiếu và điều chỉnh với Quyền; không tự đánh dấu đủ 7 chức năng.

### Điều kiện nghiệm thu

- [ ] R01–R07 có SQL thật, giao diện bộ lọc, bảng và biểu đồ, lời giải thích mục đích/giới hạn; không ghi là đã hoàn thành chỉ vì có mockup.
- [ ] Bảng và biểu đồ cùng dữ liệu/cùng bộ lọc, đúng đơn vị/số mẫu; tiền dùng DECIMAL, không nhân tiền do JOIN nhiều thuốc/y tá; không cộng DISTINCT từng nhóm thành tổng người duy nhất.
- [ ] Seed hiện có 07–14/10/2026 (tháng 7 đến 14/10); dùng phạm vi quan sát đó, không khẳng định mùa vụ hoặc dự báo. Không so nửa tháng với cả tháng. MIN/MAX không chứng minh đầy đủ; không tự biến thiếu dữ liệu thành số 0.
- [ ] R03 không xếp hạng chất lượng bác sĩ; R04 không trộn viên/chai hoặc khẳng định lượng cần nhập khi thiếu tồn kho; R05 không coi thiếu lịch sử là chưa từng mắc; R06 không suy ra bỏ điều trị; R07 không cam kết giá điều trị.
- [ ] Dữ liệu kiểm thử riêng/rollback; giữ seed chuẩn và các đáp án Q1–Q4, không đổi schema 11 bảng trong phạm vi này. Nếu cần đổi phải review riêng.
- [ ] Có expected/actual, SHA, log/ảnh, review và kiểm tra tích hợp; chạy demo bản cuối trên laptop Quyền. Không tự đánh dấu buổi tập hay nộp bài đã xong.

## Tuần 3 theo kế hoạch gốc 27/10–03/11 (lịch sử; lịch mở rộng ở trên)

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
