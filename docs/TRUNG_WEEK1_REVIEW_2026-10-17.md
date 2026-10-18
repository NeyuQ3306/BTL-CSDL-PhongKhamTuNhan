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

CI ở commit trước sửa đã thành công, run 38764675833. Local sau sửa: **11 passed, 12 skipped** (không có DB local). Compileall và diff check đạt. Sau đó commit c442384 đã được xác minh **23/23 test đạt** trên MySQL 8.4.11: https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/actions/runs/39008536160.

Không thay schema hoặc giá trị dữ liệu, không thay UI của Vương, không merge main. Theo RULES.md còn cần người khác review trước merge. Tại thời điểm rà soát PR #4 mở, chưa có review; main vẫn ở phiên bản khởi tạo.

## Bổ sung tối 17/10: mã chuẩn và giao diện

Phát hiện URL có mã khác hoa/thường với mã DB làm form sửa báo 422 dù không đổi mã. Đã sửa route edit/delete lấy mã chuẩn từ bản ghi; giữ chặn thay PK và xác nhận xóa. Thêm 6 ca MySQL cho ba loại hồ sơ, mã uppercase/mixed-case, URL lower/upper, cập nhật, từ chối đổi PK, xác nhận xóa sai/đúng. Thêm 3 ca Chromium thêm/xem/sửa/xóa qua UI với MySQL thật.

Hướng dẫn Vương: [VUONG_WEEK1_UI_HANDOFF.md](VUONG_WEEK1_UI_HANDOFF.md). Kết quả CI mới được cập nhật ở đầu file bằng chứng; 23 test là mốc trước bản sửa tối nay, không phải tổng bộ test mới.

## Kết quả bản sửa tối 17/10

**32/32 test đạt** trên Python 3.11 / MySQL 8.4.11 / Chromium, commit `ca1b178`. [CI](https://github.com/NeyuQ3306/BTL-CSDL-PhongKhamTuNhan/actions/runs/39035269920). Bộ test gồm 6 ca mã hồ sơ và 3 luồng CRUD browser mới; 9 ảnh tại `docs/evidence/week1/`. Sau dọn dữ liệu thử vẫn đủ 1.144 dòng. Tuần 2 đồng bộ cùng bản sửa và đạt 68/68 test. Không thay xác nhận review/merge hoặc việc chạy trên máy nhóm.
