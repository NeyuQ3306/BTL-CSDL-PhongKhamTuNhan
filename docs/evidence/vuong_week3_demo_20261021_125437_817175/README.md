# Diễn tập demo tuần 3 — chứng cứ chính

Ngày 21/10/2026, UTC+07:00. Trợ lý Codex thay mặt Vương chạy **Chromium tự động**, chưa có buổi tập của nhóm.

Source nền `f4869299c25fdfd0b711597e30b60ab277120f44` cộng sửa UI/test chưa commit; app khớp candidate `sha256:045a7c42b12390bc5a1cb911a1ec648215cf66df679b6576a7b22464bb398894`. Công cụ demo mới có hash riêng trong manifest 67 file và source.diff; không nhận candidate cũ tự chứa công cụ mới.

## Kết quả

- **Hai lần trọn kịch bản đạt**, thời gian thao tác tự động 10,421s và 10,327s trên datadir khác nhau. Chưa có lời nói/chuyển phần; thời lượng 13 phút là mục tiêu chưa được nhóm xác nhận.
- Python 3.11.9 / MySQL 8.4.7 / Chromium 156.0.8078.4, locale vi-VN; DB và cổng riêng, không dùng `.env` gốc.
- CRUD 3 nhóm; tiếp nhận/tái khám/qua tháng; hỗ trợ; đơn 2 thuốc 9.900đ; đóng/khỏi/tái mắc/nhiều bệnh; đủ Q1–Q4 và ca sai đều đạt. Đối chiếu UI–JSON–SQL chuẩn–expected.
- Seed 10/2026 không đổi sau ghi. Cuối có 1.162 dòng do thêm 18 dòng demo; `matches_expected_counts=false` là dự kiến. 9 nhóm findings và 10 tập audit SQL rỗng; 1.144 dòng seed giữ nguyên.
- App/DB đã đóng cổng, `.env` gốc/source/bằng chứng cũ giữ nguyên; process-check xác nhận không còn MySQL thuộc datadir step6.

## Hồ sơ

| File | Nội dung |
|---|---|
| [session.json](session.json) | SHA/candidate, môi trường, datadir/cổng,8 bước thực chạy, thời gian và cleanup |
| [execution_source_sha256.json](execution_source_sha256.json), [source.diff](source.diff) | Source thực chạy gồm công cụ mới; không gán cho riêng SHA nền |
| [expected.json](expected.json) | Expected ghi trước thao tác browser |
| [report-parity.json](report-parity.json) | Actual bốn kỳ và lịch sử DM6BN, so UI/JSON/SQL/expected |
| [SQL10/2026](sql-2026-10.json), [SQL02/2004](sql-2004-02.json), [SQL03/2004](sql-2004-03.json), [SQL12/2025](sql-2025-12.json) | Mỗi kỳ 11 tập chuẩn từ queries.sql, thay đúng tham số |
| [audit-before.json](audit-before.json), [audit-after.json](audit-after.json) | Seed ban đầu và DB sau demo |
| [console.txt](console.txt) | HTTP log và kết quả của đúng phiên |
| [visual-review.json](visual-review.json) | Đã xem 24/24 ảnh phiên này qua view_image; không nhận đã xem mọi phiên |
| [process-check.json](process-check.json) | Kiểm tra tiến trình sau cùng, count 0 |
| [delivery-checks.json](delivery-checks.json), [verify_delivery.py](verify_delivery.py) | Kiểm tra hồ sơ/link/hash và khả năng lặp lại |

## Các phiên liên quan và vướng mắc

- [Lần đầu không đạt](../vuong_week3_demo_20261021_125130_401438/session.json): W3-DEMO-01/P2 công cụ rehearsal, đã sửa và kiểm tra lại: lỗi công cụ rehearsal điền thâm niên vào form bệnh nhân. Không phải lỗi app; đã sửa chỉ điền field của entity, rồi chạy lại toàn kịch bản 2 lần. Phiên lỗi đã cleanup.
- [Lần đạt thứ nhất](../vuong_week3_demo_20261021_125348_319089/session.json): 10,421s. Ảnh phiên này không được nhận là đã rà bằng mắt.
- [Thử serve/Ctrl+C](../vuong_week3_demo_20261021_125527_974568/session.json): datadir mới khác, seed 1.144 dòng, cleanup đạt. PTY/PowerShell exit 1 sau Ctrl+C; session app success=true và các cổng đóng.
- W3-RUN-01 của runner tuần 2 còn mở; công cụ demo dùng SQL SHUTDOWN riêng, không sửa runner cũ. Không phát hiện lỗi app chặn demo mới trong phạm vi đã chạy.
- Không chạy lại full suite 179 test, không kiểm chứng máy thứ hai/T16, không xác nhận phân vai hoặc nhóm đã tập, không commit/push/PR/gửi tin nhắn.

## Ảnh đã xem — đúng phiên này

- [02-crud-patients.png](02-crud-patients.png) — 1440px; patients/DM6TMPBN
- [02-crud-doctors.png](02-crud-doctors.png) — 1440px; doctors/DM6TMPBS
- [02-crud-nurses.png](02-crud-nurses.png) — 1440px; nurses/DM6TMPYT
- [03-revisit-across-month.png](03-revisit-across-month.png) — 1440px; visits/DM6L2
- [04-nurse-support.png](04-nurse-support.png) — 1440px; visits/DM6L2
- [05-prescription.png](05-prescription.png) — 1440px; prescriptions/DM6RX
- [06-recurrence-two-diseases.png](06-recurrence-two-diseases.png) — 1440px; visits/DM6L3
- [07-closed-visit.png](07-closed-visit.png) — 1440px; visits/DM6L3
- [08-2026-10-diseases.png](08-2026-10-diseases.png) — 1440px; reports/diseases?month=2026-10
- [08-2026-10-salaries.png](08-2026-10-salaries.png) — 1440px; reports/salaries?month=2026-10
- [08-2026-10-revenue.png](08-2026-10-revenue.png) — 1440px; reports/revenue?month=2026-10
- [08-2004-02-diseases.png](08-2004-02-diseases.png) — 1440px; reports/diseases?month=2004-02
- [08-2004-02-salaries.png](08-2004-02-salaries.png) — 1440px; reports/salaries?month=2004-02
- [08-2004-02-revenue.png](08-2004-02-revenue.png) — 1440px; reports/revenue?month=2004-02
- [08-2004-03-diseases.png](08-2004-03-diseases.png) — 1440px; reports/diseases?month=2004-03
- [08-2004-03-salaries.png](08-2004-03-salaries.png) — 1440px; reports/salaries?month=2004-03
- [08-2004-03-revenue.png](08-2004-03-revenue.png) — 1440px; reports/revenue?month=2004-03
- [08-2025-12-diseases.png](08-2025-12-diseases.png) — 1440px; reports/diseases?month=2025-12
- [08-2025-12-salaries.png](08-2025-12-salaries.png) — 1440px; reports/salaries?month=2025-12
- [08-2025-12-revenue.png](08-2025-12-revenue.png) — 1440px; reports/revenue?month=2025-12
- [09-seed-history.png](09-seed-history.png) — 1440px; reports/history?patient_id=BN001
- [10-demo-history.png](10-demo-history.png) — 1440px; reports/history?patient_id=DM6BN
- [11-error-preserves-input.png](11-error-preserves-input.png) — 1440px; visits/new
- [12-mobile-history-390.png](12-mobile-history-390.png) — 390px; reports/history?patient_id=DM6BN

[Kịch bản, lệnh mở phiên mới, expected và checklist tập chung](../../VUONG_WEEK3_DEMO.md).
