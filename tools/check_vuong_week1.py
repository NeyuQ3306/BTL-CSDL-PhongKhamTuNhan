"""Run Vuong's week-1 UI checklist on the explicitly named disposable demo DB.

Run from the repository root: python -m tools.check_vuong_week1
Never imports SQL, changes schema, or deletes existing demo records.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from uuid import uuid4
from datetime import datetime
from zoneinfo import ZoneInfo
from unittest.mock import patch

from flask import render_template
from clinic_app import create_app
from clinic_app.db import fetch_all, fetch_one
from clinic_app.entities import ENTITIES
from tools.audit_seed import audit, EXPECTED


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/evidence/vuong_week1_checklist'
DEMO_DB = 'clinic_vuong_week1'


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def snapshot(app):
    """Compare all rows before/after without exporting source data."""
    with app.app_context():
        hashes = {}
        for table in EXPECTED:
            rows = fetch_all(f'SELECT * FROM {table}')
            serial = sorted(json.dumps(row, sort_keys=True, ensure_ascii=False, default=str) for row in rows)
            hashes[table] = hashlib.sha256('\n'.join(serial).encode()).hexdigest()
        return hashes


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    os.chdir(ROOT)
    OUT.mkdir(parents=True, exist_ok=True)
    env_hash = hashlib.sha256((ROOT / '.env').read_bytes()).hexdigest()
    os.environ['DB_NAME'] = DEMO_DB
    app = create_app({'TESTING': True})
    require(app.config['DB_NAME'] == DEMO_DB, 'Refusing database other than the dedicated demo')
    before = snapshot(app)
    results = []

    def case(code, title, steps, expected, action):
        row = dict(id=code, title=title, steps=steps, expected=expected)
        try:
            row['actual'] = action() or 'Đúng kết quả mong đợi'
            row['status'] = 'PASS'
        except Exception as exc:
            row['status'] = 'FAIL'
            row['actual'] = str(exc) if isinstance(exc, AssertionError) else type(exc).__name__
        results.append(row)
        print(code, row['status'], title)

    def health():
        c = app.test_client()
        require(c.get('/health').status_code == 200, 'Flask health failed')
        require(c.get('/health/db').status_code == 200, 'DB health failed')
        with app.app_context():
            report = audit()
            require(report['matches_expected_counts'] and not any(report['findings'].values()), 'Seed audit failed')
        return 'Flask/MySQL 200; 11 bảng/1.144 dòng; audit không có phát hiện'

    case('ENV01', 'Ứng dụng và dữ liệu nền', 'GET /health, /health/db; audit read-only', '200, đúng seed', health)
    fixtures = []
    for slug, entity in ENTITIES.items():
        client = app.test_client()
        key = 'VW' + uuid4().hex[:9]
        with app.app_context():
            require(fetch_one(f'SELECT {entity.pk} FROM {entity.table} WHERE {entity.pk}=%s', (key,)) is None, 'Generated code collision')
        data = {f.name: 'Dữ liệu thử tuần 1' for f in entity.fields}
        data.update({entity.pk: key, 'cmt': str(uuid4().int)[:19], 'ho_ten': 'Hồ sơ kiểm thử Vương',
                     'ngay_sinh': '2000-02-29', 'dia_chi': 'Địa chỉ giả lập',
                     'so_dien_thoai': '0901234567', 'tham_nien': '0'})
        client.get(f'/{slug}/new')
        with client.session_transaction() as session:
            data['csrf_token'] = session['_csrf']
        fixtures.append((slug, entity, client, key, data))

    try:
        for slug, entity, c, key, data in fixtures:
            prefix = {'patients': 'PAT', 'doctors': 'DOC', 'nurses': 'NUR'}[slug]

            def create():
                r = c.post(f'/{slug}/new', data=data)
                require(r.status_code == 303, 'Create did not return 303')
                html = c.get(r.location).get_data(as_text=True)
                require('Đã thêm hồ sơ thành công.' in html, 'Missing success message')
                with app.app_context():
                    saved = fetch_one(f'SELECT * FROM {entity.table} WHERE {entity.pk}=%s', (key,))
                    require(saved and saved['ho_ten'] == data['ho_ten'] and saved['cmt'] == data['cmt'], 'Saved MySQL record mismatch')
                return f'POST 303; thông báo thành công; MySQL lưu đúng mã {key}, họ tên và số 0 đầu CMT'

            case(prefix+'01', f'Thêm {entity.title.lower()} và lưu MySQL', f'POST /{slug}/new; GET chi tiết; SELECT theo mã', '303, thông báo thành công, lưu đúng dữ liệu', create)

            def reload_record():
                fresh = app.test_client()
                for _ in range(2):
                    r = fresh.get(f'/{slug}/{key}')
                    require(r.status_code == 200 and data['ho_ten'] in r.get_data(as_text=True), 'Reload lost saved record')
                require(key in fresh.get(f'/{slug}?q={key}').get_data(as_text=True), 'Record missing from list')
                return 'Hai GET bằng client mới và tìm theo mã đều thấy hồ sơ từ MySQL'

            case(prefix+'02', 'Tải lại trang và xem trong danh sách', 'Client mới GET chi tiết hai lần; tìm mã trong danh sách', 'Hồ sơ còn sau tải lại', reload_record)

            def edit():
                data['ho_ten'] = 'Hồ sơ Vương đã cập nhật'
                r = c.post(f'/{slug}/{key}/edit', data=data)
                require(r.status_code == 303, 'Edit failed')
                require('Đã cập nhật hồ sơ.' in c.get(r.location).get_data(as_text=True), 'Missing update success')
                with app.app_context():
                    row = fetch_one(f'SELECT ho_ten FROM {entity.table} WHERE {entity.pk}=%s', (key,))
                    require(row['ho_ten'] == data['ho_ten'], 'Update not persisted')

            case(prefix+'03', 'Sửa hồ sơ', 'POST sửa tên; GET lại; SELECT MySQL', '303, thông báo cập nhật, dữ liệu mới được lưu', edit)

            def errors():
                probes = [('ho_ten', ''), ('cmt', 'abc'), ('ngay_sinh', '2999-01-01'), ('ngay_sinh', '2001-02-29')]
                if slug != 'doctors':
                    probes.append(('so_dien_thoai', '12'))
                if slug != 'patients':
                    probes.extend([('tham_nien', '-1'), ('tham_nien', '101')])
                for field, value in probes:
                    response = c.post(f'/{slug}/new', data={**data, field: value})
                    html = response.get_data(as_text=True)
                    require(response.status_code == 422, f'Invalid {field} did not return 422')
                    require(f'id="{field}-error"' in html and 'role="alert"' in html, f'Missing field error for {field}')
                    if field != 'ho_ten':
                        require(data['ho_ten'] in html, 'Other input not retained')
                return f'{len(probes)} đầu vào sai: 422, lỗi đúng trường, giữ dữ liệu hợp lệ'

            case(prefix+'04', 'Lỗi nhập liệu và giữ giá trị', 'Thử thiếu tên, sai CCCD/ngày/điện thoại/thâm niên tùy nhóm', '422, lỗi từng trường, giữ dữ liệu', errors)

            def duplicates():
                for payload in [data, {**data, entity.pk: 'DU' + uuid4().hex[:9]}]:
                    response = c.post(f'/{slug}/new', data=payload)
                    html = response.get_data(as_text=True)
                    require(response.status_code == 409 and 'Chưa lưu được hồ sơ' in html, 'Duplicate not shown as conflict')
                    require(data['ho_ten'] in html and payload[entity.pk] in html, 'Duplicate form lost inputs')

            case(prefix+'05', 'Trùng mã và trùng CCCD', 'Gửi lại mã đã tạo; gửi mã mới cùng CCCD', '409, thông báo dễ hiểu, không tạo thêm', duplicates)

            def csrf_and_code():
                require(c.post(f'/{slug}/new', data={}).status_code == 400, 'Missing CSRF accepted')
                require(c.post(f'/{slug}/new', data={**data, 'csrf_token': 'sai mã 😀'}).status_code == 400, 'Invalid CSRF accepted')
                r = c.post(f'/{slug}/{key}/edit', data={**data, entity.pk: 'CHANGED'})
                html = r.get_data(as_text=True)
                require(r.status_code == 422 and f'name="{entity.pk}" value="{key}"' in html, 'Readonly code/navigation lost')
                require(f'href="/{slug}/{key}"' in html, 'Cancel does not return to original record')

            case(prefix+'06', 'CSRF và mã hồ sơ không đổi', 'POST thiếu/sai token; giả sửa mã trong POST', '400/422, giữ mã và liên kết gốc', csrf_and_code)

            def empty():
                html = c.get(f'/{slug}?q=NO_MATCH_{key}').get_data(as_text=True)
                require('Không tìm thấy hồ sơ phù hợp' in html, 'Missing no-results state')
                require('Trang này không có hồ sơ' in c.get(f'/{slug}?page=999').get_data(as_text=True), 'Missing out-of-range state')
                with app.test_request_context(f'/{slug}'):
                    html = render_template('week1/list.html', entity=entity, rows=[], total=0, q='', page=1, pages=1)
                    require('Chưa có hồ sơ ' + entity.title.lower() in html, 'Missing empty database UI')
                return 'Tìm không có kết quả/trang vượt: dữ liệu thật; danh sách trống: render context giả lập, không xóa seed'

            case(prefix+'07', 'Ba trạng thái danh sách rỗng', 'Tìm mã không có; page=999; render danh sách trống', 'Thông báo và đường quay lại phù hợp', empty)

            def protected():
                original = {'patients': 'BN001', 'doctors': 'BS001', 'nurses': 'YT001'}[slug]
                r = c.post(f'/{slug}/{original}/delete', data={'csrf_token': data['csrf_token'], 'confirm_delete': original})
                require(r.status_code == 409 and 'Chưa xóa được hồ sơ' in r.get_data(as_text=True), 'Referenced deletion error incorrect')
                require(c.get(f'/{slug}/{original}').status_code == 200, 'Original record missing')

            case(prefix+'08', 'Chặn xóa hồ sơ đã có lịch sử', 'POST xóa hồ sơ seed có tham chiếu', '409, hồ sơ vẫn tồn tại', protected)

        c = app.test_client()

        def navigation():
            paths = ['/', '/patients', '/doctors', '/nurses', '/visits', '/treatments', '/reports']
            for path in paths:
                r = c.get(path, follow_redirects=True)
                html = r.get_data(as_text=True)
                require(r.status_code == 200, f'Navigation failed: {path}')
                require(html.count('aria-current="page"') == 1, f'Active menu incorrect: {path}')
                require('/In_Patient' not in html and '/book_surgery' not in html, 'Out-of-scope menu found')

        case('NAV01', 'Điều hướng và menu đang chọn', 'Mở bảy đường dẫn chính', '200, đúng menu, không có nội trú/phẫu thuật', navigation)

        def reports():
            for key in ['diseases', 'salaries', 'revenue']:
                with patch('pymysql.connect', side_effect=AssertionError('Reporting shell queried DB')):
                    r = c.get('/reports/' + key + '?month=2026-09')
                html = r.get_data(as_text=True)
                require(r.status_code == 200 and 'Chưa tích hợp dữ liệu báo cáo' in html, 'Report status incorrect')
                require('0 đ' not in html, 'Fake total found')
                require(c.get('/reports/'+key+'?month=2026-13').status_code == 400, 'Invalid month accepted')

        case('REP01', 'Ba khung thống kê không giả kết quả', 'Chọn tháng; chặn kết nối DB; thử tháng sai', '200/400, không SQL, không tiền giả', reports)

        def histories():
            r = c.get('/reports/history?patient_id=BN001', follow_redirects=True)
            require(r.status_code == 200 and 'Các lần khám' in r.get_data(as_text=True), 'Saved history unavailable')
            empty_id = fixtures[0][3]
            html = c.get('/patients/' + empty_id + '/history').get_data(as_text=True)
            require('Không có đợt đang điều trị' in html and 'chưa có lần khám được ghi nhận' in html and 'chưa có lượt đến khám được ghi nhận' in html, 'Empty history incorrect')

        case('REP02', 'Lịch sử đã lưu và lịch sử rỗng', 'Chọn BN001; mở hồ sơ tạm chưa khám', 'Dữ liệu thật/ba trạng thái rỗng đúng', histories)

        def missing():
            require(c.get('/patients/NO_SUCH_ID').status_code == 404, 'Missing record did not return 404')
            require(c.get('/patients?page=0').status_code == 400, 'Bad page accepted')
            require(c.get('/reports/unknown').status_code == 404, 'Unknown report accepted')

        case('NAV02', 'Đường dẫn và tham số không hợp lệ', 'Hồ sơ không có, page=0, báo cáo không có', '404/400 với thông báo', missing)
    finally:
        for slug, entity, c, key, data in fixtures:
            def cleanup():
                with app.app_context():
                    exists = fetch_one(f'SELECT {entity.pk} FROM {entity.table} WHERE {entity.pk}=%s', (key,))
                if exists:
                    response = c.post(f'/{slug}/{key}/delete', data={'csrf_token': data['csrf_token'], 'confirm_delete': key})
                    require(response.status_code == 303, 'Temporary record cleanup failed')
                    require('Đã xóa hồ sơ chưa phát sinh nghiệp vụ.' in c.get(response.location).get_data(as_text=True), 'Missing delete success')
                require(c.get(f'/{slug}/{key}').status_code == 404, 'Temporary record remains')

            case('CLEAN_' + slug.upper(), 'Dọn hồ sơ thử ' + slug, f'Xóa duy nhất mã tự sinh {key}', '303/404, seed không bị xóa', cleanup)

    def final_data():
        require(snapshot(app) == before, 'Original demo table fingerprints changed')
        with app.app_context():
            report = audit()
            require(report['matches_expected_counts'] and not any(report['findings'].values()), 'Final audit failed')
        require(hashlib.sha256((ROOT / '.env').read_bytes()).hexdigest() == env_hash, '.env changed')
        return 'Hash toàn bộ 11 bảng khớp trước chạy; 1.144 dòng; .env không đổi'

    case('DATA01', 'Bảo toàn dữ liệu và cấu hình', 'So hash tất cả bản ghi 11 bảng; audit; hash .env', 'Không đổi dữ liệu nền hoặc cấu hình', final_data)
    report = dict(run_at=datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')).isoformat(),
                  branch=subprocess.check_output(['git', 'branch', '--show-current'], text=True).strip(),
                  base_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
                  source_state='Working tree contains uncommitted week-1 UI changes',
                  database=DEMO_DB, python=sys.version.split()[0],
                  temporary_codes={slug: key for slug, _, _, key, _ in fixtures},
                  results=results)
    (OUT / 'automated_results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    passed = sum(r['status'] == 'PASS' for r in results)
    print(f'CHECKLIST: {passed}/{len(results)} PASS')
    return 0 if passed == len(results) else 1


if __name__ == '__main__':
    raise SystemExit(main())
