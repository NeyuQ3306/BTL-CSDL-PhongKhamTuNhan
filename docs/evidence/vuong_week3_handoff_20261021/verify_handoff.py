"""Read-only verification of existing evidence; writes only this handoff's report."""
import ast
import hashlib
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(rel):
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))


def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    previous = {p.relative_to(ROOT).as_posix(): digest(p)
                for folder in (ROOT / 'docs/evidence').iterdir()
                if folder.is_dir() and folder != OUT and
                (folder.name.startswith('vuong_week3_') or folder.name == 'vuong_week2_prepare_20261019_225048')
                for p in sorted(folder.rglob('*')) if p.is_file()}
    baseline = OUT / 'preserved_evidence_sha256.json'
    if not baseline.exists():
        save(baseline.name, previous)
    expected_previous = json.loads(baseline.read_text())
    # The pre-existing, untracked week-2 folder intentionally is not shipped.
    optional_week2 = 'docs/evidence/vuong_week2_prepare_20261019_225048/'
    missing = set(expected_previous) - set(previous)
    assert all(p.startswith(optional_week2) for p in missing), 'Week-3 evidence missing'
    assert all(expected_previous.get(p) == h for p, h in previous.items()), 'Prior evidence changed'
    final = 'docs/evidence/vuong_week3_final_20261021/'
    manifest = read(final + 'execution_source_sha256.json')
    differences = [p for p, h in manifest.items() if digest(ROOT / p) != h]
    assert all(p in ('README.md', '.gitattributes') or p.startswith('docs/') for p in differences), differences
    executable = read('docs/evidence/vuong_week3_step5_20261021/execution_source_sha256.json')
    assert all(digest(ROOT / p) == h for p, h in executable.items())
    demo = read('docs/evidence/vuong_week3_demo_20261021_125437_817175/session.json')
    assert digest(ROOT / 'tools/vuong_week3_demo.py') == demo['demo_tool_sha256']
    xml = ET.parse(ROOT / final / 'runner-output/junit.xml').getroot()
    tests = dict(total=len(xml.findall('.//testcase')), failures=len(xml.findall('.//failure')),
                 errors=len(xml.findall('.//error')), skipped=len(xml.findall('.//skipped')))
    assert tests == dict(total=179, failures=0, errors=0, skipped=0)
    cases = read(final + 'browser-tests/vuong-acceptance/cases.json')
    assert all(cases[f'T{i:02}']['status'] == 'PASS' for i in range(1, 16))
    result = read(final + 'runner-output/results.json')
    review = read(final + 'review.json')
    assert review['audit_findings_empty'] and review['audit_total'] == 1144 and review['cleanup_pass']
    assert demo['success'] and demo['mysql_port_closed'] and demo['app_port_closed']
    assert demo['source_unchanged'] and demo['old_evidence_unchanged']

    paths = [p for p in subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0') if p]
    paths += [p.relative_to(ROOT).as_posix() for p in (ROOT / 'clinic_app').rglob('*') if p.is_file() and p.suffix in ('.py', '.js', '.html')]
    paths += ['tools/vuong_week3_demo.py', 'tests/test_vuong_week3_numeric_validation.py']
    python_paths = sorted(set(p for p in paths if p.endswith('.py')))
    for p in python_paths:
        ast.parse((ROOT / p).read_text(encoding='utf-8-sig'), filename=p)
    from jinja2 import Environment
    templates = sorted((ROOT / 'clinic_app/templates').rglob('*.html'))
    for p in templates:
        Environment().parse(p.read_text(encoding='utf-8'))
    docs = ['README.md', 'docs/SETUP.md', 'docs/USER_GUIDE.md', 'docs/VUONG_WEEK2_USER_GUIDE.md']
    docs += [p.relative_to(ROOT).as_posix() for p in (ROOT / 'docs').glob('VUONG_WEEK3*.md')]
    docs += [p.relative_to(ROOT).as_posix() for p in (ROOT / 'docs/evidence').glob('vuong_week3*/README.md')]
    broken = []
    checked = 0
    for rel in docs:
        for target in re.findall(r'\]\(([^)]+)\)', (ROOT / rel).read_text(encoding='utf-8')):
            if '://' in target or target.startswith('#'):
                continue
            checked += 1
            path = (ROOT / rel).parent / unquote(target.split('#')[0].strip('<>'))
            if not path.exists() and path.resolve() != OUT / 'verification.json':
                broken.append(dict(file=rel, target=target))
    assert not broken, broken
    evidence = [ROOT / p for p in previous if 'vuong_week3_' in p]
    scan_paths = sorted(set(evidence + [ROOT / p for p in docs] +
                            [ROOT / 'tools/vuong_week3_demo.py', ROOT / 'clinic_app/static/number-validation.js',
                             ROOT / 'tests/test_vuong_week3_numeric_validation.py']))
    suspects = []
    patterns = [r'gh[pousr]_[A-Za-z0-9]{20,}', r'github_pat_[A-Za-z0-9_]{20,}',
                r'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----',
                r'(?i)(?:DB_PASSWORD|FLASK_SECRET_KEY|password|token)\s*[=:]\s*[\x22\x27]([^\x22\x27]{8,})[\x22\x27]']
    for p in scan_paths:
        if p.suffix.lower() not in ('.md', '.py', '.js', '.json', '.txt', '.log', '.xml', '.diff', '.csv'):
            continue
        for n, line in enumerate(p.read_text(encoding='utf-8', errors='replace').splitlines(), 1):
            if any(re.search(pattern, line) for pattern in patterns):
                suspects.append(dict(file=p.relative_to(ROOT).as_posix(), line=n))
    reviewed_placeholders = [dict(file='docs/SETUP.md', line=55,
                                 reason='MAT_KHAU_MYSQL_TREN_MAY_BAN is a documented placeholder, not a credential')]
    assert suspects == [dict(file='docs/SETUP.md', line=55)], 'Review new secret candidates without printing values'
    report = dict(at=datetime.now(timezone(timedelta(hours=7))).isoformat(),
                  kind='Evidence/source/syntax/link verification, not new MySQL/browser execution',
                  source_head_at_verification=subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(),
                  candidate_id=read(final+'candidate.json')['candidate_id'],
                  full_manifest_files=len(manifest), documentation_differences=differences,
                  application_manifest_files=len(executable), application_manifest_matches=True,
                  demo_tool_matches_rehearsed_hash=True, prior_evidence_files=len(previous), prior_evidence_unchanged=True,
                  junit_actual=tests, T01_T15_all_pass=True,
                  T16=dict(status='Không thực hiện theo quyết định nhóm', actual='Chưa chạy', required=False),
                  audit_1144_clean=True, cleanup_verified_in_existing_evidence=True,
                  python_syntax_files=len(python_paths), jinja_templates=len(templates),
                  local_links_checked=checked, broken_links=broken, secret_scan_candidates=suspects,
                  secret_scan_review=reviewed_placeholders, unresolved_secret_candidates=0,
                  step6='Vương xác nhận hoàn thành; chi tiết tập chung chưa cung cấp',
                  remaining=['Trung review', 'Quyền nghiệm thu/merge', 'Kiểm tra main sau merge', 'Quyền release/tag'],
                  runner_issue='W3-RUN-01 remains open')
    save('verification.json', report)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
