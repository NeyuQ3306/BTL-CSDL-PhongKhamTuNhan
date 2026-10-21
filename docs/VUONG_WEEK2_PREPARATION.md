# Vương — chuẩn bị tuần 2, 19/10/2026

> Mốc kiểm thử lịch sử. Trạng thái bàn giao hiện tại: [VUONG_WEEK2_HANDOFF.md](VUONG_WEEK2_HANDOFF.md).

**Cập nhật sau bước 2:** UI nghiệp vụ đã được hoàn thiện và kiểm thử riêng; xem [bàn giao UI tuần 2](VUONG_WEEK2_UI_HANDOFF.md). Các thiếu sót dưới đây giữ lại như kết quả khảo sát ban đầu, không phải trạng thái hiện tại của các form.

## Bản tích hợp local

- Nhánh làm việc: `vuong/week-2`; trạng thái ban đầu sạch, HEAD `20cd47ab7530b1f088213fd5ab08a27dfc87f25a`.
- Đã fetch origin. Main vẫn tại `20cd47a`.
- PR #5 Trung vẫn open/chưa merge: `10c808238ef2f8f4f0a1aabcfc59da19079b38f8`.
- PR #10 Quyền vẫn open/chưa merge: `1bf9f8b18342eaf6d0097f3693df1bc02addfcfa`.
- Fast-forward nhánh Vương đến bản Trung, rồi merge cục bộ bản Quyền, không xung đột. Bản tích hợp: `f8d80c8ea64ce0843430b5e16eac1538b7eb2d85`.
- Không sửa nhánh Trung/Quyền, không đổi main, không push, không merge PR hoặc đăng GitHub.

Đây là nền phụ thuộc chưa được nhóm duyệt, không phải tuyên bố hai PR đã hoàn tất. Khi #5/#10 squash merge, đối chiếu với main rồi chuyển riêng thay đổi Vương sang nền main mới; tránh đưa lại lịch sử các PR phụ thuộc. PR Vương sau này phải ghi rõ phụ thuộc nếu chưa được giải quyết.

Đã đọc RULES, phân công, issue #2, mô tả/thảo luận #5, #10, WEEK2_INTEGRATION và tài liệu bàn giao. Trung đã ghi nhận hoàn tất nghiệm thu cá nhân trong bình luận bổ sung #5; checklist cũ trong mô tả PR chưa phản ánh hết cập nhật này. Phần review độc lập của Vương vẫn cần thực hiện.

## Môi trường và bằng chứng thực chạy

- Windows, Python **3.12.14**, MySQL **8.0.46**, Chromium **156.0.8078.4**. Đây không phải môi trường mục tiêu Python 3.11/MySQL 8.4.
- Dùng runtime và Chromium sẵn có từ nghiệm thu tuần 1, không sửa venv chính.
- MySQL instance mới có datadir riêng dưới `.venv/week2_prepare_20261019_214447/mysql-data`, bind loopback, cổng **55134**.
- DB duy nhất tạo trong instance đó: `clinic_vuong_week2_prepare_test`; không kết nối DB trong `.env`, không sửa `.env`.
- Mật khẩu root ngẫu nhiên chỉ giữ trong bộ nhớ tiến trình; SQL chạy bằng PyMySQL. Không dùng Workbench để import trong phiên này.
- Import: schema → seed → audit → constraints → audit → queries.
- **160 pytest đạt / 0 skipped**, 18,04 giây, bật MySQL/browser và `QUYEN_CHECK_WEEK2=1`. Gồm test backend, SQL, oracle Quyền, browser tuần 1/2 trên cùng nền tích hợp.
- Browser khảo sát **18 đường dẫn × 3 viewport = 54 lượt**, kích thước 1440/390/320 px. Trang bình thường 200; tháng `2026-13` trả 400, bệnh nhân `MISSING` trả 404.
- Audit cuối: **11 bảng, 9 trigger, 1.144 dòng**; 10 tập kết quả audit SQL rỗng và 9 nhóm findings rỗng. Hash từng bảng seed khớp trước/sau pytest và khảo sát browser.
- Bằng chứng: [kết quả máy đọc được](evidence/vuong_week2_prepare_20261019_214447/results.json), [pytest](evidence/vuong_week2_prepare_20261019_214447/pytest.txt). Tên ảnh là `<viewport>-<chỉ số đường dẫn>.png`, ánh xạ đầy đủ trong results.json.

Phiên `214402` dừng trước import do không kết nối được instance private trong sandbox; đã dừng tiến trình riêng trong finally. Không tính phiên này là đạt. Phiên `214447` chạy thành công với quyền thực thi cần thiết.

