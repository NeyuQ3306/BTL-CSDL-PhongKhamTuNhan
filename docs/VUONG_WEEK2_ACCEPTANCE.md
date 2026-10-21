# Nghiệm thu local tuần 2 của Vương — 19/10/2026

> Phạm vi hiện hành 21/10/2026: bỏ T16/máy thứ hai theo quyết định Quyền; demo trên laptop Quyền. Các nhận xét T16 bên dưới là lịch sử của phiên trước, không còn là điều kiện nghiệm thu hoặc release. Không sửa kết quả kiểm thử gốc.

> Mốc kiểm thử lịch sử. Trạng thái bàn giao hiện tại: [VUONG_WEEK2_HANDOFF.md](VUONG_WEEK2_HANDOFF.md).

Chạy lại sau review #5/#10 tại source `33901998df480d753985127ed7f7e9a791cbc5fd`: **168 passed / 0 skipped, 47,12 giây**; [JUnit](evidence/vuong_week2_prepare_20261019_224053/junit.xml), [input/expected/actual mới](evidence/vuong_week2_prepare_20261019_224053/browser-tests/vuong-acceptance/cases.json), [biên bản review phụ thuộc](VUONG_WEEK2_PR_REVIEW.md). Các số liệu dưới đây giữ nguyên phiên lịch sử, không gán cho head mới.

## Kết quả và phạm vi

**168 test đạt, 0 failure, 0 error, 0 skipped**, 48,88 giây. Đã chạy T01–T15 trên bản tích hợp hiện tại; không thấy lỗi chặn mới trong các ca đã kiểm tra. Không cần thay code ứng dụng trong bước này. Chỉ bổ sung test độc lập, cải tiến runner thu JUnit và biên bản.

Người thực hiện: trợ lý chạy công cụ trên máy Vương, không phải bằng chứng Trung/Quyền tự thao tác. Bản chạy ở nhánh `vuong/week-2`, HEAD nền `f8d80c8ea64ce0843430b5e16eac1538b7eb2d85` + working tree UI/báo cáo của bước 2–3. Chưa commit hoặc push; dùng **HEAD + manifest SHA256** để định danh source đã chạy, không gán kết quả cho riêng commit nền.

Phiên chốt: `20261019_221718` (giờ Việt Nam). Windows / Python **3.12.14** / MySQL **8.0.46** / Chromium **156.0.8078.4**. Instance MySQL mới có datadir `.venv/week2_prepare_20261019_221718/mysql-data`, chỉ bind loopback, cổng **51501**, DB **clinic_vuong_week2_prepare_test**. Không kết nối DB từ `.env`.

- [JUnit từng testcase](evidence/vuong_week2_prepare_20261019_221718/junit.xml)
- [Log đầy đủ tên testcase và trạng thái](evidence/vuong_week2_prepare_20261019_221718/pytest.txt)
- [Từng ca: ngày chạy, input, expected, actual, phương thức, ảnh](evidence/vuong_week2_prepare_20261019_221718/browser-tests/vuong-acceptance/cases.json)
- [Ma trận CSV](evidence/vuong_week2_prepare_20261019_221718/acceptance-matrix.csv)
- [Manifest source đã chạy](evidence/vuong_week2_prepare_20261019_221718/source_sha256.json)
- [Môi trường, audit, hash seed, khảo sát màn hình](evidence/vuong_week2_prepare_20261019_221718/results.json)

## Chuỗi dữ liệu độc lập

Expected được tính tay theo dữ liệu dưới đây, không lấy output backend làm đáp án. Test browser nhập thật qua form, HTTP dùng session/CSRF thật; không mock DB hoặc transaction.

1. W2BN1 khám W2B1 trong AD1 ở AC1/AC2/AC3 ngày 28/29/30-09-2001, mỗi lần 100.000 đồng; STT 1–3.
2. AC4 tái khám AD1 ngày 01/10, 100.000 đồng, STT 4. Xác nhận khỏi AD1 ngày 01/10.
3. AC5 tái mắc W2B1 ngày 02/10 với đợt mới AD2, 100.000 đồng. Thêm bệnh W2B2/đợt AD3 trong cùng lượt, 50.000 đồng.
4. W2YT1 hỗ trợ cả 5 lượt; cập nhật nhiều công việc trong AC5 rồi thêm W2YT2. Đơn AR1 cho AK5 có 2 × 1.000 + 3 × 2.000 = 8.000 đồng; đổi giá danh mục W2T1 thành 9.999 sau lưu đơn.
5. Tháng 9: khám 300.000, thuốc 0; bác sĩ không có thưởng khỏi. Tháng 10: khám 250.000, thuốc 8.000, doanh thu **258.000**; W2BS thưởng 1.000.000; W2YT1 thưởng 400.000 cho AC4/AC5, W2YT2 thưởng 200.000.
6. Lịch sử: 5 lượt / 3 đợt / 6 lần khám / 2 dòng thuốc / 6 dòng hỗ trợ, 2 đợt đang điều trị; tổng khám 550.000, thuốc 8.000. Đợt đã khỏi AD1 có STT cuối 4. AC5 được đóng ngày 02/10 sau khi thử ngày sai.

