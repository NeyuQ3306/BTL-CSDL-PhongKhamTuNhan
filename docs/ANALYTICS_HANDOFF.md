# Bàn giao SQL phân tích R01–R07 — phần Minh Quyền

Ngày 03/11/2026. Nền: main `98bd2675bfffc64be09c87dd2897148f8b02b440`.
Theo phạm vi bổ sung của issue #3 và PR #20. Đây là SQL, hợp đồng dữ liệu,
đáp án độc lập và kiểm thử; chưa phải xác nhận backend, giao diện hay biểu đồ đã xong.

## Chạy và bộ file nộp

1. Dựng DB trống theo hướng dẫn hiện có: `schema.sql` → `seed.sql` → `constraints.sql`.
   Hoặc dùng bộ `project1_submission.sql` hiện có để dựng **một lần**; không import cả hai cách vào cùng DB.
2. Chạy `queries.sql` để kiểm tra Q1–Q4 bắt buộc.
3. Mở `database/analytics_queries.sql`, chọn đúng DB, sửa bốn biến đầu file rồi chạy.
   File trả đúng 7 tập kết quả theo thứ tự R01–R07, không ghi/xóa dữ liệu.
4. Bộ SQL nộp bổ sung `analytics_queries.sql` bên cạnh bộ SQL bắt buộc. Nếu nhóm quyết định gộp
   thành một file ở bước đóng gói cuối, nối báo cáo này sau Q1–Q4 và chạy lại trên DB trống;
   không tự đổi file gộp đã nghiệm thu trong PR này.

File chuẩn đối chiếu: `database/analytics_expected.json` (tính bằng Python từ seed, không phải log MySQL).
`tools/analytics_oracle.py` tính độc lập bằng tập hợp/vòng lặp, không chạy lại câu SQL để làm đáp án.
`tools/analytics_sql.py` đọc từng SELECT có marker Rxx và bind tham số qua `%s`; không dùng nối chuỗi đầu vào.
`tools/analytics_evidence.py` chạy SQL trên MySQL, so toàn bộ trường với oracle, kiểm tra toàn bộ 1.144 dòng trước/sau.

## Hợp đồng chung cho Trung và Vương

- Bộ lọc R01–R05/R07: `start`, `end` kiểu ISO `YYYY-MM-DD`, kỳ `[start, end)`.
  Nếu UI cho chọn ngày kết thúc bao gồm ngày đó, adapter form của Vương đổi thành ngày kế tiếp
  đúng một lần trước khi gọi API. API analytics nhận `end` không bao gồm và không cộng thêm ngày.
  Tính từ ngày gốc của form mỗi lần gửi; ngày cuối bao gồm tối đa 9999-12-30.
  R06 gửi `as_of` trực tiếp, không cộng ngày. Quy ước này đã được Trung/Vương thống nhất tại PR #22.
  Mặc định `2026-07-01` đến **hết** `2026-10-14` (`end=2026-10-15`).
- R06 độc lập với kỳ trên: `as_of=2026-10-14`, `threshold=14`; xét cuối ngày đó,
  ngưỡng nguyên 0–36500, điều kiện `>=`. UI phải phân biệt hai nhóm bộ lọc.
- Ngày hợp lệ theo lịch; `start < end`; không nhận timestamp/mã SQL thay ngày.
  Ngày/giá trị sai trả lỗi dễ hiểu trước khi truy vấn, không biến lỗi thành bảng rỗng.
  Helper kiểm chứng đã có validation; Trung cần đưa cùng quy tắc vào route của mình.
- Dùng một connection và cùng snapshot khi lấy nhiều báo cáo. SET biến phiên chỉ là runner tham khảo;
  Trung có thể dùng placeholder trực tiếp trong service, nhưng không thay công thức/đơn vị đếm.
- Ngày trả JSON dạng ISO hoặc null; mã/tên/nhãn là chuỗi; COUNT là số nguyên;
  `SUM` nguyên chuyển an toàn sang int; tiền là DECIMAL, JSON dùng chuỗi thập phân để tránh mất chính xác.
  SQL giữ tên cột như dưới. Biểu đồ chuyển tiền sang số chỉ để vẽ; bảng hiển thị từ giá trị gốc.
