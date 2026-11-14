"""Opt-in real MySQL -> Flask -> browser parity against the independent seed oracle.

Requires RUN_MYSQL_TESTS=1, RUN_BROWSER_TESTS=1, a canonical seeded *_test DB,
and Playwright Chromium (or BROWSER_CHANNEL). Canonical cases are read-only;
R07 all-excluded commits and cleans up a fixture only in the named private DB.
"""
import json
import os
import threading
from collections import Counter
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

import pytest
from werkzeug.serving import make_server
from tools.analytics_oracle import canonical, expected, seed_rows
from tools.quyen_db import connect
from test_vuong_analytics_ui import assert_chart_rows
from test_vuong_r02_ui import bars as r02_bars
from test_vuong_r03_ui import bars as r03_bars
from test_vuong_r04_ui import bars as r04_bars
from test_vuong_r05_ui import bars as r05_bars
from test_vuong_r06_ui import bars as r06_bars
from test_vuong_r07_ui import segments as r07_segments, money_cell

OUT = Path('test-artifacts/vuong-analytics-mysql-ui')
FIELDS = {
    'R01': ('ma_benh','ten_benh','thu_tu_nhom','nhom_tuoi','so_dot','so_benh_nhan'),
    'R02': ('ngay','so_luot','so_benh_nhan_tiep_nhan','so_lan_kham'),
    'R03': ('ma_bac_si','ho_ten','chuyen_mon','so_lan_kham','so_dot','so_benh_nhan'),
    'R04': ('ma_thuoc','ten_thuoc','don_vi_tinh','so_don','tong_so_luong'),
    'R05': ('ma_dot','ma_benh_nhan','ho_ten','ma_benh','ten_benh','ngay_bat_dau','ngay_khoi_truoc','so_ngay_tu_lan_khoi_truoc'),
    'R06': ('ma_dot','ma_benh_nhan','ho_ten','so_dien_thoai','ma_benh','ten_benh','ma_bac_si','ten_bac_si','ngay_bat_dau','ngay_kham_cuoi','chua_co_lan_kham','so_ngay_chua_ghi_nhan','nhom_ngay'),
    'R07': ('ma_benh','ten_benh','so_dot_tinh','so_dot_loai','tb_tien_kham','tb_tien_thuoc','tb_tong','min_tong','max_tong'),
}
MONEY = set(FIELDS['R07'][4:])
ORDER = {
    'R01': lambda r: (r['ma_benh'],r['thu_tu_nhom']),
    'R02': lambda r: r['ngay'],
    'R03': lambda r: (-r['so_lan_kham'],r['ma_bac_si']),
    'R04': lambda r: (-r['so_don'],r['ma_thuoc']),
    'R05': lambda r: (r['ma_benh'],r['ngay_bat_dau'],r['ma_dot']),
    'R06': lambda r: (-r['so_ngay_chua_ghi_nhan'],r['ma_dot']),
    'R07': lambda r: (r['tb_tong'] is None,-Decimal(r['tb_tong'] or 0),r['ma_benh']),
}


def snapshot(source):
    db = connect()
    try:
        with db.cursor() as cursor:
            result = {}
            for table in source:  # Table names come exclusively from repository seed.sql.
                cursor.execute('SELECT * FROM ' + table)
                result[table] = canonical(cursor.fetchall())
            return result
    finally:
        db.rollback()
        db.close()


