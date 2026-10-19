# Bàn giao bốn báo cáo tuần 2 — Vương

> Mốc kiểm thử lịch sử. Trạng thái bàn giao hiện tại: [VUONG_WEEK2_HANDOFF.md](VUONG_WEEK2_HANDOFF.md).

Cập nhật bước 4: [Nghiệm thu độc lập T01–T15](VUONG_WEEK2_ACCEPTANCE.md) đã chạy lại toàn bộ source với 168 test đạt/0 skipped, kèm hồi quy CRUD và audit. Các số 163 test dưới đây giữ lại theo phiên bàn giao báo cáo ban đầu.

Ngày chạy: 19/10/2026, giờ Việt Nam. Nhánh `vuong/week-2`, nền `f8d80c8ea64ce0843430b5e16eac1538b7eb2d85`. Source ứng dụng/test sau sửa được định danh bằng [manifest SHA256](evidence/vuong_week2_prepare_20261019_220540/source_sha256.json); chưa commit/push. Giữ nguyên công việc bước 1–2.

## Phạm vi hoàn thiện

- Q1: bộ lọc tháng/năm, tổng đợt theo bệnh, số bệnh phát sinh; bảng theo số đợt giảm dần, ca tháng rỗng. Không nhầm đợt mắc với lần khám.
- Q2: tách bảng bác sĩ/y tá, lương cơ bản/số lần thưởng/tiền thưởng/tổng lương; tổng mỗi nhóm và toàn bộ; tháng rỗng vẫn có lương cơ bản, thông báo không phát sinh thưởng.
- Q3: chọn mã bệnh nhân bằng gợi ý từ DB hoặc tìm theo tên trong danh sách; đủ toàn bộ lượt/đợt/lần khám, đợt đã khỏi và đang điều trị, STT, đơn thuốc/liều/giá lịch sử và y tá. Có tổng tiền khám/thuốc riêng. Không lọc lịch sử theo tháng.
- Q4: tiền khám, thuốc và tổng doanh thu; bảng chi tiết, tổng hợp và trạng thái doanh thu 0.
- Tiền dùng filter `money`, ngày hiển thị dd/mm/yyyy; bảng có caption/header và vùng cuộn nhận focus cho bàn phím. Kiểm tra 1440/390/320 px không tràn ngang toàn trang; các bảng rộng cuộn trong vùng riêng.
- Tháng sai hoặc bệnh nhân không tồn tại giữ bộ lọc, báo lỗi ngay trên trang và sửa/gửi lại được. Trang tổng hợp không còn badge chờ tích hợp.

Đã sửa lỗi HTML thực tế: template lịch sử cũ chứa cả bảng thuốc/y tá trong block title. Title mới chỉ chứa văn bản, các bảng nằm trong nội dung và không bị lặp.

## Hợp đồng và thay đổi backend cần Trung review

Không đổi SQL tính báo cáo, schema/seed/trigger hoặc nghiệp vụ ghi. Endpoint và tham số giữ nguyên: `month=YYYY-MM` cho Q1/Q2/Q4, `patient_id` cho Q3; GET có `format=json` trả dữ liệu như trước.

`clinical_routes.report` bổ sung xử lý lỗi HTTP để render lại bộ lọc HTML. Với `format=json`, tháng sai trả 400, mã không tồn tại trả 404, mã sai định dạng trả 422; body có dạng `{"error":"thông báo"}`. Đây là bổ sung JSON cho đường lỗi vốn trả HTML trước đây; success payload không thêm trường UI.

JSON giữ Decimal là chuỗi (ví dụ tiền khám/thuốc/doanh thu), số đếm là số, ngày ISO và ngày chưa có là null. Một số biểu thức lương SQL có kiểu số nguyên và vẫn giữ kiểu số nguyên trong JSON như backend cũ; không tự ép tất cả tiền thành float hoặc đổi contract success.

Q3 HTML nhận thêm danh sách mã/tên bệnh nhân bằng truy vấn chỉ đọc `patient_choices`. Endpoint `/patients/<id>/history` dùng cùng template và bộ chọn. Tham số tháng trên Q3 được bỏ qua. Không có JSON mutation API mới.