- Kết quả rỗng: `rows=[]`; R03 vẫn liệt kê bác sĩ với 0 hoạt động ghi nhận.
  R07 có nhóm toàn bộ đợt bị loại thì số mẫu = 0, các số tiền = null, **không đổi null thành 0**.
- Bảng và biểu đồ dùng cùng `rows` và bộ lọc. R05 đếm dòng theo bệnh; R06 đếm dòng theo `nhom_ngay`;
  đây là tổng hợp để hiển thị, không tạo một công thức nghiệp vụ khác. Giữ bảng chi tiết để đối chiếu.
- Không cộng số bệnh nhân DISTINCT của các nhóm thành tổng người duy nhất. Không trộn số lượt,
  số lần khám và số đợt. Không gộp số lượng thuốc khác đơn vị.
- Chỉ hiển thị nhãn “dữ liệu giả lập, mô tả hồ sơ đã lưu”. Không suy diễn quy luật mùa vụ,
  chất lượng bác sĩ, điều trị đúng/sai hoặc lượng thuốc cần nhập chính xác.
- MIN/MAX ngày chỉ cho biết phạm vi quan sát, không chứng minh mọi ngày đều đầy đủ.
  R02 không tự sinh hàng ngày không có bản ghi; biểu đồ cột là mặc định, không nối qua khoảng thiếu như đã biết đầy đủ.

## Định nghĩa từng báo cáo

### R01 — bệnh theo nhóm tuổi

Cần biết bệnh nào xuất hiện nhiều trong từng nhóm tuổi → lấy đợt có ít nhất một lần khám trong kỳ,
ngày sinh bệnh nhân và bệnh → đếm mỗi đợt một lần trong nhóm tuổi tại **lần khám đầu của đợt trong kỳ**
→ hỗ trợ chọn chủ đề/đối tượng truyền thông để nhóm trình bày giá trị dữ liệu.

Cột: `ma_benh`, `ten_benh`, `thu_tu_nhom` (-1/0/1/2/3), `nhom_tuoi`, `so_dot`, `so_benh_nhan`.
Tuổi đủ năm; nhóm 0–5, 6–17, 18–59, 60+. Sinh sau ngày khám có nhóm riêng “Ngày sinh không hợp lệ”.
Không loại âm thầm dữ liệu lỗi, không đưa nhóm lỗi vào kết luận về trẻ em.
Một người có hai đợt cùng bệnh có thể cho 2 đợt/1 bệnh nhân. Thứ tự bệnh, thứ tự nhóm.
Biểu đồ cột chồng `so_dot`, trục bệnh, series nhóm tuổi; tooltip có số bệnh nhân.
Nhóm tuổi là quy ước demo, không khẳng định chuẩn lâm sàng. Không gọi số đợt là tỷ lệ mắc trong cộng đồng.

### R02 — lượng tiếp nhận và lần khám theo ngày

Cần biết ngày nào nhiều hoạt động → lượt theo `ngay_vao_vien`, người tiếp nhận DISTINCT trong ngày,
lần khám theo `ngay_kham` → thấy số lượt và khối lượng khám ghi nhận → rà soát bố trí tiếp nhận/y tá.

Cột: `ngay`, `so_luot`, `so_benh_nhan_tiep_nhan`, `so_lan_kham`. Sắp ngày tăng.
Hai tập lượt và khám tổng hợp riêng rồi ghép theo ngày; một lượt khám nhiều bệnh vẫn là một lượt.
Lần khám ngày sau của lượt cũ thuộc ngày khám, không chuyển về ngày tiếp nhận.
Cột nhóm cho lượt/lần khám; số bệnh nhân ở bảng/tooltip. Số 0 chỉ là không có bản ghi loại đó trong DB,
không kết luận bệnh viện không hoạt động. Không suy ra giờ cao điểm vì schema dùng DATE.

### R03 — khối lượng khám theo bác sĩ

