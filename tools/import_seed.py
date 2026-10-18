"""Import the reviewed week-1 seed into an EMPTY, existing database only."""
import argparse
from pathlib import Path
import pymysql
from dotenv import load_dotenv
from clinic_app.config import settings


def statements(source):
    # Supports this seed's comments, quoted strings and escaped/doubled quotes.
    import re
    tokens = re.finditer(r"'(?:''|\\.|[^'\\])*'|\"(?:\"\"|\\.|[^\"\\])*\"|--[^\n]*|/\*[\s\S]*?\*/|;|[^;'\"/-]+|.", source)
    parts = []
    for match in tokens:
        token = match.group()
        if token.startswith(('--', '/*')):
            parts.append('\n')
        elif token == ';':
            if ''.join(parts).strip():
                yield ''.join(parts).strip()
            parts = []
        else:
            parts.append(token)
    if ''.join(parts).strip():
        yield ''.join(parts).strip()


def import_seed(db):
    with db.cursor() as cur:
        cur.execute('SHOW TABLES')
        if cur.fetchone():
            raise RuntimeError('Database is not empty. Import refused; no data was changed.')
        source = Path(__file__).resolve().parents[1] / 'database/week1/clinic_seed.sql'
        try:
            for statement in statements(source.read_text(encoding='utf-8')):
                cur.execute(statement)
            db.commit()
        except Exception:
            db.rollback()
            # MySQL DDL commits implicitly. Do not drop tables or pretend atomic DDL.
            raise RuntimeError('Import failed. DML rolled back; created tables may remain. Use a new empty database.') from None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    load_dotenv()
    cfg = settings()
    db = pymysql.connect(host=cfg['DB_HOST'], port=cfg['DB_PORT'], user=cfg['DB_USER'],
                         password=cfg['DB_PASSWORD'], database=cfg['DB_NAME'], charset='utf8mb4')
    try:
        import_seed(db)
        print('Imported 11 tables. Run python -m tools.audit_seed to verify counts and business rules.')
    finally:
        db.close()


if __name__ == '__main__':
    main()
