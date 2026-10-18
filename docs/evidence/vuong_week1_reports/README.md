# Kiểm tra khung bốn báo cáo tuần 1

Ngày: 17/10/2026. Nhánh `vuong/week-1`, nền `c442384` cùng thay đổi UI chưa commit. Môi trường Windows/Python 3.14.6/MySQL 8.0.46, database demo `clinic_vuong_week1`.

## Phạm vi thực hiện

| Trang | Bộ lọc | Vùng kết quả |
|---|---|---|
| Thống kê bệnh | Tháng `YYYY-MM` | Khung bảng mã bệnh, tên bệnh, số đợt có lần khám trong tháng |
| Lương bác sĩ/y tá | Tháng `YYYY-MM` | Các ô lương cơ bản/thưởng/tổng và khung bảng theo nhân viên |
| Lịch sử và tình trạng | Mã bệnh nhân, liên kết tìm theo tên | Dùng route lịch sử hiện có: bệnh đang điều trị, các lần khám và lượt đến khám |
| Doanh thu | Tháng `YYYY-MM` | Các ô tiền khám/tiền thuốc/tổng và khung bảng khoản doanh thu |

Ba báo cáo thống kê chỉ ghi nhận tháng và hiển thị trạng thái chờ tích hợp, chưa truy vấn dữ liệu thống kê. Dấu “—” có giải thích rõ là chưa có kết quả, không phải số 0. Không có số liệu minh họa trong vùng kết quả. Chỉ lịch sử đọc dữ liệu thật qua services/query của Trung đã có; không thêm SQL, service, schema hoặc nghiệp vụ tuần 2.

## Kết quả kiểm tra

- `pytest -q` với `RUN_MYSQL_TESTS=0`: **24 passed, 12 skipped**. Test tích hợp gốc bị bỏ qua do chưa cấu hình DB `_test`; không chạy chúng trên database làm việc.
- 10 ca mới ở `tests/test_report_shells.py`: ba báo cáo tháng không kết nối database; năm ca tháng sai trả 400; chọn lịch sử chuyển đúng route và chặn mã sai; lịch sử rỗng hiển thị thông báo phù hợp từ context giả lập.
- MySQL thật: ba báo cáo trả 200; luồng `/reports/history?patient_id=BN001` theo redirect trả đúng hồ sơ; lịch sử BN001/BN002/BN003 trả 200. Audit giữ nguyên **11 bảng, 1.144 dòng**, đúng số lượng và không có phát hiện. `.env` không đổi.
- Trình duyệt: chọn tháng 2026-09 giữ lựa chọn trong URL/input và vẫn ghi rõ chưa thống kê; nhập BN001 ở bộ lọc mở `/patients/BN001/history`, hiển thị đúng tên và dữ liệu từ hồ sơ.
- Kiểm tra năm màn hình (ba thống kê, chọn lịch sử, lịch sử BN001) ở 320/390/768/1440px: **20 lượt kiểm tra**, không tràn ngang toàn trang. Bảng có vùng cuộn riêng.
- Parse toàn bộ template và `git diff --check` đạt. Không có thay đổi trong `database/` hoặc `clinic_app/services.py` so với nền Trung.

## Ảnh minh chứng

- `salary-desktop.png`: bộ lọc tháng và vùng tổng hợp/bảng lương chưa tích hợp.
- `history-desktop.png`, `history-mobile.png`: dữ liệu lịch sử hiện có của BN001.
- `revenue-mobile.png`: bộ lọc và vùng kết quả chờ tích hợp trên màn hình hẹp.

Chưa xác nhận tính đúng của thống kê bệnh/lương/doanh thu vì chưa triển khai SQL báo cáo theo phạm vi tuần 1 được giao.
