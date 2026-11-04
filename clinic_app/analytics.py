"""Read-only R01–R07 services, using Quyen's versioned SQL without new formulas."""
import re
from collections import Counter
from datetime import date
from decimal import Decimal
from functools import lru_cache
from pathlib import Path

from flask import g
from werkzeug.exceptions import BadRequest, NotFound
from .db import get_db

REPORTS = {
    'R01': 'Bệnh theo nhóm tuổi',
    'R02': 'Tiếp nhận và khám theo ngày',
    'R03': 'Khối lượng khám theo bác sĩ',
    'R04': 'Thuốc được kê',
    'R05': 'Đợt tái mắc có tiền sử ghi nhận',
    'R06': 'Lâu chưa ghi nhận khám',
    'R07': 'Chi phí đợt đã khỏi theo bệnh',
}
MONEY = {'tb_tien_kham', 'tb_tien_thuoc', 'tb_tong', 'min_tong', 'max_tong'}
VARIABLES = {'tu': 'start', 'den': 'end', 'ngay_doi_chieu': 'as_of', 'nguong_ngay': 'threshold'}
DEFAULTS = dict(start='2026-07-01', end='2026-10-15', as_of='2026-10-14', threshold=14)


def iso_date(value, field):
    if not isinstance(value, str) or not re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', value):
        raise BadRequest(f'{field} phải có dạng YYYY-MM-DD.')
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError:
        raise BadRequest(f'{field} không phải ngày hợp lệ.') from None


def filters(args, report_id=None):
    """Validate before opening MySQL. end is exclusive, never advanced a second time."""
    if report_id is not None and report_id not in REPORTS:
        raise NotFound('Không tìm thấy báo cáo R01–R07.')
    allowed = {'start', 'end', 'as_of', 'threshold', 'age_group'}
    if report_id == 'R06':
        allowed = {'as_of', 'threshold'}
    elif report_id:
        allowed = {'start', 'end'} | ({'age_group'} if report_id == 'R01' else set())
    if set(args) - allowed:
        raise BadRequest('Bộ lọc không được hỗ trợ cho báo cáo này.')
    if hasattr(args, 'getlist') and any(len(args.getlist(k)) != 1 for k in args):
        raise BadRequest('Mỗi bộ lọc chỉ được truyền một lần.')
    result = DEFAULTS.copy()
    for name in ('start', 'end', 'as_of'):
        if name in allowed:
            result[name] = iso_date(args.get(name, DEFAULTS[name]), name)
    if result['start'] >= result['end']:
        raise BadRequest('start phải trước end; end là ngày kết thúc không bao gồm.')
    value = args.get('threshold', DEFAULTS['threshold'])
    if type(value) is int:
        threshold = value
    elif isinstance(value, str) and re.fullmatch(r'[0-9]{1,5}', value):
        threshold = int(value)
    else:
        raise BadRequest('threshold phải là số nguyên từ 0 đến 36500.')
    if not 0 <= threshold <= 36500:
        raise BadRequest('threshold phải là số nguyên từ 0 đến 36500.')
    result['threshold'] = threshold
    age_group = args.get('age_group')
    if age_group is not None and str(age_group) not in {'-1', '0', '1', '2', '3'}:
        raise BadRequest('age_group chỉ nhận -1, 0, 1, 2 hoặc 3.')
    if age_group is not None:
        result['age_group'] = int(age_group)
    return result


@lru_cache(maxsize=1)
def sql_queries():
    path = Path(__file__).resolve().parents[1] / 'database' / 'analytics_queries.sql'
    source = path.read_text(encoding='utf-8')
    matches = re.findall(r'-- (R\d{2})-BEGIN\n(.*?)\n-- (R\d{2})-END', source, re.S)
    if [a for a, _, b in matches if a == b] != list(REPORTS) or len(matches) != 7:
        raise RuntimeError('SQL analytics markers must be exactly R01–R07')
    return {a: sql for a, sql, _ in matches}


def bind(sql, values):
    """Only replace allowlisted variables in trusted repository SQL, not user text."""
    params = []
    def replace(match):
        params.append(values[VARIABLES[match[1]]])
        return '%s'
    return re.sub(r'@(tu|den|ngay_doi_chieu|nguong_ngay)\b', replace, sql), tuple(params)


def serialize(rows):
    result = []
    for row in rows:
        item = {}
        for key, value in row.items():
            if value is None:
                item[key] = None
            elif key in MONEY:
                item[key] = format(Decimal(value), '.2f')
            elif isinstance(value, Decimal):
                if value != value.to_integral_value():
                    raise ValueError('Non-integral value in analytics count column')
                item[key] = int(value)
            elif isinstance(value, date):
                item[key] = value.isoformat()
            else:
                item[key] = value
        result.append(item)
    return result


def display_groups(report_id, rows):
    """Presentation-only grouping of the exact rows returned to the table."""
    if report_id == 'R05':
        counts = Counter((r['ma_benh'], r['ten_benh']) for r in rows)
        return [dict(ma_benh=k[0], ten_benh=k[1], so_dot=v) for k, v in sorted(counts.items())]
    if report_id == 'R06':
        counts = Counter(r['nhom_ngay'] for r in rows)
        return [dict(nhom_ngay=k, so_dot=counts[k]) for k in ('0–6', '7–13', '14–29', '30+')]
    return []


def payload(report_id, rows, values):
    if report_id == 'R01' and 'age_group' in values:
        rows = [r for r in rows if r['thu_tu_nhom'] == values['age_group']]
    rows = serialize(rows)
    keys = ('as_of', 'threshold') if report_id == 'R06' else ('start', 'end')
    selected = {k: values[k] for k in keys}
    if report_id == 'R01' and 'age_group' in values:
        selected['age_group'] = values['age_group']
    return dict(report_id=report_id, title=REPORTS[report_id], filters=selected,
                interval='end_exclusive' if report_id != 'R06' else 'end_of_as_of_day',
                rows=rows, row_count=len(rows), chart_groups=display_groups(report_id, rows),
                money_unit='VND', data_notice='Dữ liệu giả lập, mô tả hồ sơ đã lưu.')


def build(values, report_id=None):
    """One read-only repeatable-read snapshot for either one or all seven reports."""
    if report_id is not None and report_id not in REPORTS:
        raise NotFound('Không tìm thấy báo cáo R01–R07.')
    if g.get('in_transaction', False):
        raise RuntimeError('Analytics cannot run inside a write transaction')
    names = (report_id,) if report_id else tuple(REPORTS)
    source = sql_queries()  # fail before starting a transaction if dependency is missing
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ')
            cursor.execute('START TRANSACTION WITH CONSISTENT SNAPSHOT, READ ONLY')
            result = {}
            for name in names:
                sql, params = bind(source[name], values)
                cursor.execute(sql, params)
                result[name] = payload(name, list(cursor.fetchall()), values)
        return result[report_id] if report_id else dict(reports=result, filters=values)
    finally:
        db.rollback()  # finish read snapshot on success and failure; never commit