@pytest.fixture(scope='module')
def real_browser(app):
    if os.getenv('RUN_BROWSER_TESTS') != '1':
        pytest.skip('Set RUN_BROWSER_TESTS=1 and install Playwright Chromium')
    # The session app fixture requires RUN_MYSQL_TESTS=1 and DB_NAME ending _test.
    source = seed_rows()
    before = snapshot(source)
    assert before == {table: canonical(rows) for table, rows in source.items()}, 'DB is not canonical seed'
    from playwright.sync_api import sync_playwright
    server = make_server('127.0.0.1', 0, app, threaded=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    OUT.mkdir(parents=True, exist_ok=True)
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(channel=os.getenv('BROWSER_CHANNEL') or None)
            yield browser, f'http://127.0.0.1:{server.server_port}', source
            browser.close()
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()
        assert snapshot(source) == before, 'Seed rows changed during browser integration tests'


def reference(source, report, params, age):
    rows = expected(source, **params)[report]
    if age is not None:
        rows = [r for r in rows if r['thu_tu_nhom'] == age]
    def value(key, val):
        if val is None: return None
        if key in MONEY: return format(Decimal(val), '.2f')
        if isinstance(val, date): return val.isoformat()
        if isinstance(val, Decimal):
            assert val == int(val)
            return int(val)
        return val
    return sorted([{k: value(k, v) for k, v in row.items()} for row in rows], key=ORDER[report])


def check_chart(page, report, rows, data):
    if report == 'R01':
        assert_chart_rows(page, rows)
    elif report == 'R02':
        assert r02_bars(page) == [dict(date=r['ngay'],series=k,count=r[k],patients=r['so_benh_nhan_tiep_nhan']) for r in rows for k in ('so_luot','so_lan_kham')]
    elif report == 'R03':
        assert r03_bars(page) == [{k:r[k] for k in ('ma_bac_si','so_lan_kham','so_dot','so_benh_nhan')} for r in rows]
    elif report == 'R04':
        assert r04_bars(page) == [{k:r[k] for k in ('ma_thuoc','so_don','tong_so_luong','don_vi_tinh')} for r in rows]
    elif report == 'R05':
        counts = Counter((r['ma_benh'],r['ten_benh']) for r in rows)
        groups = [dict(ma_benh=k[0],ten_benh=k[1],so_dot=v) for k,v in sorted(counts.items())]
        assert data['chart_groups'] == groups
        assert r05_bars(page) == [{k:g[k] for k in ('ma_benh','so_dot')} for g in groups]
    elif report == 'R06':
        counts = Counter(r['nhom_ngay'] for r in rows)
        groups = [dict(nhom_ngay=k,so_dot=counts[k]) for k in ('0–6','7–13','14–29','30+')]
        assert data['chart_groups'] == groups
        assert r06_bars(page) == groups
    else:
        assert r07_segments(page) == [dict(ma_benh=r['ma_benh'],series=k,money=r[k]) for r in rows if r['so_dot_tinh'] > 0 for k in ('tb_tien_kham','tb_tien_thuoc')]


CASES = [(report, period, None) for report in FIELDS for period in ('default','august','empty')]
CASES += [('R01','default',age) for age in (-1,0,1,2,3)]
CASES += [('R06',period,None) for period in ('threshold0','threshold30')]


@pytest.mark.parametrize('report,period,age', CASES)
def test_mysql_browser_oracle(real_browser, report, period, age):
    from playwright.sync_api import expect
    browser, base, source = real_browser
    params = dict(start='2026-07-01',end='2026-10-15',as_of='2026-10-14',threshold=14)
    if period == 'august': params.update(start='2026-08-01',end='2026-09-01',as_of='2026-08-31',threshold=7)
    if period == 'empty': params.update(start='1999-01-01',end='1999-02-01',as_of='1999-01-31',threshold=0)
    if period == 'threshold0': params['threshold'] = 0
    if period == 'threshold30': params['threshold'] = 30
    wanted = reference(source, report, params, age)
    label = f'{report}-{period}' + (f'-age{age}' if age is not None else '')
    page = browser.new_page(viewport={'width':1440,'height':1000}, locale='vi-VN')
    try:
        page.goto(base + '/reports')
        page.locator('#analytics-report').select_option(report)
        if report == 'R06':
            page.locator('#analytics-as-of').fill(params['as_of'])
            page.locator('#analytics-threshold').fill(str(params['threshold']))
        else:
            page.locator('#analytics-start').fill(params['start'])
            page.locator('#analytics-through').fill((date.fromisoformat(params['end']) - timedelta(days=1)).isoformat())
            if age is not None: page.locator('#analytics-age').select_option(str(age))
        with page.expect_response(lambda response: '/api/analytics/' + report + '?' in response.url) as captured:
            page.locator('#analytics-filters button').click()
        response = captured.value
        assert response.status == 200
        data = response.json()
        (OUT / f'{label}-expected.json').write_text(json.dumps(dict(params=params,age_group=age,rows=wanted),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        (OUT / f'{label}-actual.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        expect(page.locator('#analytics-result')).to_be_visible()
        page.screenshot(path=str(OUT / f'{label}.png'), full_page=True)
        assert data['report_id'] == report
        assert data['rows'] == wanted
        assert data['row_count'] == len(wanted)
        rendered = page.locator('#analytics-table tbody tr').evaluate_all('(rows)=>rows.map(r=>[...r.cells].map(c=>c.textContent))')
        def cell(row, key):
            if report == 'R07' and key in MONEY: return money_cell(row[key])
            if report == 'R06' and key == 'ngay_kham_cuoi' and row[key] is None: return 'Chưa có lần khám'
            return str(row[key])
        assert rendered == ([[cell(r,k) for k in FIELDS[report]] for r in wanted] if wanted else [['Không có dữ liệu phù hợp bộ lọc.']])
        check_chart(page, report, wanted, data)
    finally:
        page.close()


def test_legacy_reports_desktop_mysql_smoke(real_browser):
    browser, base, _ = real_browser
    page = browser.new_page(viewport={'width':1440,'height':1000}, locale='vi-VN')
    try:
        for label, path in [('diseases','/reports/diseases?month=2026-10'),
                            ('history','/reports/history?patient_id=BN001')]:
            response = page.goto(base + path)
            status = response.status if response is not None else None
            (OUT / f'legacy-{label}-expected.json').write_text(json.dumps(dict(path=path,status=200),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            (OUT / f'legacy-{label}-actual.json').write_text(json.dumps(dict(path=path,status=status),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            assert status == 200
            page.screenshot(path=str(OUT / f'legacy-{label}.png'), full_page=True)
    finally:
        page.close()


def test_r07_mysql_all_excluded_null(real_browser):
    from playwright.sync_api import expect
    assert os.getenv('RUN_MYSQL_TESTS') == '1' and os.getenv('RUN_BROWSER_TESTS') == '1'
    if os.getenv('DB_NAME') != 'clinic_vuong_analytics_test':
        pytest.skip('Committed NULL fixture runs only in clinic_vuong_analytics_test; use run_private.py')
    browser, base, source = real_browser
    before = snapshot(source)
    db = connect()
    committed = False
    page = None
    try:
        with db.cursor() as c:
            c.execute("INSERT INTO benh VALUES ('VQANULL','Vuong QA empty prescription disease')")
            c.execute("INSERT INTO dot_dieu_tri VALUES ('VQADOT','2004-02-28',NULL,'Đang điều trị','BN001','VQANULL','BS001')")
            c.execute("INSERT INTO luot_den_kham VALUES ('VQAVISIT','2004-02-28',NULL,'BN001')")
            c.execute("INSERT INTO lan_kham_benh VALUES ('VQAEXAM',1,'2004-02-28',100,'Fixture','VQADOT','VQAVISIT')")
            c.execute("INSERT INTO don_thuoc VALUES ('VQAORDER','2004-02-28','VQAEXAM')")
            c.execute("UPDATE dot_dieu_tri SET ngay_khoi='2004-03-01',trang_thai='Đã khỏi' WHERE ma_dot='VQADOT'")
        db.commit()
        committed = True
        wanted = [dict(ma_benh='VQANULL',ten_benh='Vuong QA empty prescription disease',so_dot_tinh=0,so_dot_loai=1,
                       tb_tien_kham=None,tb_tien_thuoc=None,tb_tong=None,min_tong=None,max_tong=None)]
        page = browser.new_page(viewport={'width':1440,'height':1000}, locale='vi-VN')
        page.goto(base + '/reports')
        page.locator('#analytics-report').select_option('R07')
        page.locator('#analytics-start').fill('2004-03-01')
        page.locator('#analytics-through').fill('2004-03-01')
        with page.expect_response(lambda r: '/api/analytics/R07?' in r.url) as captured:
            page.locator('#analytics-filters button').click()
        response = captured.value
        assert response.status == 200
        data = response.json()
        (OUT / 'R07-all-excluded-expected.json').write_text(json.dumps(wanted,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        (OUT / 'R07-all-excluded-actual.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        expect(page.locator('#analytics-result')).to_be_visible()
        page.screenshot(path=str(OUT / 'R07-all-excluded.png'), full_page=True)
        assert data['rows'] == wanted and data['row_count'] == 1
        assert page.locator('#analytics-table tbody tr').evaluate_all('(rows)=>rows.map(r=>[...r.cells].map(c=>c.textContent))') == [
            ['VQANULL','Vuong QA empty prescription disease','0','1'] + ['Không có mẫu'] * 5]
        assert r07_segments(page) == []
        expect(page.locator('#r07-chart-empty')).to_contain_text('Không có mẫu')
    finally:
        if page is not None: page.close()
        db.rollback()
        if committed:
            try:
                with db.cursor() as c:
                    c.execute("DELETE FROM don_thuoc WHERE ma_don='VQAORDER'")
                    c.execute("DELETE FROM lan_kham_benh WHERE ma_lan_kham='VQAEXAM'")
                    c.execute("DELETE FROM luot_den_kham WHERE ma_luot='VQAVISIT'")
                    c.execute("DELETE FROM dot_dieu_tri WHERE ma_dot='VQADOT'")
                    c.execute("DELETE FROM benh WHERE ma_benh='VQANULL'")
                db.commit()
            except BaseException:
                db.rollback()
                raise
        db.close()
        assert snapshot(source) == before, 'Fixture cleanup changed seed rows'
