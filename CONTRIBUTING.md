# Đóng góp

Đọc [RULES.md](RULES.md) và [phân công](docs/PHAN_CONG_3_TUAN.md). Mở issue cho công việc, tạo nhánh từ main, mở PR và chờ review.

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

Mở PR trên GitHub với base main. Không commit/push trực tiếp main. Với nhánh tuần 1 đã tạo sẵn, dùng `git switch --track origin/trung/week-1` (thay tên đúng thành viên).