## Checklist đã có / còn thiếu

Các mục dưới là khảo sát nền, không đánh dấu nghiệm thu cuối T01–T15 chỉ vì pytest đạt.

| Mục | Đã có, kiểm chứng nền | Còn làm ở bước UI/báo cáo |
|---|---|---|
| Tiếp nhận | Form tạo lượt/khám/y tá, backend nguyên tử; browser test lưu được | Chia nhóm rõ hơn, đồng bộ kích thước select/input và hướng dẫn trường |
| Đợt mới / tái khám | Hai chế độ, server giữ bác sĩ và tính STT | Lọc/chọn đợt phù hợp bệnh nhân; hiện thông tin đợt; giảm nhập mã thủ công, ẩn trường không áp dụng |
| Chi tiết lượt | Có lần khám, tiền, y tá và liên kết thao tác | Trình bày ngày, trạng thái, điều hướng và xác nhận thao tác nhất quán |
| Hỗ trợ / đóng lượt / khỏi | GET form và POST nghiệp vụ có test | Phân biệt rõ đóng lượt/khỏi; ngữ cảnh bệnh nhân/đợt, thông báo lỗi và đường quay lại |
| Đơn thuốc | Nhiều dòng, thêm dòng, giữ MultiDict; giá do server lấy | **P1 UI: select thuốc tràn ngang toàn trang ở 320 px**; bổ sung xóa dòng, thứ tự focus, lỗi dễ tìm |
| Q1/Q2/Q4 | Trang HTML/JSON thật, bộ lọc và số tiền đã có; oracle đạt | Đồng bộ trình bày/bộ lọc/empty state, khả năng cuộn bảng bằng bàn phím |
| Q3 | Có hồ sơ, bệnh đang điều trị, thuốc, y tá và lịch sử | Ngày thuốc/y tá còn ISO; thống nhất định dạng, bổ sung caption/hướng dẫn vùng cuộn mới |
| Trang tổng hợp báo cáo | Các nút dẫn đến báo cáo thật | **P2: mô tả và badge vẫn ghi chờ tích hợp**, gây hiểu nhầm |
| Form lỗi | Backend trả lỗi và giữ values; có test rollback/validation | Lỗi đang ở đầu form; cần liên kết/focus đến trường hoặc dòng liên quan |
| Điều hướng | Có menu Tiếp nhận/khám và báo cáo | Menu tiếp nhận chưa có aria-current; nút Hủy các form đều về danh sách lượt, cần về đúng ngữ cảnh |
| Hồi quy | Suite tuần 1/2 đạt trên nền tích hợp | Sau sửa UI, chạy lại các ca bị ảnh hưởng và kiểm tra người dùng xuyên suốt |

Ảnh đã xem trực tiếp: `390-01.png` (tiếp nhận), `320-07.png` (lỗi tràn kê đơn), `1440-09.png` (trạng thái báo cáo cũ), `1440-10.png` (Q1), `1440-12.png` (doanh thu), `390-14.png` (lịch sử). Các ảnh khác đã được chụp tự động, chưa tuyên bố rà mắt từng ảnh.

## Thứ tự tiếp theo

1. Sửa form nghiệp vụ: responsive select/fieldset, đợt mới/tái khám, dòng thuốc, lỗi, ngữ cảnh điều hướng. Giữ field/endpoint/CSRF theo WEEK2_INTEGRATION.
2. Sửa trang tổng hợp và đồng bộ bốn báo cáo, đối chiếu đáp án Quyền.
3. Chạy checklist T01–T15 và hồi quy trên bản sau sửa; gắn expected/actual và bằng chứng cho từng ca.
4. Đóng gói tài liệu và PR sau khi được giao bước tương ứng; chưa đăng xác nhận hợp đồng hoặc approve thay thành viên trong bước chuẩn bị.

## Chạy lại tự động

Từ root repo:

```powershell
.venv/week1_acceptance_20261018/runtime/Scripts/python.exe tools/vuong_week2_prepare.py --serve
```

Mỗi lần tạo instance/datadir mới, không import chồng hoặc xóa DB cũ. Cần quyền chạy tiến trình MySQL/Chromium và kết nối loopback. Script in URL app và thư mục bằng chứng; Ctrl+C dừng app cùng instance MySQL của chính script. Không dùng app.py trực tiếp nếu chưa thiết lập kết nối private, vì app.py có thể đọc cấu hình DB đang dùng.

Phiên hiện tại mở tại `http://127.0.0.1:59426/visits/new` trong thời gian tiến trình còn chạy. Đây là URL tạm trên máy local, không phải triển khai công khai.
