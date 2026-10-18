# Import CSDL tuần 1

Hướng dẫn hiện hành duy nhất: [docs/SETUP.md](../docs/SETUP.md), gồm lấy snapshot khi PR #6/#7 chưa merge, cấu hình Windows, import và nghiệm thu.

Thứ tự: **schema.sql → seed.sql → audit.sql → constraints.sql → audit.sql → queries.sql**. Mỗi lần dùng database mới trống; mọi truy vấn audit phải trả 0 dòng. Đối chiếu báo cáo với expected_results.md. Các file chuẩn hiện thuộc PR #6; nhánh tài liệu này không chứa chúng, làm bước ghép snapshot trong SETUP.md để chạy ngay.

Không dùng hospital_db.sql, database/week1/clinic_seed.sql hoặc tools.import_seed cho đường import chuẩn. Không chạy seed sau trigger, không import chồng, không tự DROP dữ liệu. Xem SETUP.md để phân biệt MySQL trực tiếp cổng 3306 và Docker cổng 3307.

Khi tích hợp PR #6, giữ phần mô tả ràng buộc chi tiết của database/README.md từ PR đó, nhưng dẫn phần thao tác cài đặt về SETUP.md và bỏ chỉ dẫn importer cũ mâu thuẫn. Tài liệu bàn giao cũ là lịch sử, không thay hướng dẫn hiện hành.
