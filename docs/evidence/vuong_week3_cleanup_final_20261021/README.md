# Cleanup PR #13 — bằng chứng mới 21/10/2026

Source thực chạy: HEAD nền `0a8aeccf5ad7c88e4902ae66d6378ef3b5ffcd5b` cộng thay đổi chưa commit, xác định byte bằng [source-manifest.json](source-manifest.json). Không gán kết quả này cho riêng SHA nền hoặc gọi đây là full suite 179 test. Source đã chuẩn hóa LF theo .gitattributes; trước commit đối chiếu blob staged với manifest. CI trên head mới được ghi riêng trong PR.

Helper `tools/private_mysql_cleanup.py` lấy nguyên byte từ Trung/PR #12 head `d566abf5545d5c5f77caaea7deeab42fddb7f5b5`, hash `5ed56ad196c171c6dd2e2fe71f90611dc934617d1ed17e920fa6c8da963fc417`; thêm dependency dev `psutil>=6,<8` (local 7.2.2). Không merge nhánh Trung, không lấy runner/backend của PR #12. Demo luôn thử app/MySQL/log/check rồi ghi session, giữ lỗi workload gốc; chỉ lưu type exception.

## Kiểm tra mới

- [16 unit test PASS, 0 skipped](pytest.txt), [JUnit](junit.xml): SHUTDOWN lỗi, close lỗi, launcher wait timeout, lỗi app/log/helper/check, giữ failure/workload/success trung thực, không ghi thông báo chứa secret, từ chối SHUTDOWN khi identity khác và process cần đúng cả executable lẫn datadir. Wait timeout chưa dừng launcher phải success=false và vẫn có session/log closed. Đây là mock cho các syscall lỗi, không nhận đã buộc kernel gây wait timeout.
- [Rehearsal đầy đủ](../vuong_week3_demo_20261021_222527_475063/session.json), [log](rehearsal.txt), [kết quả](rehearsal-result.json): Windows/Python 3.11.9/MySQL 8.4.7/Chromium, thao tác tự động 10,753 giây, exit 0, workload/success=true, shutdown_requested=true, không fallback/errors, remaining_pids=[], launcher thoát, cổng app/DB đóng, thread dừng, log đóng. CRUD/tiếp nhận/tái khám/y tá/đơn/đóng lượt/khỏi/tái mắc/bốn báo cáo/ca sai chạy lại; [audit sau](../vuong_week3_demo_20261021_222527_475063/audit-after.json), [parity](../vuong_week3_demo_20261021_222527_475063/report-parity.json). Seed giữ nguyên, findings rỗng. Không nhận là tập nhóm, T16 hoặc rà lại toàn bộ ảnh.
- [Smoke success](../vuong_week3_demo_20261021_222446_280961/session.json): startup MySQL private mới, SHUTDOWN đạt, exit 0; [log](smoke-success.txt).
- [Smoke lỗi](../vuong_week3_demo_20261021_222453_269113/session.json): chủ động đóng connection và ném RuntimeError sau startup; exit 1 đúng dự kiến, success/workload_success=false, failure.type=RuntimeError, cleanup.success=true; fallback chỉ hai PID riêng 25212/25444, remaining_pids=[], launcher thoát/cổng đóng/log đóng/session có finished_at. Lỗi phục hồi InterfaceError/Error được giữ, không che lỗi workload; [log](smoke-error.txt).
- [Smoke harness/results](smoke.py), [actual](smoke-results.json): chạy bằng `.venv/week3-runtime/Scripts/python.exe docs/evidence/vuong_week3_cleanup_final_20261021/smoke.py`. Inventory mysqld trước/sau đều rỗng. Không dừng service/process theo tên chung, không kết nối MySQL hệ thống. DB demo/cổng/datadir riêng trong mỗi session, không xóa datadir.
- Compileall app/clinic_app/tools/tests, parse 21 template và git diff --check đạt; [kiểm tra source/helper/bằng chứng cũ](verification.json). `.env`, source và các thư mục evidence có trước mỗi phiên đều không đổi theo session; kiểm tra riêng toàn bộ evidence tracked cũ đối chiếu HEAD. Thư mục tuần 2 untracked của người dùng giữ ngoài commit.

## Bằng chứng các lần chuẩn bị

[Thử trước chuẩn hóa LF](../vuong_week3_cleanup_review_20261021/README.md) giữ riêng hash/kết quả thực chạy, không dùng hash của lần đó thay source LF cuối. Lần đầu lúc 22:21:38 dừng ở guard source vì requirements-dev thay đổi để thêm psutil, trước khi mở MySQL; thư mục tạo rỗng, chưa có session, không tính rehearsal đạt. Đã điều chỉnh guard chỉ cho phép dev dependency được thay chủ động; toàn bộ hash ứng dụng/SQL/browser từ candidate cũ vẫn phải khớp. Chưa khởi tạo DB ở lần guard lỗi.

## Còn chờ

Trung re-review head mới và quyết định thread cleanup của mình. Quyền nghiệm thu bản cuối/T01–T15 trên laptop Quyền và điều phối merge. W3-RUN-01 vẫn mở: runner tuần 2 trên PR #13 không đổi; bằng chứng helper/demo không đủ để tự đóng lỗi runner. T16 không thực hiện theo quyết định nhóm, không ghi PASS. Không approve/dismiss/resolve thay Trung, merge hoặc release/tag.
