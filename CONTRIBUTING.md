# Hướng dẫn đóng góp

Đọc [quy tắc nhóm](RULES.md) trước khi sửa mã nguồn, dữ liệu hoặc tài liệu.

## Gửi thay đổi

1. Mở Issue mô tả vấn đề hoặc liên kết Issue đã có.
2. Tạo nhánh mới từ `main` đã cập nhật.
3. Chỉ thêm các file thuộc phạm vi thay đổi; chạy các kiểm tra liên quan.
4. Mở Pull Request vào `main`, nêu thay đổi và cách kiểm chứng.
5. Chờ một thành viên khác review, xử lý nhận xét rồi squash merge. PR của Quyền cần Trung hoặc Vương review.

```sh
git fetch origin
git switch main
git pull --ff-only origin main
git switch -c feat/ten-thanh-vien-ten-viec
# Sau khi sửa và kiểm thử:
git add <cac-file-da-kiem-tra>
git commit -m "feat: mo ta thay doi"
git push -u origin feat/ten-thanh-vien-ten-viec
```

Giữ nhánh của thành viên khác. Khi đã có thay đổi local chưa commit, lưu công việc trước khi chuyển nhánh.

## Dữ liệu và kiểm thử

- Dùng dữ liệu giả và DB thử riêng; hướng dẫn ở [tests/README.md](tests/README.md).
- Thay đổi schema hoặc công thức báo cáo cần cập nhật thiết kế, SQL, backend và test liên quan.
- Không commit `.env`, mật khẩu, venv, cache hoặc datadir MySQL.
- Kết quả sinh tự động giữ trong `test-artifacts/` hoặc `local-evidence/`. Chỉ chọn bằng chứng cần review đưa vào `docs/evidence/`, ghi rõ nguồn và môi trường.
- Giữ thông tin tác giả và nguồn tham khảo trong [ATTRIBUTION.md](docs/ATTRIBUTION.md).

## Phân công và tiến độ

[Phân công nhóm](docs/PHAN_CONG_3_TUAN.md) mô tả trách nhiệm và kế hoạch. Cập nhật tiến độ, việc còn thiếu và vướng mắc trong Issue tương ứng; dùng PR để lưu review và kết quả tích hợp.

Biên bản theo tuần và tài liệu bàn giao trước đây được tra cứu từ [mục lục lịch sử](docs/history/README.md). Không chép báo cáo tiến độ vào README hoặc CONTRIBUTING.
