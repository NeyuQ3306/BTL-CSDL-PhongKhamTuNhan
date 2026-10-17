# Kết quả đối chiếu seed — bản nháp tuần 1

Dữ liệu giả do Vương bàn giao, adapter Trung. Các số dưới tính độc lập bằng Python trên giá trị INSERT, không lấy từ truy vấn MySQL. CI đối chiếu lại Q1/Q2/Q4 với cùng oracle; tháng 10 seed chỉ đến 14/10/2026.

| Tháng | Tiền khám | Tiền thuốc | Doanh thu | Tổng lương BS | Tổng lương y tá |
|---|---:|---:|---:|---:|---:|
| 2026-07 | 9,890,000 | 14,248,600 | 24,138,600 | 107,000,000 | 72,200,000 |
| 2026-08 | 9,260,000 | 9,420,000 | 18,680,000 | 105,000,000 | 71,000,000 |
| 2026-09 | 6,520,000 | 10,335,400 | 16,855,400 | 90,000,000 | 67,200,000 |
| 2026-10 | 4,680,000 | 5,820,800 | 10,500,800 | 78,000,000 | 65,600,000 |
| 2025-12 | 0 | 0 | 0 | 70,000,000 | 60,000,000 |

## Q1 tháng 2026-07

| Bệnh | Số đợt |
|---|---:|
| B008 | 6 |
| B002 | 5 |
| B006 | 5 |
| B009 | 5 |
| B012 | 5 |
| B003 | 4 |
| B007 | 4 |
| B013 | 4 |
| B005 | 3 |
| B011 | 3 |
| B001 | 1 |
| B004 | 1 |
| B010 | 1 |
| B014 | 1 |
| B015 | 1 |

## Q1 tháng 2026-08

| Bệnh | Số đợt |
|---|---:|
| B002 | 7 |
| B013 | 7 |
| B008 | 6 |
| B011 | 5 |
| B004 | 4 |
| B005 | 4 |
| B009 | 3 |
| B012 | 3 |
| B001 | 2 |
| B003 | 2 |
| B015 | 2 |
| B006 | 1 |
| B007 | 1 |
| B010 | 1 |
| B014 | 1 |

## Q1 tháng 2026-09

| Bệnh | Số đợt |
|---|---:|
| B011 | 5 |
| B001 | 3 |
| B009 | 3 |
| B003 | 2 |
| B007 | 2 |
| B013 | 2 |
| B014 | 2 |
| B004 | 1 |
| B005 | 1 |
| B006 | 1 |
| B008 | 1 |
| B012 | 1 |
| B015 | 1 |

## Q1 tháng 2026-10

| Bệnh | Số đợt |
|---|---:|
| B004 | 4 |
| B003 | 3 |
| B005 | 3 |
| B001 | 2 |
| B009 | 2 |
| B010 | 2 |
| B013 | 2 |
| B014 | 2 |
| B002 | 1 |
| B007 | 1 |
| B011 | 1 |
| B012 | 1 |

## Ca tính tay nhỏ

Bộ test tạo QD1 với phí khám 100 VND, một đơn có 2 × 1.000 + 3 × 2.000 = 8.000 VND. Đổi giá hiện tại T001 thành 9.999 không thay đổi 8.000 tiền thuốc đã kê. Cập nhật nội dung hỗ trợ cùng QL1/YT001 vẫn chỉ một dòng, tương ứng 200.000 tiền thưởng. Khỏi ngày 02/01, tái mắc ngày 03/01 được tạo QD2. Mọi dữ liệu kiểm thử rollback.

## Cỡ dữ liệu

| Bảng | Dòng |
|---|---:|
| bac_si | 10 |
| y_ta | 12 |
| benh_nhan | 40 |
| benh | 15 |
| thuoc | 30 |
| dot_dieu_tri | 137 |
| luot_den_kham | 140 |
| lan_kham_benh | 173 |
| don_thuoc | 140 |
| chi_tiet_don_thuoc | 267 |
| ho_tro | 180 |

Tổng: 1.144 dòng. Ca qua tháng, nhiều bệnh cùng lượt, tái khám/tái mắc, lần khám không kê đơn và đơn nhiều thuốc được audit; được kiểm tra bởi test_seed_covers_required_scenarios. Seed gốc chưa có chênh lệch giá danh mục/giá bán; ca đổi giá được kiểm tra riêng trong test_valid_workflow_and_rollback, không sửa dữ liệu Vương.
