# Trung — chuẩn bị tuần 3

## Phạm vi

Theo docs/PHAN_CONG_3_TUAN.md: kiểm tra/sửa backend và transaction, NULL/số tiền/dữ liệu không tồn tại/rollback; chạy MySQL thống nhất; phối hợp cài từ clone mới trên máy thứ hai; chuẩn bị giải thích route/kết nối/ràng buộc ứng dụng.

Nhánh trung/week-3 tạo từ main20cd47ab7530b1f088213fd5ab08a27dfc87f25a, không mang lịch sử PR#5/#10/#11 vào main. Không thay nhánh tuần2 hay code/schema/UI của người khác. Đây là PR nháp làm trước; chưa xác nhận nghiệm thu tuần3.

## Sản phẩm

- week3_checks/test_backend_release.py: kiểm tra tiền ở0 và trần DECIMAL(12,0), dữ liệu tiền không hợp lệ, transaction lỗi ở body/commit và phục hồi request sau, teardown khi mất kết nối; MySQL thật kiểm tra lịch sử rỗng, ngày kết thúc NULL, không kê đơn, lưu tiền lớn chính xác, rollback lượt lỗi, rollback thuốc thứ hai rồi thử lại cùng mã đơn, dữ liệu thiếu trả404.
- tools/trung_week3_preflight.py: chỉ đọc, ghi receipt không có credentials; kiểm tra11bảng/1.144dòng,9trigger,10audit SQL và9nhóm findings. Có --expected-sha; failed audit trả exit1; không import/drop/xóa, không ghi đè receipt cũ. Chạy trên DB seed sạch trước/sau dọn, không dùng kiểm tra số dòng chuẩn khi còn hồ sơ demo.
- docs/TRUNG_WEEK3_SECOND_MACHINE.md: quy trình clone mới, cài MySQL/Python và mẫu ghi nhận máy thứ hai.
- docs/TRUNG_WEEK3_BACKEND_EXPLAIN.md: tài liệu vấn đáp và ranh giới bảo vệ ở ứng dụng/SQL.
- .github/workflows/trung-week3.yml: CI riêng Python3.11/MySQL8.4, mỗi candidate một DB mới. Chỉ chạy bộ kiểm tra tuần3; không gọi đây là toàn bộ regression UI/nhóm.

## Nền kiểm tra tạm thời

| Candidate | SHA cố định | Ý nghĩa |
|---|---|---|
| Trung #5 | da59e561b187ee693842efd4c6e943c64201a4a1 | Backend và bản sửa tuần2 của Trung |
| Vương #11 | e346a9f39b6e4fa932cd689dea85c95008cb1687 | UI/context và oracle Quyền tích hợp trên nền backend10c8082 |

CI checkout từng candidate, chép đúng week3_checks và preflight từ PR tuần3 để kiểm tra, không sửa candidate trên GitHub. Không gọi hai snapshot này là tree tích hợp cuối. Workflow chuẩn của main vẫn kiểm tra nền main; workflow tuần3 mới kiểm tra backend tuần2 đã pin.

Khi #5/#10/#11 merge: cập nhật nền nhánh này từ main mới bằng merge thường (không force push); cập nhật SHA candidate sang bản tích hợp đã chốt và chạy lại. Khi sẵn sàng nộp, chuyển kiểm tra candidate pin thành kiểm tra chính head tích hợp; không để CI chỉ chứng minh snapshot cũ.

## Việc còn chờ thực tế

- Review/merge tuần2 và chạy oracle trên tree cuối do Quyền điều phối.
- Máy thứ hai thực sự clone/cấu hình/import/chạy UI với Vương, ghi phiên bản/SHA/kết quả; CI Linux không thay bằng chứng này.
- Chạy lại regression UI đầy đủ, demo nhóm, reviewer khác duyệt PR tuần3.
- Quyền phụ trách script nộp/tag; Vương phụ trách UI/demo. Không tự sửa thứ tự script nộp trong phân công: seed hiện cần trước trigger, Quyền phải xử lý mâu thuẫn này khi đóng gói dựa trên SETUP chuẩn.

Không phát hiện lỗi sản phẩm thì không thay code chỉ để có commit sửa. Các test mới phải được chạy và kết quả ghi riêng theo commit; không lấy115test tuần2 làm kết quả tuần3. Kết quả cụ thể xem Checks và mô tả PR tuần3.
