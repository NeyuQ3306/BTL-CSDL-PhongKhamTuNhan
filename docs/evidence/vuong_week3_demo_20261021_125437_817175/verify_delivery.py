"""Check delivery links, immutable execution files, rehearsal records and cleanup.

Visual-review.json records the assistant's explicit view_image review of this
session's 24 PNGs; it is not inferred from screenshot creation or assertions.
"""
import ast
from datetime import datetime, timezone, timedelta
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent


def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))


def write(name, data):
    (OUT/name).write_text(json.dumps(data, ensure_ascii=False, indent=2),encoding='utf-8')


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


sessions = ['vuong_week3_demo_20261021_125348_319089', OUT.name,
            'vuong_week3_demo_20261021_125527_974568']
summaries = []
for folder in sessions:
    path = ROOT/'docs/evidence'/folder
    s=read(path/'session.json')
    assert all(s[k] for k in ['success','source_unchanged','old_evidence_unchanged',
                             'checkout_env_unchanged','mysql_port_closed','app_port_closed','all_seed_rows_preserved'])
    assert s['group_rehearsal'] is False
    assert not any(read(path/'audit-after.json')['findings'].values())
    if folder != sessions[2]:
        assert len(s['steps'])==8 and all(x['status']=='PASS' for x in s['steps'])
        assert len(s['screenshots'])==24 and not any(x['overflow'] for x in s['screenshots'])
        assert read(path/'audit-after.json')['total']==1162
    else:
        assert read(path/'audit-after.json')['total']==1144
    summaries.append(dict(session=folder,mode=s['mode'],rehearsal_seconds=s.get('rehearsal_seconds'),
                          success=s['success'],datadir=s['datadir'],mysql_port=s['mysql_port']))
assert len({x['datadir'] for x in summaries})==3
manifest=read(OUT/'execution_source_sha256.json')
assert all(digest(ROOT/p)==h for p,h in manifest.items())
ast.parse((ROOT/'tools/vuong_week3_demo.py').read_text(encoding='utf-8'))
report=read(OUT/'session.json')
# All filenames below were viewed in six batches through view_image in this chat.
reviewed=['03-revisit-across-month.png','05-prescription.png','08-2026-10-diseases.png','08-2026-10-salaries.png',
          '08-2026-10-revenue.png','09-seed-history.png','11-error-preserves-input.png','12-mobile-history-390.png',
          '02-crud-patients.png','02-crud-doctors.png','02-crud-nurses.png','04-nurse-support.png',
          '06-recurrence-two-diseases.png','07-closed-visit.png','10-demo-history.png','08-2004-02-diseases.png',
          '08-2004-02-salaries.png','08-2004-02-revenue.png','08-2004-03-diseases.png','08-2004-03-salaries.png',
          '08-2004-03-revenue.png','08-2025-12-diseases.png','08-2025-12-salaries.png','08-2025-12-revenue.png']
assert set(reviewed)=={x['file'] for x in report['screenshots']}
write('visual-review.json',dict(reviewer='Trợ lý Codex thay mặt Vương',method='Explicit view_image of all 24 files in six batches',
      session=OUT.name,reviewed=[dict(file=p,sha256=digest(OUT/p)) for p in reviewed],
      findings='No blocking layout defect seen; wide tables remain inside scroll regions at 390px; numeric results also checked against SQL/expected',
      limits='Long images were scaled in the viewer; not screen reader, physical device or T16 verification'))
