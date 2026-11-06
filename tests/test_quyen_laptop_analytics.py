"""Additional laptop acceptance: real zero money and offline responsive R01-R07.

Uses only the runner's private instance. Original Vuong parity helpers retained.
"""
import json
import os
from pathlib import Path

import pytest
from tools.quyen_db import connect
from test_vuong_analytics_mysql_ui import real_browser, snapshot, check_chart

OUT = Path('test-artifacts/quyen-laptop-analytics')


def test_real_r07_zero_is_a_sample(real_browser):
    from playwright.sync_api import expect
    if os.getenv('DB_NAME') != 'clinic_vuong_analytics_test':
        pytest.skip('Requires the dedicated run_private.py instance')
    browser, base, source = real_browser
    before = snapshot(source)
    db = connect()
    page = None
    try:
        with db.cursor() as c:
            c.execute("INSERT INTO benh VALUES ('QQZERO','Quyen synthetic zero fee')")
            c.execute("INSERT INTO dot_dieu_tri VALUES ('QQZDOT','2005-02-28',NULL,'Đang điều trị','BN001','QQZERO','BS001')")
            c.execute("INSERT INTO luot_den_kham VALUES ('QQZVISIT','2005-02-28',NULL,'BN001')")
            c.execute("INSERT INTO lan_kham_benh VALUES ('QQZEXAM',1,'2005-02-28',0,'Synthetic zero fixture','QQZDOT','QQZVISIT')")
            c.execute("UPDATE dot_dieu_tri SET ngay_khoi='2005-03-01',trang_thai='Đã khỏi' WHERE ma_dot='QQZDOT'")
        db.commit()
        wanted = dict(ma_benh='QQZERO',ten_benh='Quyen synthetic zero fee',so_dot_tinh=1,so_dot_loai=0,
                      **{k:'0.00' for k in ('tb_tien_kham','tb_tien_thuoc','tb_tong','min_tong','max_tong')})
        page = browser.new_page(viewport={'width':1440,'height':1000},locale='vi-VN')
        page.goto(base+'/reports')
        page.locator('#analytics-report').select_option('R07')
        page.locator('#analytics-start').fill('2005-03-01')
        page.locator('#analytics-through').fill('2005-03-01')
        with page.expect_response(lambda r:'/api/analytics/R07?' in r.url) as response:
            page.locator('#analytics-filters button').click()
        data = response.value.json()
        assert response.value.status == 200 and data['rows'] == [wanted]
        expect(page.locator('#analytics-result')).to_be_visible()
        assert page.locator('#analytics-table tbody tr').evaluate_all('(rows)=>rows.map(r=>[...r.cells].map(c=>c.textContent))') == [
            ['QQZERO','Quyen synthetic zero fee','1','0']+['0.00 VND']*5]
        check_chart(page,'R07',[wanted],data)
        assert page.locator('#r07-chart .chart-segment').evaluate_all('(nodes)=>nodes.map(n=>Number(n.getAttribute("height")))') == [0,0]
        page.locator('#r07-chart .chart-segment').first.focus()
        expect(page.locator('#r07-chart-detail')).to_contain_text('0.00')
        OUT.mkdir(parents=True,exist_ok=True)
        (OUT/'R07-zero-expected-actual.json').write_text(json.dumps(dict(expected=[wanted],actual=data),ensure_ascii=False,indent=2),encoding='utf-8')
        page.screenshot(path=str(OUT/'R07-real-zero.png'),full_page=True)
    finally:
        if page: page.close()
        db.rollback()
        with db.cursor() as c:
            c.execute("DELETE FROM lan_kham_benh WHERE ma_lan_kham='QQZEXAM'")
            c.execute("DELETE FROM luot_den_kham WHERE ma_luot='QQZVISIT'")
            c.execute("DELETE FROM dot_dieu_tri WHERE ma_dot='QQZDOT'")
            c.execute("DELETE FROM benh WHERE ma_benh='QQZERO'")
        db.commit()
        db.close()
        assert snapshot(source) == before


@pytest.mark.parametrize('width',[1440,390,320])
def test_real_reports_without_external_network(real_browser,width):
    from playwright.sync_api import expect
    browser, base, _ = real_browser
    context = browser.new_context(viewport={'width':width,'height':1000},locale='vi-VN')
    external, errors, evidence = [], [], []
    context.route('**/*',lambda route:route.continue_() if route.request.url.startswith(base+'/') else (external.append(route.request.url),route.abort())[-1])
    page = context.new_page()
    page.on('pageerror',lambda error:errors.append(str(error)))
    OUT.mkdir(parents=True,exist_ok=True)
    try:
        page.goto(base+'/reports')
        for report in ('R01','R02','R03','R04','R05','R06','R07'):
            page.locator('#analytics-report').select_option(report)
            with page.expect_response(lambda r:'/api/analytics/'+report+'?' in r.url) as response:
                page.locator('#analytics-filters button').click()
            assert response.value.status == 200
            data = response.value.json()
            expect(page.locator('#analytics-result')).to_be_visible()
            check_chart(page,report,data['rows'],data)
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            before = page.locator('#analytics-result').inner_text()
            context.set_offline(True)
            assert page.locator('#analytics-result').inner_text() == before
            check_chart(page,report,data['rows'],data)
            page.screenshot(path=str(OUT/f'{report}-offline-{width}.png'),full_page=True)
            context.set_offline(False)
            evidence.append(dict(report=report,rows=data['row_count'],viewport=width,offline_retained=True))
        assert not external and not errors
        (OUT/f'offline-{width}.json').write_text(json.dumps(dict(cases=evidence,external_requests=external,page_errors=errors),ensure_ascii=False,indent=2),encoding='utf-8')
    finally:
        context.close()
