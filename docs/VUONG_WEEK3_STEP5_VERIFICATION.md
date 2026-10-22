# Đối chiếu hướng dẫn — Bước 5 tuần 3

Ngày 21/10/2026, UTC+07:00. Người thực hiện: trợ lý Codex thay mặt Vương. **Đạt tiêu chí Bước 5 đối với main đã xác minh và ứng viên hiện có**: hướng dẫn cài/chạy/sử dụng đã cập nhật, có bằng chứng đúng phiên bản và giới hạn rõ ràng. Không coi đây là chốt release/merge hoặc nghiệm thu nhóm.

## 1. Phiên bản thực sự được hướng dẫn

- Main local, origin/main và main remote xác minh bằng `git ls-remote origin refs/heads/main` cùng là `f4869299c25fdfd0b711597e30b60ab277120f44`. Không fetch/switch/reset checkout đang có sửa đổi.
- Ứng viên bước 4 = SHA nền trên + `clinic_app/templates/week1/base.html`, `clinic_app/static/number-validation.js`, `tests/test_vuong_week3_numeric_validation.py` theo [candidate](evidence/vuong_week3_final_20261021/candidate.json), [diff](evidence/vuong_week3_final_20261021/source.diff), [manifest124](evidence/vuong_week3_final_20261021/execution_source_sha256.json).
- Candidate ID: `sha256:045a7c42b12390bc5a1cb911a1ec648215cf66df679b6576a7b22464bb398894`. Main chưa có sửa ô số; kết quả 179 test thuộc ứng viên, không thuộc riêng SHA nền. Manifest124 còn gồm tài liệu tại thời điểm bước 4; các hash tài liệu thay đổi trong bước 5 không có nghĩa source thực thi đã thay đổi. Phiên bước 5 đối chiếu riêng **66 file app/tools/database/tests/config/dependencies** và tất cả khớp bước 4.
- Không phát hiện script nộp cuối đã được kiểm chứng thay quy trình import hiện hành. Không sửa schema/API/công thức hay runner.

## 2. Tài liệu đã hoàn thiện

| File | Thay đổi |
|---|---|
| [SETUP.md](SETUP.md) | Thay hướng dẫn cố định tuần 1 bằng clone main/ghi SHA; đủ phiên bản, venv, dependencies, `.env`, DB mới, import/audit, app, hồi quy và xử lý lỗi |
| [USER_GUIDE.md](USER_GUIDE.md) | Hướng dẫn hiện hành cho CRUD, tiếp nhận/tái khám, hỗ trợ, đơn nhiều thuốc, kết thúc/khỏi và bốn báo cáo; expected seed và dữ liệu giả riêng |
| [VUONG_WEEK2_USER_GUIDE.md](VUONG_WEEK2_USER_GUIDE.md) | Thêm nhãn lịch sử và dẫn hướng dẫn hiện hành; giữ nguyên nội dung lịch sử |
| [README](../README.md) | Đưa hướng dẫn hiện hành lên đầu, phân biệt main/ứng viên và nhãn lịch sử, bỏ khẳng định báo cáo chỉ là khung ở phần bắt đầu |
| [Hồ sơ tuần 3](VUONG_WEEK3_ACCEPTANCE.md) | Bổ sung mốc bước 5 và đường dẫn bằng chứng, giữ các mốc cũ để truy vết |

## 3. Lệnh và phương thức đã đối chiếu

