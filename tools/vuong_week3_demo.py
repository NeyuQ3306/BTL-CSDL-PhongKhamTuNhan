"""Fresh local demo instance. Never reads the working .env or connects to its DB.

--rehearse performs an automated Chromium rehearsal; --serve keeps a fresh seed
instance for the group until Ctrl+C. Every invocation creates a new datadir.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import secrets
import socket
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone, timedelta

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.private_mysql_cleanup import stop_private_mysql


def now():
    return datetime.now(timezone(timedelta(hours=7))).isoformat()


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def snapshot(folder):
    return {str(p.relative_to(folder)).replace('\\', '/'): digest(p)
            for p in folder.rglob('*') if p.is_file()}


def write(out, name, data):
    (out / name).write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str), encoding='utf-8')


def port_open(port):
    with socket.socket() as s:
        s.settimeout(1)
        return s.connect_ex(('127.0.0.1', port)) == 0


def finish_session(out, report, *, proc, db, server, thread, log, executable,
                   data, port, old_env, manifest, protected):
    """Attempt every cleanup stage; retain workload failure and record recovery."""
    errors = []

    def attempt(stage, action):
        try:
            return action()
        except Exception as exc:
            # Exception messages may include credentials; record only their type.
            errors.append(dict(stage=stage, type=type(exc).__name__))
            return None

    report['workload_success'] = report['success']
    if server is not None:
        if thread is not None and thread.is_alive():
            attempt('app_shutdown', server.shutdown)
        attempt('app_close', server.server_close)
        if thread is not None:
            attempt('app_join', lambda: thread.join(timeout=5))
    cleanup = attempt('mysql_cleanup', lambda: stop_private_mysql(
        proc, db, executable, data, port))
    report['mysql_cleanup'] = cleanup or dict(success=False)
    if log is not None:
        attempt('log_close', log.close)
    report['log_closed'] = log is None or log.closed
    checks = dict(
        mysql_port_closed=lambda: not port_open(port),
        app_port_closed=lambda: not port_open(server.server_port) if server is not None else True,
        app_thread_stopped=lambda: thread is None or not thread.is_alive(),
        checkout_env_unchanged=lambda: (digest(ROOT/'.env') if (ROOT/'.env').exists() else None) == old_env,
        source_unchanged=lambda: all(digest(ROOT/p) == h for p, h in manifest.items()),
        old_evidence_unchanged=lambda: all(snapshot(ROOT/rel) == values for rel, values in protected.items()))
    for key, check in checks.items():
        report[key] = attempt(key, check) is True
    report.update(finished_at=now(), cleanup_errors=errors)
    report['success'] = bool(report['workload_success'] and not errors
                             and report['mysql_cleanup']['success']
                             and report['log_closed'] and all(report[k] for k in checks))
    write(out, 'session.json', report)
    print(json.dumps({k: report.get(k) for k in [
        'success', 'workload_success', 'failure', 'mysql_cleanup', 'cleanup_errors',
        'log_closed', *checks]}, ensure_ascii=False), flush=True)


def expected():
    return dict(seed=dict(episodes=24, doctors=78000000, nurses=65600000,
                          consultation=4680000, medicine=5820800, revenue=10500800),
                demo={'2004-02': dict(episodes=1, consultation=100000, medicine=0, revenue=100000,
                                     doctor=7000000, nurse1=5200000, nurse2=5000000),
                      '2004-03': dict(episodes=3, consultation=250000, medicine=9900, revenue=259900,
                                     doctor=8000000, nurse1=5400000, nurse2=5200000)},
                history=dict(visits=3, treatments=3, current=2, examinations=4, medicines=2, support=4),
                prescription=9900, temporary_staff_remaining=0)


def rehearse(app, base, db, out, report):
    from playwright.sync_api import sync_playwright, expect
    from clinic_app.entities import ENTITIES
    from tools.quyen_db import statements
    wanted = expected()
    write(out, 'expected.json', wanted)  # before browser mutations
    steps = []
    report['steps'] = steps
    start = time.perf_counter()

    def sql_report(patient, month):
        sets = []
        with db.cursor() as c:
            for sql in statements((ROOT / 'database/queries.sql').read_text(encoding='utf-8')):
                if sql.startswith('SET @ma_benh_nhan'):
                    c.execute('SET @ma_benh_nhan=%s', (patient,))
                elif sql.startswith('SET @thang'):
                    c.execute('SET @thang=%s', (month + '-01',))
                else:
                    c.execute(sql)
                if c.description:
                    sets.append(c.fetchall())
        return sets

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        report['chromium'] = browser.version
        page = browser.new_page(viewport=dict(width=1440, height=1000), locale='vi-VN')
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        shots = []
        report['screenshots'] = shots

        def shot(name):
            page.screenshot(path=str(out / (name + '.png')), full_page=True)
            overflow = page.evaluate('document.documentElement.scrollWidth > innerWidth')
            shots.append(dict(file=name + '.png', url=page.url, width=page.viewport_size['width'], overflow=overflow))
            assert not overflow

        def mark(name, actual):
            steps.append(dict(step=name, elapsed_seconds=round(time.perf_counter()-start, 3), actual=actual, status='PASS'))

        def fill(values):
            for key, value in values.items():
                item = page.locator(f'[name="{key}"]')
                if item.evaluate('(el)=>el.tagName') == 'SELECT':
                    item.select_option(value)
                else:
                    item.fill(value)

        def save():
            page.get_by_role('button', name='Lưu', exact=True).click()

        def get(route):
            assert page.goto(base + route).status == 200

        def api(route):
            r = page.request.get(base + route)
            assert r.status == 200
            return r.json()

        get('/health/db')
        mark('01-introduction', 'Private MySQL health OK; no group presentation')
        # CRUD all three groups; retain only the main demo patient.
        for slug, key, cmt in [('patients', 'DM6TMPBN', '999000006001'),
                               ('doctors', 'DM6TMPBS', '999000006002'),
                               ('nurses', 'DM6TMPYT', '999000006003')]:
            get(f'/{slug}/new')
            entity = ENTITIES[slug]
            fields = {f.name: 'Dữ liệu giả demo' for f in entity.fields}
            fields.update({entity.pk:key, 'cmt':cmt, 'ngay_sinh':'1980-01-01',
                           'so_dien_thoai':'0900000006', 'tham_nien':'4'})
            fill({f.name:fields[f.name] for f in entity.fields})
            page.get_by_role('button', name='Thêm hồ sơ', exact=True).click()
            expect(page).to_have_url(base+f'/{slug}/{key}')
            get(f'/{slug}/{key}/edit')
            fill({'dia_chi':'Địa chỉ đã sửa trong demo'})
            page.get_by_role('button', name='Lưu thay đổi', exact=True).click()
            page.reload()
            expect(page.get_by_text('Địa chỉ đã sửa trong demo', exact=True)).to_be_visible()
            shot('02-crud-' + slug)
            page.locator('summary').click()
            fill({'confirm_delete': key})
            page.get_by_role('button', name='Xác nhận xóa', exact=True).click()
            expect(page).to_have_url(base + '/' + slug)
            assert page.request.get(base+f'/{slug}/{key}').status == 404
        get('/patients/new')
        fill(dict(ma_benh_nhan='DM6BN', cmt='999000006004', ho_ten='Bệnh nhân demo tuần 3',
                  ngay_sinh='1980-01-01', dia_chi='Hà Nội', so_dien_thoai='0900000006'))
        page.get_by_role('button', name='Thêm hồ sơ', exact=True).click()
        expect(page).to_have_url(base+'/patients/DM6BN')
        mark('02-CRUD', 'Create/read/update/reload/delete patients/doctors/nurses; DM6BN retained')

        def reception(n, when, episode, mode='new'):
            get('/visits/new')
            fill(dict(ma_luot=f'DM6L{n}', ma_benh_nhan='DM6BN', ngay_vao_vien=when, che_do_dot=mode,
                      ma_lan_kham=f'DM6K{n}', ngay_kham=when, tien_kham_chua='100000',
                      ket_luan='Theo dõi demo', ma_y_ta='YT001', ngay_ho_tro=when, noi_dung_ho_tro='Tiếp đón demo'))
            if mode == 'new':
                fill(dict(ma_dot=episode, ma_benh='B001', ma_bac_si='BS001'))
            else:
                page.locator('#episode-picker').select_option(episode)
            save()
            expect(page).to_have_url(base+f'/visits/DM6L{n}')

        def close(n, when):
            get(f'/visits/DM6L{n}/close')
            fill(dict(ngay_ra_vien=when)); save()
            expect(page).to_have_url(base+f'/visits/DM6L{n}')

        reception(1, '2004-02-28', 'DM6D1')
        close(1, '2004-02-28')
        reception(2, '2004-03-01', 'DM6D1', 'existing')
        shot('03-revisit-across-month')
        mark('03-reception-revisit', 'DM6D1: two visits across February/March, STT checked later in SQL')
        page.get_by_role('link', name='Cập nhật hỗ trợ YT001', exact=True).click()
        fill(dict(noi_dung_ho_tro='Đo huyết áp và theo dõi demo')); save()
        page.get_by_role('link', name='Ghi hỗ trợ y tá', exact=True).click()
        fill(dict(ma_y_ta='YT002', ngay_ho_tro='2004-03-01', noi_dung_ho_tro='Hỗ trợ thêm demo')); save()
        shot('04-nurse-support')
        mark('04-support', 'Updated YT001 without duplicate; added YT002')
        get('/examinations/DM6K2/prescription')
        fill(dict(ma_don='DM6RX'))
        for i, medicine, quantity, usage in [(0, 'T001', '2', 'Sáng'), (1, 'T002', '3', 'Tối')]:
            page.locator('[name="ma_thuoc"]').nth(i).select_option(medicine)
            page.locator('[name="so_luong"]').nth(i).fill(quantity)
            page.locator('[name="lieu_dung"]').nth(i).fill(usage)
        page.get_by_role('button', name='Thêm dòng thuốc', exact=True).click()
        page.get_by_role('button', name='Xóa dòng 4', exact=True).click()
        save()
        expect(page.get_by_role('heading', name='Tổng: 9.900 đ', exact=True)).to_be_visible()
        shot('05-prescription')
        mark('05-prescription', '2*1200 + 3*2500 = 9900; add/delete empty medicine row works')
        close(2, '2004-03-01')
        get('/treatments/DM6D1/cure')
        fill(dict(ngay_khoi='2004-03-01')); save()
        expect(page).to_have_url(base+'/treatments')
        reception(3, '2004-03-02', 'DM6D2')
        page.get_by_role('link', name='Khám thêm bệnh', exact=True).click()
        fill(dict(che_do_dot='new', ma_dot='DM6D3', ma_benh='B002', ma_bac_si='BS001',
                  ma_lan_kham='DM6K4', ngay_kham='2004-03-02', tien_kham_chua='50000', ket_luan='Bệnh thứ hai demo'))
        save()
        expect(page).to_have_url(base+'/visits/DM6L3')
        shot('06-recurrence-two-diseases')
        close(3, '2004-03-02')
        shot('07-closed-visit')
        mark('06-close-cure-recurrence', 'DM6D1 cured; DM6D2/DM6D3 active; all three visits closed')
        # Reports after writes: no seed staff remain from CRUD; 2004 writes cannot affect Oct 2026.
        parity = []
        for month in ['2026-10', '2004-02', '2004-03', '2025-12']:
            disease = api(f'/reports/diseases?month={month}&format=json')
            salary = api(f'/reports/salaries?month={month}&format=json')
            revenue = api(f'/reports/revenue?month={month}&format=json')
            sets = sql_report('BN001' if month == '2026-10' else 'DM6BN', month)
            actual = dict(episodes=disease['total'], consultation=int(revenue['consultation']),
                          medicine=int(revenue['medicine']), revenue=int(revenue['total']))
            assert actual['episodes'] == sum(x['so_dot_mac'] for x in sets[0])
            assert dict(tien_kham=actual['consultation'], tien_thuoc=actual['medicine'], doanh_thu=actual['revenue']) == sets[10][0]
            for kind, index, pk in [('doctors',1,'ma_bac_si'), ('nurses',2,'ma_y_ta')]:
                assert {x['ma_nhan_vien']:int(x['tong_luong']) for x in salary[kind]} == {x[pk]:int(x['tong_luong']) for x in sets[index]}
            if month == '2026-10':
                actual.update(doctors=sum(int(x['tong_luong']) for x in salary['doctors']),
                              nurses=sum(int(x['tong_luong']) for x in salary['nurses']))
                assert actual == wanted['seed']
            elif month in wanted['demo']:
                actual.update(doctor=next(int(x['tong_luong']) for x in salary['doctors'] if x['ma_nhan_vien']=='BS001'),
                              nurse1=next(int(x['tong_luong']) for x in salary['nurses'] if x['ma_nhan_vien']=='YT001'),
                              nurse2=next(int(x['tong_luong']) for x in salary['nurses'] if x['ma_nhan_vien']=='YT002'))
                assert actual == wanted['demo'][month]
            else:
                assert actual == dict(episodes=0, consultation=0, medicine=0, revenue=0)
            for kind in ['diseases', 'salaries', 'revenue']:
                get(f'/reports/{kind}?month={month}')
                if kind == 'diseases':
                    expect(page.locator('[data-report-total]')).to_have_text(str(disease['total']))
                elif kind == 'salaries':
                    for group in ['doctors','nurses']:
                        amount = sum(int(x['tong_luong']) for x in salary[group])
                        expect(page.locator(f'[data-salary-total="{group}"]')).to_have_text(f'{amount:,}'.replace(',', '.') + ' đ')
                else:
                    expect(page.locator('[data-revenue="total"]')).to_have_text(f'{actual["revenue"]:,}'.replace(',', '.') + ' đ')
                shot(f'08-{month}-{kind}')
            parity.append(dict(month=month, actual=actual, ui_json_sql_expected='PASS'))
            write(out, 'sql-'+month+'.json', sets)
        history = api('/reports/history?patient_id=DM6BN&format=json')
        actual = {key:len(history[key]) for key in wanted['history']}
        assert actual == wanted['history']
        sets = sql_report('DM6BN', '2004-03')
        assert [len(x) for x in sets[3:10]] == [1,3,3,2,4,2,4]
        assert sorted(x['so_thu_tu_trong_dot'] for x in history['examinations'] if x['ma_dot']=='DM6D1') == [1,2]
        get('/reports/history?patient_id=BN001'); shot('09-seed-history')
        get('/reports/history?patient_id=DM6BN'); shot('10-demo-history')
        write(out, 'report-parity.json', dict(months=parity, history_actual=actual, history=history))
        mark('07-four-reports', 'UI/JSON/canonical SQL/independent expected match; seed October unchanged after demo writes')
        # Last demo operation: server validation, not bypassing native browser constraints.
        get('/visits/new')
        fill(dict(ma_luot='DM6BADL', ma_benh_nhan='DM6BN', ngay_vao_vien='2004-03-03', che_do_dot='new',
                  ma_dot='DM6BAD', ma_benh='B001', ma_bac_si='BS001', ma_lan_kham='DM6BADK',
                  ngay_kham='2004-03-03', tien_kham_chua='100000', ket_luan='Thử nhập sai',
                  ma_y_ta='YT001', ngay_ho_tro='2004-03-03', noi_dung_ho_tro='Thử lỗi nghiệp vụ'))
        save()
        expect(page.get_by_role('alert')).to_contain_text('Bệnh đã có đợt đang điều trị')
        expect(page.locator('[name="ma_luot"]')).to_have_value('DM6BADL')
        shot('11-error-preserves-input')
        with db.cursor() as c:
            c.execute("SELECT COUNT(*) n FROM luot_den_kham WHERE ma_luot='DM6BADL'")
            assert c.fetchone()['n'] == 0
        page.set_viewport_size(dict(width=390, height=900))
        get('/reports/history?patient_id=DM6BN'); shot('12-mobile-history-390')
        assert not errors, errors
        mark('08-invalid-input', 'Active duplicate episode rejected in Vietnamese; input retained; no DM6BADL saved')
        report.update(rehearsal_seconds=round(time.perf_counter()-start, 3), browser_errors=errors,
                      timing_kind='Automated browser actions including screenshots/SQL; no human speech or group timing')
        browser.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--rehearse', action='store_true')
    mode.add_argument('--serve', action='store_true')
    parser.add_argument('--cleanup-check', choices=['success', 'error'],
                        help='Private DB startup/cleanup smoke only; error injects a lost connection')
    parser.add_argument('--mysqld', type=Path, default=ROOT / '.venv/week3-tools/mysql84/mysql-8.4.7-winx64/bin/mysqld.exe')
    parser.add_argument('--browsers-path', type=Path, default=ROOT / '.venv/week3-tools/browsers')
    args = parser.parse_args()
    os.chdir(ROOT)
    stamp = datetime.now(timezone(timedelta(hours=7))).strftime('%Y%m%d_%H%M%S_%f')
    out = ROOT / 'docs/evidence' / ('vuong_week3_demo_' + stamp)
    protected = {str(p.relative_to(ROOT)):snapshot(p) for p in (ROOT/'docs/evidence').iterdir() if p.is_dir()}
    out.mkdir()
    work = ROOT / '.venv' / ('week3-demo-' + stamp)
    work.mkdir()
    old_env = digest(ROOT/'.env') if (ROOT/'.env').exists() else None
    manifest = json.loads((ROOT/'docs/evidence/vuong_week3_step5_20261021/execution_source_sha256.json').read_text())
    # Development dependency changed deliberately for the scoped cleanup helper.
    # Keep the accepted application/SQL/browser sources guarded by their old hashes.
    assert all(digest(ROOT/p)==h for p,h in manifest.items() if p != 'requirements-dev.txt'), 'App source differs from accepted candidate; review first'
    for rel in ['tools/vuong_week3_demo.py', 'tools/private_mysql_cleanup.py',
                'requirements-dev.txt', 'tests/test_vuong_week3_cleanup.py']:
        manifest[rel] = digest(ROOT/rel)
    write(out, 'execution_source_sha256.json', manifest)
    (out/'source.diff').write_bytes(subprocess.check_output(['git','diff','HEAD','--','clinic_app','tests'],cwd=ROOT))
    for rel in ['clinic_app/static/number-validation.js', 'tests/test_vuong_week3_numeric_validation.py', 'tools/vuong_week3_demo.py']:
        r = subprocess.run(['git','diff','--no-index','--','/dev/null',rel],cwd=ROOT,capture_output=True)
        assert r.returncode in (0,1)
        with (out/'source.diff').open('ab') as f: f.write(r.stdout)
    with socket.socket() as s:
        s.bind(('127.0.0.1',0)); port = s.getsockname()[1]
    data = work/'mysql-data'
    report = dict(started_at=now(), mode='automated rehearsal' if args.rehearse else 'fresh seed group server',
                  executor='Trợ lý Codex thay mặt Vương', source_sha=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                  branch=subprocess.check_output(['git','branch','--show-current'],text=True).strip(), source_dirty=bool(subprocess.check_output(['git','status','--porcelain','--',
                      'clinic_app','tools','tests','requirements-dev.txt'],text=True).strip()),
                  application_candidate='sha256:045a7c42b12390bc5a1cb911a1ec648215cf66df679b6576a7b22464bb398894',
                  demo_tool_sha256=digest(Path(__file__)), python=sys.version, executable=sys.executable,
                  mysql_executable=str(args.mysqld.resolve()), datadir=str(data), mysql_port=port,
                  database='clinic_week3_demo_test', group_rehearsal=False, success=False)
    write(out,'session.json',report)
    proc = db = server = thread = log = None
    try:
        log = (work/'mysql-console.txt').open('wb')
        subprocess.run([str(args.mysqld), '--no-defaults','--initialize-insecure',f'--datadir={data}'],
                       stdout=log,stderr=subprocess.STDOUT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
        proc = subprocess.Popen([str(args.mysqld),'--no-defaults',f'--datadir={data}','--bind-address=127.0.0.1',
                                 f'--port={port}','--mysqlx=0','--skip-log-bin'],stdout=log,stderr=subprocess.STDOUT,
                                creationflags=subprocess.CREATE_NO_WINDOW)
        import pymysql
        for _ in range(100):
            try:
                db=pymysql.connect(host='127.0.0.1',port=port,user='root',autocommit=True,charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
                break
            except pymysql.OperationalError: time.sleep(.25)
        assert db is not None, 'Cannot connect to private MySQL'
        if args.cleanup_check:
            report['cleanup_check'] = args.cleanup_check
            if args.cleanup_check == 'error':
                db.close()
                raise RuntimeError('Injected workload failure with closed private connection')
            report['success'] = True
            return
        password=secrets.token_hex(24)
        with db.cursor() as c:
            c.execute("ALTER USER 'root'@'localhost' IDENTIFIED BY %s",(password,))
            c.execute('CREATE DATABASE clinic_week3_demo_test CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci')
            c.execute('SELECT VERSION() v'); report['mysql']=c.fetchone()['v']
        db.select_db('clinic_week3_demo_test')
        os.environ.update(DB_HOST='127.0.0.1',DB_PORT=str(port),DB_USER='root',DB_PASSWORD=password,
                          DB_NAME='clinic_week3_demo_test',FLASK_SECRET_KEY=secrets.token_hex(32),
                          PYTHON_DOTENV_DISABLED='1',COOKIE_SECURE='false',FLASK_DEBUG='false',
                          PLAYWRIGHT_BROWSERS_PATH=str(args.browsers_path.resolve()))
        from tools.quyen_week1_evidence import execute_file
        report['import']=[]
        for name in ['schema.sql','seed.sql','audit.sql','constraints.sql','audit.sql','queries.sql']:
            sets=execute_file(db,name,require_empty=name=='audit.sql')
            report['import'].append(dict(file=name,result_sets=len(sets)))
        from clinic_app import create_app
        from tools.audit_seed import audit, EXPECTED
        app=create_app()
        def rows():
            result={}
            with db.cursor() as c:
                for table in EXPECTED:
                    c.execute(f'SELECT * FROM `{table}`')
                    result[table]={json.dumps(x,sort_keys=True,default=str) for x in c.fetchall()}
            return result
        baseline=rows()
        report['reserved_codes_absent']=all('DM6' not in row for values in baseline.values() for row in values)
        assert report['reserved_codes_absent']
        with app.app_context(): before=audit()
        assert before['total']==1144 and before['matches_expected_counts'] and not any(before['findings'].values())
        write(out,'audit-before.json',before)
        server=__import__('werkzeug.serving',fromlist=['make_server']).make_server('127.0.0.1',0,app,threaded=True)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        base=f'http://127.0.0.1:{server.server_port}'
        report['url']=base
        print('DEMO READY '+base+' ; evidence: '+str(out.relative_to(ROOT)),flush=True)
        write(out,'session.json',report)
        if args.rehearse:
            rehearse(app,base,db,out,report)
        else:
            print('Fresh seed only. Open /patients. Ctrl+C shuts down this instance; rerun for a new datadir.',flush=True)
            try:
                while True: time.sleep(.5)
            except KeyboardInterrupt: pass
        with app.app_context(): after=audit()
        write(out,'audit-after.json',after)
        assert not any(after['findings'].values())
        report['final_sql_audit_sets']=len(execute_file(db,'audit.sql',require_empty=True))
        current=rows()
        report['all_seed_rows_preserved']=all(values<=current[table] for table,values in baseline.items())
        assert report['all_seed_rows_preserved']
        report['success']=True
    except BaseException as exc:
        report['failure']=dict(type=type(exc).__name__)
        raise
    finally:
        finish_session(out, report, proc=proc, db=db, server=server, thread=thread,
                       log=log, executable=args.mysqld, data=data, port=port,
                       old_env=old_env, manifest=manifest, protected=protected)
        if sys.exc_info()[0] is None and not report['success']:
            raise RuntimeError('Demo or cleanup failed; inspect session.json')
    assert all(report[k] for k in ['success','mysql_port_closed','app_port_closed','checkout_env_unchanged','source_unchanged','old_evidence_unchanged'])


if __name__=='__main__':
    main()
