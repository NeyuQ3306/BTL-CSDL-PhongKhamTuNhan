# Bàn giao tuần 2 của Vương

**Bản source bàn giao:** commit `fa699a6874452d273cc1e88d689dea1146ffd2f5`, đã chạy lại **168 passed / 0 skipped** sau commit (47,68 giây), [JUnit](evidence/vuong_week2_prepare_20261019_222841/junit.xml), [log](evidence/vuong_week2_prepare_20261019_222841/pytest.txt), [audit](evidence/vuong_week2_prepare_20261019_222841/results.json). Commit ghi nhận sau đó chỉ bổ sung bằng chứng/tài liệu; không sửa code đã chạy.

## Kết quả và phụ thuộc

UI nghiệp vụ và bốn báo cáo dùng MySQL thật đã hoàn thiện trên `vuong/week-2`. Source bổ sung read-only context/đường quay lại và thông báo lỗi báo cáo; không đổi schema, seed, trigger, công thức hoặc transaction ghi của Trung/Quyền.

Nền tích hợp local `f8d80c8ea64ce0843430b5e16eac1538b7eb2d85` kết hợp:

- Trung **#5**, head `10c808238ef2f8f4f0a1aabcfc59da19079b38f8`: backend luồng khám, báo cáo và UI thử.
- Quyền **#10**, head `1bf9f8b18342eaf6d0097f3693df1bc02addfcfa`: queries, expected_results và oracle độc lập.
- Main nền `20cd47a`. #5/#10 chưa merge khi đóng gói. PR Vương về main sẽ chứa thay đổi phụ thuộc; review phần Vương bằng delta từ `f8d80c8` đến nhánh Vương. Sau khi hai PR squash merge, Quyền/nhóm cần điều phối cập nhật nền để không đưa lại lịch sử phụ thuộc. Không tự merge các PR.

## Tài liệu và checklist bàn giao

| Hạng mục | Trạng thái / bằng chứng |
|---|---|
| Form lượt/đợt/lần khám/y tá/đơn/đóng lượt/khỏi | Đã triển khai và chạy Chromium với MySQL; [chi tiết UI](VUONG_WEEK2_UI_HANDOFF.md) |
| Q1–Q4, bộ lọc, tổng hợp, trạng thái rỗng/lỗi | Đã triển khai; [bảng đối chiếu](VUONG_WEEK2_REPORTS_HANDOFF.md) |
| T01–T15 và hồi quy CRUD tuần 1 | **168 local test đạt / 0 skipped**, [biên bản](VUONG_WEEK2_ACCEPTANCE.md) |
| Bằng chứng môi trường/source/audit/ảnh/log | [Chỉ mục](evidence/VUONG_WEEK2_EVIDENCE.md); có manifest, JUnit và CSV |
| Hướng dẫn dùng/chạy review | [Hướng dẫn ngắn](VUONG_WEEK2_USER_GUIDE.md) |
| Route/field/context/CSRF/JSON | [Hợp đồng đã cập nhật](WEEK2_INTEGRATION.md) |
| Rà secrets/cache/file tạm và kiểm tra đóng gói | Kết quả scan/check được lưu tại `docs/evidence/vuong_week2_delivery_checks.json` khi commit |
| Review độc lập/merge/đóng issue | Còn chờ nhóm; PR dùng **Refs #2**, không đóng issue chung |

168 test local chạy Windows/Python 3.12.14/MySQL 8.0.46/Chromium 156.0.8078.4. Seed cuối đủ 11 bảng/9 trigger/1.144 dòng, 10 tập SQL audit rỗng, hash seed và `.env` giữ nguyên. T01–T15 có input/expected/actual riêng; T06 là SQL, T07 là HTTP đồng thời, không nhận mọi ca là thao tác UI bình thường. Bộ hiện tại đã chạy lại 5 tháng báo cáo và JSON 40 bệnh nhân với oracle Quyền.

## Điểm reviewer cần xem

- Trung: `clinical_routes.py` thêm JOIN/context chỉ đọc, `routes.py` truyền danh sách mã/tên cho bộ chọn lịch sử. Lỗi báo cáo `format=json` trả `{error: message}` với HTTP400/404/422; success payload giữ nguyên. Thiếu patient_id vẫn mở bộ chọn HTML.
- Quyền: đối chiếu hiển thị tiền/ngày/số đợt và ghi nhận giới hạn SQL quản trị như database/README; Vương không thay công thức hoặc dữ liệu nguồn.
- UI: template thực thi ở `clinic_app/templates/week1/` và `week2/`, CSS/JS ở `clinic_app/static/week2.*`. File upstream tại `templates/` gốc không phải nơi chạy UI này.
- CI tích hợp thêm `QUYEN_CHECK_WEEK2=1` để oracle kiểm tra backend của nhánh hiện tại. Workflow riêng Quyền vẫn có bước kiểm chứng candidate Trung pin, không nhầm bước đó với head Vương.

## Giới hạn còn lại

T16 (clone sạch trên máy thứ hai), test local Python 3.11/MySQL 8.4, Firefox/WebKit/điện thoại thật/screen reader/JavaScript tắt và soak/load kéo dài chưa được xác nhận bởi phiên local. CI sau push ghi riêng theo commit thực chạy; không dùng CI cũ hoặc local 3.12/8.0 thay bằng chứng đó. Một cặp request đồng thời không chứng minh mọi mức tải.

Tài liệu bước 1–4 giữ mốc lịch sử ở đầu trang; lấy trang này và chỉ mục bằng chứng làm điểm vào hiện tại. Các câu “chưa commit/push/CI” bên trong biên bản cũ mô tả đúng thời điểm chạy, không phải trạng thái phát hành sau khi PR được tạo.