## Nguồn đáp án và cách đối chiếu

Đã đọc lại PR #10 qua GitHub: vẫn open, head **1bf9f8b18342eaf6d0097f3693df1bc02addfcfa**, trùng source Quyền đã tích hợp. Dùng `database/expected_results.md`, `queries.sql` và oracle độc lập của Quyền. Không dùng output backend làm expected.

Dữ liệu trên UI là kết quả đọc MySQL thật, không mock route/service hoặc hardcode số liệu vào template. Bộ seed dự án vốn là dữ liệu giả lập phục vụ bài tập, không có hồ sơ bệnh nhân thật. Ca biên được ghi thành bản ghi thử trong MySQL private rồi dọn bằng fixture; không dùng mock để thay dữ liệu nghiệm thu.

Test mới `tests/test_browser_vuong_reports.py` thực hiện trên cùng DB:

1. Tính expected độc lập từ INSERT seed; chạy nguyên `queries.sql` cho cùng tháng và bệnh nhân.
2. Gọi HTTP JSON và đọc các ô HTML trong Chromium: so từng dòng Q1, từng nhân viên và các tổng Q2, ba khoản Q4 trên 5 tháng.
3. So JSON 7 tập Q3 của cả 40 bệnh nhân với oracle Quyền; kiểm tra HTML BN001 có đúng số dòng mỗi bảng, tiêu đề sạch và layout ba viewport.
4. Ghi ca qua tháng/tái mắc/nhiều bệnh/nhiều thuốc/nhiều y tá, đổi giá danh mục; so HTML–JSON–SQL với đáp án tính tay. Kiểm tra Q3 đủ mọi tháng, hồ sơ chưa khám, mã không tồn tại, tháng/mã sai và sửa lại bộ lọc.
5. Chạy lại toàn bộ SQL/backend/browser, gồm bộ oracle ca kỳ hiện tại/ngày mai/ngày nhuận/chuyển tháng của Quyền.

## Bảng đối chiếu seed

Tất cả số tiền đơn vị đồng; mỗi dòng đã khớp HTML–JSON–SQL–expected. Tháng 10 seed chỉ có phát sinh đến 14/10, phiên chạy vào 19/10.

| Tháng | Tổng đợt theo bệnh Q1 | Khám | Thuốc | Doanh thu | Lương BS | Lương y tá | Kết quả |
|---|---:|---:|---:|---:|---:|---:|---|
| 2026-07 | 49 | 9.890.000 | 14.248.600 | 24.138.600 | 107.000.000 | 72.200.000 | Đạt |
| 2026-08 | 49 | 9.260.000 | 9.420.000 | 18.680.000 | 105.000.000 | 71.000.000 | Đạt |
| 2026-09 | 25 | 6.520.000 | 10.335.400 | 16.855.400 | 90.000.000 | 67.200.000 | Đạt |
| 2026-10 | 24 | 4.680.000 | 5.820.800 | 10.500.800 | 78.000.000 | 65.600.000 | Đạt |
| 2025-12 | 0 | 0 | 0 | 0 | 70.000.000 | 60.000.000 | Đạt |

[Bảng đối chiếu máy đọc được, kèm 40 bệnh nhân](evidence/vuong_week2_prepare_20261019_220540/browser-tests/vuong-reports/seed-parity.json).

## Bảng đối chiếu ca dữ liệu biên đã lưu

W2BN1 có đợt W2D1 khám 30/01, 31/01, 01/02/2001, khỏi 02/02; tái mắc W2D2 ngày 03/02; cùng lượt có thêm bệnh thứ hai W2D3. Đơn ngày 01/02 có 2 × 1.000 + 3 × 2.000 = 8.000 đồng. Sau kê đơn đổi giá danh mục W2T1 thành 9.999; lịch sử vẫn 1.000/viên. Y tá W2YT1 có 4 lượt hỗ trợ, W2YT2 hỗ trợ thêm lượt 03/02.

