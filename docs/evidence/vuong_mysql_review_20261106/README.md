# Kiểm MySQL và gói review phần Vương — 06/11/2026

## Kết quả

Source sản phẩm `596b38b8508fa79e5bc27d1e1e8a1c86f5cb7d5b`, nhánh `feat/vuong-analytics-ui`; `origin/main` sau fetch vẫn `a0d6c300be631cea404672ade548a67c20fea1c1`. Các file test/runner/bằng chứng mới của phiên này chưa commit. Không push, tạo PR, merge, gửi issue hoặc sửa tài liệu chung.

| Lượt thực chạy | Passed | Skipped | Failed/errors | Nội dung |
| --- | ---: | ---: | ---: | --- |
| Hồi quy `tests` + `week3_checks` | 442 | 0 | 0 | SQL/API/oracle, Q1–Q4, luồng cũ và desktop UI stub; 176,03 giây |
| MySQL → API → desktop UI | 30 | 0 | 0 | 28 ca oracle/filter, 1 ca hai trang cũ, 1 ca R07 NULL; 13,53 giây |

Hai lượt trên không chồng ca; SQL oracle chạy thêm bằng công cụ riêng, không cộng thành pytest passed. Hai module có kiểm điện thoại bị ignore, hai ca trộn desktop/điện thoại bị deselect; danh sách đầy đủ trong `results.json`, không tính chúng là skipped/PASS. Không kiểm điện thoại theo phạm vi đã thống nhất.

## Môi trường và cách chạy

Windows, Python 3.14.6, MySQL 8.0.46, Playwright Chromium từ cache cục bộ. Runtime/port/datadir/run_at thực tế nằm trong `results.json`. DB mới `clinic_vuong_analytics_test`, cổng loopback 63289 trong lượt này, datadir mới dưới `.venv/vuong_analytics_20261106_125907_567156/`; không dùng service/DB làm việc đã cấu hình trong `.env`. Mật khẩu ngẫu nhiên chỉ ở bộ nhớ, không có trong bằng chứng.

```powershell
& .venv\Scripts\python.exe docs/evidence/vuong_mysql_review_20261106/run_private.py
```

Runner dựng schema → seed → constraints đúng một lần vào DB trống; sau khi xong dừng instance bằng đúng executable/datadir/port. Cleanup thực tế: SHUTDOWN thành công, không còn process, cổng đã đóng, không dùng fallback kill. `.env` không đổi. Log MySQL gốc giữ cục bộ dưới datadir private (không commit DB dump/datadir).

## Phạm vi đối chiếu và bằng chứng

- `sql-expected-actual.json`: toàn bộ R01–R07 kỳ mặc định so SQL với oracle Python độc lập, tất cả 1.144 dòng so canonical trước/sau. Trường `base_commit` trong công cụ cũ là nền SQL lịch sử `98bd267`, **không phải source thực chạy**; source thực ở `results.json` và manifest.
- `api-oracle/`: expected/actual của bảy bộ lọc API một/tất cả báo cáo; generated bởi kiểm backend với MySQL thật, không stub. SHA được truyền đúng source của lượt chạy.
- `browser/*-expected.json` và `*-actual.json`: từng báo cáo kỳ mặc định/tháng 8/kỳ rỗng; R01 đủ nhóm -1/0/1/2/3; R06 ngưỡng 0/14/30 và ngày đối chiếu mặc định/tháng 8/kỳ rỗng. Kiểm mọi ô/thứ tự và dataset SVG; R05/R06 kiểm chart_groups độc lập từ oracle rows, R06 giữ đủ bốn nhóm 0. Không monkeypatch analytics.build.
- R07 NULL: tạo fixture có đợt đã khỏi nhưng đơn thuốc rỗng chỉ trong DB private nói trên, có commit để kết nối HTTP nhìn thấy. Expected 0 mẫu/1 đợt loại, năm số tiền NULL; bảng ghi Không có mẫu, không có money segment. Xóa đúng fixture theo FK trong finally; snapshot seed trước/sau vẫn bằng nhau. Đây là dữ liệu ca biên, không thay seed nguồn.
- `browser/*.png`: ảnh mặc định R01–R07, R07 không có mẫu và hai trang cũ. Đã xem trực tiếp ảnh R01/R06/R07 không có mẫu; không thấy lỗi bố cục trong các ảnh này. Các bảng rộng có cuộn ngang theo thiết kế.
- `seed-before.json` / `seed-after.json`: hash canonical từng bảng bằng nhau; audit cuối đủ 1.144 dòng, tất cả 9 kiểm liên bảng rỗng. Không thay schema/seed/SQL sản phẩm.
- `regression.xml/.txt`, `mysql-ui.xml/.txt`, `sql-oracle.txt`: kết quả và câu lệnh do `run_private.py` tạo.
- `source-sha256.json` chụp lúc bắt đầu; subagent bổ sung hai ca cuối trước khi chạy mysql-ui. `source-sha256-final.json` nhận diện chính xác file test đã chạy sau khi subagent dừng sửa. Không đồng nhất source HEAD sản phẩm với phần kiểm thử mới chưa commit.

