"""Reproduce step 2 without overwriting the checkout's prior test-artifacts.

Run from repository root using .venv/week3-runtime/Scripts/python.exe.
Only a byte-identical source mirror, a new private MySQL instance, and new
evidence are written. No .env contents or credentials are exported.
"""
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import socket
import subprocess
import sys
from datetime import datetime, timedelta, timezone
import xml.etree.ElementTree as ET

REPO = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
WORK = REPO / '.venv' / 'week3-final-20261021'
SOURCE = WORK / 'source'
MYSQLD = REPO / '.venv/week3-tools/mysql84/mysql-8.4.7-winx64/bin/mysqld.exe'
BROWSERS = REPO / '.venv/week3-tools/browsers'


def now():
    return datetime.now(timezone(timedelta(hours=7))).isoformat()


def git(*args):
    return subprocess.check_output(['git', *args], cwd=REPO).decode('utf-8').strip()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def snapshot(directory):
    if not directory.exists():
        return {}
    return {str(p.relative_to(directory)).replace('\\', '/'): digest(p)
            for p in sorted(directory.rglob('*')) if p.is_file()}


def main():
    assert git('branch', '--show-current') == 'vuong/week-3'
    assert not SOURCE.exists(), 'Each invocation requires a fresh source mirror'
    paths = subprocess.check_output(['git', 'ls-files', '-z'], cwd=REPO).decode('utf-8').split('\0')
    paths = [p for p in paths if p and not p.startswith('docs/evidence/')]
    assert not any(Path(p).name == '.env' for p in paths)
    paths += ['clinic_app/static/number-validation.js', 'tests/test_vuong_week3_numeric_validation.py']
    for rel in paths:
        src = REPO / rel
        dst = SOURCE / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    before = {p: digest(REPO / p) for p in paths}
    mirrored = {p: digest(SOURCE / p) for p in paths}
    assert before == mirrored
    write('execution_source_sha256.json', mirrored)
    diff = subprocess.check_output(['git','diff','HEAD','--','clinic_app','tests'], cwd=REPO).decode('utf-8')
    for rel in ['clinic_app/static/number-validation.js', 'tests/test_vuong_week3_numeric_validation.py']:
        change = subprocess.run(['git','diff','--no-index','--','/dev/null',rel], cwd=REPO, stdout=subprocess.PIPE)
        assert change.returncode in (0,1)
        diff += change.stdout.decode('utf-8')
    (OUT/'source.diff').write_text(diff, encoding='utf-8')
    write('source.diff.json', {'source_dirty':True, 'new_execution_files':['clinic_app/static/number-validation.js','tests/test_vuong_week3_numeric_validation.py'], 'identity':'base SHA + execution_source_sha256.json + source.diff'})
    protected_dirs = ['docs/evidence/vuong_week2_prepare_20261019_225048', 'test-artifacts', 'docs/evidence/vuong_week3_regression_20261021', 'docs/evidence/vuong_week3_ui_20261021', 'docs/evidence/vuong_week3_setup_20261021_111405']
    protected = {p: snapshot(REPO / p) for p in protected_dirs}
    write('protected_files_before.json', protected)
    envfile = REPO / '.env'
    env_before = digest(envfile) if envfile.exists() else None
    metadata = dict(session_id=OUT.name, started_at=now(), executor='Trợ lý Codex thay mặt Vương',
                    timezone='Asia/Bangkok (UTC+07:00)', evidence_kind='local', branch=git('branch', '--show-current'),
                    source_sha=git('rev-parse', 'HEAD'), source_dirty=True,
                    checkout_status_before=git('status', '--short'), source_copy=str(SOURCE),
                    source_copy_matches_checkout=True, python_executable=sys.executable,
                    python_version=platform.python_version(), mysql_executable=str(MYSQLD),
                    browser_cache=str(BROWSERS), flags=dict(RUN_MYSQL_TESTS='1', RUN_BROWSER_TESTS='1', QUYEN_CHECK_WEEK2='1'),
                    flags_origin='Set unconditionally by unchanged runner before pytest',
                    scope='Week-3 step-4 final candidate regression, with UI fix and four new regression cases; not CI/T16',
                    run_started=False)
    write('session.json', metadata)
    os.environ['PLAYWRIGHT_BROWSERS_PATH'] = str(BROWSERS)
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        metadata['chromium_executable'] = pw.chromium.executable_path
    env = os.environ.copy()
    env.update(PLAYWRIGHT_BROWSERS_PATH=str(BROWSERS), PYTHONIOENCODING='utf-8', PYTHONUTF8='1')
    command = [sys.executable, str(SOURCE / 'tools/vuong_week2_prepare.py'),
               '--mysqld', str(MYSQLD), '--browsers-path', str(BROWSERS)]
    metadata.update(command=command, run_started=True)
    write('session.json', metadata)
    print('Running unchanged runner on byte-identical isolated source; log: ' + str(OUT / 'runner.log'), flush=True)
    try:
        with (OUT / 'runner.log').open('w', encoding='utf-8') as log:
            completed = subprocess.run(command, cwd=SOURCE, env=env, stdout=log, stderr=subprocess.STDOUT)
        metadata['runner_exit_code'] = completed.returncode
    finally:
        outputs = sorted((SOURCE / 'docs/evidence').glob('vuong_week2_prepare_*'))
        if outputs:
            assert len(outputs) == 1
            runner_out = outputs[0]
            shutil.copytree(runner_out, OUT / 'runner-output')
            metadata['original_runner_output'] = str(runner_out)
            metadata['original_runner_name_is_legacy'] = True
            if (runner_out / 'results.json').exists():
                result = json.loads((runner_out / 'results.json').read_text(encoding='utf-8'))
                metadata.update(mysql_server_version=result.get('mysql'), chromium_version=result.get('chromium'),
                                database=result.get('database'), mysql_port=result.get('mysql_port'))
                metadata['private_datadir'] = str(SOURCE / '.venv' / ('week2_prepare_' + result['run_at']) / 'mysql-data')
                private = Path(metadata['private_datadir']).parent
                for logname, target in [('mysql-console.log', 'mysql-console.log'), ('mysql-data/server-error.txt', 'mysql-server-error.txt')]:
                    if (private / logname).exists():
                        shutil.copy2(private / logname, OUT / target)
                with socket.socket() as sock:
                    sock.settimeout(1)
                    metadata['mysql_port_closed_after_run'] = sock.connect_ex(('127.0.0.1', result['mysql_port'])) != 0
        if (SOURCE / 'test-artifacts').exists():
            shutil.copytree(SOURCE / 'test-artifacts', OUT / 'browser-tests')
        metadata['source_unchanged_after_run'] = all(digest(REPO / p) == before[p] and digest(SOURCE / p) == before[p] for p in paths)
        metadata['protected_directories_unchanged'] = {p: snapshot(REPO / p) == hashes for p, hashes in protected.items()}
        metadata['checkout_env_unchanged'] = (digest(envfile) if envfile.exists() else None) == env_before
        metadata['source_env_absent'] = not (SOURCE / '.env').exists()
        metadata['finished_at'] = now()
        junit = OUT / 'runner-output/junit.xml'
        if junit.exists():
            tree = ET.parse(junit).getroot()
            cases = tree.findall('.//testcase')
            metadata['junit_actual'] = dict(collected=len(cases), failures=len(tree.findall('.//failure')),
                                           errors=len(tree.findall('.//error')), skipped=len(tree.findall('.//skipped')))
            metadata['junit_actual']['passed'] = sum(not any(c.find(tag) is not None for tag in ['failure', 'error', 'skipped']) for c in cases)
            metadata['skips'] = [dict(test=c.attrib, reason=c.find('skipped').attrib) for c in cases if c.find('skipped') is not None]
        write('session.json', metadata)
        print(json.dumps({k: metadata[k] for k in ['source_sha', 'runner_exit_code', 'python_version', 'mysql_server_version',
                         'chromium_version', 'junit_actual', 'source_unchanged_after_run', 'protected_directories_unchanged',
                         'checkout_env_unchanged', 'mysql_port_closed_after_run'] if k in metadata}, ensure_ascii=False), flush=True)
    return metadata.get('runner_exit_code', 1)


if __name__ == '__main__':
    sys.exit(main())
