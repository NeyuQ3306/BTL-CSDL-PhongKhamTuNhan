# Gói review UI R01–R07 của Vương — 06/11/2026

## Tiêu đề PR dự kiến

feat(vuong): complete desktop analytics R01–R07 with real MySQL verification

## Nội dung PR dự kiến

Tham chiếu #3. Bổ sung bộ lọc, bảng và biểu đồ offline R01–R07 trên `/reports`. Mỗi bảng/biểu đồ dùng cùng response; adapter đổi ngày cuối bao gồm sang `end` không bao gồm đúng một lần. R06 dùng ngày đối chiếu/ngưỡng riêng. Giữ đơn vị đếm, nhóm backend R05/R06 và chuỗi tiền/NULL R07.

Phạm vi diff so với `origin/main` a0d6c300: templates/static, các bộ kiểm UI và bằng chứng phần Vương. Không thay công thức SQL/backend/schema/seed, requirements/workflow hoặc tài liệu tích hợp chung. Bộ kiểm mới chạy xuyên MySQL thật → Flask API → bảng/SVG ở desktop; bộ kiểm stub cũ vẫn được ghi riêng.

Source sản phẩm: 596b38b8508fa79e5bc27d1e1e8a1c86f5cb7d5b trên `feat/vuong-analytics-ui`; phần bổ sung kiểm thử/bằng chứng được đóng gói trong commit review hiện tại. Xem `prepublish/source-sha256.json` để xác định file kiểm thử mới sau khi sửa guard CI; manifest ở thư mục gốc giữ bằng chứng lượt đầu. Không suy ra CI của commit cũ đã kiểm phần chưa commit.

### Cách tái lập an toàn

Từ thư mục gốc repo, dùng runtime có pytest/PyMySQL/Playwright/psutil và Chromium đã cài:

```powershell
& .venv\Scripts\python.exe docs/evidence/vuong_mysql_review_20261106/run_private.py
```

Runner dùng MySQL Server 8.0 cài tại `C:/Program Files/MySQL/MySQL Server 8.0/bin/mysqld.exe`; tạo datadir/cổng loopback mới, DB `clinic_vuong_analytics_test`, mật khẩu ngẫu nhiên chỉ trong bộ nhớ. Không lấy mật khẩu `.env`, không kết nối service MySQL đang dùng, không ghi DB chung. Runner dừng đúng instance của mình khi xong; giữ log private cục bộ trong `.venv/`. Cần thay đường dẫn mysqld/cache trình duyệt nếu môi trường khác.

### Kiểm chứng và giới hạn

Kết quả thực chạy, số ca và SHA nằm trong `README.md`, `results.json`, các JUnit và expected/actual của thư mục bằng chứng này. Chỉ desktop. Các bài cũ có kiểm điện thoại được loại rõ trong `results.json`, không tính PASS.

MySQL local 8.0.46/Python 3.14.6 khác môi trường MySQL 8.4.11/Python 3.11.9 ở phiên lỗi Windows cũ của Quyền. W3-DB-01 chưa đóng; kết quả local không thay nghiệm thu laptop Quyền. Chưa nghiệm thu nhóm, hoàn tất DOCX/PPTX/demo hoặc đóng #3.

### Người review và bước tích hợp

- Trung: kiểm endpoint/bộ lọc, response chung bảng/chart, nhóm R05/R06, ngày và chuỗi tiền/NULL; đọc bằng chứng SQL/API/oracle.
- Quyền: kiểm phạm vi SQL không đổi, bằng chứng seed, chạy bản tích hợp desktop trên laptop Quyền; theo dõi W3-DB-01 và điều phối merge.

Người dùng đã cho phép commit/push/tạo PR và yêu cầu Trung/Quyền review. Phạm vi stage chỉ file test mới và thư mục bằng chứng này; các thư mục QA cũ ngoài phạm vi không đưa vào. Sau publish: kiểm CI đúng SHA head, đợi review độc lập, xử lý nhận xét rồi Quyền điều phối squash merge theo RULES. Không tự đóng #3 bằng PR chỉ bao phủ UI.

## Mẫu cập nhật tiến độ để Vương gửi thủ công

Đã hoàn thành kiểm MySQL local và chuẩn bị hồ sơ review UI R01–R07 theo kết quả kèm bằng chứng. Tiếp theo: Trung review API/UI, Quyền review tích hợp và chạy laptop Quyền; sau đó cập nhật DOCX, bàn giao ảnh/kịch bản cho PPTX và tập demo. W3-DB-01 vẫn theo dõi, chưa kết luận đã sửa. Chưa nghiệm thu nhóm/đóng #3.

Mẫu này chưa được gửi lên issue/PR hay cho thành viên nào trong phiên này.
