# Kịch bản demo tuần 3 — Vương

Ngày 21/10/2026, UTC+07:00. Mục tiêu **13 phút**, có khoảng đệm đến 15 phút. **Cập nhật khi bàn giao bước 7: Vương xác nhận đã hoàn thành bước 6 trong yêu cầu ngày 21/10/2026.** Đây là xác nhận của người dùng; trợ lý không quan sát buổi tập chung, chưa có ngày giờ/thành phần/thời lượng/vướng mắc cụ thể để điền biên bản. Giữ checklist và kết quả tự động bên dưới làm ghi nhận kỹ thuật tại thời điểm chuẩn bị; không tự điền hoặc nhận đó là bằng chứng tập chung. Phân vai bên dưới là phương án trong kịch bản, cần đối chiếu với phân vai thực tế của nhóm.

## 1. Đúng source và môi trường

Dùng checkout `vuong/week-3`, SHA nền `f4869299c25fdfd0b711597e30b60ab277120f44` cộng sửa UI/test, application candidate `sha256:045a7c42b12390bc5a1cb911a1ec648215cf66df679b6576a7b22464bb398894`. Bản demo phải khớp manifest app của [bước 5](evidence/vuong_week3_step5_20261021/execution_source_sha256.json), cùng công cụ mới [vuong_week3_demo.py](../tools/vuong_week3_demo.py). Xem [đối chiếu source bàn giao](evidence/vuong_week3_handoff_20261021/verification.json); không coi SHA nền tự chứa sửa đổi hoặc là release cuối. Mỗi phiên lưu SHA, manifest, diff, môi trường và kết quả riêng.

Cần Python 3.11 và dependencies theo [SETUP](SETUP.md); MySQL executable và Chromium hiện có đã được dùng ở bước 4–5. Công cụ demo dùng MySQL riêng, cổng loopback ngẫu nhiên, DB `clinic_week3_demo_test` trong **instance/datadir mới mỗi lần**. Tên DB giống nhau ở các instance không làm chúng dùng chung dữ liệu. Không đọc `.env`, không kết nối DB đang làm việc.

Từ gốc repository, mở **bản seed mới cho nhóm thao tác**:

```powershell
.\.venv\week3-runtime\Scripts\python.exe -X utf8 tools/vuong_week3_demo.py --serve
```

Chờ `DEMO READY http://127.0.0.1:<cổng>`, mở URL đó với `/patients`. Giữ terminal mở. Mặc định công cụ dùng `.venv/week3-tools/mysql84/mysql-8.4.7-winx64/bin/mysqld.exe`; trên máy có layout khác dùng runtime Python thực tế và truyền `--mysqld "D:/duong-dan/bin/mysqld.exe"`. `--serve` chỉ tạo seed mới, **không tự chạy phần ghi của demo**.

Diễn tập kỹ thuật tự động (cần Playwright/Chromium theo SETUP):

```powershell
.\.venv\week3-runtime\Scripts\python.exe -X utf8 tools/vuong_week3_demo.py --rehearse
```

Cache Chromium khác mặc định có thể truyền `--browsers-path "D:/duong-dan/browsers"`. Lệnh tạo phiên/evidence mới; không chạy chồng phiên cũ để tránh nhầm URL/cổng. Không dùng script dựng lại của bước 4–5 để ghi đè bằng chứng cũ.

## 2. Dữ liệu và số liệu đã chuẩn bị

Chỉ dùng dữ liệu giả. Công cụ kiểm tra không có chuỗi mã `DM6` trong seed trước khi bắt đầu; nếu không đạt, dừng và kiểm tra đúng instance. Không tự sửa mã giữa chừng hoặc xóa lịch sử để né trùng.

### CRUD

Trình bày đầy đủ thêm → chi tiết → sửa địa chỉ → tải lại → xóa đối với **bệnh nhân tạm**. Bác sĩ/y tá dùng cùng thao tác; trong khung 13 phút có thể chỉ nói nhanh và chỉ ra bằng chứng diễn tập đủ 3 nhóm, không nhận đã thao tác cả 3 trong buổi trình bày nếu thực tế chưa làm.

