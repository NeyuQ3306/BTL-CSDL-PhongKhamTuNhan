# Bằng chứng review R01–R07 của Vương — 06/11/2026

Source sản phẩm được kiểm: `596b38b8508fa79e5bc27d1e1e8a1c86f5cb7d5b`; test sau sửa guard được đóng gói tại `80157b5`. Nhánh `feat/vuong-analytics-ui`, nền main `a0d6c300`. [PR #23](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/pull/23) đang chờ Trung/Quyền review; chưa merge/đóng #3 hoặc nghiệm thu nhóm.

## Kết quả thực chạy

| Lượt local | Passed | Skipped | Failed/errors | Biên nhận |
| --- | ---: | ---: | ---: | --- |
| Hồi quy SQL/API/Q1–Q4/desktop | 442 | 0 | 0 | [JUnit](regression.xml), [log tóm tắt](regression.txt), [môi trường/audit](results.json) |
| Browser MySQL sau sửa guard | 30 | 0 | 0 | [JUnit](prepublish/mysql-ui.xml), [log tóm tắt](prepublish/mysql-ui.txt), [audit](prepublish/results.json) |
| DB private tên khác: kiểm đường skip | 29 | 1 | 0 | [log tóm tắt](prepublish-ci/mysql-ui.txt), [audit](prepublish-ci/results.json) |

Lượt đầu còn có 30 browser passed trước sửa guard; không cộng chồng với lượt recheck. Hai module mobile và hai ca trộn desktop/mobile bị loại rõ trong results.json, không tính PASS. CI đúng head `80157b5` có cả ba workflow success: [Backend/MySQL](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/actions/runs/42172643037), [Database](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/actions/runs/42172642994), [Tích hợp](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/actions/runs/42172642924). Không suy ra CI head sau commit thu gọn đã đạt.

Windows/Python 3.14.6/MySQL 8.0.46, Chromium cục bộ; chi tiết thư viện trong [environment.json](environment.json). SQL/oracle R01–R07 đạt, seed đủ 1.144 dòng, audit cuối sạch. [Hash seed trước](seed-before.json)/[sau](seed-after.json) bằng nhau; .env không đổi, cleanup instance private sạch. [Hash nguồn đã kiểm](tested-source-sha256.json) chỉ giữ các file liên quan.

## Phạm vi và mẫu đại diện

Test `tests/test_vuong_analytics_mysql_ui.py` đi qua MySQL thật → Flask → mọi ô bảng/SVG, không stub analytics.build: kỳ mặc định/tháng 8/rỗng, nhóm tuổi R01, ngưỡng/ngày R06, nhóm R05/R06 và chuỗi tiền R07.

Giữ ba ảnh đại diện: [R01](browser/R01-default.png), [R06](browser/R06-default.png), [R07 NULL](browser/R07-all-excluded.png). Ca R07 có [expected](browser/R07-all-excluded-expected.json)/[actual](browser/R07-all-excluded-actual.json): 0 mẫu, 1 đợt loại, năm số tiền NULL; bảng không đổi NULL thành 0 và không vẽ cột tiền. Fixture chỉ commit trong DB private đúng tên rồi xóa theo FK; seed phục hồi. DB tên khác skip đúng ca có ghi này.

60 GET/lượt và hai trang cũ qua browser đều HTTP 200, không tái hiện W3-DB-01 local; **vẫn theo dõi, chưa xác định nguyên nhân/đã sửa**. Laptop Quyền có môi trường khác (MySQL 8.4.11/Python 3.11.9), cần kiểm bản tích hợp riêng.

## Tái lập

```powershell
& .venv\Scripts\python.exe docs/evidence/vuong_mysql_review_20261106/run_private.py
# Chỉ kiểm lại SQL/oracle + 30 ca MySQL browser:
& .venv\Scripts\python.exe docs/evidence/vuong_mysql_review_20261106/check_publish.py
# Kiểm đường skip với DB private khác tên:
& .venv\Scripts\python.exe docs/evidence/vuong_mysql_review_20261106/check_publish.py --ci-db
```

Cần MySQL Server 8.0 tại đường dẫn ghi trong runner, pytest/PyMySQL/Playwright/psutil và Chromium. Runner tạo datadir/cổng loopback/DB mới, mật khẩu trong bộ nhớ, không lấy credentials hoặc kết nối DB làm việc từ .env; dừng đúng instance khi xong. Toàn bộ output lần chạy mới nằm trong `test-artifacts/vuong-mysql-review/` (Git ignore), tránh đưa log sinh tự động trở lại PR.

Bản bằng chứng đầy đủ trước thu gọn giữ local tại `test-artifacts/vuong-review-full-20261106/`; repo chỉ giữ biên nhận, audit/hash liên quan và mẫu đại diện. Các lượt raw mới có thể tái tạo bằng lệnh trên; không nhận bản local archive đã được upload thành artifact GitHub.

## Review còn lại

Trung (`ptt172`): hợp đồng API/UI, adapter ngày, nhóm R05/R06, tiền/NULL. Quyền (`NeyuQ3306`): seed/SQL, chạy bản tích hợp desktop trên laptop Quyền, lưu SHA/môi trường/expected/actual và log nếu gặp 503/MySQL 2003. Chờ review và CI đúng head trước Quyền điều phối merge; DOCX/PPTX/demo/bộ nộp vẫn chưa nghiệm thu.

Kiểm runner sau thu gọn: SQL/oracle đạt, 30 browser passed/0 skipped/0 failed; seed/.env không đổi, cleanup sạch. Output local: `test-artifacts/vuong-mysql-review/prepublish_20261106_061737_967296/`. Không chạy lại 442 ca hồi quy vì không đổi source sản phẩm hoặc test; không cộng chồng lượt smoke này.
