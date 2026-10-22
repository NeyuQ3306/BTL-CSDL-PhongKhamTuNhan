"""Prepare an isolated week-2 UI baseline; never connects to the configured working DB.

Run with the existing acceptance Python runtime. Each invocation creates a fresh private
MySQL datadir under .venv and writes reproducible evidence under docs/evidence.
Use --serve to keep the verified app available until Ctrl+C.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import secrets
import shutil
import socket
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone, timedelta

ROOT = Path(__file__).resolve().parents[1]


def free_port():
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        return sock.getsockname()[1]


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--serve', action='store_true')
    parser.add_argument('--mysqld', type=Path, help='Windows mysqld.exe path; otherwise discover installed 8.4/8.0 or PATH')
    parser.add_argument('--browsers-path', type=Path, help='Optional Playwright browser cache; otherwise use environment/default cache')
    parser.add_argument('--cleanup-check', choices=['success', 'error'],
                        help='Private MySQL cleanup smoke only; no suite/UI acceptance')
    args = parser.parse_args()
    os.chdir(ROOT)
    sys.path.insert(0, str(ROOT))
    stamp = datetime.now(timezone(timedelta(hours=7))).strftime('%Y%m%d_%H%M%S_%f')
    private = ROOT / '.venv' / ('week2_prepare_' + stamp)
    private.mkdir(parents=True)
    data = private / 'mysql-data'
    out = ROOT / 'docs/evidence' / ('vuong_week2_prepare_' + stamp)
    out.mkdir(parents=True)
    def env_hash():
        path=ROOT / '.env'
        return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None
    before_env = env_hash()
    candidates=[args.mysqld] if args.mysqld else [
        Path('C:/Program Files/MySQL/MySQL Server 8.4/bin/mysqld.exe'),
        Path('C:/Program Files/MySQL/MySQL Server 8.0/bin/mysqld.exe'),
        Path(shutil.which('mysqld') or '__missing_mysqld__')]
    mysqld=next((p.resolve() for p in candidates if p.is_file()),None)
    if mysqld is None:
        raise RuntimeError('Specify --mysqld with an installed Windows mysqld.exe')
    port = free_port()
    database = 'clinic_vuong_week2_prepare_test'
    report = dict(source_sha=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
                  run_at=stamp, python=sys.version, database=database, mysql_port=port,
                  dependencies={'trung': '10c808238ef2f8f4f0a1aabcfc59da19079b38f8',
                                'quyen': '1bf9f8b18342eaf6d0097f3693df1bc02addfcfa'},
                  scope='Preparation baseline, not final week-2 acceptance', screens=[],
                  preparation_success=False)
    log = (private / 'mysql-console.log').open('wb')
    proc = server = browser = thread = None
    db = None
    try:
        subprocess.run([str(mysqld), '--no-defaults', '--initialize-insecure', f'--datadir={data}'],
                       stdout=log, stderr=subprocess.STDOUT, check=True,
                       creationflags=subprocess.CREATE_NO_WINDOW)
        proc = subprocess.Popen([str(mysqld), '--no-defaults', f'--datadir={data}',
            '--bind-address=127.0.0.1', f'--port={port}', '--mysqlx=0', '--skip-log-bin',
            f'--log-error={data / "server-error.txt"}'], stdout=log, stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NO_WINDOW)
        import pymysql
        for _ in range(80):
            if proc.poll() is not None:
                raise RuntimeError('Private MySQL exited; inspect private log')
            try:
                db = pymysql.connect(host='127.0.0.1', port=port, user='root',
                    autocommit=True, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                break
            except pymysql.OperationalError:
                time.sleep(.25)
        assert db is not None
        password = secrets.token_hex(24)
        with db.cursor() as cur:
            cur.execute("ALTER USER 'root'@'localhost' IDENTIFIED BY %s", (password,))
            cur.execute(f'CREATE DATABASE `{database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci')
            cur.execute('SELECT VERSION() v')
            report['mysql'] = cur.fetchone()['v']
        os.environ.update(DB_HOST='127.0.0.1', DB_PORT=str(port), DB_USER='root',
            DB_PASSWORD=password, DB_NAME=database, FLASK_SECRET_KEY=secrets.token_hex(32),
            COOKIE_SECURE='false', FLASK_DEBUG='false', PYTHON_DOTENV_DISABLED='1',
            RUN_MYSQL_TESTS='1', RUN_BROWSER_TESTS='1', QUYEN_CHECK_WEEK2='1',
            PYTHONIOENCODING='utf-8', VUONG_ACCEPTANCE_RUN=stamp)
        if args.cleanup_check:
            report['cleanup_check'] = args.cleanup_check
            if args.cleanup_check == 'error':
                db.close()  # exercise fallback when the connection is already unavailable
                raise RuntimeError('Injected failure after private MySQL startup')
            return
        if args.browsers_path:
            os.environ['PLAYWRIGHT_BROWSERS_PATH']=str(args.browsers_path.resolve())
        elif not os.getenv('PLAYWRIGHT_BROWSERS_PATH'):
            old_cache=ROOT / '.venv/week1_acceptance_20261018/browsers'
            if old_cache.is_dir(): os.environ['PLAYWRIGHT_BROWSERS_PATH']=str(old_cache)
        from tools.quyen_week1_evidence import execute_file
        db.select_db(database)
        with db.cursor() as cur:
            cur.execute("SET time_zone='+07:00'")
        report['import'] = []
        for name in ['schema.sql', 'seed.sql', 'audit.sql', 'constraints.sql', 'audit.sql', 'queries.sql']:
            rows = execute_file(db, name, require_empty=name == 'audit.sql')
            report['import'].append(dict(file=name, result_sets=len(rows)))
        from clinic_app import create_app
        from tools.audit_seed import audit, EXPECTED
        app = create_app()
        assert app.config['DB_PORT'] == port and app.config['DB_NAME'] == database

        def snapshot():
            result = {}
            with db.cursor() as cur:
                for table in EXPECTED:
                    cur.execute(f'SELECT * FROM `{table}`')
                    rows = sorted(json.dumps(x, sort_keys=True, default=str) for x in cur.fetchall())
                    result[table] = hashlib.sha256('\n'.join(rows).encode()).hexdigest()
            return result

        baseline = snapshot()
        files = [p for p in (ROOT / 'clinic_app').rglob('*')
                 if p.is_file() and '__pycache__' not in p.parts]
        files += [Path(__file__).resolve()] + list((ROOT / 'tests').glob('test*.py'))
        files += list((ROOT / 'database').glob('*.sql')) + [ROOT / 'database/expected_results.md']
        (out / 'source_sha256.json').write_text(json.dumps({
            str(p.relative_to(ROOT)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in files if p.is_file()}, indent=2), encoding='utf-8')
        print('Private import ready; running baseline tests', flush=True)
        with (out / 'pytest.txt').open('w', encoding='utf-8') as testlog:
            result = subprocess.run([sys.executable, '-m', 'pytest', '-q', '-rA',
                                    '--junitxml='+str(out / 'junit.xml')], stdout=testlog,
                                    stderr=subprocess.STDOUT, env=os.environ.copy(), timeout=180)
        report['pytest_exit_code'] = result.returncode
        import xml.etree.ElementTree as ET
        suite=ET.parse(out / 'junit.xml').getroot().find('testsuite')
        report['pytest_junit_stats']={k:int(suite.attrib[k]) for k in ('tests','failures','errors','skipped')}
        print((out / 'pytest.txt').read_text(encoding='utf-8')[-2500:], flush=True)
        report['seed_unchanged_after_tests'] = snapshot() == baseline
        from werkzeug.serving import make_server
        server = make_server('127.0.0.1', 0, app, threaded=True)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = f'http://127.0.0.1:{server.server_port}'
        report['url'] = base
        from playwright.sync_api import sync_playwright
        with db.cursor() as cur:
            cur.execute('SELECT ma_luot FROM luot_den_kham ORDER BY ma_luot LIMIT 1')
            visit = cur.fetchone()['ma_luot']
            cur.execute('SELECT ma_lan_kham FROM lan_kham_benh ORDER BY ma_lan_kham LIMIT 1')
            exam = cur.fetchone()['ma_lan_kham']
            cur.execute('SELECT ma_dot FROM dot_dieu_tri ORDER BY ma_dot LIMIT 1')
            episode = cur.fetchone()['ma_dot']
            cur.execute('SELECT ma_don FROM don_thuoc ORDER BY ma_don LIMIT 1')
            order = cur.fetchone()['ma_don']
        routes = ['/patients', '/visits/new', f'/visits/{visit}',
            f'/visits/{visit}/examinations/new', f'/visits/{visit}/support',
            f'/visits/{visit}/close', f'/treatments/{episode}/cure',
            f'/examinations/{exam}/prescription', f'/prescriptions/{order}', '/reports',
            '/reports/diseases?month=2026-10', '/reports/salaries?month=2026-10',
            '/reports/revenue?month=2026-10', '/reports/history',
            '/reports/history?patient_id=BN001', '/reports/revenue?month=2025-12',
            '/reports/revenue?month=2026-13', '/reports/history?patient_id=MISSING']
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            report['chromium'] = browser.version
            page = browser.new_page(locale='vi-VN')
            for width in [1440, 390, 320]:
                page.set_viewport_size(dict(width=width, height=1000))
                for i, route in enumerate(routes):
                    response = page.goto(base + route)
                    entry = dict(route=route, width=width, status=response.status,
                        heading=page.locator('h1').all_text_contents(),
                        overflow=page.evaluate('document.documentElement.scrollWidth > innerWidth'),
                        screenshot=f'{width}-{i:02}.png')
                    page.screenshot(path=str(out / entry['screenshot']), full_page=True)
                    report['screens'].append(entry)
            browser.close()
            browser = None
        with app.app_context():
            report['audit'] = audit()
        report['seed_unchanged_after_browser'] = snapshot() == baseline
        with db.cursor() as cur:
            cur.execute('SHOW TRIGGERS')
            report['trigger_count'] = len(cur.fetchall())
        report['final_sql_audit_sets'] = len(execute_file(db, 'audit.sql', require_empty=True))
        assert result.returncode == 0 and report['seed_unchanged_after_tests']
        assert report['seed_unchanged_after_browser'] and report['audit']['matches_expected_counts']
        assert not any(report['audit']['findings'].values())
        assert all(x['status'] == (400 if '2026-13' in x['route'] else
                   404 if 'MISSING' in x['route'] else 200) for x in report['screens'])
        report['preparation_success'] = True
        report['env_unchanged'] = env_hash() == before_env
        print(f'BASELINE READY {base}/visits/new ; evidence: {out.relative_to(ROOT)}', flush=True)
        (out / 'results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2, default=str), encoding='utf-8')
        if args.serve:
            print('App/private DB remain active until Ctrl+C. Credentials are memory-only.', flush=True)
            while True:
                time.sleep(1)
    except BaseException as exc:
        report['failure_type'] = type(exc).__name__
        raise
    finally:
        from tools.private_mysql_cleanup import stop_private_mysql
        original_error = sys.exc_info()[0] is not None
        cleanup_errors = []
        try:
            if server:
                try:
                    if thread is not None and thread.is_alive():
                        server.shutdown()
                    server.server_close()
                    if thread is not None:
                        thread.join(timeout=5)
                except Exception as exc:
                    cleanup_errors.append(type(exc).__name__)
        finally:
            try:
                report['mysql_cleanup'] = stop_private_mysql(proc, db, mysqld, data, port)
            except Exception as exc:
                report['mysql_cleanup'] = dict(success=False, error_type=type(exc).__name__)
            finally:
                log.close()
        report['cleanup_errors'] = cleanup_errors
        report['env_unchanged'] = env_hash() == before_env
        if cleanup_errors or not report['mysql_cleanup']['success']:
            report['preparation_success'] = False
        (out / 'results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2, default=str), encoding='utf-8')
        if not original_error and (cleanup_errors or not report['mysql_cleanup']['success']):
            raise RuntimeError('Private instance cleanup failed; inspect results.json')


if __name__ == '__main__':
    main()
