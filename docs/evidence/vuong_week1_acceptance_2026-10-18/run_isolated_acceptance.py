"""Run the pinned week-1 setup in a private, previously initialized MySQL datadir.

Requires the exported UI 8c5be94 + SQL 08e4427 source, Python dependencies,
Playwright Chromium and a NEW datadir initialized with mysqld --no-defaults
--initialize-insecure. Never reads DB credentials or connects to the working DB.
See README.md for the exact invocation and environment limitations.
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--datadir', type=Path, required=True)
    parser.add_argument('--mysqld', type=Path, required=True)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    source, datadir, repo, out = [p.resolve() for p in
                                (args.source, args.datadir, args.repo, args.output)]
    assert source.is_relative_to(repo / '.venv') and datadir.is_relative_to(repo / '.venv')
    assert source != repo and not (source / '.env').exists()
    assert datadir.name == 'mysql-data' and (datadir / 'auto.cnf').is_file()
    assert not (datadir / 'acceptance-used.json').exists(), 'Use a fresh datadir for each run'
    assert out.is_relative_to(repo / 'docs/evidence')
    out.mkdir(parents=True, exist_ok=True)
    (out / 'browser').mkdir(exist_ok=True)
    env_path = repo / '.env'
    env_before = hashlib.sha256(env_path.read_bytes()).hexdigest()
    sys.path.insert(0, str(source))
    import pymysql
    from tools.quyen_db import statements
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    database = 'clinic_vuong_w1_acceptance_test'
    report = dict(run_at=datetime.now(timezone(timedelta(hours=7))).isoformat(),
                  python=sys.version.split()[0], os=sys.platform,
                  ui_sha='8c5be9469976333195eb67c9d2689638d02c045f',
                  sql_sha='08e4427f6ac8e9ba55eaba859ddab4067330ec04',
                  setup_sha='3b59effd4bb86fca1f8d239af8349e73ac09e9e6',
                  database=database, private_port=port, import_steps=[], cases=[])
    (datadir / 'acceptance-used.json').write_text(json.dumps({'database': database, 'port': port}))
    log_handle = (datadir / 'console.txt').open('wb')
    proc = subprocess.Popen([str(args.mysqld), '--no-defaults', f'--datadir={datadir}',
        '--bind-address=127.0.0.1', f'--port={port}', '--mysqlx=0', '--skip-log-bin',
        f'--log-error={datadir / "server-error.txt"}', f'--pid-file={datadir / "server.pid"}'],
        stdout=log_handle, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
    db = None
    server = None
    thread = None
    password = secrets.token_hex(24)

    def case(identifier, expected, actual):
        report['cases'].append(dict(id=identifier, expected=expected, actual=actual, status='PASS'))
        print(identifier, 'PASS', flush=True)

    def save():
        (out / 'integration_results.json').write_text(json.dumps(report, ensure_ascii=False,
             indent=2, default=str), encoding='utf-8')

    try:
        for _ in range(60):
            if proc.poll() is not None:
                raise RuntimeError('Private mysqld exited; inspect its private error log')
            try:
                db = pymysql.connect(host='127.0.0.1', port=port, user='root',
                     charset='utf8mb4', connect_timeout=2, autocommit=True,
                     cursorclass=pymysql.cursors.DictCursor)
                break
            except pymysql.OperationalError:
                time.sleep(0.5)
        assert db is not None, 'Private MySQL failed to start'
        with db.cursor() as cur:
            cur.execute('SELECT VERSION() AS v'); report['mysql'] = cur.fetchone()['v']
            cur.execute("ALTER USER 'root'@'localhost' IDENTIFIED BY %s", (password,))
            cur.execute('CREATE DATABASE `' + database + '` CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci')
        db.select_db(database)
        os.environ.update(DB_HOST='127.0.0.1', DB_PORT=str(port), DB_USER='root',
            DB_PASSWORD=password, DB_NAME=database, FLASK_SECRET_KEY=secrets.token_hex(32),
            COOKIE_SECURE='false', FLASK_DEBUG='false', RUN_MYSQL_TESTS='1', RUN_BROWSER_TESTS='1',
            PYTHON_DOTENV_DISABLED='1')
        os.chdir(source)
        with db.cursor() as cur:
            cur.execute("SET time_zone='+07:00'")
            for index, filename in enumerate(['schema.sql', 'seed.sql', 'audit.sql',
                                              'constraints.sql', 'audit.sql', 'queries.sql'], 1):
                results = []
                for sql in statements((source / 'database' / filename).read_text(encoding='utf-8')):
                    cur.execute(sql)
                    if cur.description:
                        rows = cur.fetchall()
                        if filename == 'audit.sql':
                            assert not rows, f'{filename} found inconsistent records'
                        results.append(rows)
                entry = dict(order=index, file=filename, result_sets=len(results),
                             row_counts=[len(rows) for rows in results])
                if filename == 'audit.sql':
                    assert len(results) == 10
                if filename == 'queries.sql':
                    entry['results'] = results
                    assert results[-1][0] == dict(tien_kham=4680000, tien_thuoc=5820800, doanh_thu=10500800)
                    assert sum(int(r['tong_luong']) for r in results[1]) == 78000000
                    assert sum(int(r['tong_luong']) for r in results[2]) == 65600000
                report['import_steps'].append(entry)
                print('IMPORT', index, filename, 'PASS', flush=True)
            cur.execute('SHOW TABLES'); assert len(cur.fetchall()) == 11
            cur.execute('SHOW TRIGGERS'); report['trigger_count'] = len(cur.fetchall())
            assert report['trigger_count'] > 0
        from clinic_app import create_app
        from tools.audit_seed import audit, EXPECTED
        from clinic_app.entities import ENTITIES
        app = create_app({'TESTING': True})
        assert app.config['DB_NAME'] == database and app.config['DB_PORT'] == port

        def snapshot():
            with db.cursor() as cur:
                hashes = {}
                for table in EXPECTED:
                    cur.execute(f'SELECT * FROM {table}')
                    data = sorted(json.dumps(r, sort_keys=True, ensure_ascii=False, default=str)
                                  for r in cur.fetchall())
                    hashes[table] = hashlib.sha256('\n'.join(data).encode()).hexdigest()
                return hashes

        before = snapshot()
        with app.app_context():
            report['audit_before'] = audit()
        assert report['audit_before']['matches_expected_counts']
        assert not any(report['audit_before']['findings'].values())
        result = subprocess.run([sys.executable, '-m', 'pytest', '-v'], cwd=source,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8',
            env={**os.environ, 'PYTHONIOENCODING': 'utf-8'})
        (out / 'pytest.txt').write_text(result.stdout, encoding='utf-8')
        report['pytest_exit_code'] = result.returncode
        assert result.returncode == 0 and '72 passed' in result.stdout and ' skipped' not in result.stdout
        for file in (source / 'test-artifacts/week1').glob('*.png'):
            shutil.copy2(file, out / 'browser' / ('pytest-' + file.name))
        case('PYTEST', '72 passed, no skipped, canonical SQL and UI together', '72 passed; exit 0')
        assert snapshot() == before, 'pytest changed seed rows'
        from werkzeug.serving import make_server
        from playwright.sync_api import sync_playwright, expect
        server = make_server('127.0.0.1', 0, app, threaded=True)
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        base = f'http://127.0.0.1:{server.server_port}'
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            report['chromium'] = browser.version
            page = browser.new_page(viewport={'width': 1440, 'height': 1000}, locale='vi-VN')
            for health in ['/health', '/health/db']:
                assert page.goto(base + health).status == 200
            case('HEALTH', 'Flask and private DB health both 200', 'Both 200')
            for slug, entity in ENTITIES.items():
                key = 'VA' + slug[:2] + secrets.token_hex(3)
                fields = {f.name: 'Kiểm thử Vương' for f in entity.fields}
                fields.update({entity.pk: key, 'cmt': '000' + str(secrets.randbelow(10**9)).zfill(9),
                    'ngay_sinh': '2000-01-01', 'so_dien_thoai': '0901234567', 'tham_nien': '4'})
                created = False

                def fill(values):
                    page.goto(f'{base}/{slug}/new')
                    for f in entity.fields:
                        page.locator(f'[name="{f.name}"]').fill(values[f.name])

                def shot(label):
                    name = f'{slug}-{label}.png'
                    page.screenshot(path=str(out / 'browser' / name), full_page=True)
                    return 'browser/' + name

                try:
                    fill(fields)
                    page.get_by_role('button', name='Thêm hồ sơ', exact=True).click()
                    expect(page).to_have_url(f'{base}/{slug}/{key}')
                    created = True
                    case(slug + '-create', 'Saved details and success notice', shot('created'))
                    with db.cursor() as cur:
                        cur.execute(f'SELECT * FROM {entity.table} WHERE {entity.pk}=%s', (key,))
                        saved = cur.fetchone()
                        assert saved['cmt'] == fields['cmt'] and saved['ho_ten'] == fields['ho_ten']
                    case(slug + '-select', 'Independent MySQL SELECT matches input and leading zeros', saved)
                    page.reload()
                    expect(page.get_by_role('heading', name=fields['ho_ten'], exact=True)).to_be_visible()
                    case(slug + '-reload', 'Record remains after browser reload', shot('reloaded'))
                    page.goto(f'{base}/{slug}?q={key}')
                    expect(page.locator(f'a[href="/{slug}/{key}"]')).to_be_visible()
                    case(slug + '-list', 'Search returns the stored record', key)
                    page.goto(f'{base}/{slug}/{key.lower()}/edit')
                    expect(page.locator(f'[name="{entity.pk}"]')).to_have_value(key)
                    page.locator('[name="dia_chi"]').fill('Địa chỉ đã sửa qua trình duyệt')
                    page.get_by_role('button', name='Lưu thay đổi', exact=True).click()
                    page.reload()
                    with db.cursor() as cur:
                        cur.execute(f'SELECT dia_chi FROM {entity.table} WHERE {entity.pk}=%s', (key,))
                        assert cur.fetchone()['dia_chi'] == 'Địa chỉ đã sửa qua trình duyệt'
                    case(slug + '-edit', 'Edit persisted after reload and independent SELECT', shot('edited'))
                    probes = [('duplicate-code', fields, 409, 'Chưa lưu được hồ sơ'),
                        ('duplicate-cmt', {**fields, entity.pk: 'VX' + secrets.token_hex(4)}, 409, 'Chưa lưu được hồ sơ'),
                        ('invalid-cmt', {**fields, 'cmt': 'abc'}, 422, 'Chưa lưu hồ sơ:'),
                        ('future-birth', {**fields, 'ngay_sinh': '2999-01-01'}, 422, 'Chưa lưu hồ sơ:')]
                    for label, values, status, message in probes:
                        fill(values)
                        with page.expect_response(lambda r: r.request.method == 'POST') as response:
                            page.get_by_role('button', name='Thêm hồ sơ', exact=True).click()
                        assert response.value.status == status
                        expect(page.get_by_role('alert')).to_contain_text(message)
                        expect(page.locator('[name="ho_ten"]')).to_have_value(fields['ho_ten'])
                        case(slug + '-' + label, f'HTTP {status}; error shown; inputs retained', shot(label))
                    original = {'patients': 'BN001', 'doctors': 'BS001', 'nurses': 'YT001'}[slug]
                    page.goto(f'{base}/{slug}/{original}')
                    page.locator('summary').click()
                    page.locator('[name="confirm_delete"]').fill(original)
                    with page.expect_response(lambda r: r.request.method == 'POST') as response:
                        page.get_by_role('button', name='Xác nhận xóa', exact=True).click()
                    assert response.value.status == 409
                    expect(page.get_by_role('alert')).to_contain_text('Chưa xóa được hồ sơ')
                    evidence = shot('protected')
                    assert page.goto(f'{base}/{slug}/{original}').status == 200
                    case(slug + '-protected', '409; referenced seed record remains', evidence)
                finally:
                    if created:
                        page.goto(f'{base}/{slug}/{key}')
                        page.locator('summary').click()
                        page.locator('[name="confirm_delete"]').fill(key)
                        page.get_by_role('button', name='Xác nhận xóa', exact=True).click()
                        expect(page).to_have_url(f'{base}/{slug}')
                        evidence = shot('cleaned')
                        assert page.goto(f'{base}/{slug}/{key}').status == 404
                        case(slug + '-cleanup', 'Only newly created fixture deleted; then 404', evidence)
            page.goto(f'{base}/patients/BN001/history')
            expect(page.get_by_text('Các lần khám', exact=True)).to_be_visible()
            page.screenshot(path=str(out / 'browser/patient-history.png'), full_page=True)
            case('HISTORY', 'BN001 history visible from canonical DB', 'browser/patient-history.png')
            browser.close()
        report['seed_hash_before'] = before
        report['seed_hash_after'] = snapshot()
        assert before == report['seed_hash_after']
        with app.app_context():
            report['audit_after'] = audit()
        assert report['audit_after']['matches_expected_counts']
        assert not any(report['audit_after']['findings'].values())
        report['env_unchanged'] = hashlib.sha256(env_path.read_bytes()).hexdigest() == env_before
        assert report['env_unchanged']
        report['status'] = 'PASS'
    except BaseException as exc:
        report['status'] = 'FAIL'
        report['error'] = str(exc) if isinstance(exc, AssertionError) else type(exc).__name__
        raise
    finally:
        if server:
            server.shutdown(); thread.join(timeout=5); server.server_close()
        if db:
            try:
                with db.cursor() as cur: cur.execute('SHUTDOWN')
            except pymysql.MySQLError:
                pass
            db.close()
        try:
            proc.wait(timeout=20)
        except subprocess.TimeoutExpired:
            proc.terminate(); proc.wait(timeout=10)
        log_handle.close()
        report['private_mysql_stopped'] = proc.poll() is not None
        report['env_unchanged'] = hashlib.sha256(env_path.read_bytes()).hexdigest() == env_before
        save()
    print('ACCEPTANCE PASS; private MySQL stopped; existing .env unchanged', flush=True)


if __name__ == '__main__':
    main()
