# Chỉ mục bằng chứng tuần 2 — Vương

## Xác nhận cuối 20/10/2026

[Biên bản cập nhật](../VUONG_WEEK2_PR_REVIEW.md) ghi source #5 `da59e56`, kiểm tra source/test và đọc CI 115 passed/0 skipped, phản hồi/resolve hai thread UI bằng `Vuong-it`. Cùng biên bản ghi approval có phạm vi của Trung trên #11 `e346a9f` và log CI 168 passed/0 skipped trên merge thử `f3c1690`. Đây là xác nhận bằng bằng chứng có sẵn, không phải lần chạy local mới. [Bàn giao hiện hành](../VUONG_WEEK2_HANDOFF.md) phân biệt phần đã xong và việc chờ tích hợp/nghiệm thu nhóm; dữ liệu lịch sử bên dưới giữ nguyên.

## Review phụ thuộc và chạy lại tích hợp

[Biên bản review](../VUONG_WEEK2_PR_REVIEW.md): PR5 source gốc `10c8082` chạy 108 test/0 skip, PR10 source gốc `1bf9f8b` chạy 78 SQL test/0 skip; Vương `3390199` chạy lại 168 test/0 skip trong phiên `20261019_224053`. Mỗi kết quả có JUnit/log/manifest/audit riêng; không dùng source đã sửa của Vương làm bằng chứng UI gốc Trung. [CI log trích theo SHA và review ID](vuong_pr_review_ci.json); [harness](vuong_pr_review_harness/README.md). Thư mục 224053 giữ ảnh browser và khảo sát của chính phiên mới.

## Phiên nghiệm thu chính

[Biên bản T01–T15](../VUONG_WEEK2_ACCEPTANCE.md), phiên `20261019_221718`: 168 passed, 0 skipped. [JUnit](vuong_week2_prepare_20261019_221718/junit.xml), [test log](vuong_week2_prepare_20261019_221718/pytest.txt), [cases JSON](vuong_week2_prepare_20261019_221718/browser-tests/vuong-acceptance/cases.json), [ma trận CSV](vuong_week2_prepare_20261019_221718/acceptance-matrix.csv), [audit/môi trường](vuong_week2_prepare_20261019_221718/results.json), [manifest](vuong_week2_prepare_20261019_221718/source_sha256.json).

Thư mục phiên chính giữ đầy đủ ảnh khảo sát, luồng nghiệp vụ, hồi quy CRUD, báo cáo và ca T01–T15. Dữ liệu trên ảnh là seed/dữ liệu thử của bài tập, không phải hồ sơ thật. Source lúc đó được định danh bằng HEAD nền + manifest, vì các thay đổi Vương còn trong working tree.

## Các mốc trước đó

| Phiên | Ý nghĩa |
|---|---|
| 214402 | Không kết nối được instance trong sandbox, dừng trước import; không tính đạt |
| 214447 | Nền tích hợp, 160 test đạt và phát hiện UI kê đơn tràn 320 px |
| 215312 | Một selector test mới lỗi, helper gặp stdout cp1252; không tính đạt toàn suite |
| 215400 | UI nghiệp vụ: 161 test đạt |
| 220415 | Báo cáo mới đạt, selector test cũ trùng tổng hiển thị; không tính đạt toàn suite |
| 220540 | Bốn báo cáo: 163 test đạt |
| 221500 | 168 test đạt; sau đó tăng độ độc lập của hai trường hợp T06 |
| 221718 | Phiên nghiệm thu chốt T01–T15, 168 test đạt |

Để tránh đưa ảnh lặp/file trung gian vào PR, các phiên trước chỉ giữ log/results/manifest và ảnh/JSON được tài liệu tham chiếu. Ảnh thừa đã chuyển vào `.venv/week2_evidence_archive` cục bộ (Git bỏ qua), không xóa dữ liệu nguồn. Một số `screens[].screenshot` trong results lịch sử chỉ là tên tại thời điểm chạy; bộ ảnh khảo sát đầy đủ của phiên chốt nằm ở 221718.

## Đóng gói và commit

Source commit **fa699a6874452d273cc1e88d689dea1146ffd2f5** được chạy lại ở `20261019_222841`: 168 passed/0 skipped, 47,68 giây. [JUnit](vuong_week2_prepare_20261019_222841/junit.xml), [test log](vuong_week2_prepare_20261019_222841/pytest.txt), [results/audit](vuong_week2_prepare_20261019_222841/results.json), [manifest](vuong_week2_prepare_20261019_222841/source_sha256.json), [cases T01–T15](vuong_week2_prepare_20261019_222841/browser-tests/vuong-acceptance/cases.json). Có ảnh các ca nghiệm thu và JSON đối chiếu; các ảnh khảo sát/CRUD/báo cáo lặp của lần này được giữ trong archive local, bộ ảnh đầy đủ đã có tại 221718. Tên ảnh khảo sát trong results là tên lúc thu thập, không cam kết mọi ảnh lặp đều nằm trong PR.

`vuong_week2_delivery_checks.json` ghi kết quả kiểm tra secrets/file tạm, template, Python, link tài liệu và đồng nhất source với snapshot kiểm thử. Nếu có phiên chạy lại sau commit, đó là kiểm chứng bổ sung được trỏ riêng trong tài liệu bàn giao/PR; không sửa số liệu lịch sử để gán cho commit mới.