## W3-DB-01

60 GET chỉ đọc (15 lượt × health, thống kê bệnh tháng 10, lịch sử BN001 và analytics tổng) đều HTTP 200; không thấy MySQL 2003 trong log của lượt kiểm này. Hai trang từng liên quan lỗi cũng HTTP 200 qua trình duyệt desktop. Xem `w3-db-01-read-checks.json`, `app-read-checks.txt`, ảnh và status JSON legacy trong `browser/`. Không retry thao tác ghi.

Kết luận: **không tái hiện local, vẫn theo dõi, chưa xác định nguyên nhân/đã sửa**. Môi trường này MySQL 8.0.46/Python 3.14.6, khác MySQL 8.4.11/Python 3.11.9 ở phiên lỗi cũ trên laptop Quyền; cần Quyền chạy lại bản tích hợp. Không tự nghiệm thu laptop Quyền hoặc toàn nhóm.

## Review và việc tiếp theo

Subagent 6.1 Terra đã rà hợp đồng và bổ sung kiểm browser MySQL; orchestrator rà mã test, chạy thực, kiểm ảnh và bằng chứng. Không tìm thấy lỗi sản phẩm cần sửa trong phạm vi đã chạy. Nghi vấn chart_groups chưa đối chiếu rows tại client là gợi ý hardening, không phải mismatch thực tế; test mới đối chiếu nhóm backend độc lập và đã đạt, không tự đổi hợp đồng/backend.

`REVIEW_PACKET.md` có tiêu đề/nội dung PR dự kiến, cách chạy, giới hạn và điểm Trung/Quyền cần review; chỉ là hồ sơ cục bộ. Chưa có review độc lập của thành viên nhóm, CI cho phần mới, push/PR/merge hay nghiệm thu nhóm. Bước tiếp: rà và commit phần mới đúng phạm vi, sau khi được người dùng cho phép mới push/tạo PR; Trung review API, Quyền review tích hợp và chạy laptop Quyền. Sau đó cập nhật DOCX/PPTX/demo/bộ nộp.

## Rà trước publish

Ca R07 NULL có ghi fixture chỉ chạy khi DB_NAME đúng `clinic_vuong_analytics_test`. Khi CI dùng DB `_test` khác, ca này được skip rõ lý do; 29 ca read-only còn lại vẫn có thể chạy. Không mở rộng quyền ghi fixture sang DB khác, không sửa workflow dùng chung. Lượt private trước publish được lưu riêng trong `prepublish/`; kết quả gốc 442/30 phía trên được giữ nguyên.

Lượt `prepublish`: SQL oracle đạt, 30 browser passed/0 skipped/0 failed; seed và `.env` không đổi, cleanup sạch. Source test sau chỉnh guard được ghi tại `prepublish/source-sha256.json`. Cách tái lập phần recheck: `python docs/evidence/vuong_mysql_review_20261106/check_publish.py`; thêm `--ci-db` để kiểm guard với DB private tên khác. Các lượt recheck không cộng chồng vào 442/30 của lượt gốc. Người dùng đã cho phép publish PR, yêu cầu Trung/Quyền review; không merge hoặc đóng #3.

Lượt `prepublish-ci`: DB private khác tên đạt 29 passed/1 skipped/0 failed; đúng ca fixture R07 được skip, seed/`.env` không đổi và cleanup sạch. Guard đã được kiểm cả đường chạy và đường skip.