T05/T06/T07/T13 dùng các bộ fixture riêng, cùng danh mục thử nhưng được tạo/dọn độc lập giữa từng test. Không cộng số dòng của các fixture riêng vào chuỗi trên.

## Ma trận T01–T15

Tất cả trạng thái trong bảng là **Đạt local** của phiên chốt; phương thức ghi rõ để không nhầm mọi ca đều được nhập bằng UI bình thường.

| ID | Thao tác / input | Expected và actual đã khớp | Phương thức / bằng chứng |
|---|---|---|---|
| T01 | Khám AD1 ba lần 28/29/30-09 | Q1 tháng 9 = 1, STT SQL = [1,2,3] | Browser form → báo cáo + SQL; `T01-three-visits.png` |
| T02 | Khỏi AD1 ngày 01/10, tạo AD2 ngày 02/10 | Hai mã đợt W2B1; Q1 tháng 10 = 2 trước khi thêm bệnh khác | Browser + SQL; `T02-recurrence.png` |
| T03 | AD1 có khám tháng 9 và 10 | Mỗi tháng tính một đợt | Hai trang báo cáo HTML; `T03-cross-month.png` |
| T04 | AC5 khám thêm W2B2/AD3 | Hai lần khám thuộc AD2/AD3, đều W2BN1 | Browser + SELECT chủ đợt; `T04-two-diseases.png` |
| T05 | Gửi AC2 của W2BN2 tham chiếu AD1/W2BN1 | HTTP422; AC2=0, AK2=0; AD1 ban đầu vẫn còn 1 | HTTP cố tình sửa payload qua session browser + SQL; JSON biên bản |
| T06 | Trùng (AC2,AD1), sau đó STT1/AD1 trên AC3 chưa thuộc AD1 | Cả hai SQL1644; AD1 vẫn chỉ 2 lần khám, AKBAD=0 | Browser tạo nền + direct SQL; JSON ghi từng câu thử |
| T07 | Hai session/CSRF gửi đồng thời hai mã đợt cùng bệnh nhân/bệnh | Một 303, một 409; chỉ 1 lượt/1 đợt/1 lần khám | Hai HTTP connection bắt đầu bằng barrier, thời gian request chồng nhau + SQL |
| T08 | Tái khám tháng 9, khỏi ngày 01/10 | Thưởng W2BS tháng 9 = 0, tháng 10 = 1.000.000 | Browser xem hai kỳ lương; `T08-cure-month.png` |
| T09 | W2YT1 nhiều công việc trong AC5, thêm W2YT2 | AC5 có 2 cặp; mỗi người một khoản/AC5; YT1 tháng 10 thêm khoản AC4 | Browser form/bảng lương + SELECT; `T09-nurse-bonuses.png` |
| T10 | AK1 không kê đơn | Có lần khám hợp lệ, ma_don=null, tien_thuoc=0 | HTTP JSON từ session browser; dữ liệu MySQL thật |
| T11 | Đơn 2 thuốc, đổi giá danh mục, 2 y tá hỗ trợ | Thuốc giữ 8.000; phí khám tháng 10 giữ 250.000; tổng 258.000 | Browser lưu/reload đơn và báo cáo + SQL đổi riêng giá thuốc thử; `T11-historical-prices.png` |
| T12 | Số lượng 0/-1, tiền khám -1, ngày ra trước ngày vào | Các trường hợp HTTP422; giữ giá trị nhập; không header đơn/AC6; ngày ra vẫn null | Browser bỏ kiểm tra HTML khi thử số lượng, HTTP sửa payload tiền, browser ngày sai + SQL; `T12-invalid-close.png` |
| T13 | Đơn ARFAIL, thuốc W2T1 hợp lệ rồi ZZMissing không tồn tại | HTTP404; header=0, detail=0; lịch sử tiền thuốc 0 | HTTP gửi field lặp thật, SQL kiểm tra rollback; `T13-no-partial-prescription.png` |
| T14 | Tháng 12/2000 rỗng | Q1=[]/0, doanh thu=0; W2BS 7 triệu, y tá 5 triệu | Browser + JSON; `T14-empty-month.png` |
| T15 | Xem W2BN1, truyền tháng rỗng để thử lọc lịch sử | Đủ các số dòng ở chuỗi trên, AD1 STT4; không bị cắt lịch sử | Browser + JSON, ảnh `T15-history-1440/390/320.png` |

Ảnh trong [thư mục nghiệm thu](evidence/vuong_week2_prepare_20261019_221718/browser-tests/vuong-acceptance/T01-three-visits.png). T05/T07/T13 là ca dữ liệu mà UI đã ngăn chọn sai hoặc không thể dựng lỗi giữa giao dịch bằng thao tác thường; vì vậy kiểm tra HTTP/SQL được ghi tách, không gọi đó là thao tác UI của người dùng.

