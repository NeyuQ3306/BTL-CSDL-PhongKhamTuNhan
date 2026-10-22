# Kiểm tra trực tiếp lại W3-UX-01

Trợ lý Codex thay mặt Vương thao tác cua_repl trên Codex IAB, DB/datadir mới. Source SHA nền f486929 + sửa UI/test, manifest124 khớp phiên cuối; xem [candidate](../vuong_week3_final_20261021/candidate.json).

- [interactive-retest.json](interactive-retest.json): -1/101/1.5 báo tiếng Việt; sửa5 → valid=true,customError=false,message rỗng; tên/địa chỉ được giữ. Không POST tạo bác sĩ hợp lệ, không đổi seed.
- [doctor-vietnamese.jpg](doctor-vietnamese.jpg): ảnh tooltip tiếng Việt đã xem trực tiếp.
- [session.json](session.json), [source manifest](execution_source_sha256.json): executable,thời gian,môi trường và bảo toàn seed/.env/source.
- [audit-before.json](audit-before.json), [audit-after.json](audit-after.json): baseline và sau fixture danh mục giả; không dùng chênh lệch fixture để kết luận seed sai.
- [cleanup cuối](../vuong_week3_final_20261021/cleanup.json): instance này shutdown graceful, app/DB đóng cổng; tab đã đóng.

IAB không cung cấp số phiên bản qua API; không lấy Chromium156 của suite gán cho IAB. Full suite và bốn ca hồi quy có trong [phiên cuối](../vuong_week3_final_20261021/README.md). Chưa có kiểm thử lại với JavaScript tắt.
