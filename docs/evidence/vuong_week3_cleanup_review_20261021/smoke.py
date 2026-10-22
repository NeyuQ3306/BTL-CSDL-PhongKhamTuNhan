"""Reproduce private cleanup success and injected lost-connection failure."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import psutil

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
os.chdir(ROOT)

def mysql_inventory():
    rows=[]
    for p in psutil.process_iter():
        try:
            if p.name().lower() != 'mysqld.exe':
                continue
            args=p.cmdline()
            data=next((a.split('=',1)[1] for a in args if a.startswith('--datadir=')),None)
            rows.append(dict(pid=p.pid,created=p.create_time(),executable=p.exe(),datadir=data))
        except (psutil.Error,OSError):
            pass
    return sorted(rows,key=lambda x:x['pid'])

before=mysql_inventory()
results=[]
for case in ['success','error']:
    existing=set((ROOT/'docs/evidence').glob('vuong_week3_demo_*'))
    command=[sys.executable,'tools/vuong_week3_demo.py','--rehearse','--cleanup-check',case]
    result=subprocess.run(command,capture_output=True,text=True,encoding='utf-8',env={**os.environ,'PYTHONIOENCODING':'utf-8'})
    (OUT/f'smoke-{case}.txt').write_text(result.stdout+result.stderr,encoding='utf-8')
    fresh=set((ROOT/'docs/evidence').glob('vuong_week3_demo_*'))-existing
    assert len(fresh)==1
    folder=fresh.pop()
    session=json.loads((folder/'session.json').read_text(encoding='utf-8'))
    assert result.returncode==(0 if case=='success' else 1)
    assert session['success']==(case=='success')
    assert session['workload_success']==(case=='success')
    assert session['mysql_cleanup']['success']
    assert session['mysql_cleanup']['remaining_pids']==[]
    assert session['mysql_port_closed'] and session['log_closed']
    assert session['old_evidence_unchanged'] and session['checkout_env_unchanged']
    if case=='error':
        assert session['failure']['type']=='RuntimeError'
        assert not session['mysql_cleanup']['shutdown_requested']
        assert session['mysql_cleanup']['fallback_pids']
    results.append(dict(case=case,exit_code=result.returncode,evidence=str(folder.relative_to(ROOT)),session=session))
after=mysql_inventory()
assert before==after, 'Unrelated MySQL inventory changed'
(OUT/'smoke-results.json').write_text(json.dumps(dict(command_python=sys.executable,smoke_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),before=before,after=after,unrelated_mysql_unchanged=before==after,runs=results),ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps([dict(case=x['case'],exit=x['exit_code'],evidence=x['evidence'],cleanup=x['session']['mysql_cleanup']) for x in results],indent=2))