| Tháng | Tổng đợt Q1 | Khám | Thuốc | Doanh thu | W2BS | W2YT1 | W2YT2 | Kết quả |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 2001-01 | 1 | 250 | 0 | 250 | 7.000.000 | 5.400.000 | 5.000.000 | Đạt |
| 2001-02 | 3 | 550 | 8.000 | 8.550 | 8.000.000 | 5.400.000 | 5.200.000 | Đạt |
| 2001-03 | 0 | 0 | 0 | 0 | 7.000.000 | 5.000.000 | 5.000.000 | Đạt |

Q3 W2BN1: 4 lượt / 3 đợt / 5 lần khám / 2 dòng thuốc / 5 dòng hỗ trợ, 2 đợt đang điều trị. Tổng khám 800, thuốc 8.000 đồng. HTML, JSON và SQL đều giữ toàn bộ dữ liệu khi truyền tháng 01/2001; JSON với `month=INVALID` cũng không cắt lịch sử. W2BN2 có hồ sơ nhưng không có lịch sử: các bảng rỗng, tổng 0. MISSING trả 404, không được diễn giải thành hồ sơ rỗng hợp lệ.

[Bảng đối chiếu ca biên](evidence/vuong_week2_prepare_20261019_220540/browser-tests/vuong-reports/edge-parity.json).

## Kết quả chạy và bằng chứng

- Phiên thành công `20261019_220540`: **163 passed / 0 skipped**, 34,64 giây. Windows, Python 3.12.14, MySQL 8.0.46, Chromium 156.0.8078.4. Chưa thay nghiệm thu môi trường mục tiêu Python 3.11/MySQL 8.4.
- Instance MySQL private mới, DB `clinic_vuong_week2_prepare_test`; cổng và URL chính xác trong results.json. Không truy cập DB cấu hình đang dùng.
- Audit cuối 10 tập SQL rỗng, 11 bảng/9 trigger/1.144 dòng; 9 nhóm findings rỗng. Seed khớp hash trước/sau test và khảo sát browser, `.env` không đổi.
- [Pytest](evidence/vuong_week2_prepare_20261019_220540/pytest.txt), [audit và khảo sát 54 trang](evidence/vuong_week2_prepare_20261019_220540/results.json).
- Ảnh báo cáo: [Q1](evidence/vuong_week2_prepare_20261019_220540/browser-tests/vuong-reports/diseases-1440.png), [Q2](evidence/vuong_week2_prepare_20261019_220540/browser-tests/vuong-reports/salaries-320.png), [Q3](evidence/vuong_week2_prepare_20261019_220540/browser-tests/vuong-reports/history-390.png), [Q4](evidence/vuong_week2_prepare_20261019_220540/browser-tests/vuong-reports/revenue-390.png), [tháng sai](evidence/vuong_week2_prepare_20261019_220540/browser-tests/vuong-reports/invalid-month.png), [hồ sơ chưa khám](evidence/vuong_week2_prepare_20261019_220540/browser-tests/vuong-reports/empty-history.png).

Đã rà trực tiếp ảnh Q2 320 px, Q3 390 px, Q4 390 px và tháng sai; không nhận đã rà bằng mắt mọi ảnh. Bảng rộng dùng vùng cuộn riêng, không ép toàn bộ cột vào màn hình nhỏ.

Phiên `220415` có 162 test đạt/1 test cũ lỗi selector: tổng 122.000 đồng xuất hiện cả ô tổng hợp và dòng tổng trong bảng. Đã sửa test để chọn đúng `[data-revenue="total"]`, không bỏ bớt hiển thị hoặc làm yếu kiểm tra số tiền. Phiên đó không được ghi là đạt toàn suite.

App của phiên thành công ở `http://127.0.0.1:62031/reports` trong thời gian tiến trình còn chạy. Chưa đăng GitHub, chưa approve/merge hoặc đánh dấu hoàn tất tuần 2 thay nhóm. Bước tiếp theo là checklist nghiệm thu tổng thể và rà lỗi còn lại theo ACCEPTANCE.md.
