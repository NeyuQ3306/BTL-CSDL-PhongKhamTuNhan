# Ứng viên cuối Bước 4 — 21/10/2026

**179 passed / 0 failure / 0 error / 0 skipped, 59,78 giây.** Đã chạy toàn bộ suite bắt buộc sau sửa UI, gồm MySQL, Chromium và oracle Quyền; không chỉ chạy ca lỗi. Người chạy: trợ lý Codex thay mặt Vương. Đây là local, chưa phải CI/review/merge/T16.

## Định danh source và thay đổi

- Nhánh `vuong/week-3`; SHA nền `f4869299c25fdfd0b711597e30b60ab277120f44` **cộng thay đổi chưa commit**. Không nhận commit nền tự chứa bản sửa.
- Candidate: `sha256:045a7c42b12390bc5a1cb911a1ec648215cf66df679b6576a7b22464bb398894`, tính từ manifest source canonical JSON.
- [candidate.json](candidate.json), [manifest 124 file](execution_source_sha256.json), [source.diff](source.diff) bao gồm cả hai file source mới chưa được Git theo dõi.
- Sửa UI: thêm `clinic_app/static/number-validation.js` và nạp trong `clinic_app/templates/week1/base.html`. Script bắt invalid/input/change cho ô số, dùng thông báo tiếng Việt và xóa custom error khi sửa. Không đổi min/max/step, không tắt validation, không đổi backend/API/schema/công thức. Delegation áp dụng cho dòng thuốc tạo động.
- Thêm `tests/test_vuong_week3_numeric_validation.py`: bốn ca doctor/nurse/fee/quantity trên **Chromium locale en-US**; kiểm tra âm/0/vượt max/số lẻ, không có POST khi sai, giữ input, sửa hợp lệ hết lỗi, dòng thuốc động và ô số lượng trống tùy chọn.
- Runtime: Python **3.11.9**, MySQL Server **8.4.7**, Chromium **156.0.8078.4**; executable và dependency của phiên có trong [session.json](session.json), [dependencies.txt](dependencies.txt).

## Bằng chứng

| Bằng chứng | Nội dung |
|---|---|
| [session.json](session.json) | Giờ chạy, lệnh, executable, SHA nền/source_dirty=true, kết quả bảo toàn source/file |
| [runner-output/junit.xml](runner-output/junit.xml) | 179 testcase thực chạy, không failure/error/skip |
| [runner-output/pytest.txt](runner-output/pytest.txt) | Tên từng testcase và kết quả cuối |
| [runner-console.txt](runner-console.txt) | Stdout/stderr runner của đúng phiên |
| [runner-output/results.json](runner-output/results.json) | Import/audit, phiên bản thực chạy, kiểm tra seed, 54 trang/viewport |
| [review.json](review.json) | Rà XML, ca lỗi mới, T01–T15, audit và trạng thái cleanup |
| [acceptance-matrix.csv](acceptance-matrix.csv) | T01–T15 cập nhật đúng actual/người/ngày/source cuối |
| [browser-tests/vuong-acceptance/cases.json](browser-tests/vuong-acceptance/cases.json) | Input/expected/actual mới, run_id `20261021_121231`; HTTP/SQL/concurrency/rollback được ghi đúng phương thức |
| [doctor.json](browser-tests/vuong-week3/doctor.json), [nurse.json](browser-tests/vuong-week3/nurse.json) | Retest thâm niên âm, vượt100, số lẻ và phục hồi |
| [fee.json](browser-tests/vuong-week3/fee.json), [quantity.json](browser-tests/vuong-week3/quantity.json) | Retest tiền/số lượng, giới hạn, dòng thêm động và ô tùy chọn |
| [IAB retest](../vuong_week3_step4_retest_20261021/interactive-retest.json), [ảnh tooltip tiếng Việt](../vuong_week3_step4_retest_20261021/doctor-vietnamese.jpg) | Trợ lý trực tiếp thao tác IAB, thấy thông báo tiếng Việt và hết custom error khi sửa về5; đã xem ảnh này |
| [cleanup.json](cleanup.json) | Đóng cổng của cả retest và full suite, không còn tiến trình MySQL/browser riêng |
| [final-verification.json](final-verification.json) | Rà source sau chạy, giữ bằng chứng cũ, link và diff/hồ sơ bàn giao |

