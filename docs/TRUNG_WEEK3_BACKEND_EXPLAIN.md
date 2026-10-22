# Trung — giải thích backend khi vấn đáp

## Luồng yêu cầu

app.py gọi create_app trong clinic_app/__init__.py: nạp cấu hình/.env, đăng ký blueprint, CSRF và handler lỗi. routes.py quản lý hồ sơ/tra cứu; clinical_routes.py nhận form nghiệp vụ và báo cáo. workflows.py chịu trách nhiệm ghi; reports.py đọc bốn báo cáo. Giao diện không tự quyết định giá thuốc hoặc STT tái khám.

Ví dụ tiếp nhận: GET /visits/new lấy lựa chọn danh mục và CSRF. POST cùng URL kiểm CSRF, parse dữ liệu, gọi create_visit. Service khóa bệnh nhân, tạo lượt/đợt/lần khám/hỗ trợ trong một transaction. Thành công commit rồi303 về chi tiết lượt; bất kỳ bước nào lỗi thì rollback toàn bộ, báo lỗi và giữ dữ liệu form khi thích hợp. Không tự retry request ghi khi không biết kết quả commit, tránh tạo trùng.

## Kết nối và transaction

db.py giữ một kết nối trong Flask g theo request/app context, autocommit=False, timezone+07. fetch_one/fetch_all dùng placeholder %s với tuple tham số; tham số được driver xử lý, không ghép đầu vào vào SQL. Tên bảng động chỉ lấy từ cấu hình nội bộ cố định.

transaction() begin/yield/commit, lỗi rollback và giải phóng cờ trong finally; không hỗ trợ transaction lồng nhau. Teardown rollback phần còn lại và đóng kết nối, không tự commit. Khi mất kết nối hoặc commit không được xác nhận, báo thất bại vận hành; ứng dụng không thể bảo đảm chứng minh server chưa commit chỉ từ lỗi mạng. Cần tra mã hồ sơ/đơn trước khi thử lại, không tuyên bố mọi lỗi kết nối đều chắc chắn không lưu.

## Ràng buộc ứng dụng

Patient lock FOR UPDATE tuần tự hóa thao tác cùng bệnh nhân. Sau khi khóa, service dùng locking read hiện tại cho lượt/đợt/lần khám để tránh snapshot cũ khi có request đồng thời. Danh mục/giá dùng FOR SHARE; thuốc khóa theo thứ tự mã. Ghi SQL trực tiếp có thể không theo giao thức này; FK/UQ/CHECK/trigger và audit của Quyền bổ sung bảo vệ, không khẳng định trigger kiểm tra được mọi điều kiện tại COMMIT.

Lượt và đợt phải cùng bệnh nhân; bác sĩ cố định theo đợt. STT trong đợt liên tiếp; một bệnh chỉ khám một lần trong lượt. Đợt khỏi không tái khám; tái mắc tạo đợt mới sau ngày khỏi. Đóng lượt không tự xác nhận khỏi, xác nhận khỏi không tự đóng các lượt.

## NULL và tiền

ngay_ra_vien NULL nghĩa là lượt đang mở; ngay_khoi NULL nghĩa là chưa có ngày khỏi. Không thay NULL bằng một ngày giả hoặc chuỗi rỗng trong DB. Lần khám không có đơn là trạng thái hợp lệ; lịch sử dùng LEFT JOIN và tiền thuốc0 khi không kê. JSON ngày chưa có là null; HTML thể hiện trạng thái dễ hiểu.

Tiền dùng Decimal/DECIMAL(12,0), không dùng float. Tiền khám nguyên đồng không âm, tối đa999999999999; số lượng thuốc nguyên dương tối đa2147483647. Server lấy giá danh mục khi lưu vào don_gia_ban; thay giá hiện tại không làm đổi tiền lịch sử. Client không được gửi tổng/giá để quyết định tiền lưu. Tổng nhiều dòng có thể lớn hơn trần một ô tiền; không tự giới hạn tổng bằng trần một bản ghi.

## Báo cáo và lỗi

Q1 đếm distinct đợt có khám trong kỳ, không đếm số lần khám. Q2 bác sĩ7triệu+1triệu/đợt khỏi theo ngày khỏi; y tá5triệu+200nghìn/cặp y tá–lượt theo ngày hỗ trợ. Q3 toàn bộ lịch sử, không cắt theo tháng. Q4 cộng riêng phí khám và chi tiết thuốc theo giá đã lưu để tránh nhân tiền khi JOIN nhiều thuốc/y tá. Kỳ dùng [đầu tháng, đầu tháng sau); tháng hiện tại dừng ở ngày mai theo Việt Nam.

400 là bộ lọc/CSRF sai,404 không có dữ liệu,409 trùng/xung đột trạng thái,422 đầu vào nghiệp vụ không hợp lệ,503 lỗi vận hành DB theo handler. Báo cáo format=json có error envelope cho lỗi HTTP400/404/422; lỗi hạ tầng500/503 hiện vẫn có thể là HTML. Không gọi đây là JSON API ghi: các thao tác ghi hiện là form POST và303.

## Câu hỏi tự luyện

- Vì sao khóa bệnh nhân trước mà không chỉ khóa mã đợt? Hai request có thể cùng tạo hai mã đợt mới cho một bệnh nếu chưa có hàng đợt để khóa.
- Đơn thuốc lỗi ở dòng thứ hai có để lại header không? Transaction rollback cả header/chi tiết; test kiểm tra0dòng rồi thử lại cùng mã thành công.
- Làm sao chứng minh clone máy khác chạy được? Ghi SHA, phiên bản, import/audit, pytest và thao tác UI thực; CI/máy cũ không thay bằng chứng máy thứ hai.
- Test commit failure có chứng minh mọi mất mạng đều không lưu? Không; mock chứng minh nhánh xử lý rollback/cleanup. Kết quả commit trên server có thể không xác định khi kết nối mất.