| Nhóm | Mã | CMT | Input khác |
|---|---|---|---|
| Bệnh nhân tạm | `DM6TMPBN` | `999000006001` | Tên Dữ liệu giả demo, sinh1980-01-01, địa chỉ Hà Nội, SĐT0900000006 |
| Bác sĩ tạm | `DM6TMPBS` | `999000006002` | Cùng thông tin chung, bậc nghề/chuyên môn/trình độ: Dữ liệu giả demo; thâm niên4 |
| Y tá tạm | `DM6TMPYT` | `999000006003` | Cùng thông tin chung, trình độ Dữ liệu giả demo, thâm niên4 |
| Bệnh nhân cho luồng khám | `DM6BN` | `999000006004` | Tên Bệnh nhân demo tuần3, sinh1980-01-01, Hà Nội, SĐT0900000006; giữ lại để có lịch sử |

Địa chỉ sau sửa: `Địa chỉ đã sửa trong demo`. Xóa hồ sơ tạm qua phần mở rộng xóa, nhập đúng mã xác nhận. **Phải xóa nhân sự tạm trước Q2**; nếu còn, lương cơ bản của họ làm tổng lương khác đáp án seed. Không xóa `DM6BN` sau khi phát sinh khám.

### Bộ lượt/đợt

Dùng danh mục seed: `BS001`, `YT001`, `YT002`, bệnh `B001`/`B002`, thuốc `T001` giá 1.200đ và `T002` giá 2.500đ. Tên thực tế hiển thị cạnh mã trên dropdown. Ngày2004 là dữ liệu giả lịch sử; không đổi đồng hồ máy/server.

| Thứ tự | Lượt / lần khám | Ngày | Chế độ / đợt | Phí và y tá |
|---|---|---|---|---|
| 1 | `DM6L1` / `DM6K1` | 2004-02-28 | Đợt mới `DM6D1`, B001/BS001 | 100.000đ, YT001, ngày hỗ trợ cùng ngày |
| 2 | `DM6L2` / `DM6K2` | 2004-03-01 | Tái khám `DM6D1` | 100.000đ, YT001; thêm YT002 |
| 3 | `DM6L3` / `DM6K3` | 2004-03-02 | Tái mắc: đợt mới `DM6D2`, B001/BS001 | 100.000đ, YT001 |
| 4 | Trong `DM6L3` / `DM6K4` | 2004-03-02 | Khám thêm bệnh: đợt mới `DM6D3`, B002/BS001 | 50.000đ, không tạo thêm lượt/hỗ trợ |

Kết luận `Theo dõi demo`, nội dung hỗ trợ `Tiếp đón demo`. Kết thúc từng lượt với ngày ra đúng ngày vào. Đóng `DM6L1` trước khi tạo `DM6L2`; **đóng lượt không tự khỏi đợt**. Sau kê đơn ở K2 và đóng L2, xác nhận khỏi D1 ngày 2004-03-01; sau đó mới tạo tái mắc D2 ngày 02/03. Đóng L3, để D2/D3 đang điều trị.

Đơn `DM6RX`, ngày 2004-03-01, gắnK2: T001 số lượng 2/liều dùng `Sáng`; T002 số lượng 3/liều dùng `Tối`. Tổng **2 × 1.200 + 3 × 2.500 = 9.900đ**. Có thể thêm rồi xóa một dòng trống để minh họa nút động; không đổi giá seed. L1/K1 không kê đơn vẫn hợp lệ.

### Expected báo cáo sau khi làm toàn bộ thao tác ghi

CRUD nhân sự tạm đã được xóa; dùng nhân sự seed trong khám, không sửa seed. Dữ liệu2004 không làm thay đổi phát sinh10/2026. Q3 chọnBN001 để chỉ seed, sau đó chọnDM6BN để chỉ luồng vừa ghi.

| Kỳ / nền | Q1 tổng đợt | Tiền khám | Tiền thuốc | Doanh thu | Lương cần chỉ |
|---|---:|---:|---:|---:|---|
| 10/2026 — seed giữ nguyên | 24 | 4.680.000 | 5.820.800 | 10.500.800 | TổngBS 78.000.000; tổngYT 65.600.000 |
| 02/2004 — sau toàn bộ demo | 1 | 100.000 | 0 | 100.000 | BS001: 7.000.000; YT001: 5.200.000; YT002: 5.000.000 |
| 03/2004 — sau toàn bộ demo | 3 | 250.000 | 9.900 | 259.900 | BS001: 8.000.000; YT001: 5.400.000; YT002: 5.200.000 |
| 12/2025 — không phát sinh | 0 | 0 | 0 | 0 | Tổng lương cơ bảnBS 70.000.000; YT 60.000.000 |

