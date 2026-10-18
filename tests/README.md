# Kiểm thử

Checklist UI tuần 1 của Vương: `docs/VUONG_WEEK1_CHECKLIST.md`. Chạy lại bằng `python -m tools.check_vuong_week1` từ gốc repo khi database giả lập riêng `clinic_vuong_week1` đã có seed và quyền CRUD. Công cụ tạo/dọn hồ sơ tự sinh, không import lại dữ liệu và không đổi schema. Không đổi tên database này thành database thật để chạy checklist.

Ma trận ca kiểm thử ở ../docs/ACCEPTANCE.md. CI khởi tạo mới kiểm tra cú pháp, chưa chứng minh nghiệp vụ đúng. Trung bổ sung test backend và MySQL, Quyền bổ sung script đối chiếu SQL, Vương ghi kết quả UI theo tuần. Không chạy test phá dữ liệu trên DB cá nhân có dữ liệu cần giữ.