index='''# Diễn tập demo tuần 3 — chứng cứ chính

Ngày 21/10/2026, UTC+07:00. Trợ lý Codex thay mặt Vương chạy **Chromium tự động**, chưa có buổi tập của nhóm.

Source nền `f4869299c25fdfd0b711597e30b60ab277120f44` cộng sửa UI/test chưa commit; app khớp candidate `sha256:045a7c42b12390bc5a1cb911a1ec648215cf66df679b6576a7b22464bb398894`. Công cụ demo mới có hash riêng trong manifest67file và source.diff; không nhận candidate cũ tự chứa công cụ mới.

## Kết quả

- **Hai lần trọn kịch bản đạt**, thời gian thao tác tự động10,421s và10,327s trên datadir khác nhau. Chưa có lời nói/chuyển phần; thời lượng13phút là mục tiêu chưa được nhóm xác nhận.
- Python3.11.9 / MySQL8.4.7 / Chromium156.0.8078.4, localevi-VN; DB và cổng riêng, không dùng `.env` gốc.
- CRUD3nhóm; tiếp nhận/tái khám/qua tháng; hỗ trợ; đơn2thuốc9.900đ; đóng/khỏi/tái mắc/nhiều bệnh; đủQ1–Q4 và ca sai đều đạt. Đối chiếu UI–JSON–SQL chuẩn–expected.
- Seed10/2026 không đổi sau ghi. Cuối có1.162dòng do thêm18dòng demo; `matches_expected_counts=false` là dự kiến. 9nhóm findings và10tập auditSQL rỗng;1.144dòng seed giữ nguyên.
- App/DB đã đóng cổng, `.env` gốc/source/bằng chứng cũ giữ nguyên; process-check xác nhận không còn MySQL thuộc datadir step6.

## Hồ sơ

| File | Nội dung |
|---|---|
| [session.json](session.json) | SHA/candidate, môi trường, datadir/cổng,8bước thực chạy, thời gian và cleanup |
| [execution_source_sha256.json](execution_source_sha256.json), [source.diff](source.diff) | Source thực chạy gồm công cụ mới; không gán cho riêng SHA nền |
| [expected.json](expected.json) | Expected ghi trước thao tác browser |
| [report-parity.json](report-parity.json) | Actual bốn kỳ và lịch sử DM6BN, so UI/JSON/SQL/expected |
| [SQL10/2026](sql-2026-10.json), [SQL02/2004](sql-2004-02.json), [SQL03/2004](sql-2004-03.json), [SQL12/2025](sql-2025-12.json) | Mỗi kỳ11tập chuẩn từ queries.sql, thay đúng tham số |
| [audit-before.json](audit-before.json), [audit-after.json](audit-after.json) | Seed ban đầu và DB sau demo |
| [console.txt](console.txt) | HTTP log và kết quả của đúng phiên |
| [visual-review.json](visual-review.json) | Đã xem24/24ảnh phiên này qua view_image; không nhận đã xem mọi phiên |
| [process-check.json](process-check.json) | Kiểm tra tiến trình sau cùng, count0 |
| [delivery-checks.json](delivery-checks.json), [verify_delivery.py](verify_delivery.py) | Kiểm tra hồ sơ/link/hash và khả năng lặp lại |

## Các phiên liên quan và vướng mắc

- [Lần đầu không đạt](../vuong_week3_demo_20261021_125130_401438/session.json): lỗi công cụ rehearsal điền thâm niên vào form bệnh nhân. Không phải lỗi app; đã sửa chỉ điền field của entity, rồi chạy lại toàn kịch bản2lần. Phiên lỗi đã cleanup.
- [Lần đạt thứ nhất](../vuong_week3_demo_20261021_125348_319089/session.json):10,421s. Ảnh phiên này không được nhận là đã rà bằng mắt.
- [Thử serve/Ctrl+C](../vuong_week3_demo_20261021_125527_974568/session.json): datadir mới khác, seed1.144dòng, cleanup đạt. PTY/PowerShell exit1 sauCtrl+C; session app success=true và các cổng đóng.
- W3-RUN-01 của runner tuần2 còn mở; công cụ demo dùng SQL SHUTDOWN riêng, không sửa runner cũ. Không phát hiện lỗi app chặn demo mới trong phạm vi đã chạy.
- Không chạy lại full suite179test, không kiểm chứng máy thứhai/T16, không xác nhận phân vai hoặc nhóm đã tập, không commit/push/PR/gửi tin nhắn.

## Ảnh đã xem — đúng phiên này

'''
for old, new in {
    'manifest67file':'manifest 67 file', 'tự động10,421s và10,327s':'tự động 10,421s và 10,327s',
    'thời lượng13phút':'thời lượng 13 phút', 'Python3.11.9 / MySQL8.4.7 / Chromium156.0.8078.4':'Python 3.11.9 / MySQL 8.4.7 / Chromium 156.0.8078.4',
    'localevi-VN':'locale vi-VN', 'CRUD3nhóm':'CRUD 3 nhóm', 'đơn2thuốc9.900đ':'đơn 2 thuốc 9.900đ',
    'đủQ1–Q4':'đủ Q1–Q4', 'Seed10/2026':'Seed 10/2026', 'có1.162dòng':'có 1.162 dòng',
    'thêm18dòng':'thêm 18 dòng', '9nhóm':'9 nhóm', 'và10tập auditSQL':'và 10 tập audit SQL',
    ';1.144dòng':'; 1.144 dòng', '8bước':'8 bước', 'kỳ11tập':'kỳ 11 tập',
    'Đã xem24/24ảnh':'Đã xem 24/24 ảnh', 'count0':'count 0', 'kịch bản2lần':'kịch bản 2 lần',
    ':10,421s':': 10,421s', 'seed1.144dòng':'seed 1.144 dòng', 'exit1 sauCtrl+C':'exit 1 sau Ctrl+C',
    'runner tuần2':'runner tuần 2', 'suite179test':'suite 179 test', 'máy thứhai':'máy thứ hai',
    'lỗi công cụ rehearsal':'W3-DEMO-01/P2 công cụ rehearsal, đã sửa và kiểm tra lại: lỗi công cụ rehearsal'
}.items():
    index=index.replace(old,new)
