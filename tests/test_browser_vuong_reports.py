"""UI/JSON/SQL parity against independent INSERT oracle and stored clinical cases."""
import json
import os
import threading
from collections import Counter, defaultdict
from pathlib import Path
import pytest
from werkzeug.serving import make_server
from test_quyen_week2_reports import ROWS, sql_results, expected_history, same
from test_week2 import clinical_data, visit
from clinic_app import workflows as w
from clinic_app.db import transaction

pytestmark = pytest.mark.skipif(os.getenv('RUN_BROWSER_TESTS') != '1', reason='Requires Chromium')
OUT = Path('test-artifacts/vuong-reports')


def money(n):
    return f'{int(n):,}'.replace(',', '.') + ' đ'


@pytest.fixture
def report_browser(app):
    from playwright.sync_api import sync_playwright
    server = make_server('127.0.0.1', 0, app, threaded=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
    OUT.mkdir(parents=True, exist_ok=True)
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            page = browser.new_page(viewport={'width': 1440, 'height': 1000}, locale='vi-VN')
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            yield page, f'http://127.0.0.1:{server.server_port}'
            assert not errors, errors
            browser.close()
    finally:
        server.shutdown(); thread.join(timeout=5); server.server_close()


def json_get(page, url, status=200):
    response = page.request.get(url)
    assert response.status == status
    assert 'application/json' in response.headers['content-type']
    return response.json()


def test_seed_reports_ui_json_sql_expected(report_browser):
    from playwright.sync_api import expect
    page, base = report_browser
    evidence = []
    for month in ['2026-07', '2026-08', '2026-09', '2026-10', '2025-12']:
        episodes = {x['ma_dot']: x for x in ROWS['dot_dieu_tri']}
        diseases = defaultdict(set)
        for x in ROWS['lan_kham_benh']:
            if x['ngay_kham'].startswith(month):
                diseases[episodes[x['ma_dot']]['ma_benh']].add(x['ma_dot'])
        disease_counts = {key: len(value) for key, value in diseases.items()}
        fees = sum(x['tien_kham_chua'] for x in ROWS['lan_kham_benh'] if x['ngay_kham'].startswith(month))
        orders = {x['ma_don'] for x in ROWS['don_thuoc'] if x['ngay_lap_don'].startswith(month)}
        drugs = sum(x['so_luong'] * x['don_gia_ban'] for x in ROWS['chi_tiet_don_thuoc'] if x['ma_don'] in orders)
        results = sql_results('BN001', month)
        assert {x['ma_benh']: x['so_dot_mac'] for x in results[0]} == disease_counts
        assert results[-1][0] == dict(tien_kham=fees, tien_thuoc=drugs, doanh_thu=fees+drugs)
        disease_json = json_get(page, f'{base}/reports/diseases?month={month}&format=json')
        assert set(disease_json) == {'month', 'rows', 'total'}
        assert {x['ma_benh']: x['so_dot_mac'] for x in disease_json['rows']} == disease_counts
        assert all(isinstance(x['so_dot_mac'], int) for x in disease_json['rows'])
        assert disease_json['total'] == sum(disease_counts.values())
        page.goto(f'{base}/reports/diseases?month={month}')
        expect(page.locator('[data-report-total]')).to_have_text(str(sum(disease_counts.values())))
        expect(page.locator('[data-disease]')).to_have_count(len(disease_counts))
        for code, count in disease_counts.items():
            expect(page.locator(f'[data-disease="{code}"] [data-count]')).to_have_text(str(count))
        if not disease_counts:
            expect(page.get_by_text('Không có phát sinh trong tháng.', exact=True)).to_be_visible()
        page.screenshot(path=str(OUT / f'{month}-diseases.png'), full_page=True)
        salary_json = json_get(page, f'{base}/reports/salaries?month={month}&format=json')
        assert set(salary_json) == {'month', 'doctors', 'nurses', 'total'}
        page.goto(f'{base}/reports/salaries?month={month}')
        salary_totals = {}
        for kind, source, pk, counts, basic, bonus, sql_rows in [
            ('doctors', 'bac_si', 'ma_bac_si', Counter(x['ma_bac_si'] for x in ROWS['dot_dieu_tri'] if x['ngay_khoi'] and x['ngay_khoi'].startswith(month)), 7000000, 1000000, results[1]),
            ('nurses', 'y_ta', 'ma_y_ta', Counter(x['ma_y_ta'] for x in ROWS['ho_tro'] if x['ngay_ho_tro'].startswith(month)), 5000000, 200000, results[2])]:
            wanted = {x[pk]: basic + bonus*counts[x[pk]] for x in ROWS[source]}
            assert {x[pk]: int(x['tong_luong']) for x in sql_rows} == wanted
            assert {x['ma_nhan_vien']: int(x['tong_luong']) for x in salary_json[kind]} == wanted
            for row in salary_json[kind]:
                assert isinstance(row['so_lan_thuong'], int)
                assert int(row['luong_co_ban']) == basic
                assert int(row['tien_thuong']) == bonus*counts[row['ma_nhan_vien']]
            for code, total in wanted.items():
                expect(page.locator(f'[data-employee="{code}"] [data-salary]')).to_have_text(money(total))
            salary_totals[kind] = sum(wanted.values())
            expect(page.locator(f'[data-salary-total="{kind}"]')).to_have_text(money(salary_totals[kind]))
        assert int(salary_json['total']) == sum(salary_totals.values())
        expect(page.locator('[data-report-total]')).to_have_text(money(sum(salary_totals.values())))
        page.screenshot(path=str(OUT / f'{month}-salaries.png'), full_page=True)
        revenue_json = json_get(page, f'{base}/reports/revenue?month={month}&format=json')
        assert set(revenue_json) == {'month', 'consultation', 'medicine', 'total'}
        assert revenue_json == dict(month=month, consultation=str(fees), medicine=str(drugs), total=str(fees+drugs))
        page.goto(f'{base}/reports/revenue?month={month}')
        for key, value in [('consultation', fees), ('medicine', drugs), ('total', fees+drugs)]:
            expect(page.locator(f'[data-revenue="{key}"]')).to_have_text(money(value))
        page.screenshot(path=str(OUT / f'{month}-revenue.png'), full_page=True)
        evidence.append(dict(month=month, episodes=sum(disease_counts.values()), consultation=fees,
            medicine=drugs, revenue=fees+drugs, salaries=salary_totals, ui_json_sql_expected='PASS'))
    # Check the actual JSON contract for all patients, not only the service-level oracle.
    groups = [list(ROWS['benh_nhan'][0]), list(ROWS['luot_den_kham'][0]),
        list(ROWS['dot_dieu_tri'][0])+['ten_benh','bac_si','lan_kham_hien_tai'],
        ['ma_dot','ten_benh','lan_kham_hien_tai'], list(ROWS['lan_kham_benh'][0]),
        list(ROWS['chi_tiet_don_thuoc'][0])+['ma_lan_kham','ngay_lap_don','ten_thuoc','don_vi_tinh','thanh_tien'],
        list(ROWS['ho_tro'][0])+['ho_ten']]
    history_evidence = []
    for patient in ROWS['benh_nhan']:
        pid = patient['ma_benh_nhan']
        data = json_get(page, f'{base}/reports/history?patient_id={pid}&month=2025-12&format=json')
        assert set(data) == {'patient','visits','treatments','current','examinations','medicines','support'}
        for row in data['treatments']:
            row['bac_si'] = row['ten_bac_si']
        actual = [[data['patient']]] + [data[k] for k in ('visits','treatments','current','examinations','medicines','support')]
        expected = expected_history(pid)
        # Decimal JSON strings are deliberately converted only for oracle numeric fields.
        for observed, wanted, keys in zip(actual, expected, groups):
            for row in observed:
                for key in keys:
                    sample = next((x[key] for x in wanted if x.get(key) is not None), None)
                    if isinstance(sample, int):
                        row[key] = int(row[key])
            same(observed, wanted, keys)
        history_evidence.append(dict(patient=pid, groups=[len(x) for x in actual], json_expected='PASS'))
    page.goto(base+'/reports/history?patient_id=BN001')
    assert '<' not in page.title() and 'Thuốc đã kê' not in page.title()
    for key, selector in [('visits','[data-visit]'),('treatments','[data-treatment]'),('examinations','[data-exam]'),('medicines','[data-medicine]'),('support','[data-support]')]:
        data = json_get(page, base+'/reports/history?patient_id=BN001&format=json')
        expect(page.locator(selector)).to_have_count(len(data[key]))
    for width in [1440, 390, 320]:
        page.set_viewport_size({'width': width, 'height': 1000})
        for kind in ['diseases','salaries','revenue','history']:
            route = f'/reports/{kind}?'+('patient_id=BN001' if kind=='history' else 'month=2026-10')
            page.goto(base+route)
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            page.screenshot(path=str(OUT / f'{kind}-{width}.png'), full_page=True)
    (OUT/'seed-parity.json').write_text(json.dumps(dict(months=evidence,patients=history_evidence),ensure_ascii=False,indent=2),encoding='utf-8')


def test_stored_edge_cases_and_errors(app, clinical_data, report_browser):
    from playwright.sync_api import expect
    page, base = report_browser
    with app.app_context():
        w.create_visit(visit())
        w.create_visit(visit(2,'2001-01-31',che_do_dot='existing',tien_kham_chua='150'))
        w.create_visit(visit(3,'2001-02-01',che_do_dot='existing',tien_kham_chua='200'))
        w.cure('W2D1',{'ngay_khoi':'2001-02-02'})
        w.create_visit(visit(4,'2001-02-03',ma_dot='W2D2',tien_kham_chua='300'))
        w.add_examination('W2L4',visit(5,'2001-02-03',ma_dot='W2D3',ma_benh='W2B2',tien_kham_chua='50'))
        w.record_support('W2L4',dict(ma_y_ta='W2YT2',ngay_ho_tro='2001-02-03',noi_dung_ho_tro='Hỗ trợ thêm'))
        w.prescribe('W2K3',{'ma_don':'W2P1','ngay_lap_don':'2001-02-01'},[
            dict(ma_thuoc='W2T1',so_luong='2',lieu_dung='Sáng'),dict(ma_thuoc='W2T2',so_luong='3',lieu_dung='Tối')])
        with transaction() as db, db.cursor() as cur:
            cur.execute("UPDATE thuoc SET gia_hien_tai=9999 WHERE ma_thuoc='W2T1'")
    comparison = []
    for month, count, fees, drugs, doctor, nurse1, nurse2 in [
        ('2001-01',1,250,0,7000000,5400000,5000000),
        ('2001-02',3,550,8000,8000000,5400000,5200000),
        ('2001-03',0,0,0,7000000,5000000,5000000)]:
        sql = sql_results('W2BN1',month)
        assert sum(x['so_dot_mac'] for x in sql[0]) == count
        assert sql[-1][0] == dict(tien_kham=fees,tien_thuoc=drugs,doanh_thu=fees+drugs)
        revenue = json_get(page,f'{base}/reports/revenue?month={month}&format=json')
        assert int(revenue['total']) == fees+drugs
        page.goto(f'{base}/reports/revenue?month={month}')
        expect(page.locator('[data-revenue="consultation"]')).to_have_text(money(fees))
        expect(page.locator('[data-revenue="medicine"]')).to_have_text(money(drugs))
        expect(page.locator('[data-revenue="total"]')).to_have_text(money(fees+drugs))
        page.screenshot(path=str(OUT/f'edge-{month}-revenue.png'),full_page=True)
        q1=json_get(page,f'{base}/reports/diseases?month={month}&format=json')
        assert q1['total']==count
        page.goto(f'{base}/reports/diseases?month={month}')
        expect(page.locator('[data-report-total]')).to_have_text(str(count))
        salaries=json_get(page,f'{base}/reports/salaries?month={month}&format=json')
        page.goto(f'{base}/reports/salaries?month={month}')
        for group, code, total, sql_group, pk in [('doctors','W2BS',doctor,sql[1],'ma_bac_si'),('nurses','W2YT1',nurse1,sql[2],'ma_y_ta'),('nurses','W2YT2',nurse2,sql[2],'ma_y_ta')]:
            assert int(next(x for x in salaries[group] if x['ma_nhan_vien']==code)['tong_luong'])==total
            assert int(next(x for x in sql_group if x[pk]==code)['tong_luong'])==total
            expect(page.locator(f'[data-employee="{code}"] [data-salary]')).to_have_text(money(total))
        comparison.append(dict(month=month,episodes=count,fees=fees,medicines=drugs,total=fees+drugs,
                               doctor=doctor,nurse1=nurse1,nurse2=nurse2,ui_json_sql_expected='PASS'))
    history=json_get(page,base+'/reports/history?patient_id=W2BN1&month=INVALID&format=json')
    assert [len(history[k]) for k in ('visits','treatments','examinations','medicines','support')]==[4,3,5,2,5]
    history_sql=sql_results('W2BN1','2001-01')
    assert [len(history_sql[i]) for i in (4,5,7,8,9)]==[4,3,5,2,5]
    assert sum(int(x['tien_kham_chua']) for x in history_sql[7])==800
    assert sum(int(x['thanh_tien']) for x in history_sql[8])==8000
    assert any(x['ngay_ra_vien'] is None for x in history['visits'])
    assert {x['ma_thuoc']:int(x['don_gia_ban']) for x in history['medicines']}=={'W2T1':1000,'W2T2':2000}
    page.goto(base+'/reports/history?patient_id=W2BN1&month=2001-01')
    expect(page.locator('[data-treatment]')).to_have_count(3)
    expect(page.locator('[data-exam]')).to_have_count(5)
    expect(page.locator('[data-current]')).to_have_count(2)
    expect(page.locator('[data-history-fees]')).to_have_text('800 đ')
    expect(page.locator('[data-history-medicines]')).to_have_text('8.000 đ')
    expect(page.locator('[data-medicine="W2T1"]')).to_contain_text('1.000 đ')
    expect(page.locator('[data-medicine="W2T1"]')).to_contain_text('01/02/2001')
    page.screenshot(path=str(OUT/'edge-history.png'),full_page=True)
    page.goto(base+'/reports/history')
    page.get_by_label('Mã bệnh nhân *',exact=True).fill('W2BN2')
    page.get_by_role('button',name='Xem lịch sử',exact=True).click()
    expect(page.get_by_text('Bệnh nhân có hồ sơ nhưng chưa có lịch sử khám được ghi nhận.',exact=True)).to_be_visible()
    expect(page.locator('[data-history-fees]')).to_have_text('0 đ')
    empty=json_get(page,base+'/reports/history?patient_id=W2BN2&format=json')
    assert all(not empty[k] for k in ('visits','treatments','current','examinations','medicines','support'))
    page.screenshot(path=str(OUT/'empty-history.png'),full_page=True)
    for kind in ['diseases','salaries','revenue']:
        url=f'{base}/reports/{kind}?month=2026-13'
        assert page.goto(url).status==400
        expect(page.get_by_role('alert')).to_contain_text('YYYY-MM')
        expect(page.locator('[name="month"]')).to_have_value('2026-13')
        assert set(json_get(page,url+'&format=json',400))=={'error'}
    page.screenshot(path=str(OUT/'invalid-month.png'),full_page=True)
    page.locator('[name="month"]').fill('2001-02')
    page.get_by_role('button',name='Xem báo cáo',exact=True).click()
    expect(page.locator('[data-revenue="total"]')).to_have_text('8.550 đ')
    url=base+'/reports/history?patient_id=MISSING'
    assert page.goto(url).status==404
    expect(page.locator('[name="patient_id"]')).to_have_value('MISSING')
    assert set(json_get(page,url+'&format=json',404))=={'error'}
    assert set(json_get(page,base+'/reports/history?patient_id=%3Cscript%3E&format=json',422))=={'error'}
    page.screenshot(path=str(OUT/'missing-patient.png'),full_page=True)
    page.locator('[name="patient_id"]').fill('W2BN1')
    page.get_by_role('button',name='Xem lịch sử',exact=True).click()
    expect(page.locator('[data-history-fees]')).to_have_text('800 đ')
    (OUT/'edge-parity.json').write_text(json.dumps(comparison,ensure_ascii=False,indent=2),encoding='utf-8')
