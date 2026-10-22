# Hồ sơ nghiệm thu tuần 3 của Vương

Lập ngày **21/10/2026**, múi giờ UTC+07:00 (Asia/Bangkok, cùng giờ Việt Nam). Người lập: **trợ lý Codex thay mặt Vương**, không phải xác nhận Vương đã tự thao tác kiểm thử.

**Cập nhật hiện hành 22/10/2026:** ứng viên [#17](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/pull/17) tại `1964a4a10e8634384ce2ebf5951bc66e5525f755` đã tích hợp #12–#15 và được Trung approve; #13 của Vương đã được Trung approve/resolve cleanup. Chưa merge hoặc chốt nghiệm thu toàn nhóm/release. #16 đã được Vương approve nhưng chưa tích hợp. [Bàn giao #17](VUONG_WEEK3_HANDOFF.md) ghi source, review, Windows/CI, lỗi và việc còn chờ.

Quyền chạy Windows trên source `dd1f41e4b1459bb82b5d288eb2a02d85de0d81b3`; head#17 chỉ thêm12file evidence. Ba phiên [073906](evidence/vuong_week2_prepare_20261022_073906_519771/results.json) (194pass/1fail, HTTP503/MySQL2003 theo PR), [074813](evidence/vuong_week2_prepare_20261022_074813_773699/results.json) (195tests/0failure/error/skip), [075907](evidence/vuong_week2_prepare_20261022_075907_328633/results.json) ([JUnit236tests/0failure/error/skip](evidence/vuong_week2_prepare_20261022_075907_328633/junit.xml), gồm `tests week3_checks`) giữ riêng. Phiên cuối audit11bảng/9trigger/1.144dòng sạch, seed giữ nguyên/cleanup đạt; bốn workflow CI head#17 success. Đây là đọc bằng chứng Quyền và trạng thái CI, không nhận trợ lý chạy lại Windows hoặc xem ảnh còn trên máy Quyền.

W3-RUN-01 vẫn mở chờ Trung/Quyền quyết định đóng, dù bản sửa đã tích hợp và được Trung review. HTTP503/MySQL2003 tiếp tục theo dõi, hai phiên sau không tái hiện nhưng chưa chứng minh đã sửa. T16 không thực hiện/actual chưa chạy/không tính PASS. Vương xác nhận bước6 ngày21/10; chưa có chi tiết buổi tập chung để điền.

**Các mục1–10 bên dưới là hồ sơ lịch sử ngày21/10**, gồm ma trận ca với input/actual/source tại thời điểm chạy. Các câu “chưa commit/push/PR/CI”, “chờ Trung sửa/review”, “chưa tập chung” trong các mốc đó không thay trạng thái hiện hành này. Không thay SHA hoặc kết quả cũ thành kết quả trên #17/commit tài liệu mới.

## 1. Trạng thái và nguồn chuẩn tại thời điểm chuẩn bị 21/10 (lịch sử)

**Bước 1 đã chuẩn bị; Bước 2 đạt hồi quy tự động local ngày 21/10/2026: 175 passed / 0 failure / 0 error / 0 skipped. Bước 3 đã kiểm tra UI; Bước 4 đã sửa và kiểm tra lại UX, suite ứng viên cuối 179/179 đạt. Còn W3-RUN-01 về cleanup công cụ chờ Trung, có workaround; không có lỗi sản phẩm chặn được phát hiện.** Không chuyển kết quả, ảnh, số lượng 168 test hoặc trạng thái đạt tuần 2 thành nghiệm thu tuần 3. Chưa xác minh CI, chưa nghiệm thu nhóm, chưa thực hiện T16.

- Nhánh mới: `vuong/week-3`, tạo bằng `git switch -c vuong/week-3 origin/main` sau khi fetch thành công.
- SHA nền: `f4869299c25fdfd0b711597e30b60ab277120f44`; `main`, `origin/main` và HEAD nhánh mới cùng SHA tại thời điểm chuẩn bị.
- `git merge --ff-only origin/main` trả `Already up to date.`; không dùng lại nhánh tuần 2.
- Trước chuẩn bị: không có thay đổi tracked hoặc staged; có thư mục untracked `docs/evidence/vuong_week2_prepare_20261019_225048/`. Giữ nguyên, không stage hoặc đưa vào commit mới.
- Hồ sơ và sửa UI tuần 3 hiện chưa commit. Bản cuối có thay đổi source sau SHA nền; định danh bằng [candidate + diff/manifest124](evidence/vuong_week3_final_20261021/candidate.json), không gán kết quả cho riêng commit nền. Chưa push, mở PR hoặc merge.
- Môi trường Bước 2 thực chạy: **Python 3.11.9 / MySQL 8.4.7 / Chromium 156.0.8078.4**; đúng dòng Python 3.11/MySQL 8.4 mục tiêu, runtime riêng mới. Xem [phiên kiểm thử](evidence/vuong_week3_regression_20261021/session.json).

Nguồn ca: [ACCEPTANCE.md](ACCEPTANCE.md). Đã đối chiếu [RULES.md](../RULES.md), [phân công](PHAN_CONG_3_TUAN.md), [nghiệm thu tuần 2](VUONG_WEEK2_ACCEPTANCE.md), [hướng dẫn tuần 2](VUONG_WEEK2_USER_GUIDE.md), [SETUP.md](SETUP.md) và kế hoạch người dùng cung cấp tại `D:\Codex\plan_week3.md`. Hướng dẫn nhánh/SHA tuần cũ chỉ là tham khảo lịch sử; không checkout về bản cũ để nghiệm thu tuần 3.

Bằng chứng chuẩn bị: [chỉ mục](evidence/vuong_week3_setup_20261021_111405/README.md), [thông tin chuẩn bị](evidence/vuong_week3_setup_20261021_111405/preparation.json), [manifest bằng chứng cũ được giữ nguyên](evidence/vuong_week3_setup_20261021_111405/preserved_week2_sha256.json), [kiểm tra hồ sơ](evidence/vuong_week3_setup_20261021_111405/verification.json). Đây là bằng chứng Bước 1, không phải bằng chứng các ca đạt.

**Điều chỉnh phạm vi 21/10/2026:** Vương thông báo Quyền và cả nhóm đã chốt bỏ thực hiện T16. Trạng thái hiện hành: **Không thực hiện theo quyết định nhóm**; actual vẫn **Chưa chạy**, không tính đạt, không còn cổng nghiệm thu hoặc việc chờ máy thứ hai. Nguồn quyết định hiện đã ghi tại [issue #3](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/issues/3) và [PR #14](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/pull/14). Các ghi nhận chờ T16 ở mốc Bước 1–3 bên dưới là lịch sử, đã được quyết định này thay thế. Không sửa bằng chứng phiên cũ.

## 2. Ma trận T01–T16

Tình huống và expected giữ nguyên từ `docs/ACCEPTANCE.md`. Bảng ghi input dự kiến và input/actual của **phiên tự động ứng viên cuối Bước 4**; T16 chưa thực hiện. Các kiểm tra tương tác bổ sung Bước 3 được ghi riêng tại mục 7 và giữ kết quả lịch sử Bước 2 trong chỉ mục phiên tương ứng. Expected cụ thể cho từng dữ liệu giả có trong JSON ca, độc lập với output ứng dụng. Một ID có thể cần nhiều lần thử; giữ từng kết quả riêng, không ghi đè lịch sử.

| ID | Input/tình huống dự kiến | Expected theo chuẩn | Actual | Trạng thái | Phương thức dự kiến; thực tế | Người thực thi ca | Ngày giờ chạy | SHA/source thực chạy | Liên kết bằng chứng ca |
|---|---|---|---|---|---|---|---|---|---|
| T01 | Một bệnh nhân khám cùng bệnh 3 lần trong một đợt/tháng<br>Ứng viên cuối: AD1 khám 28/29/30-09-2001 | Thống kê 1 đợt, STT 1–3 | {"episodes":1,"sequence":[1,2,3]} | Đạt local — ứng viên cuối | Browser + SQL (tự động; không phải kiểm tra tay) | Trợ lý Codex thay mặt Vương | 2026-10-21T12:13:14.241659+07:00 | f4869299c25fdfd0b711597e30b60ab277120f44 + [manifest124](evidence/vuong_week3_final_20261021/execution_source_sha256.json) | [JSON ca](evidence/vuong_week3_final_20261021/browser-tests/vuong-acceptance/cases.json); [ảnh](evidence/vuong_week3_final_20261021/browser-tests/vuong-acceptance/T01-three-visits.png) |
| T02 | Khỏi rồi tái mắc cùng bệnh trong tháng<br>Ứng viên cuối: AD1 khỏi 01/10, AD2 tái mắc 02/10/2001 | Tạo MaDot mới, thống kê 2 đợt | {"episodes":["AD1","AD2"],"q1":2} | Đạt local — ứng viên cuối | Browser + SQL (tự động; không phải kiểm tra tay) | Trợ lý Codex thay mặt Vương | 2026-10-21T12:13:16.054270+07:00 | f4869299c25fdfd0b711597e30b60ab277120f44 + [manifest124](evidence/vuong_week3_final_20261021/execution_source_sha256.json) | [JSON ca](evidence/vuong_week3_final_20261021/browser-tests/vuong-acceptance/cases.json); [ảnh](evidence/vuong_week3_final_20261021/browser-tests/vuong-acceptance/T02-recurrence.png) |
| T03 | Một đợt có lần khám ở hai tháng<br>Ứng viên cuối: AD1 khám cả 09/2001 và 10/2001 | Mỗi tháng có khám tính đợt một lần | {"2001-09":1,"2001-10":1} | Đạt local — ứng viên cuối | Browser tự động xem hai kỳ; nhãn legacy Browser + JSON trong JSON ca | Trợ lý Codex thay mặt Vương | 2026-10-21T12:13:14.847853+07:00 | f4869299c25fdfd0b711597e30b60ab277120f44 + [manifest124](evidence/vuong_week3_final_20261021/execution_source_sha256.json) | [JSON ca](evidence/vuong_week3_final_20261021/browser-tests/vuong-acceptance/cases.json); [ảnh](evidence/vuong_week3_final_20261021/browser-tests/vuong-acceptance/T03-cross-month.png) |
| T04 | Một lượt khám hai bệnh<br>Ứng viên cuối: AC5 thêm bệnh W2B2, đợt AD3 | Hai lần khám khác đợt, cùng bệnh nhân | [{"ma_dot":"AD2","ma_benh_nhan":"W2BN1"},{"ma_dot":"AD3","ma_benh_nhan":"W2BN1"}] | Đạt local — ứng viên cuối | Browser + SQL (tự động; không phải kiểm tra tay) | Trợ lý Codex thay mặt Vương | 2026-10-21T12:13:16.497625+07:00 | f4869299c25fdfd0b711597e30b60ab277120f44 + [manifest124](evidence/vuong_week3_final_20261021/execution_source_sha256.json) | [JSON ca](evidence/vuong_week3_final_20261021/browser-tests/vuong-acceptance/cases.json); [ảnh](evidence/vuong_week3_final_20261021/browser-tests/vuong-acceptance/T04-two-diseases.png) |
| T05 | Đợt và lượt của hai bệnh nhân khác nhau<br>Ứng viên cuối: AC2 của W2BN2 tham chiếu AD1 của W2BN1 | Từ chối, rollback | {"luot_den_kham":0,"lan_kham_benh":0,"dot_dieu_tri":1} | Đạt local — ứng viên cuối | Browser HTTP + SQL (tự động; không phải kiểm tra tay) | Trợ lý Codex thay mặt Vương | 2026-10-21T12:13:20.728397+07:00 | f4869299c25fdfd0b711597e30b60ab277120f44 + [manifest124](evidence/vuong_week3_final_20261021/execution_source_sha256.json) | [JSON ca](evidence/vuong_week3_final_20261021/browser-tests/vuong-acceptance/cases.json) |
| T06 | Trùng (lượt,đợt) hoặc (đợt,STT)<br>Ứng viên cuối: Trùng (AC2,AD1), trùng (AD1,STT=1) | Từ chối | {"attempts":[{"kind":"duplicate_visit_episode","visit":"AC2","sequence":3,"date":"2001-09-29","mysql_code":1644},{"kind":"duplicate_episode_sequence","visit":"AC3","sequence":1,"date":"2001-09-30","mysql_code":1644}],"exam_count":2,"rejected_row":0} | Đạt local — ứng viên cuối | Browser setup + direct SQL (tự động; không phải kiểm tra tay) | Trợ lý Codex thay mặt Vương | 2026-10-21T12:13:23.108102+07:00 | f4869299c25fdfd0b711597e30b60ab277120f44 + [manifest124](evidence/vuong_week3_final_20261021/execution_source_sha256.json) | [JSON ca](evidence/vuong_week3_final_20261021/browser-tests/vuong-acceptance/cases.json) |
| T07 | Tạo đợt đang điều trị thứ hai cho cùng bệnh nhân/bệnh<br>Ứng viên cuối: Hai session CSRF độc lập cùng tạo đợt bệnh W2B1 cho W2BN1, bắt đầu bằng barrier | Từ chối, kể cả hai yêu cầu đồng thời | {"requests":[{"status":409,"started":9406.187,"finished":9406.281,"visit":"AC1"},{"status":303,"started":9406.187,"finished":9406.281,"visit":"AC2"}],"counts":{"luot_den_kham":1,"dot_dieu_tri":1,"lan_kham_benh":1}} | Đạt local — ứng viên cuối | Concurrent real HTTP + SQL (tự động; không phải kiểm tra tay) | Trợ lý Codex thay mặt Vương | 2026-10-21T12:13:24.579730+07:00 | f4869299c25fdfd0b711597e30b60ab277120f44 + [manifest124](evidence/vuong_week3_final_20261021/execution_source_sha256.json) | [JSON ca](evidence/vuong_week3_final_20261021/browser-tests/vuong-acceptance/cases.json) |
| T08 | Khỏi tháng 10, tái khám tháng 9<br>Ứng viên cuối: Tái khám 09/2001, khỏi 01/10/2001 | Thưởng bác sĩ tháng 10 đúng 1 triệu/đợt | {"2001-09":0,"2001-10":1000000} | Đạt local — ứng viên cuối | Browser tự động đối chiếu lương hai kỳ với expected cố định | Trợ lý Codex thay mặt Vương | 2026-10-21T12:13:15.394284+07:00 | f4869299c25fdfd0b711597e30b60ab277120f44 + [manifest124](evidence/vuong_week3_final_20261021/execution_source_sha256.json) | [JSON ca](evidence/vuong_week3_final_20261021/browser-tests/vuong-acceptance/cases.json); [ảnh](evidence/vuong_week3_final_20261021/browser-tests/vuong-acceptance/T08-cure-month.png) |
| T09 | Một y tá nhiều công việc cùng lượt<br>Ứng viên cuối: YT1 nhiều việc AC5, thêm YT2; YT1 còn hỗ trợ AC4 | Một khoản 200 nghìn; hai y tá thì mỗi người một khoản | {"pairs_ac5":2,"yt1_oct_bonus":400000,"yt2_oct_bonus":200000} | Đạt local — ứng viên cuối | Browser + SQL (tự động; không phải kiểm tra tay) | Trợ lý Codex thay mặt Vương | 2026-10-21T12:13:17.295455+07:00 | f4869299c25fdfd0b711597e30b60ab277120f44 + [manifest124](evidence/vuong_week3_final_20261021/execution_source_sha256.json) | [JSON ca](evidence/vuong_week3_final_20261021/browser-tests/vuong-acceptance/cases.json); [ảnh](evidence/vuong_week3_final_20261021/browser-tests/vuong-acceptance/T09-nurse-bonuses.png) |
| T10 | Khám không kê đơn<br>Ứng viên cuối: AK1 không kê đơn | Hợp lệ, tiền thuốc 0 | {"order":null,"medicine":"0"} | Đạt local — ứng viên cuối | HTTP JSON qua session browser tự động; dữ liệu MySQL thật | Trợ lý Codex thay mặt Vương | 2026-10-21T12:13:17.376939+07:00 | f4869299c25fdfd0b711597e30b60ab277120f44 + [manifest124](evidence/vuong_week3_final_20261021/execution_source_sha256.json) | [JSON ca](evidence/vuong_week3_final_20261021/browser-tests/vuong-acceptance/cases.json) |
| T11 | Một đơn nhiều thuốc, giá hiện tại thay đổi sau kê<br>Ứng viên cuối: AR1: 2×1.000+3×2.000; giá W2T1 đổi 9.999; AC5 có 2 y tá | Tổng tiền theo đơn giá đã lưu, tiền khám không nhân đôi | {"medicine":8000,"fees":250000,"total":258000} | Đạt local — ứng viên cuối | Browser + SQL (tự động; không phải kiểm tra tay) | Trợ lý Codex thay mặt Vương | 2026-10-21T12:13:18.285314+07:00 | f4869299c25fdfd0b711597e30b60ab277120f44 + [manifest124](evidence/vuong_week3_final_20261021/execution_source_sha256.json) | [JSON ca](evidence/vuong_week3_final_20261021/browser-tests/vuong-acceptance/cases.json); [ảnh](evidence/vuong_week3_final_20261021/browser-tests/vuong-acceptance/T11-historical-prices.png) |
| T12 | Số lượng 0/âm, tiền âm, ngày ra trước ngày vào<br>Ứng viên cuối: Số lượng 0/-1; tiền khám -1; ngày ra 01/10 trước ngày vào 02/10 | Từ chối với lỗi dễ hiểu | {"quantity":[{"input":"0","status":422,"header_count":0},{"input":"-1","status":422,"header_count":0}],"negative_fee":422,"visit_ac6":0,"invalid_close":422,"end_date":null} | Đạt local — ứng viên cuối | Browser + tampered HTTP + SQL (tự động; không phải kiểm tra tay) | Trợ lý Codex thay mặt Vương | 2026-10-21T12:13:18.816538+07:00 | f4869299c25fdfd0b711597e30b60ab277120f44 + [manifest124](evidence/vuong_week3_final_20261021/execution_source_sha256.json) | [JSON ca](evidence/vuong_week3_final_20261021/browser-tests/vuong-acceptance/cases.json); [ảnh](evidence/vuong_week3_final_20261021/browser-tests/vuong-acceptance/T12-invalid-close.png) |
| T13 | Lỗi giữa lúc tạo đơn và chi tiết<br>Ứng viên cuối: ARFAIL: W2T1 hợp lệ được ghi trước ZZMissing không tồn tại | Không tồn tại đơn dang dở sau rollback | {"http_status":404,"counts":{"don_thuoc":0,"chi_tiet_don_thuoc":0}} | Đạt local — ứng viên cuối | Browser HTTP + SQL (tự động; không phải kiểm tra tay) | Trợ lý Codex thay mặt Vương | 2026-10-21T12:13:26.238717+07:00 | f4869299c25fdfd0b711597e30b60ab277120f44 + [manifest124](evidence/vuong_week3_final_20261021/execution_source_sha256.json) | [JSON ca](evidence/vuong_week3_final_20261021/browser-tests/vuong-acceptance/cases.json); [ảnh](evidence/vuong_week3_final_20261021/browser-tests/vuong-acceptance/T13-no-partial-prescription.png) |
| T14 | Tháng không có phát sinh<br>Ứng viên cuối: Tháng 12/2000 không có dữ liệu khám | Không lỗi, tổng 0; lương cơ bản vẫn đúng | {"diseases":{"month":"2000-12","rows":[],"total":0},"total_revenue":0,"doctor":7000000,"nurse":5000000} | Đạt local — ứng viên cuối | Browser + JSON (tự động; không phải kiểm tra tay) | Trợ lý Codex thay mặt Vương | 2026-10-21T12:13:19.335873+07:00 | f4869299c25fdfd0b711597e30b60ab277120f44 + [manifest124](evidence/vuong_week3_final_20261021/execution_source_sha256.json) | [JSON ca](evidence/vuong_week3_final_20261021/browser-tests/vuong-acceptance/cases.json); [ảnh](evidence/vuong_week3_final_20261021/browser-tests/vuong-acceptance/T14-empty-month.png) |
| T15 | Xem hồ sơ<br>Ứng viên cuối: W2BN1, thêm month rỗng để kiểm tra toàn lịch sử | Đủ lịch sử và bệnh đang điều trị, STT hiện tại đúng | {"counts":{"visits":5,"treatments":3,"examinations":6,"medicines":2,"support":6,"current":2},"sequence_ad1":4,"fees":550000,"medicines":8000} | Đạt local — ứng viên cuối | Browser + JSON + SQL (tự động; không phải kiểm tra tay) | Trợ lý Codex thay mặt Vương | 2026-10-21T12:13:19.803286+07:00 | f4869299c25fdfd0b711597e30b60ab277120f44 + [manifest124](evidence/vuong_week3_final_20261021/execution_source_sha256.json) | [JSON ca](evidence/vuong_week3_final_20261021/browser-tests/vuong-acceptance/cases.json); [ảnh](evidence/vuong_week3_final_20261021/browser-tests/vuong-acceptance/T15-history-1440.png) |
| T16 | Import và chạy từ clone mới trên máy thứ hai | Chạy theo README, không phụ thuộc file riêng của máy tác giả | Chưa chạy | Không thực hiện theo quyết định nhóm 21/10/2026; không tính đạt | Clone mới trên thiết bị thứ hai + import/chạy theo tài liệu; thực tế chưa chạy | Chưa chạy | Chưa chạy | Chưa chạy | Chưa chạy |

**T01–T15 đạt local trên ứng viên cuối Bước 4; T16 không thực hiện theo quyết định nhóm, chưa chạy và không tính đạt.** SHA nền phải đi cùng [candidate/diff/manifest124](evidence/vuong_week3_final_20261021/candidate.json), vì source sửa chưa commit. Kết quả Bước2–3 chỉ còn là lịch sử; phiên cuối đã chạy lại HTTP/SQL/concurrency/rollback. [Sổ lỗi và retest](VUONG_WEEK3_ISSUES.md).

## 3. Quy ước ghi phiên kiểm thử

Mỗi lần chạy tạo thư mục mới trong `docs/evidence/`, ví dụ `vuong_week3_YYYYMMDD_HHMMSS/`, không ghi đè phiên trước. Nếu runner hiện hành tạo tên `vuong_week2_prepare_<timestamp>`, giữ nguyên thư mục đầu ra và dẫn liên kết chính xác trong chỉ mục phiên tuần 3; tên runner/thư mục không xác định kỳ nghiệm thu.

Dùng [SESSION_TEMPLATE.json](evidence/vuong_week3_setup_20261021_111405/SESSION_TEMPLATE.json) làm mẫu cho `session.json` của phiên mới. Chỉ điền từ giá trị thực tế; chưa có thì ghi `Chưa chạy`. Hồ sơ cần đủ:

1. ID phiên, giờ bắt đầu/kết thúc có `+07:00`, người trực tiếp thao tác (trợ lý thay mặt Vương hoặc thành viên thực sự chạy), local/CI và lệnh đã chạy.
2. Nhánh và `git rev-parse HEAD`; trạng thái source trước/sau chạy. Nếu có sửa chưa commit: ghi SHA nền + manifest SHA256 source thực thi + diff đã rà secrets và danh sách source untracked liên quan. Không chỉ ghi SHA nền rồi nhận là commit đó đã đạt.
3. Python: đường dẫn executable và phiên bản của đúng venv chạy runner. MySQL: executable và **SELECT VERSION() của server thử thực sự kết nối**, không chỉ phiên bản client. Chromium: executable và phiên bản browser thực sự khởi chạy; ghi phiên bản Playwright/dependencies liên quan.
4. Tên DB thử, cổng, cách cách ly, thứ tự import, audit trước/sau, kiểm tra dữ liệu nền; không có mật khẩu, token, khóa hoặc dữ liệu bệnh nhân thật. Không sao chép `.env` hoặc dump cá nhân vào bằng chứng.
5. Tổng test thu thập, pass/failure/error/skipped cùng nguyên nhân; đường dẫn JUnit/log/audit/ảnh và biên bản ca. Không cố định số lượng bằng 168 của tuần 2.
6. Mỗi ca có input cụ thể, expected độc lập, actual đo được, phương thức thực tế, thời điểm/người thực thi, định danh source và đường dẫn ảnh/log. Không có ảnh thì dẫn log phù hợp; thiếu bằng chứng thì ghi rõ.
7. Nếu source thay đổi trong phiên, chia phiên hoặc chạy lại phần bị ảnh hưởng. Không gán kết quả trước sửa cho source sau sửa. Đường dẫn bằng chứng phải tồn tại trước khi đánh dấu đạt.

Định danh source bao phủ ứng dụng, templates/static, test, runner, SQL, oracle và cấu hình liên quan; không chỉ hash Python hoặc chỉ ghi HEAD. Rà diff trước khi lưu, tránh xuất nguyên môi trường hoặc nội dung file bí mật. Không thu thập bằng chứng cũ vào phiên mới để thay kết quả chưa chạy.

| Phiên | Phạm vi | Ngày giờ | SHA | Python/MySQL/Chromium thực chạy | Kết quả | Bằng chứng |
|---|---|---|---|---|---|---|
| Chuẩn bị Bước 1 | Git và hồ sơ, không chạy test | Xem prepared_at trong preparation.json (UTC+07:00) | f4869299c25fdfd0b711597e30b60ab277120f44 | Chưa chạy; chưa xác minh runtime | Đã chuẩn bị | [Chỉ mục chuẩn bị](evidence/vuong_week3_setup_20261021_111405/README.md) |
| Hồi quy Bước 2 local | Suite tự động, DB/source cách ly | 2026-10-21T11:28:20.216758+07:00 → 2026-10-21T11:29:33.586131+07:00 | f4869299c25fdfd0b711597e30b60ab277120f44 | 3.11.9 / 8.4.7 / 156.0.8078.4 | 175 pass; 0 failure/error/skip | [Chỉ mục](evidence/vuong_week3_regression_20261021/README.md) |
| UI Bước 3 local | Tương tác cua_repl + SQL, DB thử mới | 2026-10-21T11:39:42+07:00 → 11:51:33+07:00 | f4869299c25fdfd0b711597e30b60ab277120f44 | Python3.11.9/MySQL8.4.7; IAB chưa xác minh phiên bản | 49 ghi nhận; 0 lỗi chặn; 1 quan sát UX P3 | [Chỉ mục UI](evidence/vuong_week3_ui_20261021/README.md) |
| Ứng viên cuối Bước4 | Full suite sau sửa UI | 2026-10-21T12:12:30.381436+07:00 → 2026-10-21T12:13:46.836673+07:00 | SHA nền f486929 + manifest124/candidate045a7c42 | Python3.11.9/MySQL8.4.7/Chromium156.0.8078.4 | 179 pass, 0 failure/error/skip; audit sạch | [Chỉ mục cuối](evidence/vuong_week3_final_20261021/README.md) |

## 4. Quyết định T16 và việc còn lại

T16 không thực hiện theo quyết định của Quyền và cả nhóm, do Vương thông báo ngày 21/10/2026. Không cần gửi đề nghị chốt máy, người phối hợp hoặc lịch trước 30/10. Không nhận ca này là đã kiểm thử đạt trên máy thứ hai.

| Việc | Người phụ trách | Trạng thái |
|---|---|---|
| T16 | Nhóm đã quyết định | Không thực hiện; actual chưa chạy; loại khỏi phạm vi bắt buộc |
| Sửa source cleanup runner W3-RUN-01 | Trung | Còn mở; đã có workaround và bằng chứng; độc lập với T16 |
| Kết quả T01–T15 và sửa UI W3-UX-01 | Trợ lý thay mặt Vương | Đã kiểm tra local trên ứng viên cuối; xem mục 8 |

Nội dung bàn giao hiện hành: [bản nháp cho Trung và thông tin cho Quyền](VUONG_WEEK3_STEP4_HANDOFF.md). Trợ lý chưa tự gửi ra ngoài.

## 5. Kiểm tra hoàn thành Bước 1

- [x] Kiểm tra branch, remote và thay đổi local; giữ nguyên bằng chứng tuần 2 untracked.
- [x] Fetch origin; xác nhận main cập nhật bằng fast-forward; tạo nhánh mới từ origin/main.
- [x] Tạo đủ T01–T16, trường input/expected/actual/trạng thái/phương thức/người/ngày giờ/SHA/bằng chứng.
- [x] Chuẩn bị mẫu ghi môi trường/source và cách lưu phiên mới; chưa nhận runtime hoặc ca kiểm thử nào đã chạy.
- [x] T16 ghi chờ nhóm; soạn tin nhắn và danh sách phụ thuộc rõ ràng.
- [x] Vương gửi tin nhắn nhóm.

**Tiêu chí chuẩn bị Bước 1 đạt:** có nhánh, hồ sơ và danh sách chờ; không dùng kết quả tuần 2 để đánh dấu đạt. Vương đã gửi tin nhắn; đến ngày 21/10/2026 đã thông báo quyết định nhóm bỏ T16 (xem mục 4). Bước 2 đã chạy đạt local; Bước 3 đã kiểm tra; Bước 4 có kết quả tại mục8.

## 6. Kết quả Bước 2 — hồi quy local 21/10/2026

**Đạt tiêu chí Bước 2:** 175 test được thu thập, 175 pass, 0 failure, 0 error, 0 skipped; pytest 55,74 giây. Đã đọc XML từng testcase và log, đối chiếu đủ 15 ID ca với đúng run_id `20261021_112820`, SHA thực chạy và file ảnh/log. Không cố định số lượng bằng 168 của tuần 2. [JUnit](evidence/vuong_week3_regression_20261021/runner-output/junit.xml), [log test](evidence/vuong_week3_regression_20261021/runner-output/pytest.txt), [review](evidence/vuong_week3_regression_20261021/review.json).

Runner nguyên bản chạy trên bản sao source 122 file tracked khớp byte để giữ nguyên test-artifacts cũ. Không có thay đổi source thực thi hoặc diff source chưa commit; tài liệu tuần 3 mới vẫn untracked. Dùng SHA cùng [manifest đầy đủ](evidence/vuong_week3_regression_20261021/execution_source_sha256.json), không chỉ manifest giới hạn runner sinh ra. `scope`/SHA phụ thuộc cũ trong results.json là nhãn hard-code, không phải source checkout thực tế.

Môi trường mới: Python 3.11.9/MySQL 8.4.7/Chromium 156.0.8078.4. Không khác dòng major/minor mục tiêu; phiên bản và executable thực tế trong [session.json](evidence/vuong_week3_regression_20261021/session.json), dependencies/nguồn tải trong [chỉ mục](evidence/vuong_week3_regression_20261021/README.md). DB mới thuộc instance/datadir riêng, không dùng .env hoặc DB cá nhân.

Audit: 11 bảng, 9 trigger, 1.144 dòng; matches_expected_counts=true; 9 nhóm findings rỗng; 10 tập audit SQL cuối rỗng. Hash nội dung seed từng bảng trước/sau suite và sau browser đều khớp. Import theo schema → seed → audit → constraints → audit → queries. [Kết quả chi tiết](evidence/vuong_week3_regression_20261021/runner-output/results.json).

Các module MySQL, browser và oracle Quyền đều chạy thực tế: test_quyen_database 26 ca, test_quyen_week2_reports 52 ca; có đối chiếu UI/JSON/SQL/oracle qua 5 tháng và 40 bệnh nhân. T05/T06/T07/T13 ghi đúng HTTP/SQL/concurrency/rollback; không nhận là kiểm tra tay. Khảo sát tự động 54 trang/viewport 1440/390/320 px không phát hiện tràn ngang toàn trang. Tại thời điểm chốt Bước 2 chưa xem ảnh bằng mắt/chưa làm Bước 3; phiên Bước 3 mới có kết quả tại mục 7.

Đã xử lý sự cố môi trường khởi động Playwright trong sandbox trước khi runner chạy; retry được cấp quyền và thành công. Runner để sót MySQL con sau khi kết thúc: đã xác minh executable/datadir, dừng riêng và chờ thoát; trạng thái cuối 0 tiến trình MySQL/browser riêng, app/DB đều đóng cổng theo [cleanup.json](evidence/vuong_week3_regression_20261021/cleanup.json). Đề nghị Bước 4 xem xét cải thiện cleanup cây tiến trình trên Windows; chưa sửa runner. Không còn failure/error/skip sản phẩm trong suite này, không khẳng định hết lỗi ngoài phạm vi suite.

Hash xác nhận .env, test-artifacts cũ và 58 file bằng chứng tuần 2 được giữ nguyên. Không commit/push, chưa chạy/xác minh CI. T16 vẫn “Chờ nhóm chốt máy thứ hai”; kết quả local không thay T16. **Bước 3 được cập nhật riêng tại mục 7; Bước 4 được cập nhật tại mục8.**

## 7. Kết quả Bước 3 — tương tác trình duyệt 21/10/2026

*Mốc lịch sử trước sửa UI; trạng thái lỗi và ứng viên cuối hiện hành xem mục8/sổ lỗi.*

**Đã kiểm tra đủ CRUD, luồng khám, bốn báo cáo, ca biên và trải nghiệm UI trên DB thử mới. Không phát hiện lỗi chặn luồng, sai tiền/báo cáo hoặc tràn ngang toàn trang trong phạm vi đã chạy.** Có quan sát UX P3 về thông báo native tiếng Anh, chưa sửa. Chưa chuyển Bước 4.

Người trực tiếp thao tác: **trợ lý Codex thay mặt Vương** qua `cua_repl` trên Codex in-app browser (IAB), không phải Vương tự thao tác. Python3.11.9/MySQL8.4.7; **phiên bản IAB chưa xác minh do API không cung cấp**, không lấy Chromium156 của runner để thay thế. Thời gian/source/datadir ở [session.json](evidence/vuong_week3_ui_20261021/session.json), [manifest122 file](evidence/vuong_week3_ui_20261021/execution_source_sha256.json).

[Chỉ mục đầy đủ](evidence/vuong_week3_ui_20261021/README.md) · [49 ghi nhận input/expected/actual, người/ngày/SHA](evidence/vuong_week3_ui_20261021/ui-observations.json) · [bảng đối chiếu ca/phương thức](evidence/vuong_week3_ui_20261021/coverage-matrix.csv) · [expected tính độc lập](evidence/vuong_week3_ui_20261021/expected.json) · [review](evidence/vuong_week3_ui_20261021/review.json).

| ID | Bổ sung tương tác và actual Bước 3 | Phương thức / bằng chứng |
|---|---|---|
| T01 | U3D1 ba lần 28/29/30-09-2001, STT1–3; Q1 tháng9 một đợt | UI + SQL; [ảnh](evidence/vuong_week3_ui_20261021/07-third-visit.jpg) |
| T02 | Khỏi U3D1 rồi tái mắc U3D2; Q1 tháng10 U3B1=2 | UI + SQL; [Q1](evidence/vuong_week3_ui_20261021/15-custom-diseases.jpg) |
| T03 | U3D1 khám thêm01/10, giữ STT4; hai kỳ đều tính đợt có khám | UI lọc tháng + SQL; [SQL tháng9](evidence/vuong_week3_ui_20261021/sql-reports-2001-09.json), [tháng10](evidence/vuong_week3_ui_20261021/sql-reports-2001-10.json) |
| T04 | U3L5 gồm U3D2/U3D3 của cùng bệnh nhân, phí150.000 | UI + SQL; [ảnh](evidence/vuong_week3_ui_20261021/08-two-diseases.jpg) |
| T05 | Không chạy mới bằng UI; đã đạt HTTP sửa payload + SQL ở Bước2 cùng SHA | Giữ bằng chứng chuyên biệt ở bảng mục2; không gọi là thao tác tay mới |
| T06 | Không chạy mới bằng UI; đã đạt direct SQL kiểm tra hai kiểu trùng độc lập ở Bước2 cùng SHA | Giữ bằng chứng chuyên biệt ở bảng mục2 |
| T07 | UI từ chối đợt đang điều trị thứ hai; không lưu U3L6/U3D4/U3K7 | [Ảnh](evidence/vuong_week3_ui_20261021/25-active-episode-rejected.jpg), [SQL](evidence/vuong_week3_ui_20261021/sql-rejected-active-episode.json); concurrency vẫn là phiên chuyên biệt Bước2 |
| T08 | U3BS tháng9=7tr, tháng10=8tr, thưởng chỉ tháng khỏi | UI/Q2 + SQL; [ảnh](evidence/vuong_week3_ui_20261021/16-custom-salaries.jpg) |
| T09 | U3YT1 nhiều việc vẫn một dòng/lượt; tháng10YT1=5,4tr/YT2=5,2tr | UI hỗ trợ/Q2 + SQL; không nhân thưởng theo số việc |
| T10 | U3K1 không đơn vẫn hợp lệ, thuốc0; Q4 tháng9 thuốc0 | UI/Q3/Q4 + [SQL](evidence/vuong_week3_ui_20261021/sql-crud-and-no-order.json) |
| T11 | U3RX1 hai thuốc tổng8.000; đổi riêng giá U3T1 lên9.999 vẫn giữ giá cũ; khám250.000/thuốc8.000/tổng258.000 tháng10 | UI + SQL đổi giá fixture/đối chiếu; [đơn](evidence/vuong_week3_ui_20261021/10-historical-price.jpg), [Q4](evidence/vuong_week3_ui_20261021/17-custom-revenue.jpg) |
| T12 | UI chặn số lượng0/-1, phí-1 bằng native validation; server từ chối ngày ra trước ngày vào và giữ dữ liệu | [Ảnh](evidence/vuong_week3_ui_20261021/11-invalid-close.jpg); server nhận payload âm vẫn theo kiểm thử chuyên biệt Bước2, không suy ra từ native validation |
| T13 | Không có phiên mới Bước3; HTTP/SQL rollback đơn dang dở đã đạt Bước2 cùng SHA | Giữ bằng chứng chuyên biệt ở bảng mục2, không gọi là thao tác tay |
| T14 | Q1/Q4 kỳ2000-12 tổng0; Q2 vẫn lương cơ bản | UI + [SQL](evidence/vuong_week3_ui_20261021/sql-reports-2000-12.json) |
| T15 | 5 lượt/3 đợt/6 khám/2 dòng thuốc/6 hỗ trợ; 2 đợt đang điều trị; U3D1 đã khỏi/STT4 | UI + SQL; [lịch sử](evidence/vuong_week3_ui_20261021/18-custom-history.jpg) |
| T16 | Chưa chạy | **Chờ nhóm chốt máy thứ hai** |

CRUD mới bổ sung đủ thêm/xem/sửa/reload/xóa ở bệnh nhân/bác sĩ/y tá; mã trùng và dữ liệu sai bị từ chối; đã có lịch sử thì xóa U3BN1/U3BS/U3YT1 đều bị chặn. Không sửa/xóa seed hoặc hồ sơ thật. Input dùng bộ mã giả U3, tách khỏi bộ W2 của Bước2.

Đã lọc báo cáo seed tháng10/2026 và đối chiếu đáp án Quyền: Q1=24, doanh thu10.500.800. Q2 sau thêm nhân viên U3 phải cộng lương cơ bản: BS85.000.000/y tá75.600.000; phép tính có trong expected.json. Các kỳ2001 dùng expected tự tính từ input U3; SQL chạy nguyên queries.sql và lưu11 tập/kỳ để đối chiếu độc lập.

UI/bàn phím: Enter thêm/xóa dòng thuốc giữ dữ liệu, focus sang dòng mới; ArrowRight cuộn bảng lịch sử tại320px (scrollLeft0→24,233). Hủy/đường quay lại/menu hoạt động, lỗi lọc sai mã có thể sửa và tiếp tục. 16 nhóm URL ×1440/390/320px và1 lần bàn phím =49 phép đo, **0 tràn ngang toàn trang**; bảng rộng cuộn riêng. [Responsive](evidence/vuong_week3_ui_20261021/responsive.json), [bàn phím](evidence/vuong_week3_ui_20261021/keyboard.json). Đã xem33/52 ảnh theo [danh sách](evidence/vuong_week3_ui_20261021/visual-review.json), không nhận đã rà bằng mắt mọi ảnh.

**W3-UX-01/P3:** native tooltip của ô số (thâm niên/phí âm, số lượng0/âm) hiện tiếng Anh trong IAB; dữ liệu sai vẫn bị chặn, thông báo nghiệp vụ/server của app vẫn tiếng Việt. [Ghi nhận, tái hiện và expected/actual](evidence/vuong_week3_ui_20261021/findings.json). Chưa sửa/chưa kiểm thử lại; để Bước4 xem xét, không tự đóng lỗi.

Audit sau còn31 dòng U3 chủ đích:1.175 dòng; matches_expected_counts=false là dự kiến khi fixture còn trong DB riêng. Cả9 nhóm findings rỗng, toàn bộ1.144 dòng seed của11 bảng giữ nguyên theo so sánh nội dung. [Audit](evidence/vuong_week3_ui_20261021/audit-after.json). Source/.env giữ nguyên; app/MySQL private đã shutdown, cổng đóng và tab kiểm thử đóng. [Cleanup](evidence/vuong_week3_ui_20261021/cleanup.json).

Chưa xác minh phiên bản IAB; chưa thử thiết bị di động thật/screen reader, CI hoặc T16. T05/T06/T13 và concurrencyT07 không có phiên mới Bước3 nhưng có bằng chứng chuyên biệt Bước2 cùng SHA. Không dùng clone/DB khác trên cùng máy để thay T16. Không sửa source sản phẩm, chưa commit/push. **Mốc lịch sử Bước3: chưa sửa; kết quả sửa/kiểm tra lại xem mục8.**

## 8. Kết quả Bước 4 — bản ứng viên cuối

**Đạt tiêu chí local Bước4:** W3-UX-01 đã sửa và kiểm tra lại; toàn suite **179 pass / 0 failure / 0 error / 0 skipped**,59,78giây. Không có lỗi chặn demo/sai nghiệp vụ còn được chứng minh trong phạm vi kiểm thử. **W3-RUN-01 còn mở cho Trung** về cleanup công cụ; workaround dừng đúng instance đã được kiểm tra lại, không nhận source runner đã sửa.

[Sổ lỗi đủ tái hiện/expected/actual/người phụ trách/trạng thái](VUONG_WEEK3_ISSUES.md) · [bản nháp bàn giao từng người, chưa gửi](VUONG_WEEK3_STEP4_HANDOFF.md) · [chỉ mục chứng cứ cuối](evidence/vuong_week3_final_20261021/README.md).

Bản kiểm thử cuối **chưa commit**: SHA nền `f4869299c25fdfd0b711597e30b60ab277120f44` + candidate `sha256:045a7c42b12390bc5a1cb911a1ec648215cf66df679b6576a7b22464bb398894`, [diff](evidence/vuong_week3_final_20261021/source.diff) và [manifest124](evidence/vuong_week3_final_20261021/execution_source_sha256.json). Không gán kết quả cho riêng SHA nền. Source không thay đổi trong/sau suite; các chỉnh sửa hồ sơ sau đó không thuộc source thực thi.

UI sửa trong `clinic_app/static/number-validation.js` và base template UI; giữ nguyên native min/max/step và validation server. Event delegation áp dụng dòng thuốc mới, sửa số hợp lệ xóa custom error. Không thay backend/API/schema/công thức. Bốn test mới có ý nghĩa hồi quy: trình duyệt en-US, số âm/0/vượt max/số lẻ, không POST khi sai, giữ input, phục hồi đúng và số lượng trống tùy chọn. [Actual retest4nhóm](evidence/vuong_week3_final_20261021/browser-tests/vuong-week3/quantity.json); [IAB trực tiếp/ảnh tiếng Việt](evidence/vuong_week3_step4_retest_20261021/doctor-vietnamese.jpg). Không nhận enhancement chạy khi JavaScript tắt; phiên bản IAB vẫn chưa xác minh.

Full suite sau sửa chạy mới trên Python3.11.9/MySQL8.4.7/Chromium156.0.8078.4, MySQL/browser/oracle Quyền đều bật. [JUnit](evidence/vuong_week3_final_20261021/runner-output/junit.xml), [log từng test](evidence/vuong_week3_final_20261021/runner-output/pytest.txt), [review](evidence/vuong_week3_final_20261021/review.json). T01–T15 ở bảng mục2 được cập nhật từ đúng run_id `20261021_121231`, gồm kiểm thử chuyên biệt HTTP/SQL/concurrency/rollback; không lấy kết quả source cũ để chốt bản sửa.

Audit cuối:11bảng/9trigger/1.144dòng, matches_expected_counts=true,9nhóm findings rỗng,10tập SQL audit rỗng. Hash nội dung seed trước/sau suite và khảo sát browser khớp; [kết quả](evidence/vuong_week3_final_20261021/runner-output/results.json). App/MySQL retest/full-suite và browser test đều đã dừng, cổng đóng theo [cleanup](evidence/vuong_week3_final_20261021/cleanup.json). Bằng chứng cũ và test-artifacts/.env không bị thay đổi.

Chưa chạy/xác minh CI. T16 **không thực hiện theo quyết định nhóm 21/10/2026**; chưa chạy và không tính đạt, không còn phụ thuộc máy thứ hai. Đã rà diff và file mới để loại secrets/.env/venv/cache/datadir/dump khỏi danh sách bàn giao. Không stage bằng chứng tuần2 untracked, không commit/push/PR/merge hoặc làm Bước5–7. Việc còn lại của người dùng: chuyển nội dung nháp cho Trung/Quyền khi phù hợp; không cần tự chạy lại các lệnh local đã có bằng chứng.

## 9. Kết quả Bước 5 — hướng dẫn hiện hành

Ngày21/10/2026: **đạt tiêu chí Bước5 trên main đã xác minh/ứng viên hiện có**, chi tiết và giới hạn trong [biên bản đối chiếu](VUONG_WEEK3_STEP5_VERIFICATION.md). [SETUP](SETUP.md) đã bỏ điểm bắt đầu tuần1, [USER_GUIDE](USER_GUIDE.md) hướng dẫn bản tích hợp; tài liệu tuần2 giữ nhãn lịch sử. Main remote xác minh `f4869299c25fdfd0b711597e30b60ab277120f44`; candidate bước4 có sửa chưa commit, không nhận main chứa bản sửa đó.

[Phiên setup mới](evidence/vuong_week3_step5_20261021/setup-results.json): 66file thực thi/config/dependencies khớp bước4; import đúng6bước trên DB mới,11bảng/9trigger/1.144dòng, audit sạch; audit/app đọc .env riêng,11route HTTP200; cleanup cổng/app/MySQL hoàn tất và .env/bằng chứng cũ giữ nguyên. Đây là smoke cài/chạy mới, không nhận HTTP200 thay toàn suite. Kết quả nghiệp vụ/CRUD/bốn báo cáo vẫn truy về suite179/179 đúng candidate bước4; cài dependencies từ mạng, Workbench GUI/Docker chưa chạy mới và được ghi rõ.

W3-RUN-01 còn mở, SETUP ghi workaround; không thay source runner. T16 không thực hiện theo quyết định nhóm21/10/2026, actual chưa chạy, không tính PASS/việc chờ. Các câu “chưa làm Bước5” hoặc “chờ máy thứ hai” trong mốc cũ là lịch sử, nhường trạng thái hiện hành cho mục này và quyết định nhóm. Chưa commit/push/PR/merge/triển khai hoặc làm bước6–7.

## 10. Bước 6 — chuẩn bị và diễn tập kỹ thuật, chưa tập chung

Ngày 21/10/2026 đã chuẩn bị [kịch bản demo 13 phút](VUONG_WEEK3_DEMO.md), bộ mã giả DM6, expected theo từng nền dữ liệu, phân vai đề xuất, lời dẫn, câu hỏi và checklist tập chung. [Công cụ demo riêng](../tools/vuong_week3_demo.py) tạo instance/datadir mới mỗi lần; có chế độ seed cho nhóm và rehearsal tự động. Không sửa source ứng dụng hoặc runner tuần 2.

Hai phiên Chromium mới chạy trọn kịch bản trên hai datadir khác nhau, lần lượt 10,421 và 10,327 giây thao tác tự động; chưa gồm lời nói của nhóm. UI/JSON/SQL/expected khớp, seed tháng 10/2026 giữ nguyên; dữ liệu demo năm 2004 thêm 18 dòng hợp lệ. [Phiên chính và 24 ảnh đã xem lại](evidence/vuong_week3_demo_20261021_125437_817175/README.md). Chế độ --serve đã được mở/dừng bằng Ctrl+C trên datadir khác và cleanup đạt. W3-RUN-01 cũ vẫn mở; đây không phải sửa source runner đó hoặc chạy lại full suite 179 test.

**Chưa hoàn tất toàn bộ Bước 6:** nhóm cần xác nhận phân vai, tập cùng nhau ít nhất một lần, bấm giờ có lời nói/chuyển phần, ghi vướng mắc và kiểm tra lại phần sửa. Không nhận Vương/Trung/Quyền đã tham gia; không gửi tin nhắn, commit/push/PR/merge. T16 không thuộc phạm vi.
