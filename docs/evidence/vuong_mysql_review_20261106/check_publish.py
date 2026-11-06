"""Recheck only changed MySQL UI tests, retaining the original 442-case regression.
Run normally for the named private DB; add --ci-db to verify NULL-fixture skip.
"""
from pathlib import Path
import sys, hashlib, json
p=Path(__file__).with_name('run_private.py').resolve()
s=p.read_text(encoding='utf-8-sig')
ci='--ci-db' in sys.argv
folder='prepublish-ci' if ci else 'prepublish'
out=p.parent/folder
out.mkdir(exist_ok=True)
s=s.replace('OUT = Path(__file__).resolve().parent', "OUT = Path(__file__).resolve().parent / '"+folder+"'")
s=s.replace("        ok=phase('regression',args) and ok", "        # Existing 442-case regression retained; changed MySQL module runs below.")
if ci: s=s.replace('clinic_vuong_analytics_test','clinic_vuong_analytics_ci_test')
(out/'runner-variant.json').write_text(json.dumps(dict(base_runner_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),executed_variant_sha256=hashlib.sha256(s.encode()).hexdigest(),omit_unchanged_regression=True,ci_database_name=ci),indent=2)+'\n',encoding='utf-8')
exec(compile(s,str(p),'exec'),{'__name__':'__main__','__file__':str(p)})