Runner nguyên bản chạy trên bản sao source khớp byte `.venv/week3-final-20261021/source`, DB/datadir mới; không copy `.env`. Tên runner/DB và trường scope/dependency SHA cũ trong JSON là nhãn lịch sử hard-code, không phải checkout các SHA phụ thuộc cũ. Source thực thi phải tra candidate/manifest của phiên này.

## Audit và kiểm thử lại

Import schema → seed → audit → constraints → audit → queries. Audit cuối: **11 bảng, 9 trigger, 1.144 dòng**, matches_expected_counts=true; cả9 nhóm findings rỗng, cả10 tập audit SQL cuối rỗng. SHA256 nội dung từng bảng seed trước/sau suite và sau browser khớp. Source124 file, `.env`, test-artifacts gốc và hồ sơ Bước1–3/bằng chứng tuần2 untracked được giữ nguyên; kết quả kiểm tra có trong session/review.

T01–T15 được chạy lại đầy đủ trên source cuối, không gán kết quả cũ cho bản sửa. Bốn ca mới đều đạt; native constraints vẫn chặn dữ liệu sai trong trình duyệt en-US, thông báo chuyển tiếng Việt; thay số hợp lệ không còn custom error. Ca server nhận payload sai/rollback vẫn chạy trong suite cũ. Không thay thế test server bằng việc browser đã chặn POST.

Kiểm tra IAB trực tiếp trên DB mới xác nhận -1/101/1.5 lần lượt báo tiếng Việt; sửa5 → valid=true/customError=false/message rỗng, giữ tên/địa chỉ. Phiên bản IAB vẫn chưa xác minh do API không cung cấp; không nhận IAB là Chromium156 của suite. JS tắt vẫn dùng validation native theo ngôn ngữ browser; không nhận phần enhancement chạy khi JS tắt.

## Lỗi còn lại và bàn giao

- **W3-UX-01: đã sửa và đã kiểm tra lại**, có ảnh IAB, bốn ca regression và suite179/179; chưa commit hoặc qua review nhóm.
- **W3-RUN-01: chờ Trung xử lý source runner.** Tái hiện ở phiên cuối: runner exit0 nhưng MySQL con PID13296, cổng57136 còn sau parent. Đã kiểm tra đúng executable/datadir, dừng riêng child, chờ thoát và xác nhận cổng đóng. Đây là workaround cho phiên, không nhận source runner đã sửa. Không có MySQL hệ thống bị tác động.
- **W3-ENV-01: đã xử lý và kiểm tra lại** qua quyền thực thi phù hợp; không có lỗi setup mới ở phiên cuối.
- Không có lỗi backend/SQL/sai tiền/chặn demo đã được chứng minh còn mở trong phạm vi suite. Không kết luận mọi lỗi ngoài suite đều hết.

[Sổ lỗi](../../VUONG_WEEK3_ISSUES.md) · [bản nháp bàn giao cho từng người](../../VUONG_WEEK3_STEP4_HANDOFF.md) · [hồ sơ nghiệm thu](../../VUONG_WEEK3_ACCEPTANCE.md).

Tiêu chí local Bước4 đạt: không còn lỗi chặn demo/sai nghiệp vụ trong các ca đã chạy; lỗi công cụ còn lại được ghi người phụ trách và workaround. **T16 vẫn “Chờ nhóm chốt máy thứ hai”**. Chưa gửi tin nhắn, push, PR, merge hoặc làm Bước5–7.

## Tái hiện phiên

```powershell
& '.venv/week3-runtime/Scripts/python.exe' 'docs/evidence/vuong_week3_final_20261021/run_final.py'
```

Script đã dùng được giữ trong [run_final.py](run_final.py); lệnh runner chính xác trong session.json. Muốn chạy phiên mới phải dùng thư mục evidence/WORK mới, không chạy đè phiên này; script chặn mirror đã tồn tại. Runner vẫn cần kiểm tra/dọn process riêng trên Windows theo W3-RUN-01. Venv, datadir và gói runtime không thuộc bộ file bàn giao.
