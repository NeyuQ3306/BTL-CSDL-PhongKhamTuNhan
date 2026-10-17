# Bộ đối chiếu tính tay backend tuần 2

Bộ này là bằng chứng kiểm thử của Trung, không thay thế `expected_results.md` do Quyền nghiệm thu cho dữ liệu seed toàn nhóm. Test tự tạo hồ sơ W2 riêng trong DB `_test` và dọn toàn bộ sau chạy; không thay 1.144 bản ghi nguồn.

## Kịch bản có kết quả xác định

Bệnh nhân W2BN1; bác sĩ W2BS; y tá W2YT1/W2YT2; bệnh W2B1/W2B2; thuốc W2T1 giá 1.000 và W2T2 giá 2.000 đồng.

| Ngày | Lượt/lần | Đợt, bệnh | Tiền khám | Hỗ trợ |
|---|---|---|---:|---|
| 30/01/2001 | W2L1/W2K1 | W2D1, W2B1, lần 1 | 100 | W2YT1 |
| 31/01/2001 | W2L2/W2K2 | W2D1, W2B1, lần 2 | 150 | W2YT1 |
| 01/02/2001 | W2L3/W2K3 | W2D1, W2B1, lần 3 | 200 | W2YT1 |
| 03/02/2001 | W2L4/W2K4 | W2D2, tái mắc W2B1 | 300 | W2YT1 + W2YT2 |
| 03/02/2001 | W2L4/W2K5 | W2D3, W2B2 | 50 | cùng lượt, không cộng hỗ trợ lại |

W2D1 khỏi 02/02/2001. W2D2, W2D3 còn điều trị. Đơn W2P1 ở W2K3 ngày 01/02 gồm 2 viên W2T1 + 3 viên W2T2 = 8.000 đồng. Sau lưu, đổi giá hiện tại W2T1 thành 9.999 đồng; doanh thu vẫn dùng giá bán 1.000 đồng trong đơn.

## Đáp án

| Báo cáo | Tháng 01/2001 | Tháng 02/2001 | Tháng 03/2001 |
|---|---|---|---|
| Bệnh W2B1 | 1 đợt | 2 đợt | không phát sinh |
| Bệnh W2B2 | không phát sinh | 1 đợt | không phát sinh |
| Tiền khám | 250 | 550 | 0 |
| Tiền thuốc | 0 | 8.000 | 0 |
| Tổng doanh thu | 250 | 8.550 | 0 |
| Lương W2BS | 7.000.000 | 8.000.000 | 7.000.000 |
| Lương W2YT1 | 5.400.000 | 5.400.000 | 5.000.000 |
| Lương W2YT2 | 5.000.000 | 5.200.000 | 5.000.000 |

Lịch sử: 4 lượt, 3 đợt, 5 lần khám, 2 dòng thuốc, 5 bản ghi hỗ trợ; đợt W2D1 có STT lớn nhất 3; đang mắc W2B1/W2B2 ở W2D2/W2D3. W2BN2 chưa khám: lịch sử rỗng hợp lệ.

## Ca lỗi và đồng thời

- Sai y tá sau khi tạo lượt/đợt/lần khám: 404 và cả ba bản ghi mới không tồn tại.
- Khác bệnh nhân giữa lượt/đợt: 422, không có lượt mới.
- Đợt đang điều trị trùng bệnh, thêm cùng bệnh trong một lượt, thêm sau khỏi hoặc sau đóng lượt: 409.
- Ngày sai hoặc tiền âm: 422; ngày đóng lượt trước ngày vào bị chặn.
- Ghi nhiều công việc cùng y tá/lượt: vẫn một bản ghi; đổi ngày bắt đầu cũ bị chặn 409.
- Ghi đơn có dòng thuốc thứ hai không tồn tại: 404, rollback cả header lẫn dòng đầu.
- Đơn rỗng/thuốc lặp/số lượng sai/ngày đơn khác ngày khám: từ chối; lần khám có đơn không nhận đơn thứ hai.
- Hai request đồng thời tạo đợt cùng bệnh: một thành công, một 409. Hai request tái khám đồng thời: hai lần mới có STT 2 và 3, không trùng.
- Báo cáo tháng hiện tại: chặn khoảng ở ngày hôm nay + 1; tháng 12 và tháng 2 nhuận có biên đúng. Bộ lọc sai/chuỗi SQL trả 400.

## Minh chứng browser riêng

Test Chromium tạo lượt W2L7 ngày 01/02/2001: tiền khám 120.000, kê 2 viên thuốc giá 1.000 → đơn 2.000, doanh thu 122.000. Xác nhận khỏi 02/02; nhập ngày ra 31/01 bị từ chối, lượt vẫn mở. Có 5 ảnh trong artifact `week2-browser-<run_id>`: lượt, đơn, doanh thu, lịch sử, lỗi validation.

Ảnh được tạo từ lượt test thật, không phải ảnh thiết kế. Bản sao lâu dài đã lưu tại `docs/evidence/week2/`; artifact CI gốc giữ 30 ngày. Kết quả chạy: 59/59 test đạt tại commit 26bc627, chi tiết trong `docs/evidence/trung_week2_results.txt`.
