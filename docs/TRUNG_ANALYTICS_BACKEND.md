# Trung — backend R01–R07, bàn giao bổ sung tuần 3

Ngày 04/11/2026. Tham chiếu issue #3, kế hoạch #20 và SQL Quyền #21
(head `e65d05893e073f05c8d2efa256abc82125f5b3bf`, nền main `98bd267`).
Phạm vi: route/service JSON và kiểm thử. Chưa bổ sung giao diện/biểu đồ,
chưa nghiệm thu toàn nhóm, chưa thay thế bốn báo cáo Q1–Q4.

## Tích hợp

- `clinic_app/analytics.py`: đọc nguyên SELECT có marker từ
  `database/analytics_queries.sql` của #21, thay biến allowlist bằng `%s` và bind giá trị.
  Không sao chép công thức báo cáo sang Python/JavaScript.
- `clinic_app/analytics_routes.py`: blueprint API, lỗi đầu vào JSON 400,
  mã báo cáo không tồn tại 404, lỗi kết nối MySQL 503, lỗi DB khác 500.
  Không trả host/mật khẩu/SQL/chi tiết exception cho người dùng.
- `clinic_app/__init__.py`: đăng ký blueprint mới. Không đổi route/UI cũ.
- Một request lấy một hoặc cả bảy báo cáo trong cùng transaction
  `REPEATABLE READ`, `WITH CONSISTENT SNAPSHOT, READ ONLY`. Luôn rollback
  để kết thúc snapshot cả khi thành công/lỗi, không commit hay retry thao tác ghi.
- SQL phụ thuộc #21. Không merge PR backend trước khi Quyền review và thống nhất
  tích hợp SQL. Cài từ clone mới phải có `database/analytics_queries.sql`.

## API để Vương nối bảng và biểu đồ

| GET | Bộ lọc | Mặc định |
| --- | --- | --- |
| `/api/analytics` | `start`, `end`, `as_of`, `threshold`, tùy chọn `age_group` | Toàn bộ R01–R07 trong cùng snapshot |
| `/api/analytics/R01` | `start`, `end`, tùy chọn `age_group` | Bệnh theo nhóm tuổi |
| `/api/analytics/R02` | `start`, `end` | Tiếp nhận và khám theo ngày |
| `/api/analytics/R03` | `start`, `end` | Khối lượng khám theo bác sĩ |
| `/api/analytics/R04` | `start`, `end` | Thuốc được kê |
| `/api/analytics/R05` | `start`, `end` | Đợt tái mắc |
| `/api/analytics/R06` | `as_of`, `threshold` | Lâu chưa ghi nhận khám |
| `/api/analytics/R07` | `start`, `end` | Chi phí đợt đã khỏi |

Mặc định `start=2026-07-01`, `end=2026-10-15`, `as_of=2026-10-14`, `threshold=14`.
Kỳ `[start,end)` gồm start, không gồm end. Backend không cộng thêm ngày vào end.
Nếu form Vương cho chọn ngày cuối bao gồm, adapter form phải chuyển sang ngày kế
chính xác một lần trước khi gọi API. R06 dùng cuối ngày as_of và không nhận bộ lọc kỳ.
Ngày phải đúng lịch và dạng ASCII YYYY-MM-DD, start < end; ngưỡng nguyên 0–36500.
Không nhận tham số lặp, tham số lạ hay bộ lọc của báo cáo khác. `age_group` thuộc
-1/0/1/2/3, chỉ lọc R01 trên cùng tập rows từ SQL, không tính lại tuổi.
Khi lấy tất cả, age_group chỉ ảnh hưởng R01. Bỏ age_group để xem đầy đủ nhóm.

Ví dụ sau khi chạy app theo SETUP:

```text
http://127.0.0.1:5000/api/analytics
http://127.0.0.1:5000/api/analytics/R01?start=2026-07-01&end=2026-10-15&age_group=2
http://127.0.0.1:5000/api/analytics/R06?as_of=2026-10-14&threshold=14
```

Một báo cáo trả:

```json
{
  "report_id": "R01",
  "title": "Bệnh theo nhóm tuổi",
  "filters": {"start": "2026-07-01", "end": "2026-10-15"},
  "interval": "end_exclusive",
  "rows": [],
  "row_count": 0,
  "chart_groups": [],
  "money_unit": "VND",
  "data_notice": "Dữ liệu giả lập, mô tả hồ sơ đã lưu."
}
```

API toàn bộ trả `{reports: {R01: {...}, ..., R07: {...}}, filters: {...}}`.
Ví dụ JSON trên minh họa hình dạng, không phải kết quả seed. Kết quả thực chạy
được ghi riêng trong bằng chứng kiểm thử; không gán một kết quả mẫu cho mọi bộ lọc.

## Quy ước dữ liệu, bảng và biểu đồ

- `rows` giữ tên/cột/thứ tự SQL #21. Ngày ISO/null; COUNT và SUM số lượng nguyên
  trả JSON integer. Năm số tiền R07 trả chuỗi thập phân hai chữ số, ví dụ
  `"1234.50"`; giá trị không có mẫu là null. Không chuyển tiền qua float ở server.
- `row_count` là số dòng, không phải số bệnh nhân duy nhất hay tổng hoạt động.
- Bảng và biểu đồ lấy cùng một response. Chỉ chuyển chuỗi tiền thành Number
  để vẽ, giữ nguyên chuỗi gốc để hiển thị/đối chiếu. Không vẽ null như tiền 0.
- `chart_groups` chỉ dùng R05 (số dòng/đợt theo bệnh) và R06 (số dòng/đợt theo
  nhóm ngày sau lọc ngưỡng, đủ bốn nhóm kể cả số 0). Các báo cáo khác dùng rows.
