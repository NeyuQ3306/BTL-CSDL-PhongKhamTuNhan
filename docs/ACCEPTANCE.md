# Kiểm thử nghiệm thu Project 1

Vương quản lý kết quả; Quyền tính đáp án mẫu; Trung bổ sung test tự động cho backend. Chưa có ca nào được đánh dấu chạy đạt tại thời điểm khởi tạo.

**Bổ sung 19/10/2026:** [Biên bản local tuần 2 của Vương](VUONG_WEEK2_ACCEPTANCE.md) đã đối chiếu T01–T15, 168 test đạt/0 skipped trên source được định danh bằng HEAD và manifest. Biên bản phân biệt browser/HTTP/SQL, CI và phần chưa chạy. T16 và nghiệm thu toàn nhóm chưa được xác nhận.

Kết quả kiểm tra **UI tuần 1 của Vương, ngày 17/10/2026** được ghi riêng trong [VUONG_WEEK1_CHECKLIST.md](VUONG_WEEK1_CHECKLIST.md): 33 ca script trên MySQL và 14 ca trình duyệt đạt, có ảnh/log và phần chưa chạy. Kết quả UI này không tự đánh dấu các ca nghiệp vụ toàn dự án bên dưới là đã đạt.

| ID | Tình huống | Kết quả mong đợi |
|---|---|---|
| T01 | Một bệnh nhân khám cùng bệnh 3 lần trong một đợt/tháng | Thống kê 1 đợt, STT 1–3 |
| T02 | Khỏi rồi tái mắc cùng bệnh trong tháng | Tạo MaDot mới, thống kê 2 đợt |
| T03 | Một đợt có lần khám ở hai tháng | Mỗi tháng có khám tính đợt một lần |
| T04 | Một lượt khám hai bệnh | Hai lần khám khác đợt, cùng bệnh nhân |
| T05 | Đợt và lượt của hai bệnh nhân khác nhau | Từ chối, rollback |
| T06 | Trùng (lượt,đợt) hoặc (đợt,STT) | Từ chối |
| T07 | Tạo đợt đang điều trị thứ hai cho cùng bệnh nhân/bệnh | Từ chối, kể cả hai yêu cầu đồng thời |
| T08 | Khỏi tháng 10, tái khám tháng 9 | Thưởng bác sĩ tháng 10 đúng 1 triệu/đợt |
| T09 | Một y tá nhiều công việc cùng lượt | Một khoản 200 nghìn; hai y tá thì mỗi người một khoản |
| T10 | Khám không kê đơn | Hợp lệ, tiền thuốc 0 |
| T11 | Một đơn nhiều thuốc, giá hiện tại thay đổi sau kê | Tổng tiền theo đơn giá đã lưu, tiền khám không nhân đôi |
| T12 | Số lượng 0/âm, tiền âm, ngày ra trước ngày vào | Từ chối với lỗi dễ hiểu |
| T13 | Lỗi giữa lúc tạo đơn và chi tiết | Không tồn tại đơn dang dở sau rollback |
| T14 | Tháng không có phát sinh | Không lỗi, tổng 0; lương cơ bản vẫn đúng |
| T15 | Xem hồ sơ | Đủ lịch sử và bệnh đang điều trị, STT hiện tại đúng |
| T16 | Import và chạy từ clone mới trên máy thứ hai | Chạy theo README, không phụ thuộc file riêng của máy tác giả |

Mỗi kết quả ghi: ngày chạy, người chạy, commit, dữ liệu đầu vào, expected, actual, đạt/chưa đạt, ảnh hoặc log. T01–T15 phải đạt trước release; T16 là cổng nghiệm thu cuối.