| Nội dung | Mức kiểm chứng / bằng chứng |
|---|---|
| SHA remote main | **Chạy mới** `git ls-remote`; [kết quả xác minh cuối](evidence/vuong_week3_step5_20261021/document-checks.json) |
| Clone mới, `git switch --detach` | **Đối chiếu Git/source**, không clone hoặc đổi nhánh trong checkout hiện tại; không nhận đã cài mới từ mạng trong bước 5 |
| `py -3.11 -m venv`, pip requirements, Chromium install | **Đối chiếu cấu trúc/lệnh và dependencies của runtime đã chạy bước 4**, không cài lại hoặc tải gói mới bước 5. Python thực dùng là executable 3.11.9 được ghi trong session; tài liệu có phương án đường dẫn tuyệt đối khi thiếu `py` |
| `.env.example`, sinh secret, DB_* | **Đọc source + chạy mới** bằng `.env` phát sinh trong bản sao cách ly, bỏ DB_*/FLASK_* kế thừa khỏi child env; audit/app đọc đúng DB private. `.env` gốc không sửa/không xuất nội dung |
| CREATE DATABASE, import sáu bước, SHOW TABLES/TRIGGERS | **Chạy SQL mới qua PyMySQL/parser repo**, đúng nội dung file/thứ tự. Không thao tác Workbench GUI mới; các thao tác mở tab/default schema là hướng dẫn client, chưa nhận đã kiểm chứng UI Workbench trên máy này |
| `python -m tools.audit_seed` | **Chạy mới**, 1.144 dòng, counts đúng, 9 nhóm findings rỗng; hai lượt audit SQL trước/sau constraints mỗi lượt 10 tập rỗng |
| `python app.py` và URL | **Chạy mới process thật**, loopback:5000, 11 route HTTP 200 gồm health/DB/CRUD/tiếp nhận/bốn báo cáo. Đây là smoke HTTP, không tự nhận đã thao tác CRUD qua browser mới |
| Runner `--serve`, `--mysqld`, `--browsers-path` | **Đối chiếu argparse/source** và phiên runner bước 4. Không chạy lại `--serve` hoặc suite bước 5; W3-RUN-01 còn mở và được ghi workaround |
| Flask CLI cổng 5001, cài native/Docker, bảng lỗi | **Đối chiếu source/cấu hình**, chưa chạy mới từng phương án/lỗi; không khẳng định đã thử mọi nhánh cài đặt |

Phiên mới dùng MySQL executable sẵn có **8.4.7**, Python **3.11.9**, source mirror và datadir mới dưới `.venv/week3-step5-20261021_124050`; DB `clinic_week3_demo_test` trên cổng **54498**. Không dùng DB đang làm việc hoặc `.env` gốc. [Session/lệnh/kết quả](evidence/vuong_week3_step5_20261021/setup-results.json), [audit](evidence/vuong_week3_step5_20261021/audit.json), [SQL mặc định — 11 tập](evidence/vuong_week3_step5_20261021/queries-default.json).

Lần đầu trong sandbox không kết nối được private MySQL, **không đạt**, không chạy import: [attempt1](evidence/vuong_week3_step5_20261021/attempt1-sandbox.json). MySQL log cho biết server đã ready; chỉ từ đó chưa kết luận lỗi app/MySQL. Đã chạy lại với quyền thực thi phù hợp trên datadir mới và đạt. Trường cổng đóng ở attempt1 được đo trong sandbox nên không dùng làm bằng chứng cleanup ngoài sandbox; lần rà process có quyền sau cùng không còn MySQL thuộc datadir step5. Lần đạt shutdown bằng kết nối private và xác nhận đóng cổng app/DB, xóa `.env` sinh trong mirror, giữ nguyên `.env` gốc và toàn bộ bằng chứng trước bước 5.

## 4. Truy vết kết nối, CRUD, nghiệp vụ và đủ bốn báo cáo

Tất cả bằng chứng bước 4 dưới đây thuộc **SHA nền + candidate045a7c42**, run_id `20261021_121231`, Python3.11.9/MySQL8.4.7/Chromium156.0.8078.4. **179 testcase / 0 failure / 0 error / 0 skip** trong [JUnit](evidence/vuong_week3_final_20261021/runner-output/junit.xml); [log test](evidence/vuong_week3_final_20261021/runner-output/pytest.txt), [session](evidence/vuong_week3_final_20261021/session.json). Đã đọc lại XML/actual và so hash source, không chỉ dựa vào câu tổng kết trong README cũ.

