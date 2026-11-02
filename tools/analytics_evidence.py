"""Read-only R01-R07 evidence against canonical seed; fail on any difference."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from tools.quyen_db import connect, ROOT
from tools.analytics_sql import run, SQL_PATH
from tools.analytics_oracle import seed_rows, expected, normalize, canonical


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='test-artifacts/analytics/seed-results.json')
    args = parser.parse_args()
    source = seed_rows()
    params = dict(start='2026-07-01',end='2026-10-15',as_of='2026-10-14',threshold=14)
    db = connect()
    try:
        with db.cursor() as c:
            c.execute('SELECT VERSION() AS version')
            version = c.fetchone()['version']
            before = {}
            for table, rows in source.items():
                c.execute('SELECT * FROM '+table)
                actual = canonical(c.fetchall())
                assert actual == canonical(rows), 'Not canonical seed: '+table
                before[table] = actual
        actual = run(db,**params)
        wanted = expected(source,**params)
        for name in actual:
            assert canonical(actual[name]) == canonical(wanted[name]), name
        with db.cursor() as c:
            for table in source:
                c.execute('SELECT * FROM '+table)
                assert canonical(c.fetchall()) == before[table], 'Changed: '+table
        evidence = dict(generated_at=datetime.now(timezone.utc).isoformat(),mysql_version=version,
            base_commit='98bd2675bfffc64be09c87dd2897148f8b02b440',
            sql_sha256=hashlib.sha256(SQL_PATH.read_bytes()).hexdigest(),
            seed_sha256=hashlib.sha256((ROOT/'database/seed.sql').read_bytes()).hexdigest(),
            parameters=params,seed_rows=sum(map(len,source.values())),seed_unchanged=True,
            oracle_match=True,results=normalize(actual),expected=normalize(wanted))
        path = Path(args.output)
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(dict(mysql_version=version,oracle_match=True,seed_unchanged=True,
            result_rows={k:len(v) for k,v in actual.items()},output=str(path)),ensure_ascii=False))
    finally:
        db.rollback()
        db.close()


if __name__ == '__main__':
    main()