- R01 không cộng DISTINCT bệnh nhân giữa nhóm; nhóm -1 là ngày sinh lỗi.
  R02 chỉ có ngày ghi nhận, không tự điền ngày thiếu là đã biết 0 hoạt động.
  R03 giữ bác sĩ không hoạt động với 0. R04 giữ đơn vị từng thuốc.
  R05 không đồng nhất số đợt tái mắc với số người; R06 không gọi trễ hẹn/bỏ điều trị.
  R07 chọn đợt khỏi trong kỳ nhưng tính toàn bộ chi phí của đợt, giữ số mẫu/đợt loại,
  không so trực tiếp với doanh thu Q4 theo ngày phát sinh.
- API không thêm authentication mới, tiếp tục phạm vi demo giả lập hiện tại.
  Không dùng dữ liệu bệnh nhân thật để chụp ảnh hay đẩy lên GitHub.

## Kiểm thử

Trên DB thử riêng tên kết thúc `_test`, dựng schema/seed/constraints đúng một lần
bằng công cụ hiện có. Không chạy import vào DB demo đang có dữ liệu.

```powershell
$env:RUN_MYSQL_TESTS = '1'
$env:QUYEN_CHECK_WEEK2 = '1'
python -m pytest tests/test_trung_analytics_backend.py tests/test_quyen_analytics.py -v
python -m pytest tests week3_checks -v
python -m tools.audit_seed
```

Cấu hình DB theo SETUP, không đưa .env/mật khẩu vào log. Bộ mới kiểm API một/tất cả,
đối chiếu mọi cột của bảy kỳ với oracle seed độc lập, các ca biên SQL của Quyền,
nhóm tuổi/rỗng, số tiền lớn/NULL, tham số sai, bind, read snapshot/rollback và lỗi 503.
Mỗi kỳ đối chiếu còn lưu expected/actual JSON tại `test-artifacts/trung-analytics/`,
được workflow hiện có upload cùng artifact. Kết quả chạy thật, phiên bản và giới hạn được ghi tại
`docs/evidence/trung_analytics_backend_20261104/README.md`.

## Việc còn phụ thuộc

Vương nối các form/bảng/biểu đồ từ API trên, giữ tài nguyên biểu đồ offline,
kiểm responsive/rỗng/NULL và cập nhật DOCX/ảnh. Quyền review SQL/backend rồi
nghiệm thu end-to-end trên bản tích hợp. Trung cập nhật slide bằng ảnh kết quả
của giao diện sau tích hợp; các slide đang có SQL chưa phải chứng nhận UI mới.
Không đánh dấu đủ 7 chức năng hay đóng issue #3 ở bước bàn giao backend.

## Trung xác nhận với review UI của Vương — 04/11/2026

Đối chiếu review [5763153761](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/pull/22#pullrequestreview-5763153761)
tại head e4353a9. Trung xác nhận giữ nguyên cấu trúc response và bộ lọc nêu trong review.

- Adapter form thuộc phần tích hợp UI của Vương chịu trách nhiệm duy nhất chuyển
  ngày cuối **bao gồm** thành `end` **không bao gồm**. Adapter có thể nằm ở lớp
  giao diện phía server hoặc client; API analytics không tự chuyển và không cộng ngày.
  Luôn tính từ giá trị ngày cuối gốc của form mỗi lần gửi, tránh cộng lại khi retry/reload.
- Ví dụ form từ 01/07/2026 đến hết 14/10/2026 gửi
  `start=2026-07-01&end=2026-10-15`.
  Một ngày duy nhất 29/02/2004 gửi `start=2004-02-29&end=2004-03-01`.
  Phép cộng là ngày lịch, không chuyển múi giờ làm lệch ngày.
- Ngày cuối bao gồm tối đa là **9999-12-30** vì API chỉ nhận ISO bốn chữ số năm,
  nên `9999-12-31` không có ngày kế tiếp biểu diễn được trong hợp đồng này.
  Adapter báo lỗi dễ hiểu trước khi gọi API nếu chọn ngày cuối 9999-12-31,
  không tràn năm, không kẹp ngày âm thầm. `as_of` của R06 không cộng ngày nên
  vẫn nhận 9999-12-31.
- Nếu UI dùng ngay nhãn “Ngày kết thúc không bao gồm”, gửi trực tiếp ngày đó,
  không áp dụng bước chuyển ngày cuối bao gồm. Không thêm cờ ngầm vào API.
- Endpoint tổng trả `{reports, filters}`; endpoint lẻ trả một payload có
  `report_id/title/filters/interval/rows/row_count/chart_groups/money_unit/data_notice`.
  `row_count` là số dòng. Bảng/biểu đồ lấy cùng response; tiền chuỗi/null,
  ngày ISO/null, nhóm R05/R06 và các giới hạn diễn giải giữ nguyên hợp đồng.
- Câu “backend đổi” trong ANALYTICS_HANDOFF của #21 được hiểu là bước adapter
  chuẩn hóa đầu vào **trước** API; nó không yêu cầu API #22 cộng lần nữa.
  Ghi rõ ranh giới tại đây, giữ nguyên dependency #21 để Quyền điều phối
  thống nhất câu chữ tài liệu chung khi tích hợp, không sửa công thức SQL.

Đã nhận nit dòng trống tại EOF clinic_app/__init__.py và dọn trong bản tiếp theo;
không đổi logic backend. Xác nhận này chỉ chốt hợp đồng triển khai từ phía Trung,
không tự ghi UI/biểu đồ/nghiệm thu đã xong, không resolve thay reviewer.
#21 và #22 chưa merge; chờ Quyền điều phối #21, sau đó Trung đồng bộ main,
kiểm tra diff/CI #22 trước tích hợp.