Tháng03 có **B001 = 2 đợt** (D1 qua tháng và D2 tái mắc), **B002 = 1 đợt**, tổng 3. D1 chỉ tính 1 lần mỗi tháng có khám; STT D1=[1,2]. Q2 thưởng khỏi D1 ở tháng 03, hỗ trợ cập nhật nhiều công việc vẫn tính 1 dòng y tá/lượt. Các quy ước đối chiếu [đáp án Quyền](../database/expected_results.md); các số 2004 ở đây tính từ input demo, được kiểm tra với SQL chuẩn trong phiên diễn tập, không nhận là số liệu nguyên bản của ca QW2 trong đáp án.

Q3 DM6BN: **3 lượt / 3 đợt / 4 lần khám / 2 dòng thuốc / 4 dòng hỗ trợ**, D1 đã khỏi, D2/D3 đang điều trị, cả 3 lượt đã đóng. BN001: 7 nhóm kết quả có số dòng `[1,3,4,1,5,8,3]`.

## 3. Kịch bản trình bày 13 phút

| Thời gian | Người đề xuất | Thao tác / lời dẫn ngắn | Kết quả cần chỉ ra |
|---|---|---|---|
| 00:00–00:40 | Vương → Quyền | “Đây là bản tích hợp trên MySQL, dữ liệu giả; một lượt có thể khám nhiều bệnh.” Chỉ SHA/candidate và `/health/db` | Kết nối thật; chưa nhận là release cuối |
| 00:40–02:30 | Vương | CRUD bệnh nhân tạm; chỉ nhanh cùng mẫu ở BS/YT hoặc bằng chứng; tạo DM6BN | Reload vẫn lưu địa chỉ, xóa hồ sơ tạm thành công |
| 02:30–05:00 | Vương | Tạo L1/D1/K1, đóng L1; tái khám L2/K2 ngày 01/03, chọn D1 | Bác sĩ/bệnh giữ nguyên, STT 2; đợt qua tháng |
| 05:00–05:45 | Vương → Trung | Cập nhật YT001, thêm YT002. “Một y tá có thể làm nhiều việc nhưng không nhân đôi thưởng trong một lượt.” | L2 có 2 y tá, không tạo 2 dòng YT001 |
| 05:45–07:00 | Vương | Kê DM6RX với 2 thuốc, thêm/xóa dòng trống, lưu đơn | Tổng 9.900đ do server tính, ngày đơn đúng ngày khám |
| 07:00–08:30 | Vương → Trung | Đóng L2, xác nhận khỏi D1; tạo L3/D2 ngày 02/03, thêm B002/D3/K4, đóng L3 | Đóng lượt và khỏi là 2 thao tác; tái mắc đợt mới; nhiều bệnh cùng lượt |
| 08:30–11:40 | Vương → Quyền | Đủ Q1/Q2/Q3/Q4 seed 10/2026; Q3 DM6BN; chỉ Q1 tháng 02/03 và ca trống 12/2025 | Đọc đúng số bảng trên; giải thích không cộng trùng/qua tháng/thưởng |
| 11:40–12:30 | Vương → Trung | Tạo lượt sai `DM6BADL`, mã khám `DM6BADK`, đợt mới `DM6BAD`, ngày 2004-03-03, B001/BS001/DM6BN, phí 100000/YT001; bấm Lưu | Server từ chối vì D2 còn đang điều trị; tiếng Việt, giữ input, không lưu lượt dang dở |
| 12:30–13:00 | Vương | Chỉ ảnh 390px hoặc thu cửa sổ; chốt kết quả và giới hạn | Bảng cuộn vùng riêng; không nhận kiểm chứng thiết bị thật/T16 |

Nếu làm đủ CRUD 3 nhóm trực tiếp mà vượt thời lượng, dùng tối đa 2 phút đệm, rút phần giải thích lặp lại; không bỏ bốn báo cáo hoặc ca sai. Không đổi expected để che dữ liệu khác nền.

