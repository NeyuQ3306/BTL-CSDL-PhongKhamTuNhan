# Hợp đồng tích hợp ban đầu

Đây là quy ước phát triển cần Trung và Vương hoàn thiện trước 15/10, chưa phải API đã triển khai.

## Tên vật lý

11 bảng: benh_nhan, benh, dot_dieu_tri, luot_den_kham, bac_si, lan_kham_benh, y_ta, ho_tro, don_thuoc, chi_tiet_don_thuoc, thuoc. Cột snake_case tương ứng thuộc tính PDF (MaBenhNhan -> ma_benh_nhan). Dùng một tên thống nhất trên mọi OS.

## Màn hình và route mục tiêu

| Màn hình | GET mục tiêu | Dữ liệu chính |
|---|---|---|
| Bệnh nhân | /patients | Danh sách và bộ lọc tên/mã |
| Hồ sơ | /patients/<id>/history | Lượt, đợt, lần khám, đơn, bệnh đang điều trị |
| Lượt khám | /visits | Lượt và các lần khám theo bệnh |
| Đợt điều trị | /treatments | Bệnh nhân, bệnh, bác sĩ phụ trách, trạng thái |
| Thuốc | /medicines | Danh mục, đơn vị, giá hiện tại |
| Đơn thuốc | /prescriptions | Lần khám, ngày lập, các dòng thuốc |
| Thống kê bệnh | /reports/diseases?month=2026-10 | Bệnh, số đợt có lần khám trong tháng, giảm dần |
| Lương | /reports/salaries?month=2026-10 | Nhân viên, lương cơ bản, thưởng, tổng |
| Doanh thu | /reports/revenue?month=2026-10 | Tiền khám, tiền thuốc, tổng |

POST dùng cho thay đổi dữ liệu, không GET. Jinja server-rendered để giảm khối lượng API/frontend. Field và template context cần ghi rõ trong PR backend đầu tiên; không tự đổi khi frontend đã dùng.

## Quy ước báo cáo

Tháng lọc dạng YYYY-MM; khoảng thời gian là từ đầu tháng (bao gồm) đến đầu tháng tiếp theo (không bao gồm). Tháng hiện tại chỉ lấy sự kiện đến thời điểm hiện tại; ngày lưu theo giờ Việt Nam. Bác sĩ thưởng theo ngày khỏi; y tá theo ngày bắt đầu hỗ trợ của lượt. Doanh thu theo ngày khám và ngày lập đơn, là doanh thu ghi nhận từ dữ liệu khám/kê đơn, chưa phải quản lý thu tiền thực tế.

Không JOIN thẳng lần khám với nhiều dòng thuốc rồi SUM tiền khám. Aggregate từng nguồn trước. Không có dữ liệu: báo cáo rỗng/tổng 0; lương vẫn gồm lương cơ bản cho nhân viên trong phạm vi mô hình.

## Ràng buộc bắt buộc

Một bác sĩ/đợt; một lần khám tối đa một đơn; một y tá/lượt có một khoản thưởng; cùng bệnh nhân giữa lượt và đợt; không trùng đợt đang điều trị cho một bệnh; UNIQUE(lượt,đợt), UNIQUE(đợt,STT). Ngày hợp lệ, số lượng dương, tiền không âm. Không cho xóa danh mục đang được lịch sử tham chiếu. Tạo các bản ghi phụ thuộc trong cùng giao dịch; chỉ nghiệm thu trạng thái hoàn tất đủ bản ghi con theo PDF.
