"""Step-3 private DB/app; no UI automation or production configuration reads."""
import hashlib, json, os, secrets, socket, subprocess, sys, threading, time
from pathlib import Path
from datetime import datetime, timezone, timedelta
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
PRIVATE=ROOT/'.venv/week3-step4-retest-20261021'
sys.path.insert(0,str(ROOT))
os.chdir(ROOT)
def now(): return datetime.now(timezone(timedelta(hours=7))).isoformat()
def write(name,obj): (OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2,default=str),encoding='utf-8')
def free_port():
    with socket.socket() as s: s.bind(('127.0.0.1',0)); return s.getsockname()[1]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    PRIVATE.mkdir(parents=True,exist_ok=False)
    mysqld=ROOT/'.venv/week3-tools/mysql84/mysql-8.4.7-winx64/bin/mysqld.exe'
    data=PRIVATE/'mysql-data'; port=free_port()
    before_env=sha(ROOT/'.env') if (ROOT/'.env').exists() else None
    files=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')
    files += ['clinic_app/static/number-validation.js', 'tests/test_vuong_week3_numeric_validation.py']
    manifest={p:sha(ROOT/p) for p in files if p and not p.startswith('docs/evidence/')}
    write('execution_source_sha256.json',manifest)
    log=(OUT/'mysql-console.txt').open('w',encoding='utf-8')
    subprocess.run([str(mysqld),'--no-defaults','--initialize-insecure',f'--datadir={data}'],stdout=log,stderr=subprocess.STDOUT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
    proc=subprocess.Popen([str(mysqld),'--no-defaults',f'--datadir={data}','--bind-address=127.0.0.1',f'--port={port}','--mysqlx=0','--skip-log-bin'],stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    import pymysql
    db=None; server=None
    metadata=dict(started_at=now(),source_sha=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),branch='vuong/week-3',executor='Trợ lý Codex thay mặt Vương',method='Interactive browser through cua_repl; SQL fixtures and read-only oracle logged separately',python=sys.version,mysqld=str(mysqld),datadir=str(data),mysql_port=port,database='clinic_vuong_week3_step4_test')
    try:
        for _ in range(120):
            try: db=pymysql.connect(host='127.0.0.1',port=port,user='root',autocommit=True,charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor); break
            except pymysql.OperationalError: time.sleep(.25)
        assert db is not None
        password=secrets.token_hex(24)
        with db.cursor() as cur:
            cur.execute("ALTER USER 'root'@'localhost' IDENTIFIED BY %s",(password,))
            cur.execute('CREATE DATABASE clinic_vuong_week3_step4_test CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci')
            cur.execute('SELECT VERSION() version'); metadata['mysql']=cur.fetchone()['version']
        db.select_db(metadata['database'])
        os.environ.update(DB_HOST='127.0.0.1',DB_PORT=str(port),DB_USER='root',DB_PASSWORD=password,DB_NAME=metadata['database'],FLASK_SECRET_KEY=secrets.token_hex(32),COOKIE_SECURE='false',FLASK_DEBUG='false',PYTHON_DOTENV_DISABLED='1')
        from tools.quyen_week1_evidence import execute_file
        metadata['imports']=[]
        for name in ['schema.sql','seed.sql','audit.sql','constraints.sql','audit.sql','queries.sql']:
            result=execute_file(db,name,require_empty=name=='audit.sql');metadata['imports'].append(dict(file=name,result_sets=len(result)))
        from tools.audit_seed import audit,EXPECTED
        from clinic_app import create_app
        app=create_app()
        def rows():
            output={}
            with db.cursor() as cur:
                for table in EXPECTED:
                    cur.execute(f'SELECT * FROM `{table}`')
                    output[table]=cur.fetchall()
            return output
        seed=rows()
        with app.app_context(): write('audit-before.json',audit())
        with db.cursor() as cur:
            cur.execute("INSERT INTO benh VALUES ('U3B1','Bệnh giả kiểm thử UI tuần 3 A'),('U3B2','Bệnh giả kiểm thử UI tuần 3 B')")
            cur.execute("INSERT INTO thuoc VALUES ('U3T1','Thuốc giả UI 1','viên',1000),('U3T2','Thuốc giả UI 2','viên',2000)")
        write('sql-fixtures.json',dict(method='Direct SQL setup only; not UI',diseases=['U3B1','U3B2'],medicines=[dict(id='U3T1',price=1000),dict(id='U3T2',price=2000)]))
        from werkzeug.serving import make_server
        server=make_server('127.0.0.1',0,app,threaded=True)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        metadata['url']=f'http://127.0.0.1:{server.server_port}'
        write('session.json',metadata);print(metadata['url'],flush=True)
        request=PRIVATE/'request.json'
        while True:
            if not request.exists(): time.sleep(.2);continue
            job=json.loads(request.read_text(encoding='utf-8'));request.unlink()
            if job['action']=='stop': break
            result=dict(at=now(),method='Direct SQL; not UI',request=job)
            try:
                with db.cursor() as cur:
                    if job['action']=='query':
                        assert job['sql'].lstrip().upper().startswith(('SELECT ','SHOW '))
                        cur.execute(job['sql'],job.get('params',()));result['rows']=cur.fetchall()
                    elif job['action']=='price':
                        cur.execute("UPDATE thuoc SET gia_hien_tai=9999 WHERE ma_thuoc='U3T1'");result['affected']=cur.rowcount
                    elif job['action']=='reports':
                        result['sets']=[]
                        from tools.quyen_db import statements
                        for sql in statements((ROOT/'database/queries.sql').read_text(encoding='utf-8')):
                            if sql.startswith('SET @ma_benh_nhan'): cur.execute('SET @ma_benh_nhan=%s',(job.get('patient','BN001'),))
                            elif sql.startswith('SET @thang'): cur.execute('SET @thang=%s',(job.get('month','2026-10')+'-01',))
                            else: cur.execute(sql)
                            if cur.description: result['sets'].append(cur.fetchall())
                    else: raise ValueError('Unsupported task command')
            except Exception as exc: result['error']=str(exc)
            write(job['output'],result)
    finally:
        if server: server.shutdown();server.server_close()
        if db:
            with app.app_context(): write('audit-after.json',audit())
            final=rows()
            def normalized(row): return json.dumps(row,sort_keys=True,default=str)
            preserved={table:set(map(normalized,original)).issubset(set(map(normalized,final[table]))) for table,original in seed.items()}
            metadata['seed_rows_unchanged']=preserved
            metadata['source_unchanged']=all(sha(ROOT/p)==h for p,h in manifest.items())
            metadata['env_unchanged']=(sha(ROOT/'.env') if (ROOT/'.env').exists() else None)==before_env
            try:
                with db.cursor() as cur: cur.execute('SHUTDOWN')
            except pymysql.OperationalError: pass
            db.close()
        proc.wait(timeout=25)
        log.close()
        metadata['finished_at']=now();metadata['private_mysql_parent_exit']=proc.returncode
        write('session.json',metadata)
if __name__=='__main__': main()
