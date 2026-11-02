"""SQL contract runner for verification/handoff; no routes or UI here."""
import re
from datetime import date
from pathlib import Path

SQL_PATH = Path(__file__).resolve().parents[1] / 'database/analytics_queries.sql'


def queries():
    source = SQL_PATH.read_text(encoding='utf-8')
    result = dict(re.findall(r'-- (R\d{2})-BEGIN\n(.*?)\n-- R\d{2}-END', source, re.S))
    if list(result) != [f'R{i:02}' for i in range(1, 8)]:
        raise ValueError('Expected exactly R01-R07')
    return result


def run(db, start, end, as_of, threshold=14):
    """Existing connection; never commits. Dates are ISO, end is exclusive."""
    dates = []
    for value in (start, end, as_of):
        if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
            raise ValueError('Expected YYYY-MM-DD')
        dates.append(date.fromisoformat(value))
    if dates[0] >= dates[1]:
        raise ValueError('start must precede exclusive end')
    if type(threshold) is not int or not 0 <= threshold <= 36500:
        raise ValueError('threshold must be an integer in 0..36500')
    with db.cursor() as cursor:
        cursor.execute('SET @tu=%s, @den=%s, @ngay_doi_chieu=%s, @nguong_ngay=%s',
                       (start, end, as_of, threshold))
        output = {}
        for name, sql in queries().items():
            cursor.execute(sql)
            output[name] = list(cursor.fetchall())
    return output
