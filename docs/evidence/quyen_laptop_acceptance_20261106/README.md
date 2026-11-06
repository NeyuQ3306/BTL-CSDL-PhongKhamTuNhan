# Nghiệm thu laptop Quyền — 06/11/2026

## Kết quả và nguồn
Phiên Windows thực chạy 15:07–15:13 (UTC+07), Python3.12.10, MySQL8.4.11, Chromium156.
Nguồn ứng dụng: `2c01db2fe1d2d424f7dfe5b0a8192188d2c5fdc0`.
Khi chạy, runner Quyền và `tests/test_quyen_laptop_analytics.py` là file local chưa commit; không gán SHA ứng dụng cho hai file mới. Hash thực chạy ở [source-sha256.json](run/source-sha256.json).

| Phase | Passed | Failed/errors/skipped |
|---|---:|---|
| [Hồi quy](run/regression.xml) |453|0/0/0|
| [MySQL–Playwright](run/mysql-ui.xml) |30|0/0/0|
| [Windows cleanup](run/windows-cleanup.xml) |2|0/0/0|

Đối chiếu lại file được Quyền cung cấp: 485 test ID phân biệt; các số đếm JUnit khớp [results](run/results.json) và [console](runner-console.txt). Đây là review bằng chứng phiên laptop, không phải chạy lại Windows/MySQL tại môi trường review.
85 file trong manifest đã đối chiếu byte/SHA256 với đúng commit GitHub; runner và test bổ sung cũng khớp SHA256 được ghi. Manifest có87file, không có nghĩa fingerprint toàn bộ repository (không bao gồm mọi file week3_checks/windows_checks).

[SQL expected/actual](run/sql-expected-actual.json): R01–R07 cùng tập dòng sau canonicalization, giữ số lần xuất hiện, lần lượt29/83/10/29/6/19/15dòng. Oracle có thứ tự sinh khác SQL; không dùng so sánh list nguyên thứ tự để kết luận sai dữ liệu. Browser parity test kiểm thứ tự riêng. Trường base_commit trong công cụ SQL là nền lịch sử, không phải source_sha phiên này.

[Seed trước](run/seed-before.json)/[sau](run/seed-after.json) có11hash giống nhau; runner đối chiếu nội dung với canonical seed mỗi phase. [Audit](run/audit.json):1.144dòng,9nhóm findings rỗng. [MySQL log](run/mysql-server.txt) ghi shutdown hoàn tất; results ghi cổng đóng/launcher thoát, .env trước/sau đều vắng mặt. [Postflight](postflight.json) là biên nhận kiểm tại laptop, không phải truy vấn lại dịch vụ máy Quyền từ xa.

## Test bổ sung và phạm vi
[Test Quyền](../../../tests/test_quyen_laptop_analytics.py) có1ca R07 với mẫu hợp lệ0.00VND, khác NULL/không có mẫu;3ca viewport1440/390/320px, mỗi ca đủ R01–R07, chặn tài nguyên ngoài server local, kiểm tràn trang, chart và giữ kết quả sau khi offline.
Không gọi đây là truy vấn mới khi server tắt: API vẫn cần Flask/MySQL.
30ca MySQL UI kế thừa test Vương; 453ca hồi quy gồm backend/SQL/stub UI và4ca mới, không gọi tất cả là browser MySQL.

Fixture R07 ghi trong DB tên clinic_vuong_analytics_test trên instance private mới; cleanup theo FK rồi đối chiếu snapshot. Test có skip guard trên DB khác tên. Kết quả CI sau khi thêm test có thể có skip đúng guard; không thay số485local bằng sốCI hoặc cộng hai bộ.

## Cách ly và tái lập
Runner kế thừa Vương, hỗ trợ QUYEN_MYSQLD, không dùng credentials .env. Tạo datadir/cổng loopback và mật khẩu ngẫu nhiên riêng. Không chạm dịch vụ MySQL84 làm việc. Không đưa venv/datadir lên Git.
Từ repo gốc, với venv/dependencies/Chromium đã chuẩn bị:
```powershell
$env:QUYEN_MYSQLD = 'C:/Program Files/MySQL/MySQL Server 8.4/bin/mysqld.exe'
$env:QUYEN_EVIDENCE_OUTPUT = Join-Path (Get-Location) 'local-evidence/quyen-rerun-UNIQUE'
.venv/Scripts/python.exe docs/evidence/quyen_laptop_acceptance_20261106/run_private.py
```
Chọn hậu tố UNIQUE mới; không chạy đồng thời. Output phải nằm ngoài test-artifacts vì runner copy thư mục test-artifacts vào output. Phần ảnh copy có thể chứa artifact cũ nếu chạy trên workspace đã dùng; đối chiếu timestamp/phase trước khi sử dụng làm bằng chứng mới.

## Giới hạn gói đã nhận
Gói này giữ log/JUnit/audit/hash/SQL expected–actual và nguồn test/runner. 161ảnh, JSON browser riêng và raw thư mục windows-cleanup vẫn nằm trên laptop, chưa được gửi trong gói review; không nhận đã xem các ảnh đó. Kết quả2cleanup có JUnit/log và postflight nhưng chưa đối chiếu từng raw results.json của2instance.
verify_evidence.py được giữ nguyên như công cụ kiểm tại laptop; cần đầy đủ bộ local, source đúng hash và Windows/MySQL84. Không chạy script đó trên gói rút gọn hoặc máy khác để xác nhận trạng thái laptop; script có ghi lại postflight.json.
Các log UTF-16 được chuyển UTF-8 khi đóng gói; không thay giá trị kết quả hay mã Python đã kiểm.
Không xác nhận DOCX/PPTX, import bộ SQL nộp cuối, buổi tập demo, Drive/quyền giảng viên, release hay nộp bài. Issue#3 giữ mở.