Chuyển phần: Vương “Mời Trung giải thích vì sao không để lại lượt dang dở khi lỗi”; Trung nói khóa/transaction/rollback từ source rồi trả “Vương tiếp tục kết quả trên UI”. Vương “Mời Quyền giải thích đợt qua tháng và tiền thưởng”; Quyền nói quy tắc SQL rồi trả cho Vương chuyển báo cáo.

## 4. Lặp lại, dừng và sự cố

Ctrl+C ở terminal `--serve` để server Flask đóng và gửi `SHUTDOWN` trên chính kết nối MySQL private. Đọc kết quả cuối: `mysql_port_closed`, `app_port_closed`, `checkout_env_unchanged`, `source_unchanged`, `old_evidence_unchanged` đều true. **Dữ liệu demo không được xóa bằng SQL**; datadir cũ giữ trong `.venv`, lần tiếp theo chạy lệnh tạo datadir/instance/seed mới và mở URL mới. Đây là cách khởi tạo lại, không phụ thuộc dữ liệu còn sót.

W3-RUN-01 của runner tuần 2 vẫn mở; công cụ demo riêng dùng shutdown bằng kết nối trước khi chờ process, không nhận đã sửa runner cũ. Nếu cổng/tiến trình còn, đối chiếu đúng executable/datadir/cổng trong session rồi xử lý riêng; không dừng MySQL hệ thống hoặc theo tên chung. Dừng demo nếu chưa xác minh đúng môi trường. Không chạy lại import trên DB đã có lịch sử.

Nếu kết quả báo cáo sai nền, kiểm tra nhân sự tạm đã xóa và đúng URL/cổng trước; không sửa SQL/seed để ép đáp án. Nếu lỗi giữa buổi, ghi bước/mã/ngày/ảnh và dùng ảnh đã kiểm chứng để giải thích, nói rõ đây là bằng chứng phiên trước; không giả vờ ảnh là kết quả chạy trực tiếp.

## 5. Tập chung và câu hỏi dự kiến

- [ ] Nhóm xác nhận phân vai, người bấm và người giữ thời gian.
- [ ] Khởi tạo phiên `--serve` mới; xác nhận nguồn, health và mã DM6 chưa tồn tại.
- [ ] Cả nhóm tập ít nhất 1 lần theo thứ tự trên, bấm giờ cả lời nói/chuyển phần.
- [ ] Ghi thời gian thực tế, điểm vướng, ai xử lý, sửa gì và kiểm tra lại phần bị ảnh hưởng.
- [ ] Kết thúc sạch, chuẩn bị phiên mới cho buổi demo chính; không dùng lại DB đã ghi.

| Câu hỏi | Gợi ý trả lời từ source |
|---|---|
| Tái khám khác tái mắc? | Tái khám tiếp tục đợt đang điều trị, STT liên tiếp; tái mắc sau ngày khỏi tạo đợt mới. `clinic_app/workflows.py`, `database/constraints.sql` |
| Một đợt qua hai tháng có bị cộng trùng? | Q1 đếm DISTINCT đợt trong từng kỳ có khám; mỗi kỳ tính một lần. Không cộng các tháng để suy ra số đợt toàn thời gian. `database/queries.sql` |
| Vì sao đóng lượt chưa khỏi? | Hai đối tượng khác nhau; `close_visit` khóa lượt, `cure` kết thúc đợt. `clinic_app/workflows.py` |
| Giá thuốc đổi thì đơn cũ thế nào? | Chi tiết đơn lưu `don_gia_ban`; doanh thu đọc giá đã lưu. Kịch bản này không đổi giá seed; kiểm thử giá lịch sử ở bước 4 |
| Làm sao tránh ghi một phần? | Backend khóa bệnh nhân trước, ghi trong transaction và rollback khi lỗi; DB có PK/FK/CHECK/index/trigger. Không tuyên bố trigger chặn mọi giao dịch SQL quản trị dang dở. `clinic_app/db.py`, `clinic_app/workflows.py`, `database/README.md` |
| Thưởng y tá có bị nhân theo số công việc? | Mỗi cặp lượt–y tá là một dòng, cập nhật nội dung không nhân thưởng. Y tá tính theo ngày hỗ trợ; bác sĩ theo ngày khỏi |
| Tại sao tháng rỗng vẫn có lương? | Công thức giữ lương cơ bản cho toàn bộ nhân sự; không có phát sinh thì thưởng bằng 0 |
| Đã thử máy khác chưa? | T16 không thực hiện theo quyết định nhóm, actual chưa chạy; không lấy diễn tập cùng máy làm bằng chứng máy thứ hai |

