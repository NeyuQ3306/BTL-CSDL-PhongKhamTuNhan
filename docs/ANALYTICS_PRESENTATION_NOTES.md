# Ghi chú học và dẫn dắt báo cáo — phần SQL của Quyền

Đọc cùng [hợp đồng bàn giao](ANALYTICS_HANDOFF.md). Các số dưới là đáp án Python
độc lập từ seed chuẩn; chỉ sử dụng như kết quả đã chạy sau khi đối chiếu log MySQL của PR.
Phạm vi 01/07–14/10/2026; ngày đối chiếu 14/10; ngưỡng 14 ngày.

## Cách mở phần trình bày

“Ngoài bốn yêu cầu truy vấn bắt buộc, nhóm xây dựng thêm bảy báo cáo để khai thác dữ liệu
đã lưu. Mỗi báo cáo xuất phát từ một câu hỏi quản lý, trả về bảng để kiểm chứng và dùng
biểu đồ để nhìn rõ sự khác biệt. Dữ liệu của nhóm là dữ liệu giả lập trong phạm vi có hạn,
nên kết quả minh họa khả năng của hệ thống, không phải kết luận về bệnh viện thực tế.”

## Dẫn dắt từng báo cáo

| Báo cáo | Cần biết → dữ liệu → đọc kết quả → sử dụng |
|---|---|
| R01 | Bệnh phân bố theo tuổi thế nào → đợt có khám và ngày sinh → 137 đợt xuất hiện trong kỳ, phân thành 29 tổ hợp bệnh/tuổi → chọn nhóm đối tượng để minh họa kế hoạch truyền thông |
| R02 | Ngày nào cần rà soát nguồn lực → ngày tiếp nhận và ngày khám → 140 lượt, 173 lần khám trong kỳ, 83 ngày có hoạt động ghi nhận → rà soát bố trí tiếp nhận/y tá; hai số khác nhau vì một lượt có thể khám nhiều bệnh |
| R03 | Công việc được phân bổ thế nào → bác sĩ của đợt và lần khám → BS004 có 28 lần khám, 19 đợt, 16 bệnh nhân trong kỳ → rà soát phân công theo chuyên môn; không kết luận bác sĩ này giỏi hơn |
| R04 | Thuốc nào thường xuất hiện trong đơn → đơn và chi tiết thuốc → T018 xuất hiện trong 18 đơn, tổng 276 gói → minh họa rà soát nhu cầu cung ứng; không lấy 276 làm số phải nhập khi chưa biết tồn kho |
| R05 | Có đợt mắc lại cùng bệnh sau khi đã khỏi không → đợt mới và lịch sử trước nó → 6 đợt đáp ứng định nghĩa trong dữ liệu mẫu → mở hồ sơ để rà soát/tư vấn theo dõi |
| R06 | Hồ sơ đang điều trị nào lâu chưa có lần khám mới → trạng thái theo ngày và lần khám cuối → 19 đợt đạt ngưỡng, 18 đợt nhóm 30+ ngày và 1 đợt nhóm 14–29 → lập danh sách rà soát/liên hệ, không gọi là bỏ điều trị |
| R07 | Chi phí ghi nhận của đợt khỏi khác nhau theo bệnh thế nào → toàn bộ chi phí từng đợt đã khỏi trong kỳ → 100 đợt đạt kiểm tra cấu trúc, 0 bị loại, chia 15 bệnh → giải thích chi phí tham khảo kèm số mẫu và min/max |

Trong 10 phút của cả nhóm chỉ nên minh họa sâu 2–3 báo cáo tiêu biểu, đặt đủ 7 báo cáo
ở bảng tổng quan/phụ lục. Quyền giải thích SQL; Trung giải thích luồng lấy dữ liệu;
Vương thao tác bộ lọc và biểu đồ theo phân vai nhóm chốt.

## Câu hỏi có thể được hỏi và ý trả lời

**Vì sao không chỉ thêm/sửa/xóa?** Đề có nói tính năng phụ nhưng chưa định nghĩa chi tiết.
Nhóm bổ sung báo cáo khai thác dữ liệu để thể hiện rõ năng lực truy vấn và mục đích sử dụng;
không tự khẳng định mỗi biểu đồ hoặc mỗi SELECT được tính một chức năng/được cộng điểm riêng.

**Dữ liệu ít thì báo cáo có ý nghĩa không?** Vẫn có thể kiểm chứng công thức và mô tả tập dữ liệu
hiện có. Hạn chế là không đủ căn cứ suy rộng, dự báo mùa vụ hay so sánh các kỳ có độ bao phủ khác nhau.
Nhóm không khẳng định bệnh viện thực tế không lưu dữ liệu lâu năm; hạn chế đang nói là seed của bài tập.

**Vì sao dùng DISTINCT?** Một đợt có nhiều lần khám; nếu đếm các dòng JOIN sẽ đếm lại đợt.
R01 chọn một ngày mốc rồi đếm đợt; R03 đếm riêng lần khám, đợt và người vì đó là ba đơn vị khác nhau.

**Vì sao tiền khám không bị nhân lên khi đơn có nhiều thuốc?** Tổng khám và tổng thuốc được
tính riêng theo đợt trước khi ghép. Test có hai thuốc và hai y tá nhưng phí khám vẫn chỉ tính một lần.
Giá thuốc dùng giá bán đã lưu trên đơn, không lấy giá hiện tại của danh mục.

**Vì sao R07 khác doanh thu Q4?** Q4 cộng tiền phát sinh trong kỳ. R07 chọn đợt khỏi trong kỳ,
nhưng cộng toàn bộ lịch sử của các đợt đó; hai báo cáo trả lời hai câu hỏi khác nhau.

**Vì sao không gọi R06 là bệnh nhân trễ hẹn?** Schema chưa có ngày hẹn. Chỉ biết khoảng cách
đến lần khám được ghi nhận cuối, nên đây là danh sách cần rà soát. Khi chọn ngày quá khứ,
phải xét ngày bắt đầu/ngày khỏi, không lấy trạng thái hiện tại để suy ngược.

**Biểu đồ có thay cho SQL không?** Không. SQL trả bảng tổng hợp; bảng và biểu đồ dùng cùng kết quả.
Đổi bộ lọc phải đổi cả hai. Biểu đồ giúp quan sát, bảng giúp truy vết số và kiểm tra.

**Làm sao biết truy vấn đúng?** Có đáp án tính độc lập bằng Python từ toàn bộ seed,
so sánh mọi cột với SQL chạy MySQL, thêm ca biên có đáp án tính tay, kiểm tra seed trước/sau,
và chạy lại các truy vấn bắt buộc Q1–Q4. Chỉ viện dẫn số test/log của lần chạy thực sự thành công.
