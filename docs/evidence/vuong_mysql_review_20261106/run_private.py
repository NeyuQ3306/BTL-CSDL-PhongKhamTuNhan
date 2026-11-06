"""Reproduce Vuong's desktop review on a fresh private MySQL instance only.
Run: .venv/Scripts/python.exe docs/evidence/vuong_mysql_review_20261106/run_private.py
No .env credentials are loaded. Existing services/data are never touched.
"""
import os, sys, json, hashlib, secrets, socket, subprocess, time, logging, io
from pathlib import Path
from datetime import datetime, timezone, timedelta
import xml.etree.ElementTree as ET
ROOT = Path(__file__).resolve().parents[3]
OUT = Path(os.environ.get('VUONG_EVIDENCE_OUTPUT', ROOT / 'test-artifacts' / 'vuong-mysql-review' / datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f')))
OUT.mkdir(parents=True, exist_ok=True)
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))
def save(name, data):
    (OUT/name).write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str)+'\n', encoding='utf-8')
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args): return subprocess.check_output(['git',*args], text=True).strip()
def main():
    stamp=datetime.now(timezone(timedelta(hours=7))).strftime('%Y%m%d_%H%M%S_%f')
    private=ROOT/'.venv'/('vuong_analytics_'+stamp)
    private.mkdir()
    data=private/'mysql-data'
    mysqld=Path('C:/Program Files/MySQL/MySQL Server 8.0/bin/mysqld.exe')
    assert mysqld.is_file()
    with socket.socket() as sock:
        sock.bind(('127.0.0.1',0)); port=sock.getsockname()[1]
    report=dict(run_at=stamp,source_sha=git('rev-parse','HEAD'),origin_main=git('rev-parse','origin/main'),
        branch=git('branch','--show-current'),python=sys.version,private_datadir=str(data),mysql_port=port,
        database='clinic_vuong_analytics_test',scope='Local desktop MySQL review; not Quyen laptop/group acceptance',
        success=False,phases=[])
    env_hash=digest(ROOT/'.env')
    os.environ.update(PYTHON_DOTENV_DISABLED='1',PYTHONIOENCODING='utf-8',DB_HOST='127.0.0.1',DB_PORT=str(port),
        DB_USER='root',DB_NAME=report['database'],DB_PASSWORD=secrets.token_hex(24),FLASK_SECRET_KEY=secrets.token_hex(32),
        COOKIE_SECURE='false',FLASK_DEBUG='false',RUN_MYSQL_TESTS='1',RUN_BROWSER_TESTS='1',QUYEN_CHECK_WEEK2='1',
        VUONG_ACCEPTANCE_RUN=stamp,GITHUB_SHA=report['source_sha'])
    cache=ROOT/'.venv/week1_acceptance_20261018/browsers'
    if cache.is_dir(): os.environ['PLAYWRIGHT_BROWSERS_PATH']=str(cache)
    proc=db=None
    console=(private/'console.log').open('wb')
    def snapshot():
        db.rollback()
        from tools.analytics_oracle import seed_rows, canonical
        result={}
        with db.cursor() as c:
            for table, wanted in seed_rows().items():
                c.execute('SELECT * FROM `'+table+'`')
                actual=canonical(c.fetchall())
                assert actual==canonical(wanted), 'Seed mismatch: '+table
                result[table]=hashlib.sha256(json.dumps(actual,default=str,sort_keys=True).encode()).hexdigest()
        db.rollback()
        return result
    def phase(name, args, timeout=900):
        print('Running '+name,flush=True)
        with (OUT/(name+'.txt')).open('w',encoding='utf-8') as log:
            done=subprocess.run([sys.executable,*args],stdout=log,stderr=subprocess.STDOUT,timeout=timeout)
        entry=dict(name=name,exit_code=done.returncode,seed_unchanged=snapshot()==baseline)
        xml=OUT/(name+'.xml')
        if xml.exists():
            suites=list(ET.parse(xml).getroot().iter('testsuite'))
            entry['counts']={k:sum(int(s.attrib.get(k,0)) for s in suites) for k in ['tests','failures','errors','skipped']}
            entry['counts']['passed']=entry['counts']['tests']-sum(entry['counts'][k] for k in ['failures','errors','skipped'])
        report['phases'].append(entry)
        save('results.json',report)
        print(entry,flush=True)
        return done.returncode==0 and entry['seed_unchanged']
    try:
        subprocess.run([str(mysqld),'--no-defaults','--initialize-insecure','--datadir='+str(data)],stdout=console,stderr=subprocess.STDOUT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
        proc=subprocess.Popen([str(mysqld),'--no-defaults','--datadir='+str(data),'--bind-address=127.0.0.1','--port='+str(port),'--mysqlx=0','--skip-log-bin','--log-error='+str(data/'server-error.txt')],stdout=console,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        import pymysql
        for _ in range(100):
            if proc.poll() is not None: raise RuntimeError('Private MySQL exited')
            try:
                db=pymysql.connect(host='127.0.0.1',port=port,user='root',autocommit=True,cursorclass=pymysql.cursors.DictCursor)
                break
            except pymysql.OperationalError: time.sleep(.25)
        if db is None: raise RuntimeError('Private MySQL startup timeout')
        with db.cursor() as c:
            c.execute("ALTER USER 'root'@'localhost' IDENTIFIED BY %s",(os.environ['DB_PASSWORD'],))
            c.execute('CREATE DATABASE `clinic_vuong_analytics_test` CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci')
            c.execute('SELECT VERSION() version, @@datadir datadir, @@port port'); report['mysql']=c.fetchone()
        db.select_db(report['database'])
        from tools.quyen_db import install
        install(db)
        baseline=snapshot(); save('seed-before.json',baseline)
        files=list((ROOT/'clinic_app').rglob('*'))+list((ROOT/'tests').glob('*.py'))+list((ROOT/'database').glob('*'))+list((ROOT/'tools').glob('*.py'))+[Path(__file__)]
        save('source-sha256.json',{p.relative_to(ROOT).as_posix():digest(p) for p in files if p.is_file() and '__pycache__' not in p.parts})
        ok=phase('sql-oracle',['-m','tools.analytics_evidence','--output',str(OUT/'sql-expected-actual.json')])
        # Exclude historical mobile-only/mixed tests; retain desktop clinical, API, SQL, Q1-Q4 and stub UI regression.
        deselected=['tests/test_browser_vuong_reports.py::test_seed_reports_ui_json_sql_expected','tests/test_vuong_acceptance.py::test_acceptance_browser_t01_t04_t08_t12_t14_t15']
        args=['-m','pytest','tests','week3_checks','-q','-ra','--junitxml='+str(OUT/'regression.xml'),
            '--ignore=tests/test_browser_vuong_week2.py','--ignore=tests/test_vuong_week3_numeric_validation.py',
            '--ignore=tests/test_vuong_analytics_mysql_ui.py']+['--deselect='+x for x in deselected]
        report['excluded_mobile']=['tests/test_browser_vuong_week2.py','tests/test_vuong_week3_numeric_validation.py',*deselected]
        ok=phase('regression',args) and ok
        test=ROOT/'tests/test_vuong_analytics_mysql_ui.py'
        if test.exists():
            ok=phase('mysql-ui',['-m','pytest',str(test),'-q','-ra','--junitxml='+str(OUT/'mysql-ui.xml')]) and ok
        else:
            report['mysql_ui_pending']=True; ok=False
        from clinic_app import create_app
        from tools.audit_seed import audit
        app=create_app({'TESTING':True})
        with app.app_context(): report['audit']=audit()
        # Repeated GET-only checks of original failure routes while the actual private DB is alive.
        stream=io.StringIO(); handler=logging.StreamHandler(stream); app.logger.addHandler(handler)
        checks=[]
        client=app.test_client()
        routes=['/health/db','/reports/diseases?month=2026-10','/reports/history?patient_id=BN001','/api/analytics']
        for index in range(15):
            for route in routes:
                response=client.get(route)
                checks.append(dict(iteration=index+1,route=route,expected=200,actual=response.status_code,time=datetime.now(timezone.utc).isoformat()))
        app.logger.removeHandler(handler)
        report['w3_db_01']=dict(checks=len(checks),unexpected=[x for x in checks if x['actual']!=200],mysql_2003_observed='2003' in stream.getvalue(),conclusion='Not reproduced locally; remains open pending original laptop verification')
        save('w3-db-01-read-checks.json',checks)
        (OUT/'app-read-checks.txt').write_text(stream.getvalue(),encoding='utf-8')
        after=snapshot();save('seed-after.json',after)
        report['seed_unchanged']=baseline==after
        report['success']=ok and baseline==after and not report['w3_db_01']['unexpected'] and report['audit']['matches_expected_counts'] and not any(report['audit']['findings'].values())
    except BaseException as exc:
        report['failure_type']=type(exc).__name__
        raise
    finally:
        from tools.private_mysql_cleanup import stop_private_mysql
        report['cleanup']=stop_private_mysql(proc,db,mysqld,data,port)
        console.close()
        report['env_unchanged']=digest(ROOT/'.env')==env_hash
        if not report['cleanup']['success'] or not report['env_unchanged']: report['success']=False
        save('results.json',report)
        print('Evidence: '+str(OUT)+'; success='+str(report['success']),flush=True)
if __name__=='__main__': main()
