from pathlib import Path
import subprocess, zipfile, io

repo=Path.cwd()
base=repo/'.venv/pr_review_20261019'
base.mkdir(exist_ok=True)
for pr,sha in [(5,'10c808238ef2f8f4f0a1aabcfc59da19079b38f8'),(10,'1bf9f8b18342eaf6d0097f3693df1bc02addfcfa')]:
    target=base/f'pr{pr}'
    target.mkdir(exist_ok=True)
    archive=subprocess.check_output(['git','archive','--format=zip',sha])
    with zipfile.ZipFile(io.BytesIO(archive)) as t: t.extractall(target)
    s=(repo/'tools/vuong_week2_prepare.py').read_text(encoding='utf-8')
    s=s.replace('ROOT = Path(__file__).resolve().parents[1]',f'ROOT = Path({str(target)!r})\nREPO = Path({str(repo)!r})')
    s=s.replace("out = ROOT / 'docs/evidence' / ('vuong_week2_prepare_' + stamp)",f"out = REPO / 'docs/evidence' / ('vuong_review_pr{pr}_' + stamp)")
    s=s.replace("subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()",repr(sha))
    s=s.replace("old_cache=ROOT / '.venv/week1_acceptance_20261018/browsers'","old_cache=REPO / '.venv/week1_acceptance_20261018/browsers'")
    s=s.replace("scope='Preparation baseline, not final week-2 acceptance'",f"scope='Review unmodified PR #{pr} head; runner only is external'")
    s=s.replace('[Path(__file__).resolve()] + list', '[] + list')
    s=s.replace('out.relative_to(ROOT)', 'out.relative_to(REPO)')
    if pr==10:
        s=s.replace("QUYEN_CHECK_WEEK2='1'", "QUYEN_CHECK_WEEK2='0'")
        s=s.replace("'-m', 'pytest', '-q', '-rA',","'-m', 'pytest', 'tests/test_quyen_database.py', 'tests/test_quyen_week2_reports.py', '-q', '-rA',")
        start=s.index('        from werkzeug.serving import make_server')
        end=s.index('        with app.app_context():',start)
        s=s[:start]+"        base = 'SQL-only exact PR10 head'\n"+s[end:]
    else:
        s=s.replace("heading=page.locator('h1').all_text_contents(),", "heading=page.locator('h1').all_text_contents(), title=page.title(), document_width=page.evaluate('document.documentElement.scrollWidth'), controls=page.locator('input,select,button').evaluate_all('(els)=>els.map(e=>({name:e.name,text:e.tagName,left:e.getBoundingClientRect().left,right:e.getBoundingClientRect().right})).filter(e=>e.right>innerWidth)'),")
        needle='            browser.close()'
        probes="""            report['json_probes']=[]
            for route in ['/reports/revenue?month=2026-10&format=json','/reports/revenue?month=2026-13&format=json','/reports/history?patient_id=MISSING&format=json']:
                r=page.request.get(base+route)
                report['json_probes'].append(dict(route=route,status=r.status,content_type=r.headers.get('content-type'),body=r.text()[:400]))
            report['missing_csrf_status']=page.request.post(base+'/visits/new',form={}).status
"""
        s=s.replace(needle,probes+needle)
    start=s.index("        assert all(x['status']")
    end=s.index("        report['preparation_success']",start)
    s=s[:start]+s[end:]
    (base/f'run_pr{pr}.py').write_text(s,encoding='utf-8')
print(base)
