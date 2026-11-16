"""Capture current UI against a fresh, isolated MySQL database in CI.

Never runs against a developer's existing accounts. No fixture or service stubs.
"""
import argparse
import hashlib
import json
import logging
import os
from pathlib import Path
import secrets
import threading
from io import BytesIO
from PIL import Image

from playwright.sync_api import sync_playwright
from werkzeug.security import generate_password_hash
from werkzeug.serving import make_server
from clinic_app import create_app
from clinic_app.db import transaction
from tools.quyen_db import connect, install


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='test-artifacts/report-images')
    args = parser.parse_args()
    if os.getenv('GITHUB_ACTIONS') != 'true' or os.getenv('DB_NAME') != 'clinic_report_images_test':
        raise SystemExit('Only the disposable CI database clinic_report_images_test is supported.')
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    db = connect()
    try:
        install(db)  # requires a completely empty database; no DROP or FK bypass
        with db.cursor() as c:
            c.execute('SELECT VERSION() AS version')
            mysql_version = c.fetchone()['version']
    finally:
        db.close()
    password = secrets.token_urlsafe(18)
    app = create_app({'SECRET_KEY': secrets.token_hex(32), 'SESSION_COOKIE_SECURE': False})
    result = app.test_cli_runner().invoke(args=['init-auth', '--username', 'admin_demo'],
                                          input=password+'\n'+password+'\n')
    if result.exit_code:
        raise RuntimeError('init-auth failed; no credentials or command output are exported.')
    with app.app_context(), transaction() as db, db.cursor() as c:
        c.execute("INSERT INTO app_user (username,password_hash,role,doctor_id) VALUES (%s,%s,'doctor','BS001')",
                  ('bacsi_demo', generate_password_hash(secrets.token_urlsafe(18))))
        c.execute("INSERT INTO app_user (username,password_hash,role) VALUES (%s,%s,'reception')",
                  ('tiepnhan_demo', generate_password_hash(password)))
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    server = make_server('127.0.0.1', 0, app, threaded=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f'http://127.0.0.1:{server.server_port}'
    errors = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            page = browser.new_page(viewport={'width': 1440, 'height': 1100}, locale='vi-VN')
            page.on('pageerror', lambda error: errors.append(str(error)))
            def goto(path):
                response = page.goto(base+path)
                assert response and response.status == 200, (path, response.status if response else None)
            def shot(selector, name, nth=None):
                locator = page.locator(selector)
                if nth is not None:
                    locator = locator.nth(nth)
                locator.screenshot(path=str(out/name))
            def panorama(selector, name):
                # Stitch real horizontal scroll positions; never modify UI styles/data.
                region=page.locator(selector)
                metrics=region.evaluate('(e)=>({visible:e.clientWidth,total:e.scrollWidth})')
                visible,total=metrics['visible'],metrics['total']
                tiles=[]
                for left in range(0,total,visible):
                    actual=region.evaluate('(e,x)=>{e.scrollLeft=x;return e.scrollLeft}',left)
                    tile=Image.open(BytesIO(region.screenshot())).convert('RGB')
                    tiles.append((actual,tile))
                    if actual+visible>=total:break
                canvas=Image.new('RGB',(total+2,tiles[0][1].height),'white')
                for left,tile in tiles:
                    canvas.paste(tile.crop((1,0,1+visible,tile.height)),(left+1,0))
                canvas.save(out/name,optimize=True)
                region.evaluate('(e)=>e.scrollLeft=0')
            def login(username):
                goto('/auth/login')
                page.locator('#username').fill(username)
                page.locator('#password').fill(password)
                page.locator('button[type=submit]').click()
                page.wait_for_url('**/patients')
            goto('/auth/login')
            shot('.auth-card', 'login.png')  # empty fields; never screenshot a password
            login('admin_demo')
            goto('/health/db')
            assert page.locator('body').inner_text().find('mysql') >= 0
            for kind in ('diseases', 'salaries', 'revenue', 'history'):
                goto('/reports/'+kind+'?'+('patient_id=BN001' if kind=='history' else 'month=2026-10'))
                if kind == 'diseases':
                    assert page.locator('[data-report-total]').inner_text() == '24'
                    shot('.clinical-table', 'q1-diseases.png')
                elif kind == 'salaries':
                    assert '143.600.000' in page.locator('[data-report-total]').inner_text()
                    shot('.report-summary', 'q2-summary.png')
                    shot('.clinical-table', 'q2-doctors.png', 0)
                    shot('.clinical-table', 'q2-nurses.png', 1)
                elif kind == 'revenue':
                    assert '10.500.800' in page.locator('[data-revenue="total"]').inner_text()
                    shot('#main-content', 'q4-revenue.png')
                else:
                    shot('.report-summary', 'q3-summary.png')
                    shot('.clinical-table', 'q3-treatments.png', 0)
            goto('/auth/users')
            page.locator('details.account-editor').nth(1).evaluate('(e)=>e.open=true')
            shot('details.account-editor', 'accounts-edit.png', 1)
            shot('form.record-form', 'accounts-create.png')
            goto('/visits/new')
            shot('#main-content', 'combined-form.png')
            goto('/reports')
            for i in range(1, 8):
                rid=f'R{i:02}'
                page.locator('#analytics-report').select_option(rid)
                page.locator('#analytics-filters button').click()
                page.wait_for_function("() => document.querySelector('#analytics-status').textContent.includes('Đã tải') || document.querySelector('#analytics-status').getAttribute('role') === 'alert'")
                assert f'dòng {rid}' in page.locator('#analytics-status').inner_text(), page.locator('#analytics-status').inner_text()
                page.locator(f'#r{i:02}-chart').wait_for(state='visible')
                panorama(f'#r{i:02}-chart-scroll', rid.lower()+'-chart.png')
                table=page.locator('#analytics-table')
                panorama('#analytics-table >> xpath=..', rid.lower()+'-table.png')
                cells=table.locator('thead th').all()
                assert all(c.evaluate('(e)=>getComputedStyle(e).textAlign')=='center' for c in cells)
                if i == 7:
                    assert '265.714,29' in table.locator('tbody tr').first.inner_text()
                    assert 'VND' not in table.locator('tbody').inner_text()
            # Separate browser context, independent reception session.
            context=browser.new_context(viewport={'width':1440,'height':1100},locale='vi-VN')
            reception=context.new_page()
            reception.goto(base+'/auth/login')
            reception.locator('#username').fill('tiepnhan_demo')
            reception.locator('#password').fill(password)
            reception.locator('button[type=submit]').click()
            reception.wait_for_url('**/patients')
            response=reception.goto(base+'/visits/new')
            assert response.status==200
            reception.locator('#main-content').screenshot(path=str(out/'reception.png'))
            context.close()
            assert not errors, errors
            browser.close()
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()
    images=sorted(out.glob('*.png'))
    manifest=dict(source_sha=os.getenv('SOURCE_SHA', os.getenv('GITHUB_SHA')),
                  mysql_version=mysql_version,auth_enabled=True,sql_stubs=False,
                  clinical_seed_rows=1144,horizontal_scroll_images='stitched real scroll positions without style changes',images={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in images})
    (out/'capture.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Captured {len(images)} images with authenticated app and MySQL {mysql_version}.')


if __name__ == '__main__':
    main()