for shot in report['screenshots']:
    index+=f"- [{shot['file']}]({shot['file']}) — {shot['width']}px; {shot['url'].split(':',2)[-1].split('/',1)[-1]}\n"
index+='\n[Kịch bản, lệnh mở phiên mới, expected và checklist tập chung](../../VUONG_WEEK3_DEMO.md).\n'
(OUT/'README.md').write_text(index,encoding='utf-8')
files=['README.md','docs/USER_GUIDE.md','docs/VUONG_WEEK3_DEMO.md','docs/VUONG_WEEK3_ACCEPTANCE.md',str((OUT/'README.md').relative_to(ROOT))]
broken=[]; links=0
for rel in files:
    path=ROOT/rel
    for target in re.findall(r'\]\(([^)]+)\)',path.read_text(encoding='utf-8-sig')):
        if '://' in target or target.startswith('#'): continue
        resolved=(path.parent/target.split('#')[0]).resolve(); links+=1
        if not resolved.exists() and resolved!=OUT/'delivery-checks.json': broken.append(dict(file=rel,target=target))
assert not broken,broken
process=read(OUT/'process-check.json');assert process['count']==0
diff=subprocess.run(['git','diff','--check'],cwd=ROOT,capture_output=True,text=True)
assert diff.returncode==0,diff.stdout
write('delivery-checks.json',dict(checked_at=datetime.now(timezone(timedelta(hours=7))).isoformat(),success=True,
      sessions=summaries,files=files,links_checked=links,broken_links=broken,execution_files_match=len(manifest),
      screenshots_viewed=24,private_mysql_process_count=process['count'],git_diff_check=diff.returncode,
      group_rehearsal_done=False,full_step6_complete=False,remaining='Group confirms roles, rehearses together, times speech/transitions and records follow-up'))
print(json.dumps(dict(success=True,links=links,execution_files=len(manifest),screenshots_reviewed=24,group_rehearsal_done=False)))
