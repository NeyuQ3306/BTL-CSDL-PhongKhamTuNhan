# Kiểm tra tương tác UI tuần 3 — Bước 3

**Đã kiểm tra đủ 5 nhóm yêu cầu trên DB thử riêng; không phát hiện lỗi chặn luồng, sai báo cáo hoặc tràn ngang toàn trang trong phạm vi đã chạy.** Có một quan sát UX mức P3 về ngôn ngữ thông báo validation native, chưa sửa. Không thực hiện Bước 4.

Người thực thi: **trợ lý Codex thay mặt Vương**, không phải Vương tự thao tác. Thời gian: 21/10/2026, 11:39–11:51 UTC+07:00. Nhánh `vuong/week-3`, SHA `f4869299c25fdfd0b711597e30b60ab277120f44`, source không đổi; [manifest 122 file](execution_source_sha256.json).

## Môi trường và phương thức

- Python 3.11.9 / server MySQL 8.4.7, mới khởi tạo datadir `.venv/week3-ui-20261021/mysql-data`, DB `clinic_vuong_week3_ui_test`, chỉ bind loopback. Không đọc cấu hình kết nối từ `.env`, không dùng DB của Bước 2 hoặc DB cá nhân.
- Trực tiếp điều khiển **Codex in-app browser qua cua_repl**, đọc trạng thái sau thao tác và xem ảnh thật. Đây là phiên tương tác mới, không phải chạy lại script browser pytest hoặc nhận kết quả Bước 2 là kiểm tra tay mới.
- **Phiên bản IAB chưa xác minh:** API hiện không cung cấp số phiên bản; `navigator` không có trong phạm vi evaluate chỉ đọc. Không gán Chromium 156 của runner Bước 2 cho IAB. Xem [browser-environment.json](browser-environment.json).
- SQL riêng chỉ dùng dựng danh mục giả không có UI, đổi giá thuốc thử và đối chiếu kết quả. Các thao tác tạo/sửa/xóa nhân sự/bệnh nhân và toàn bộ chuỗi khám mới đều qua form UI. Không sửa source, API, schema hoặc công thức.
- 49 lượt ghi nhận tương tác, 49 phép đo responsive = 16 nhóm URL × 3 viewport + 1 lần kiểm tra bàn phím. Đây không phải 49 testcase pytest. Có 52 ảnh JPG; **đã xem 33 ảnh cụ thể**, không nhận đã xem mọi ảnh đã lưu.

## Bộ input và expected độc lập

[expected.json](expected.json) được lập từ input U3 và quy ước trong [đáp án Quyền](../../../database/expected_results.md), không lấy output SQL làm expected. SQL dùng nguyên `database/queries.sql` với tham số tương ứng; kết quả được lưu riêng để đối chiếu UI–SQL–expected.

- Qua UI: bệnh nhân U3BN1 (sinh 01/01/1980), bác sĩ U3BS, y tá U3YT1/U3YT2. Tên/CCCD/địa chỉ/điện thoại là dữ liệu giả. CRUD xóa dùng U3TMPBN/U3TMPBS/U3TMPYT riêng, chưa có lịch sử.
- SQL fixture: bệnh U3B1/U3B2, thuốc U3T1 giá 1.000 và U3T2 giá 2.000. [sql-fixtures.json](sql-fixtures.json).
- U3D1 khám 28/29/30-09 và 01-10-2001 qua U3L1–4/U3K1–4, mỗi lần 100.000; STT1–4. Khỏi 01/10.
- Tái mắc 02/10 tạo U3D2/U3L5/U3K5, phí 100.000; cùng lượt thêm bệnh U3B2/U3D3/U3K6 phí 50.000. U3YT1 hỗ trợ cả 5 lượt; cập nhật nhiều công việc ở lượt 5 không tạo thêm dòng; U3YT2 hỗ trợ thêm lượt 5.
- Đơn U3RX1 cho U3K5: 2 × 1.000 + 3 × 2.000 = **8.000**. SQL đổi riêng giá danh mục U3T1 lên 9.999 sau kê; UI tải lại vẫn dùng giá đã lưu. U3K1 và các lần khác không kê đơn vẫn hợp lệ. Kết thúc U3L5 ngày 02/10 không tự xác nhận khỏi U3D2/U3D3.

| Kỳ | Q1 U3B1/U3B2 | Khám / thuốc / doanh thu | U3BS | U3YT1 | U3YT2 |
|---|---|---|---:|---:|---:|
| 2001-09 | 1 / 0 | 300.000 / 0 / 300.000 | 7.000.000 | 5.600.000 | 5.000.000 |
| 2001-10 | 2 / 1 | 250.000 / 8.000 / 258.000 | 8.000.000 | 5.400.000 | 5.200.000 |
| 2000-12 | 0 / 0 | 0 / 0 / 0 | 7.000.000 | 5.000.000 | 5.000.000 |