T06 được tăng chất lượng so với phiên đầu: lần thử trùng STT dùng AC3 có một bệnh khác, chưa có cặp (AC3,AD1); ngày khám nằm đúng khoảng của AC3. Nhờ đó việc từ chối không bị lẫn với trường hợp trùng (lượt,đợt). Trigger trả SQL1644, không khẳng định riêng UNIQUE1062 là cơ chế đã bắt lỗi trong hai lần thử này.

## Kiểm tra bổ sung và hồi quy

- **CSRF local:** thiếu/sai token ở POST lâm sàng trả400, không tạo lượt. Test cũ tiếp tục kiểm tra token Unicode và CRUD. Không tắt CSRF trên app khi kiểm thử.
- **Transaction local:** ngoài T05/T13 còn các test lỗi tạo lượt ở nhiều bước, đơn thứ hai, dòng thuốc không cân, ngày sai, tái khám đợt khỏi/lượt đóng và cấp STT đồng thời. Test có chủ đích gây lỗi rồi xác nhận SQL không lưu một phần.
- **CRUD tuần 1 qua Chromium:** bệnh nhân/bác sĩ/y tá đều thêm → xem → sửa bằng URL khác hoa/thường → xóa → GET404. Có ảnh trong `browser-tests/week1/`. Backend local kiểm tra thêm trùng mã/CMT, bảo vệ xóa hồ sơ tham chiếu, XSS escaping, mã không được sửa và validation.
- **Báo cáo local:** chạy lại UI–JSON–SQL–oracle 5 tháng và JSON 40 bệnh nhân; các ca kỳ hiện tại/ngày mai/năm nhuận/chuyển tháng của Quyền cũng chạy local trong suite. Bảng chi tiết ở `browser-tests/vuong-reports/seed-parity.json` và `edge-parity.json`.
- **Responsive local:** 18 đường dẫn × 3 viewport 1440/390/320 px, 0 trang tràn ngang toàn trang. Có thêm ảnh bốn báo cáo ở ba viewport, form kê đơn 320 px và T15 ba viewport. Bảng rộng cuộn trong vùng riêng.
- **Bàn phím local:** Enter thêm/xóa dòng thuốc, focus tới dòng mới và tới lỗi server, ID/label không trùng. Không có lỗi JavaScript được ghi trong các test browser mới.

Đã xem trực tiếp ảnh T01, T12 và T15 320 px của phiên chốt; không nhận đã rà bằng mắt mọi ảnh tự động.

## Dọn dữ liệu và audit

Runner tạo instance/datadir mới cho phiên này, import schema → seed → audit → constraints → audit → queries. Fixture chỉ dọn mã thử do suite tạo (W2/AC/AD/AK/AR và mã CRUD riêng), không xóa hoặc sửa seed để làm đẹp số đếm. Lỗi direct SQL được rollback; giá danh mục thay đổi trong T11 chỉ thuộc W2T1 là thuốc thử và được dọn cùng fixture.

Sau toàn suite và browser khảo sát: **11 bảng / 9 trigger / 1.144 dòng**, `matches_expected_counts=true`, 9 nhóm findings rỗng, 10 tập audit SQL rỗng. Hash từng bảng seed trước/sau toàn suite và browser giống nhau; `.env` không đổi. Đây là bằng chứng dữ liệu nền được bảo toàn, không chỉ kiểm tra tổng số dòng.

## Phân biệt local, CI và chưa chạy

| Nhóm bằng chứng | Trạng thái |
|---|---|
| T01–T15, CSRF, hồi quy CRUD, báo cáo, responsive của bản working tree này | **Đã chạy local**, theo JUnit/manifest/biên bản ở trên |
| CI của source Vương hiện tại | **Chưa chạy**, do chưa push. Không đổi số local thành số CI |
| CI lịch sử của Trung/Quyền ở các bản phụ thuộc | Chỉ là tham khảo đã ghi trong bàn giao trước; không thay kết quả nghiệm thu source Vương hiện tại, không được đọc lại log trong bước này |
| T16: clone mạng sạch trên máy thứ hai | **Chưa chạy**, cổng tuần 3; không đánh dấu đạt từ private instance trên cùng máy |
| Windows/Python 3.11/MySQL 8.4 theo môi trường mục tiêu | **Chưa chạy local trong phiên này**; kết quả trên 3.12/8.0 không tự thay thế |
| Firefox/WebKit, trình duyệt điện thoại thật, screen reader, JavaScript tắt, soak/load kéo dài | **Chưa chạy**; không khẳng định từ Chromium viewport hoặc một cặp request đồng thời |
| Review/approve/merge và nghiệm thu cả nhóm | **Chưa thực hiện**, cần các bước bàn giao/review sau |

Phiên trước `221500` đã có 168 test đạt nhưng T06 còn chồng lý do từ chối; phiên chốt `221718` chạy lại toàn suite sau khi tách hai tình huống. Không phát hiện lỗi ứng dụng mới cần sửa. Không đăng GitHub hoặc thay trạng thái issue.

App private phiên chốt còn chạy tại `http://127.0.0.1:60167/reports` khi tiến trình còn sống. Không cần người dùng thao tác thêm để hoàn tất bước kiểm thử này.