| Phạm vi | Bằng chứng đúng phiên bản |
|---|---|
| Kết nối/import/audit | [Kết quả runner bước 4](evidence/vuong_week3_final_20261021/runner-output/results.json), [health/DB và audit mới bước 5](evidence/vuong_week3_step5_20261021/setup-results.json) |
| CRUD bệnh nhân/bác sĩ/y tá, chặn xóa có lịch sử | JUnit: `test_crud[patients/doctors/nurses]`, `test_browser_week1_crud[patients/doctors/nurses]`, `test_history_prevents_delete[...]`; log từng ca ở trên |
| Tiếp nhận/tái khám, nhiều bệnh, hỗ trợ, đơn nhiều thuốc, kết thúc/khỏi | [T01–T15 input/expected/actual/phương thức](evidence/vuong_week3_final_20261021/browser-tests/vuong-acceptance/cases.json); [ảnh lượt](evidence/vuong_week3_final_20261021/browser-tests/week2/01-visit.png), [ảnh đơn](evidence/vuong_week3_final_20261021/browser-tests/week2/02-prescription.png); JUnit `test_vuong_clinical_workflow`, `test_browser_clinical_flow` |
| Q1 — bệnh | [UI–JSON–SQL–expected](evidence/vuong_week3_final_20261021/browser-tests/vuong-reports/seed-parity.json), [ảnh tháng10](evidence/vuong_week3_final_20261021/browser-tests/vuong-reports/2026-10-diseases.png): 24 đợt |
| Q2 — lương | Cùng seed-parity, [ảnh lương](evidence/vuong_week3_final_20261021/browser-tests/vuong-reports/2026-10-salaries.png): BS78.000.000/y tá65.600.000 |
| Q3 — lịch sử/tình trạng | Cùng seed-parity phần patients, [ảnh BN001](evidence/vuong_week3_final_20261021/browser-tests/vuong-reports/history-1440.png); BN001 có 7 tập với số dòng `[1,3,4,1,5,8,3]` |
| Q4 — doanh thu | Cùng seed-parity, [ảnh doanh thu](evidence/vuong_week3_final_20261021/browser-tests/vuong-reports/2026-10-revenue.png): khám4.680.000 + thuốc5.820.800 =10.500.800 |
| Ca biên/kỳ trống/giá lịch sử | [edge-parity](evidence/vuong_week3_final_20261021/browser-tests/vuong-reports/edge-parity.json), T01–T15; kỳ12/2025 Q1/Q4=0, Q2 vẫn lương cơ bản70.000.000/60.000.000 |
| Validation/giữ dữ liệu/dòng động | [Retest bước 4](evidence/vuong_week3_final_20261021/browser-tests/vuong-week3/quantity.json), bốn ca numeric regression trong JUnit |

Ảnh được liên kết từ phiên đúng candidate để truy vết; bước 5 không nhận đã chụp mới hoặc xem lại bằng mắt toàn bộ ảnh. T05/T06/T13/concurrency/rollback phải đọc đúng phương thức HTTP/SQL/chuyên biệt trong cases, không gọi tất cả là thao tác tay trên UI.

## 5. Kết luận phạm vi và việc sau đó

Không có source thực thi đổi ở bước 5 nên không chạy lại toàn suite đã đạt; kiểm chứng mới tập trung phần hướng dẫn cài/chạy và đọc `.env`. Cài mới từ mạng, Workbench GUI, Docker, từng cách xử lý lỗi và thiết bị khác chưa được kiểm chứng mới, đã ghi rõ thay vì đánh dấu PASS.

W3-RUN-01 vẫn chờ Trung sửa source, hướng dẫn có workaround kiểm tra đúng instance. Chưa có blocker tài liệu/cài chạy mới trong phiên đạt. Release/main sau merge cần đối chiếu SHA và kiểm tra lại theo bước 7; không nhận việc tương lai này đã hoàn tất. T16 **không thực hiện theo quyết định nhóm ngày21/10/2026**, actual **chưa chạy**, không tính PASS và không phải việc chờ.

Không gọi subagent, không gửi tin nhắn, không commit/push/PR/triển khai. Không thay đổi các sửa UI/test và bằng chứng có sẵn của người dùng. Có thể chuyển sang bước 6 chuẩn bị/tập demo.