Q3 U3BN1: 5 lượt / 3 đợt / 6 lần khám / 2 dòng thuốc / 6 dòng hỗ trợ; 2 đợt đang điều trị, U3D1 đã khỏi/STT4; khám tổng 550.000 và thuốc 8.000. Không cắt lịch sử theo tháng.

Seed 2026-10 vẫn Q1=24, khám 4.680.000 + thuốc 5.820.800 = **10.500.800**. Q2 cần cộng lương cơ bản nhân viên giả mới: BS **78.000.000 + 7.000.000 = 85.000.000**, y tá **65.600.000 + 2 × 5.000.000 = 75.600.000**. Không coi chênh lệch hợp lệ này là sai báo cáo.

## Đối chiếu T01–T15 và phương thức

| Ca | Bổ sung Bước 3 | Bằng chứng / phần chuyên biệt |
|---|---|---|
| T01 | Tái khám U3D1 STT1–3; Q1 tháng9 chỉ một đợt | UI + SQL; [ảnh STT3](07-third-visit.jpg), sql-reports-2001-09.json |
| T02 | Khỏi rồi tạo U3D2, Q1 tháng10 U3B1=2 | UI + SQL; [ảnh Q1](15-custom-diseases.jpg) |
| T03 | U3D1 qua tháng, Q1 tháng9=1/tháng10 tính U3D1 một lần | UI lọc cả hai kỳ + SQL |
| T04 | Hai bệnh trong U3L5, hai đợt cùng bệnh nhân | [Ảnh lượt](08-two-diseases.jpg), SQL/Q3 |
| T05 | Không giả vờ dựng sai chủ sở hữu bằng UI bình thường | **Chưa chạy mới ở Bước 3**; HTTP sửa payload + SQL của Bước 2 cùng SHA đã đạt |
| T06 | Không giả vờ nhập STT do hệ thống cấp bằng UI | **Chưa chạy mới ở Bước 3**; direct SQL hai trường hợp độc lập của Bước 2 cùng SHA đã đạt |
| T07 | UI gửi tuần tự đợt đang điều trị trùng, bị từ chối; SQL không có U3L6/U3D4/U3K7 | [Ảnh từ chối](25-active-episode-rejected.jpg), [SQL rollback](sql-rejected-active-episode.json); **ca đồng thời** dùng bằng chứng chuyên biệt Bước 2 |
| T08 | Xác nhận khỏi tháng10 và xem Q2 tháng9/10 | [Ảnh lương](16-custom-salaries.jpg), SQL từng kỳ |
| T09 | Sửa nhiều công việc rồi thêm y tá2; xem đúng thưởng từng người | UI hỗ trợ + Q2 + SQL; mỗi cặp lượt–y tá một dòng |
| T10 | Không kê đơn U3K1; UI lịch sử và Q4 tháng9 tiền thuốc0 | [SQL không có đơn](sql-crud-and-no-order.json), ảnh/lịch sử |
| T11 | UI kê2 thuốc, SQL đổi giá giả, tải lại đơn và xem Q4 | [Ảnh giá lịch sử](10-historical-price.jpg), [ảnh doanh thu](17-custom-revenue.jpg) |
| T12 | UI số lượng0/-1, phí-1 bị native validation chặn; ngày ra sai bị server từ chối bằng tiếng Việt | [Ảnh ngày sai](11-invalid-close.jpg); **server nhận payload âm** có kiểm thử HTTP chuyên biệt Bước 2, không suy ra từ native validation |
| T13 | Không cố gây lỗi giữa giao dịch bằng UI bình thường | **Chưa chạy mới ở Bước 3**; HTTP + SQL rollback đơn dang dở của Bước 2 cùng SHA đã đạt |
| T14 | Lọc kỳ2000-12 ở Q1/Q2/Q4: tổng0, vẫn có lương cơ bản | UI + sql-reports-2000-12.json |
| T15 | Lọc U3BN1; xem đủ lịch sử, đợt đang điều trị và STT4 | [Ảnh lịch sử](18-custom-history.jpg), SQL Q3 |