Biên bản buổi tập chung — **để trống đến khi thực hiện**: ngày giờ ___; người tham gia ___; thời lượng ___; chỗ vướng ___; thay đổi ___; kết quả kiểm tra lại ___; người xác nhận ___.

## 6. Kết quả diễn tập kỹ thuật và bằng chứng

**Hai lần diễn tập tự động đạt trên hai datadir mới:** [lần 1 sau sửa công cụ](evidence/vuong_week3_demo_20261021_125348_319089/session.json) mất **10,421 giây**; [lần 2 / bản chứng cứ chính](evidence/vuong_week3_demo_20261021_125437_817175/session.json) mất **10,327 giây** cho thao tác browser, chụp ảnh và đối chiếu SQL. Phiên thứ hai từ 12:54:38 đến 12:54:55, khoảng **17,04 giây** cả khởi tạo và cleanup. Không có lời trình bày của con người; **chưa xác nhận thời lượng 13 phút**, chưa tập chung.

Python **3.11.9**, MySQL **8.4.7**, Chromium **156.0.8078.4**, locale vi-VN. Đạt đủ CRUD ba nhóm, tiếp nhận/tái khám, hỗ trợ, đơn 9.900đ, đóng lượt/khỏi/tái mắc/nhiều bệnh, bốn báo cáo và ca sai. UI/JSON/SQL chuẩn/expected khớp; seed tháng 10/2026 vẫn nguyên số liệu sau ghi. Cuối phiên có **1.162 dòng** do thêm 18 dòng demo, `matches_expected_counts=false` là dự kiến; cả 9 nhóm findings và 10 tập audit SQL rỗng, toàn bộ 1.144 dòng seed giữ nguyên.

Đã xem lại **24/24 ảnh của phiên thứ hai** qua công cụ xem ảnh; không nhận đã xem ảnh của mọi phiên. [Chỉ mục bằng chứng và ảnh](evidence/vuong_week3_demo_20261021_125437_817175/README.md), [expected](evidence/vuong_week3_demo_20261021_125437_817175/expected.json), [actual/SQL parity](evidence/vuong_week3_demo_20261021_125437_817175/report-parity.json), [rà ảnh](evidence/vuong_week3_demo_20261021_125437_817175/visual-review.json).

[Thử `--serve` + Ctrl+C](evidence/vuong_week3_demo_20261021_125527_974568/session.json) trên datadir thứ ba đạt: seed 1.144 dòng, audit sạch, app/MySQL đóng cổng. PowerShell/PTY trả exit 1 sau Ctrl+C; session của chương trình ghi `success=true` và cleanup thành công, không nhận đây là lỗi app. Đây chỉ là kiểm tra mở/dừng server, chưa có nhóm thao tác.

**W3-DEMO-01 / P2 đối với công cụ rehearsal — đã sửa và kiểm tra lại.** [Lần đầu không đạt](evidence/vuong_week3_demo_20261021_125130_401438/session.json): chọn CRUD bệnh nhân, script điền cả `tham_nien` không tồn tại trên form, actual timeout 30 giây; expected chỉ điền trường của loại hồ sơ đang mở. SHA nền/công cụ/môi trường trong session và diff của phiên lỗi. Đã sửa công cụ chỉ điền trường của từng loại hồ sơ rồi chạy lại toàn kịch bản hai lần. Không sửa app/backend/schema/công thức. Không có lỗi ứng dụng chặn demo mới được chứng minh; W3-RUN-01 của runner cũ vẫn mở. Không chạy lại full suite 179 test ở bước 6; source app khớp candidate cũ, công cụ mới được kiểm chứng bằng các phiên trên.

**Phần còn lại thuộc nhóm:** xác nhận phân vai; tập ít nhất một lần với lời nói/chuyển phần, bấm giờ thật; ghi vướng mắc và kiểm tra lại thay đổi nếu có. T16 ngoài phạm vi. Chưa commit/push/PR, không gửi tin nhắn hoặc tự nhận nghiệm thu nhóm.
