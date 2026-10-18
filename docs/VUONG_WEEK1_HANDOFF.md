# Bàn giao tuần 1 — Vương

Ngày cập nhật: 18/10/2026. Nhánh `vuong/week-1`, [PR #7](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/pull/7) đang mở, đã hết Draft khi đối chiếu GitHub. **Phần UI và kiểm thử đã sẵn sàng review; chưa xác nhận hoàn tất toàn bộ tuần 1 hoặc tự merge.**

## Sản phẩm

| Đầu việc | Kết quả |
|---|---|
| Layout/menu | Tiếng Việt; bệnh nhân, bác sĩ, y tá, lượt/đợt khám và bốn nhóm báo cáo; không có menu giường/phẫu thuật |
| Hồ sơ ba nhóm | Danh sách/thêm/sửa/chi tiết, hướng dẫn nhập, lỗi đúng trường, thông báo, trạng thái rỗng, phân trang |
| Tích hợp MySQL | Thêm bệnh nhân qua trình duyệt, SELECT độc lập, tải lại và tìm trong danh sách đạt; CRUD cả ba nhóm được kiểm tra |
| Khung báo cáo | Ba bộ lọc tháng và vùng kết quả chưa tích hợp; lịch sử dùng service/query có sẵn, không thêm SQL tuần 2 |
| Responsive | Kiểm tra ở 320/390/768/1440px; bảng cuộn trong vùng riêng, menu/form không tràn trang |
| Bằng chứng | Checklist expected/actual, ảnh PNG, JSON/log, công cụ chạy lại, hướng dẫn sử dụng |

Backend nền Trung tại `5a25395699905cc5f79af4904bd73d95073963a0` đã được squash merge qua PR #4 thành `b51b0afb3b0d03f6fa30a255b1efc614b89a9bbd`. Nhánh Vương đã đồng bộ main bằng merge commit `8c5be9469976333195eb67c9d2689638d02c045f`; tree trùng hoàn toàn commit UI `33d45a06eb7e237796d3d240fd6d419fabd00bd1`. Local đã fast-forward tới `8c5be94` ngày 18/10. Không cần đồng bộ lại phần backend đã merge hoặc tính sáu commit Trung thành đóng góp UI.

Phần Vương giữ nguyên schema, SQL, `app.py`, field và CSRF. Thay đổi nhỏ ở routes gồm GET khung báo cáo, context mã chuẩn cho form sửa và xử lý lỗi FK 1217/1451. Seed giả Vương bàn giao qua adapter Trung được bộ SQL Quyền kế thừa 1.144 dòng.

## Tài liệu và kiểm thử

- [Hướng dẫn sử dụng](VUONG_WEEK1_USER_GUIDE.md).
- [Checklist, 14 ca trình duyệt và ảnh/log](VUONG_WEEK1_CHECKLIST.md).
- [Bằng chứng sau đồng bộ backend](evidence/vuong_week1_final/README.md).
- [Hợp đồng tích hợp](INTEGRATION.md).
- [Nội dung PR đã chuẩn bị](VUONG_WEEK1_PR.md).

**Local ngày 17/10:** 33/33 ca checklist MySQL đạt; thêm/sửa/xóa qua URL khác hoa/thường của cả ba nhóm đạt; pytest **25 passed, 21 skipped**. 21 ca bỏ qua gồm 18 test MySQL gốc cần database `_test` và 3 test Playwright chưa bật trong lần chạy local đó. Không tính skipped là đạt và không thay số liệu local bằng kết quả CI.

Ảnh trình duyệt trước khi đồng bộ backend vẫn là bằng chứng của phiên bản tương ứng đã ghi trong checklist. Kiểm tra bổ sung sau đồng bộ được lưu riêng. Dữ liệu nền giữ 11 bảng/1.144 dòng, hash không đổi sau dọn các hồ sơ tạm. Máy Vương thực tế dùng Windows/Python 3.14.6/MySQL 8.0.46.

**CI đã đối chiếu trực tiếp log ngày 18/10:**

| Phạm vi | Snapshot và bằng chứng | Kết quả |
|---|---|---|
| Backend/UI sau đồng bộ main | `8c5be9469976333195eb67c9d2689638d02c045f`; [run 39092326435](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/actions/runs/39092326435), job `117571499620` | **46 passed**, không skipped; compile/Jinja đạt; seed adapter, audit 11 bảng/1.144 dòng, findings rỗng |
| SQL/trigger Quyền + backend/UI Vương cùng DB | SQL `08e4427f6ac8e9ba55eaba859ddab4067330ec04` + UI `33d45a06eb7e237796d3d240fd6d419fabd00bd1`; [run 39092264670](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/actions/runs/39092264670), job `117571317667` | **72 passed** = 26 SQL + 46 backend/UI, không skipped; audit 11 bảng/1.144 dòng, findings rỗng |

Cả hai job dùng Ubuntu/Python 3.11.17/MySQL 8.4.11/Chromium. Run tích hợp thuộc PR #8 tại workflow commit `89539428d4b522a44938bc21115114c595cc207b`, checkout riêng hai snapshot trên; không phải test 72 ca trên head PR #7 hoặc xác nhận #6/#7 đã merge. Đợt cập nhật tài liệu này chỉ đọc lại log đã chạy, không chạy lại MySQL/browser local. [Chi tiết và trích log](evidence/vuong_week1_final/README.md#doi-chieu-ci-18102026).

## Phụ thuộc review

- **Trung:** review các route GET báo cáo, context `record_id` lấy mã chuẩn DB, CSRF/field, xử lý FK và cập nhật nhãn nút trong test browser. Hợp đồng đã chạy trên máy Vương; chưa đăng lời xác nhận lên PR của Trung.
- **Quyền:** review adapter/schema/seed và tính nhất quán thiết kế; duyệt UI/phạm vi; điều phối merge theo RULES.md.
- Backend Trung [PR #4](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/pull/4) đã merge; main được đối chiếu tại `b51b0af`. PR #7 đã đồng bộ main, đang mở và hết Draft. Review COMMENT của Quyền trên #7 không thay cho approval cuối; cần review hợp lệ và xử lý nhận xét trước merge theo RULES.md.
- Bộ SQL [PR #6](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/pull/6) và hướng dẫn trong [PR #8](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/pull/8) vẫn cần hoàn tất review. Hướng dẫn thử tích hợp hiện được đề xuất tại [SETUP của PR #8](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/blob/3b59effd4bb86fca1f8d239af8349e73ac09e9e6/docs/SETUP.md): DB mới, schema → seed → audit → constraints → audit → queries. Không chạy chồng importer adapter cũ. Hướng dẫn này chưa được xác nhận chạy trên cả ba máy.

## Phần chưa hoàn thành

- Chưa rà trực quan hai PDF YC1 trong `docs/design/`.
- Chưa xác nhận chạy cùng bộ tích hợp theo hướng dẫn mới trên máy cả ba thành viên; chưa thử điện thoại thật. CI môi trường mục tiêu đã đạt như bảng trên, không thay cho nghiệm thu máy thật.
- 21 test tùy chọn chưa chạy trong phiên local 17/10; đã có job CI chạy đủ 46 ca trên snapshot nêu trên. Commit cập nhật tài liệu tiếp theo phải xem Checks theo SHA mới, không gán run cũ cho commit mới.
- Chưa đăng xác nhận hợp đồng lên PR #4; chưa hoàn tất review/merge PR #7 và nghiệm thu chung SQL/UI của nhóm. Ba UI thống kê còn là khung; tích hợp báo cáo/luồng khám/đơn đa bước thuộc tuần 2.

## Rà nội dung trước commit

Không đưa `.env`, `.venv`, file cấu hình cá nhân, database dump hoặc credentials thật vào commit. Ảnh/log của Vương chứa hồ sơ tự sinh hoặc seed được nhóm xác định là giả lập; hồ sơ thử đã được dọn. Kết quả quét cụ thể được lưu trong thư mục bằng chứng cuối. Không đổi giấy phép/nguồn upstream.
