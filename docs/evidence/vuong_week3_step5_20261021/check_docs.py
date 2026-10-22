"""Read-only document/evidence checks; writes only document-checks.json here."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
files = ['README.md', 'docs/SETUP.md', 'docs/USER_GUIDE.md',
         'docs/VUONG_WEEK3_STEP5_VERIFICATION.md', 'docs/VUONG_WEEK2_USER_GUIDE.md',
         'docs/VUONG_WEEK3_ACCEPTANCE.md',
         str((OUT / 'README.md').relative_to(ROOT))]
broken = []
link_count = 0
for rel in files:
    path = ROOT / rel
    for target in re.findall(r'\]\(([^)]+)\)', path.read_text(encoding='utf-8-sig')):
        if '://' in target or target.startswith('#'):
            continue
        target = target.split('#')[0]
        link_count += 1
        resolved = (path.parent / target).resolve()
        if not resolved.exists() and resolved != OUT / 'document-checks.json':
            broken.append(dict(file=rel, target=target))

manifest = json.loads((OUT / 'execution_source_sha256.json').read_text())
mismatches = [p for p, h in manifest.items() if hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != h]
tree = ET.parse(ROOT / 'docs/evidence/vuong_week3_final_20261021/runner-output/junit.xml').getroot()
stats = dict(tests=len(tree.findall('.//testcase')), failures=len(tree.findall('.//failure')),
             errors=len(tree.findall('.//error')), skipped=len(tree.findall('.//skipped')))
cases = json.loads((ROOT / 'docs/evidence/vuong_week3_final_20261021/browser-tests/vuong-acceptance/cases.json').read_text(encoding='utf-8'))
assert all(cases[f'T{i:02}']['status'] == 'PASS' for i in range(1, 16))
sql = json.loads((OUT / 'queries-default.json').read_text(encoding='utf-8'))
assert len(sql) == 11
actual = dict(episodes=sum(x['so_dot_mac'] for x in sql[0]),
              doctors=sum(x['tong_luong'] for x in sql[1]), nurses=sum(x['tong_luong'] for x in sql[2]),
              history_groups=[len(x) for x in sql[3:10]],
              revenue={k: int(v) for k, v in sql[10][0].items()})
expected = dict(episodes=24, doctors=78000000, nurses=65600000, history_groups=[1, 3, 4, 1, 5, 8, 3],
                revenue=dict(tien_kham=4680000, tien_thuoc=5820800, doanh_thu=10500800))
assert actual == expected
process = json.loads((OUT / 'process-check.json').read_text(encoding='utf-8-sig'))
remote = (OUT / 'remote-main.txt').read_text(encoding='utf-8-sig').strip()
assert remote.split()[0] == 'f4869299c25fdfd0b711597e30b60ab277120f44'
setup = json.loads((OUT / 'setup-results.json').read_text(encoding='utf-8'))
assert all(setup[k] for k in ('success', 'db_port_closed', 'app_port_closed', 'checkout_env_unchanged',
                            'old_evidence_unchanged', 'execution_source_unchanged'))
assert not broken and not mismatches and process['count'] == 0
assert stats == dict(tests=179, failures=0, errors=0, skipped=0)
diff = subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True, text=True)
assert diff.returncode == 0, diff.stdout
old_guide = subprocess.check_output(['git', 'show', 'HEAD:docs/VUONG_WEEK2_USER_GUIDE.md'], cwd=ROOT).decode('utf-8')
current_guide = (ROOT / 'docs/VUONG_WEEK2_USER_GUIDE.md').read_text(encoding='utf-8-sig')
assert current_guide.split('\n\n', 1)[1].rstrip() == old_guide.replace('\r\n', '\n').rstrip()
report = dict(checked_at=datetime.now(timezone(timedelta(hours=7))).isoformat(), success=True,
              main_remote=remote, source_base=setup['base_sha'], execution_file_count=len(manifest),
              execution_mismatches=mismatches, files_checked=files, relative_links=link_count, broken_links=broken,
              step4_junit=stats, step4_T01_T15='PASS, run_id 20261021_121231; inherited evidence, not rerun',
              new_SQL_actual=actual, new_SQL_expected=expected, step5_private_mysql_process_count=process['count'],
              git_diff_check_exit=diff.returncode,
              doc_sha256={p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in files},
              unchanged_app_source=True, new_full_suite_run=False,
              week2_guide_historical_body_preserved=True,
              limits=['Not a new dependency installation/clone', 'Not Workbench GUI or Docker verification',
                      'Not CI/release/group approval/T16', 'W3-RUN-01 remains open'])
(OUT / 'document-checks.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({k: report[k] for k in ['success', 'relative_links', 'broken_links', 'execution_file_count', 'step4_junit', 'git_diff_check_exit']}, indent=2))
