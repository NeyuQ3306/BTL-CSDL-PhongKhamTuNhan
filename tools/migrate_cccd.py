"""Inspect or explicitly apply the cmt -> cccd migration to the configured schema."""
import argparse
from pathlib import Path

from dotenv import load_dotenv
from tools.quyen_db import connect, statements

TABLES = ('bac_si', 'y_ta', 'benh_nhan')


def inspect(db):
    states = {}
    with db.cursor() as cur:
        for table in TABLES:
            cur.execute('SELECT COLUMN_NAME FROM information_schema.COLUMNS '
                        'WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=%s '
                        "AND COLUMN_NAME IN ('cmt','cccd')", (table,))
            states[table] = {r['COLUMN_NAME'] for r in cur.fetchall()}
    if any(names not in ({'cmt'}, {'cccd'}) for names in states.values()):
        raise RuntimeError('Each profile table must contain exactly one of cmt/cccd; no changes made')
    return states


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true', help='Apply DDL after stopping the app and backing up')
    args = parser.parse_args()
    load_dotenv()
    db = connect()
    try:
        before = inspect(db)
        for table, names in before.items():
            print(f'{table}: {next(iter(names))}')
        if not args.apply:
            print('Check only. To migrate, stop the app, back up and run again with --apply.')
            return
        source = Path(__file__).resolve().parents[1] / 'database/migrations/001_cmt_to_cccd.sql'
        with db.cursor() as cur:
            for sql in statements(source.read_text(encoding='utf-8')):
                cur.execute(sql)
        if any(names != {'cccd'} for names in inspect(db).values()):
            raise RuntimeError('Migration incomplete; keep the app stopped and inspect the schema')
        print('All three profile columns are cccd. Existing values and constraints are retained.')
    except Exception:
        # DDL implicitly commits. Do not claim rollback can undo completed ALTERs.
        print('If any ALTER ran, it may already be committed. Keep the app stopped; inspect before retrying.')
        raise
    finally:
        db.close()


if __name__ == '__main__':
    main()
