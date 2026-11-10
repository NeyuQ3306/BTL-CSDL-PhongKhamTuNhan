# Quản lý phòng khám tư nhân

Bài tập lớn Cơ sở dữ liệu — Project 1. Nhóm: Nguyễn Minh Quyền, Phan Trọng Trung, Vũ Đại Vương.

Ứng dụng Flask và MySQL quản lý hồ sơ bệnh nhân, bác sĩ, y tá; tiếp nhận, tái khám, điều trị và kê đơn. Bốn báo cáo bắt buộc: thống kê bệnh theo đợt trong tháng, lương bác sĩ/y tá, lịch sử bệnh nhân và doanh thu khám/thuốc. Dữ liệu hoàn toàn giả lập.

## Dành cho người chấm

- [Hướng dẫn cài đặt và chạy](docs/SETUP.md)
- [Hướng dẫn sử dụng](docs/USER_GUIDE.md)
- [Bộ nộp và yêu cầu của giảng viên](docs/SUBMISSION.md)
- [Mô hình ER](docs/design/ER_Phong_kham_Ban_chot.pdf) và [lược đồ quan hệ](docs/design/Luoc_do_quan_he_Phong_kham_Ban_chot.pdf)
- [SQL nộp](database/project1_submission.sql) và [kết quả kỳ vọng](database/expected_results.md)

Dùng nhánh main. Bản tích hợp kỹ thuật hiện tại: 98bd2675bfffc64be09c87dd2897148f8b02b440 (PR #17). Python 3.11, Flask 3, PyMySQL, MySQL Server 8.4, HTML/CSS/Jinja. Workbench là công cụ nhập SQL, không thay MySQL Server.

SQL gộp chạy một lần trên schema mới trống, sau khi chọn default schema. Không nhập thêm bộ SQL rời lên cùng schema. Chi tiết cấu hình và kiểm tra ở SETUP.

## Kết quả kiểm chứng

11 bảng, 9 trigger, 1.144 dòng seed. Tháng 10/2026: tiền khám 4.680.000đ + thuốc 5.820.800đ = 10.500.800đ. CI trên main ghi 195 test đạt; bộ tích hợp trước merge ghi 236 Linux và 2 Windows cleanup test. Windows trên laptop Quyền ghi 236 test ở source dd1f41e. Xem [hồ sơ kỹ thuật](docs/WEEK3_FINAL_STATUS.md) để phân biệt phiên bản và phạm vi từng lần chạy.

Lỗi kết nối gián đoạn HTTP503/MySQL2003 vẫn theo dõi, chưa xác định nguyên nhân. Nghiệm thu/demo trên laptop Quyền; T16 máy thứ hai không thực hiện. Chưa coi kiểm thử tự động là xác nhận diễn tập hay đã nộp bài.

## Bộ nộp

Hạn chính thức: hết ngày **15/11/2026**, giờ Việt Nam. Mốc 03/11 là kế hoạch nội bộ. DOCX do Vương chỉnh sửa, PPTX do Trung chỉnh sửa; chờ kiểm tra bản cuối. Repo hiện private; đang chờ tài khoản GitHub giảng viên để cấp quyền, chưa xác nhận người chấm truy cập được.

## Mã nguồn và làm việc nhóm

- clinic_app/: backend, templates và static đang chạy; app.py là entry point.
- database/: schema, seed, constraints, audit, truy vấn và SQL gộp.
- tests/, week3_checks/: kiểm thử; docs/: thiết kế, hướng dẫn và bằng chứng.
- Quyền phụ trách CSDL/SQL và tích hợp; Trung phụ trách backend; Vương phụ trách UI và kiểm thử người dùng.

Thay đổi qua PR và review theo [RULES](RULES.md). [Phân công](docs/PHAN_CONG_3_TUAN.md). [Lịch sử README trước đóng gói](docs/README_HISTORY.md).

## Nguồn tham khảo

Dựa trên [scmeyer41/hospital-database-management-system](https://github.com/scmeyer41/hospital-database-management-system). Giữ lịch sử và [ghi nhận nguồn](docs/ATTRIBUTION.md); không tự gán giấy phép cho mã tham khảo.

## Cập nhật cột CCCD

Bản hiện tại dùng `cccd` cho hồ sơ bác sĩ, y tá và bệnh nhân. Database cũ có cột `cmt` phải dừng app, sao lưu và chạy migration trước khi khởi động backend mới. Xem [hướng dẫn đổi cột](docs/CCCD_MIGRATION.md). Không nhập lại seed trên database đang có dữ liệu.