Chi tiết input/expected/actual/người/ngày/SHA: [ui-observations.json](ui-observations.json). Bảng máy đọc: [coverage-matrix.csv](coverage-matrix.csv). Bằng chứng chuyên biệt được dùng lại **từ Bước 2 của cùng SHA tuần 3**, không dùng kết quả tuần 2: [cases.json](../vuong_week3_regression_20261021/browser-tests/vuong-acceptance/cases.json), [JUnit](../vuong_week3_regression_20261021/runner-output/junit.xml). Không nhận đã chạy phiên chuyên biệt mới hoặc thao tác tay cho các ca đó.

## CRUD và trải nghiệm bổ sung

Đã trực tiếp thêm/xem/sửa/tải lại/xóa hồ sơ chưa có lịch sử ở cả bệnh nhân, bác sĩ và y tá; thử mã trùng ở cả ba. Điện thoại `abc`/CCCD `abc` trả lỗi tiếng Việt và giữ dữ liệu hợp lệ; thâm niên -1 bị native validation chặn. Sau khi có lịch sử, xóa U3BN1/U3BS/U3YT1 đều bị chặn, hồ sơ còn nguyên. SQL xác nhận ba mã tạm đã xóa và đợt/lượt/lần khám từ request lỗi không tồn tại.

Đã dùng đường quay lại/Hủy/menu, sửa mã lọc không tồn tại rồi xem lại bình thường. Enter thêm dòng thuốc thứ4, focus đến select mới; Enter xóa dòng4/3 vẫn giữ hai dòng đã nhập. Bảng lịch sử tại320 px nhận phím ArrowRight và scrollLeft tăng từ0 lên24,233 px, không cuộn ngang cả trang. [keyboard.json](keyboard.json).

Thông báo nghiệp vụ server tiếng Việt, giữ dữ liệu lỗi và đưa focus đến phần lỗi. **W3-UX-01/P3:** thông báo native của ô số hiện tiếng Anh trong IAB; không mất dữ liệu và không chặn hoàn thành luồng. Xem [findings.json](findings.json). Chưa sửa/kiểm thử lại; cần xem xét ở Bước 4.

16 nhóm URL: danh sách bệnh nhân/bác sĩ/y tá/lượt/đợt, form tạo bệnh nhân/bác sĩ/y tá/tiếp nhận, form kê đơn, đơn đã lưu, chi tiết lượt và bốn báo cáo. Đã đo mỗi nhóm ở1440/390/320px: **0 tràn ngang toàn trang**. Bảng rộng có wrapper `overflow-x:auto`; danh sách đợt dùng `.table-wrap` thay vì role region, cũng cuộn riêng. [responsive.json](responsive.json), [33 ảnh đã xem](visual-review.json). Chỉ xác nhận viewport giả lập, chưa thử điện thoại vật lý/screen reader.

## Audit, bảo toàn và kết thúc

- [audit-before.json](audit-before.json): 1.144 dòng seed và findings rỗng.
- [audit-after.json](audit-after.json): 1.175 dòng = 1.144 + **31 dòng U3 chủ đích**, cả9 nhóm findings vẫn rỗng. `matches_expected_counts=false` là **đúng khi còn fixture mới**, không phải seed sai; không xóa seed để ép số đếm. Tất cả seed gốc của11 bảng được so nội dung và giữ nguyên theo [session.json](session.json).
- Source và `.env` giữ nguyên; bằng chứng cũ được rà hash riêng ở [final-verification.json](final-verification.json). Không thay dữ liệu ở DB làm việc thật.
- Đã shutdown MySQL private bằng kết nối trong bộ nhớ và dừng app; cả hai cổng đóng, không còn process MySQL private. [cleanup.json](cleanup.json). Không để credential vào log. Tab kiểm thử riêng đã đóng, viewport trả mặc định.
- [review.json](review.json): kết quả rà SQL/expected, số ghi nhận, responsive và giới hạn. [app-console.txt](app-console.txt) là log HTTP phiên này; [browser-console.json](browser-console.json) không ghi warn/error ở lần đọc cuối. [serve_private.py](serve_private.py) là harness cách ly, không phải sửa sản phẩm; cần tên DB/datadir/evidence mới nếu chạy phiên khác.

**Chưa chạy/chưa xác minh:** phiên bản IAB; T05/T06/T13 và concurrencyT07 không có phiên chuyên biệt mới ở Bước3 (đã có kết quả Bước2 cùng SHA); thiết bị di động thật/screen reader; CI; T16. T16 tiếp tục **“Chờ nhóm chốt máy thứ hai”**, không thay bằng instance khác trên máy Vương. Không sửa lỗi sản phẩm, không chuyển Bước4, không commit/push/PR.

[Hồ sơ tuần 3](../../VUONG_WEEK3_ACCEPTANCE.md).
