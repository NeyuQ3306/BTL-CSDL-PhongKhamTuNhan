# Rà soát tuần 1 của Trung — 17/10/2026

Đối chiếu nhánh `trung/week-1` tại commit `544fa8147099a76407ad1e840485ba0b76728555`, PR #4, mã nguồn, tài liệu và Actions. Mã backend/test local được đối chiếu blob SHA với GitHub trước sửa.

## Lỗi tái hiện và sửa

1. `clinic_app/security.py`: CSRF chứa Unicode gây TypeError trong secrets.compare_digest, trả500 thay vì400. Sửa bằng kiểm tra ASCII trước so sánh; hai test hồi quy dùng tiếng Việt/emoji.
2. `clinic_app/validation.py`: mã hồ sơ new trùng GET /<slug>/new; lưu thành công nhưng redirect mở form tạo thay vì chi tiết. Chặn new (không phân biệt hoa/thường) khi tạo. Giữ nguyên hợp đồng route; thêm ba ca integration cho bệnh nhân/bác sĩ/y tá, mỗi ca thử new và NEW.

## Đối chiếu phân công

| Đầu việc | Kết quả kiểm tra |
|---|---|
| Môi trường Python/MySQL, chạy source gốc, log | Backend mới đã có CI Python3.11/MySQL8.4 và log. Source gốc mới được thử lỗi kết nối lúc import + đọc mã; chưa có bằng chứng chạy toàn bộ UI upstream với DB gốc. |
| Tách DB/.env/module, bảng chữ thường | Đã có config/db/services/routes/validation, application factory, adapter seed snake_case. |
| Chốt route/form/context với Vương trước15/10 | Có hợp đồng INTEGRATION.md, nhưng chưa có xác nhận của Vương trên PR. Không đủ bằng chứng hoàn tất chốt đúng hạn. |
| CRUD ba đối tượng và nền lượt/đợt/lần khám | Đã triển khai CRUD; nền đọc lịch sử/lượt/đợt. Ghi nghiệp vụ nhiều bước thuộc tuần2. |
| Kết nối DB thật, validation, tài liệu | Đã kiểm thử MySQL8.4 qua CI; có SETUP, INTEGRATION, HANDOFF và kiểm thử rollback/FK/CRUD. Hai lỗi đầu vào bổ sung được sửa trong lần rà soát này. |

## Kiểm thử

CI ở commit trước sửa đã thành công, run 38764675833. Local sau sửa: **11 passed, 12 skipped** (không có DB local). Compileall và diff check đạt. Workflow sẽ chạy đầy đủ **23 ca** trên MySQL8.4 khi đẩy bản sửa; kết quả thực tế xem Actions của commit, không suy ra thành công từ unit test.

Không thay schema hoặc giá trị dữ liệu, không thay UI của Vương, không merge main. Theo RULES.md còn cần người khác review trước merge. Tại thời điểm rà soát PR #4 mở, chưa có review; main vẫn ở phiên bản khởi tạo.
