"""Verify setup on a fresh private instance and source copy; no working DB access.

Run from repository root with .venv/week3-runtime/Scripts/python.exe.
Each invocation uses a new work folder; evidence refuses overwrite.
"""
import hashlib
import json
import os
from pathlib import Path
import secrets
import shutil
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone, timedelta
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def snapshot(p):
    return {str(x.relative_to(p)).replace('\\', '/'): digest(x)
            for x in p.rglob('*') if x.is_file()}


def free_port():
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


def is_open(port):
    with socket.socket() as s:
        return s.connect_ex(('127.0.0.1', port)) == 0


def main():
    assert not (OUT / 'setup-results.json').exists(), 'Use a new evidence directory'
    now = datetime.now(timezone(timedelta(hours=7)))
    work = ROOT / '.venv' / ('week3-step5-' + now.strftime('%Y%m%d_%H%M%S'))
    work.mkdir()
    source = work / 'source'
    source.mkdir()
    env_before = digest(ROOT / '.env') if (ROOT / '.env').exists() else None
    protected = {str(p.relative_to(ROOT)): snapshot(p) for p in (ROOT / 'docs/evidence').iterdir()
                 if p.is_dir() and p != OUT}
    report = dict(started_at=now.isoformat(), kind='local setup verification, not CI/T16',
                  base_sha=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                  python=sys.version, executable=sys.executable, work=str(work), success=False)
    manifest = json.loads((ROOT / 'docs/evidence/vuong_week3_final_20261021/execution_source_sha256.json').read_text())
    selected = {p: h for p, h in manifest.items() if p.startswith(('clinic_app/', 'tools/', 'database/', 'tests/'))
                or p in ('app.py', '.env.example', 'requirements.txt', 'requirements-dev.txt')}
    assert all(digest(ROOT / p) == h for p, h in selected.items()), 'Execution files differ from step 4'
    report['step4_execution_files_match'] = len(selected)
    for rel in selected:
        target = source / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, target)
    (OUT / 'execution_source_sha256.json').write_text(json.dumps(selected, indent=2), encoding='utf-8')
    mysql = ROOT / '.venv/week3-tools/mysql84/mysql-8.4.7-winx64/bin/mysqld.exe'
    db_port, app_port = free_port(), free_port()
    database = 'clinic_week3_demo_test'
    data = work / 'mysql-data'
    report.update(mysql_executable=str(mysql), datadir=str(data), db_port=db_port, app_port=app_port, database=database)
    proc = app_proc = db = None
    log = (work / 'mysql-console.txt').open('wb')
    app_log = (work / 'app-console.txt').open('wb')
    try:
        subprocess.run([str(mysql), '--no-defaults', '--initialize-insecure', f'--datadir={data}'],
                       stdout=log, stderr=subprocess.STDOUT, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        proc = subprocess.Popen([str(mysql), '--no-defaults', f'--datadir={data}', '--bind-address=127.0.0.1',
                                 f'--port={db_port}', '--mysqlx=0', '--skip-log-bin'],
                                stdout=log, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
        import pymysql
        for _ in range(120):
            if proc.poll() is not None:
                raise RuntimeError('Private MySQL exited')
            try:
                db = pymysql.connect(host='127.0.0.1', port=db_port, user='root', autocommit=True,
                                     charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
                break
            except pymysql.OperationalError:
                time.sleep(.25)
        assert db is not None
        password = secrets.token_hex(24)
        with db.cursor() as c:
            c.execute("ALTER USER 'root'@'localhost' IDENTIFIED BY %s", (password,))
            c.execute(f'CREATE DATABASE `{database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci')
            c.execute('SELECT VERSION() v')
            report['mysql_version'] = c.fetchone()['v']
            c.execute("SET time_zone='+07:00'")
        db.select_db(database)
        from tools.quyen_week1_evidence import execute_file
        report['import'] = []
        for name in ['schema.sql', 'seed.sql', 'audit.sql', 'constraints.sql', 'audit.sql', 'queries.sql']:
            sets = execute_file(db, name, require_empty=name == 'audit.sql')
            report['import'].append(dict(file=name, result_sets=len(sets)))
            if name == 'queries.sql':
                (OUT / 'queries-default.json').write_text(json.dumps(sets, ensure_ascii=False, indent=2, default=str), encoding='utf-8')
        with db.cursor() as c:
            c.execute('SHOW TABLES')
            report['table_count'] = len(c.fetchall())
            c.execute('SHOW TRIGGERS')
            report['trigger_count'] = len(c.fetchall())
        assert report['table_count'] == 11 and report['trigger_count'] == 9
        # Generated secrets remain only in the ignored, private source copy.
        envfile = source / '.env'
        envfile.write_text(f'FLASK_SECRET_KEY={secrets.token_hex(32)}\nFLASK_DEBUG=false\nCOOKIE_SECURE=false\n'
                           f'DB_HOST=127.0.0.1\nDB_PORT={db_port}\nDB_USER=root\nDB_PASSWORD={password}\nDB_NAME={database}\n', encoding='utf-8')
        env = {k: v for k, v in os.environ.items() if not k.startswith(('DB_', 'FLASK_', 'MYSQL_'))
               and k not in ('PYTHON_DOTENV_DISABLED', 'PYTHONPATH')}
        env.update(PYTHONIOENCODING='utf-8', PYTHONUTF8='1')
        command = [sys.executable, '-m', 'tools.audit_seed']
        completed = subprocess.run(command, cwd=source, env=env, capture_output=True, text=True, encoding='utf-8', check=True)
        audit = json.loads(completed.stdout)
        assert audit['total'] == 1144 and audit['matches_expected_counts'] and not any(audit['findings'].values())
        report['audit_command'] = command
        report['dotenv_verified_without_DB_environment'] = True
        (OUT / 'audit.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding='utf-8')
        # app.py fixes port 5000; use it when available, otherwise documented Flask CLI.
        if not is_open(5000):
            app_port = 5000
            command = [sys.executable, 'app.py']
        else:
            command = [sys.executable, '-m', 'flask', '--app', 'app', 'run', '--host', '127.0.0.1', '--port', str(app_port)]
        report.update(app_port=app_port, app_command=command)
        app_proc = subprocess.Popen(command, cwd=source, env=env, stdout=app_log, stderr=subprocess.STDOUT,
                                    creationflags=subprocess.CREATE_NO_WINDOW)
        base = f'http://127.0.0.1:{app_port}'
        for _ in range(80):
            if app_proc.poll() is not None:
                raise RuntimeError('Private app exited')
            try:
                with urlopen(base + '/health', timeout=1) as r:
                    assert r.status == 200
                break
            except OSError:
                time.sleep(.25)
        report['http'] = []
        routes = ['/health', '/health/db', '/patients', '/doctors', '/nurses', '/visits/new', '/reports',
                  '/reports/diseases?month=2026-10', '/reports/salaries?month=2026-10',
                  '/reports/revenue?month=2026-10', '/reports/history?patient_id=BN001']
        for route in routes:
            with urlopen(base + route, timeout=10) as response:
                body = response.read().decode('utf-8')
                assert response.status == 200
                row = dict(route=route, status=response.status)
                if route.startswith('/health'):
                    row['json'] = json.loads(body)
                    assert row['json']['status'] == 'ok'
                report['http'].append(row)
        report['success'] = True
    finally:
        if app_proc:
            app_proc.terminate()
            app_proc.wait(timeout=20)
        if db:
            try:
                with db.cursor() as c:
                    c.execute('SHUTDOWN')
            finally:
                db.close()
        if proc:
            try:
                proc.wait(timeout=30)
            except subprocess.TimeoutExpired:
                proc.terminate()
                proc.wait(timeout=20)
        log.close()
        app_log.close()
        if (source / '.env').exists():
            (source / '.env').unlink()
        report.update(db_port_closed=not is_open(db_port), app_port_closed=not is_open(app_port),
                      checkout_env_unchanged=(digest(ROOT / '.env') if (ROOT / '.env').exists() else None) == env_before,
                      old_evidence_unchanged=all(snapshot(ROOT / rel) == values for rel, values in protected.items()),
                      execution_source_unchanged=all(digest(ROOT / p) == h for p, h in selected.items()),
                      finished_at=datetime.now(timezone(timedelta(hours=7))).isoformat())
        (OUT / 'setup-results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    assert all(report[k] for k in ('success', 'db_port_closed', 'app_port_closed', 'checkout_env_unchanged',
                                  'old_evidence_unchanged', 'execution_source_unchanged'))
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
