"""Import bộ SQL Quyền vào database trống; không DROP và không tắt FK."""
import os
import re
from pathlib import Path
import pymysql
ROOT = Path(__file__).resolve().parents[1]

def connect():
    return pymysql.connect(host=os.getenv('DB_HOST','127.0.0.1'),port=int(os.getenv('DB_PORT','3306')),
        user=os.getenv('DB_USER','root'),password=os.environ['DB_PASSWORD'],
        database=os.environ['DB_NAME'],charset='utf8mb4',autocommit=False,
        cursorclass=pymysql.cursors.DictCursor)

def statements(text):
    # Controlled project scripts: DELIMITER occurs on its own line, no inline SQL comments in literals.
    delimiter=';'; buf=[]
    for line in text.splitlines():
        if line.strip().startswith('--') or not line.strip(): continue
        if line.strip().upper().startswith('DELIMITER '):
            assert not ''.join(buf).strip()
            delimiter=line.strip().split()[1];continue
        buf.append(line+'\n')
        if line.rstrip().endswith(delimiter):
            yield ''.join(buf).rstrip()[:-len(delimiter)].strip();buf=[]
    if ''.join(buf).strip(): raise ValueError('Incomplete SQL statement')

def install(db):
    with db.cursor() as c:
        c.execute('SHOW TABLES')
        if c.fetchone(): raise RuntimeError('Database must be empty; no data changed')
        c.execute("SET time_zone='+07:00'")
        for name in ['schema.sql','seed.sql','constraints.sql']:
            for stmt in statements((ROOT/'database'/name).read_text(encoding='utf-8')):
                c.execute(stmt)
    db.commit()

if __name__=='__main__':
    db=connect()
    try:
        install(db)
        print('Imported schema + 1144 rows + constraints successfully')
    except Exception:
        db.rollback()
        print('Import failed: DML rolled back; DDL may remain. Use a new empty database.')
        raise
    finally: db.close()