Cần biết phân bố công việc → lần khám trong kỳ và bác sĩ cố định của đợt → số lần khám, đợt và người khác nhau
→ hỗ trợ rà soát lịch/phân công đợt mới theo chuyên môn, không xếp hạng chất lượng.

Cột: `ma_bac_si`, `ho_ten`, `chuyen_mon`, `so_lan_kham`, `so_dot`, `so_benh_nhan`.
Giữ bác sĩ không có hoạt động với 0; xếp lần khám giảm, mã tăng để xử lý hòa.
Thanh ngang theo `so_lan_kham`. Không sửa bác sĩ của đợt cũ: repo đã khóa thuộc tính này.

### R04 — thuốc được kê

Cần biết thuốc nào thường được kê → đơn theo ngày lập và chi tiết đơn → số đơn DISTINCT chứa thuốc,
tổng lượng từng thuốc theo đơn vị → hỗ trợ rà soát nguồn cung; không suy ra số cần nhập khi chưa có tồn kho.

Cột: `ma_thuoc`, `ten_thuoc`, `don_vi_tinh`, `so_don`, `tong_so_luong`.
Thứ tự số đơn giảm, mã tăng. Thanh ngang `so_don`; bảng ghi lượng/đơn vị từng thuốc.
Đây là lượng **kê**, không phải đã bán, đã uống hay chỉ định tự dùng thuốc.

### R05 — đợt tái mắc có tiền sử ghi nhận

Cần biết ai có đợt mới của cùng bệnh sau một đợt đã khỏi → đợt bắt đầu trong kỳ và toàn bộ lịch sử trước đó
→ mỗi đợt mới một dòng, ngày khỏi gần nhất trước ngày bắt đầu → rà soát hồ sơ/tư vấn theo dõi.

Cột: `ma_dot`, `ma_benh_nhan`, `ho_ten`, `ma_benh`, `ten_benh`, `ngay_bat_dau`,
`ngay_khoi_truoc`, `so_ngay_tu_lan_khoi_truoc`. Xếp bệnh/ngày bắt đầu/mã đợt.
So sánh nghiêm ngặt `ngay_khoi_truoc < ngay_bat_dau`; nhiều đợt cũ không nhân dòng đợt mới.
Biểu đồ số dòng theo bệnh (đơn vị **đợt tái mắc**, không phải bệnh nhân); bảng giúp truy vết.
Không có lịch sử không có nghĩa chưa từng mắc. Đây là định nghĩa theo mô hình bài tập,
không tự phân biệt tái phát/tái nhiễm hay khẳng định mọi bệnh trong seed đều có cách diễn tiến này.

### R06 — đang điều trị tại ngày đối chiếu, lâu chưa ghi nhận khám

Cần biết hồ sơ nào cần rà soát → đợt bắt đầu không sau ngày đối chiếu, chưa khỏi hoặc khỏi sau ngày đó,
lần khám gần nhất không sau ngày đó → khoảng cách ngày đạt ngưỡng → lập danh sách liên hệ rà soát.

Cột: `ma_dot`, `ma_benh_nhan`, `ho_ten`, `so_dien_thoai`, `ma_benh`, `ten_benh`, `ma_bac_si`,
`ten_bac_si`, `ngay_bat_dau`, `ngay_kham_cuoi` (nullable), `chua_co_lan_kham` (0/1),
`so_ngay_chua_ghi_nhan`, `nhom_ngay` (0–6, 7–13, 14–29, 30+).
Đợt khỏi đúng ngày đối chiếu không còn đang điều trị vào cuối ngày. Lần khám tương lai không ảnh hưởng kết quả.
Nếu chưa có lần khám, tính từ ngày bắt đầu và hiển thị rõ “chưa có lần khám”; không giả tạo ngày khám.
Xếp số ngày giảm/mã tăng. Bảng ưu tiên; biểu đồ số đợt từng nhóm ngày **sau lọc ngưỡng**.
Không gọi “trễ hẹn/bỏ điều trị” vì DB không lưu lịch hẹn. Thông tin liên hệ chỉ dùng trong bảng demo giả lập,
không đưa lên biểu đồ công khai nếu sau này thay bằng dữ liệu thật.

