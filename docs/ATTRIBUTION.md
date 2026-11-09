# Ghi nhận nguồn

## Mã nguồn tham khảo

Nhóm tham khảo [hospital-database-management-system](https://github.com/scmeyer41/hospital-database-management-system) của **scmeyer41 và Richard Tashjian**.

Mã được nhập tại commit `711d7b1bdff824901a75e086525d0a9f5ca14701`; lịch sử ba commit gốc được giữ. [README upstream](UPSTREAM_README.md) lưu nội dung dự án tham khảo, gồm các chức năng không thuộc bản phòng khám của nhóm.

Tại thời điểm nhập chưa thấy LICENSE cho toàn repo. Thông tin này không cấp thêm quyền sử dụng hoặc phân phối mã tham khảo; nhóm không tự gán giấy phép MIT/ISC cho mã đó.

## Phần phát triển của nhóm

- Thiết kế mô hình phòng khám tư nhân với 11 bảng và các ràng buộc theo đề.
- Tổ chức schema, seed, audit, trigger, bốn nhóm truy vấn nghiệp vụ và bảy báo cáo R01–R07.
- Xây dựng nghiệp vụ tiếp nhận, điều trị, kê đơn, giao diện bảng/biểu đồ và bộ kiểm thử.
- Viết hướng dẫn cài đặt, sử dụng và tài liệu thiết kế.

Công cụ cleanup MySQL trong `tools/private_mysql_cleanup.py` do Trung (`ptt172`) bàn giao tại PR #12, commit `d566abf5545d5c5f77caaea7deeab42fddb7f5b5`.

Biểu đồ R01–R07 dùng mã SVG của nhóm, không đóng gói thư viện biểu đồ bên thứ ba.