### R07 — chi phí đợt đã khỏi theo bệnh

Cần biết chi phí ghi nhận của đợt hoàn tất → chọn đợt có ngày khỏi trong kỳ, lấy toàn bộ lần khám/đơn của đợt,
kể cả trước đầu kỳ → trung bình và min/max theo bệnh, kèm số mẫu → giải thích chi phí tham khảo.

Cột: `ma_benh`, `ten_benh`, `so_dot_tinh`, `so_dot_loai`, `tb_tien_kham`, `tb_tien_thuoc`,
`tb_tong`, `min_tong`, `max_tong`. Tiền VND; trung bình làm tròn 2 chữ số sau dấu thập phân.
Tiền khám cộng một lần/lần khám; thuốc dùng `so_luong * don_gia_ban` lịch sử, không dùng giá hiện tại.
Hai tổng được tính riêng theo đợt trước khi ghép, không JOIN trực tiếp làm nhân tiền khám.

Kiểm tra cấu trúc tối thiểu: có lần khám, dãy số thứ tự liên tục từ 1, không có đơn rỗng.
Đợt không đạt được tính vào `so_dot_loai`; không lấy chi phí 0 thay cho hồ sơ thiếu.
Không có đơn nào được hiểu là không ghi nhận kê thuốc trong mô hình này; phải kiểm tra nhập liệu nếu dùng dữ liệu khác.
**Các kiểm tra này không chứng minh hồ sơ đầy đủ ngoài thực tế.** Chỉ nghiệm thu seed với giả định lịch sử mẫu
được nhập đầy đủ; dữ liệu khác phải được xác nhận trước khi kết luận chi phí toàn đợt.

Cột chồng trung bình tiền khám/thuốc; tooltip ghi `tb_tong`, số mẫu và khoảng min/max.
Do làm tròn riêng, hai thành phần có thể lệch tổng đã làm tròn tối đa 0,01 VND; không coi là lỗi SQL.
Xếp `tb_tong` giảm/mã tăng; nhóm số mẫu 0 không vẽ cột tiền. Không gọi đây là báo giá,
không so với doanh thu Q4 (Q4 theo ngày phát sinh; R07 theo nhóm đợt khỏi).

## Kiểm chứng và nghiệm thu tiếp theo

Trong DB **thử nghiệm** có tên kết thúc `_test`, cấu hình biến môi trường DB như hướng dẫn repo:

```bash
python -m tools.quyen_db
# Bỏ dòng import trên nếu DB thử đã có seed chuẩn.
# Đặt RUN_MYSQL_TESTS=1, QUYEN_CHECK_WEEK2=1 trước khi chạy:
python -m pytest tests/test_quyen_analytics.py tests/test_quyen_database.py tests/test_quyen_week2_reports.py -v
python -m tools.analytics_evidence
```

Workflow `Quyen analytics MySQL 8.4` cài DB riêng, chạy toàn bộ lệnh trên và lưu JSON/JUnit vào artifact.
Test dữ liệu biên ghi trong transaction riêng, luôn rollback. Seed chính/schema/Q1–Q4 không đổi.
Runner bằng tay chỉ dùng SELECT và biến phiên. Test đối chiếu kiểm tra toàn bộ cột, không chỉ số dòng.
Các ca: kỳ rỗng/biên ngày/ngày nhuận, tuổi trước và đúng sinh nhật, nhiều bệnh/lượt,
nhiều thuốc/y tá, tái mắc có nhiều đợt cũ, trạng thái tại quá khứ, chưa khám,
giá thuốc lịch sử, đợt qua kỳ và đợt thiếu dữ liệu.

Trung tích hợp route/validation rồi đối chiếu cùng oracle; Vương nối bảng/biểu đồ trên cùng bộ rows,
kiểm tra trạng thái rỗng/NULL và chụp bằng chứng. Quyền review phần bàn giao của hai bạn,
đối chiếu end-to-end, kiểm tra bộ SQL nộp và nghiệm thu demo khi có bản tích hợp.
Không đánh dấu toàn bộ R01–R07 hay issue #3 hoàn thành chỉ vì SQL đã đạt.
