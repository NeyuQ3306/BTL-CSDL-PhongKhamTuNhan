"""Read-only release receipt; never print credentials or import/drop a database."""
import argparse
import json
import platform
import subprocess
from pathlib import Path
from clinic_app import create_app
from clinic_app.db import fetch_all, fetch_one
from tools.audit_seed import audit
from tools.quyen_db import statements


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--expected-sha', help='Require this exact git HEAD')
    parser.add_argument('--output', type=Path, help='Create a new JSON receipt; existing file is not overwritten')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=root, capture_output=True, text=True)
    sha = result.stdout.strip() if result.returncode == 0 else None
    if args.expected_sha and sha != args.expected_sha:
        parser.error('Source HEAD does not match --expected-sha; no DB queries executed')
    app = create_app()
    with app.app_context():
        data = audit()
        triggers = fetch_one('SELECT COUNT(*) n FROM information_schema.TRIGGERS WHERE TRIGGER_SCHEMA=DATABASE()')['n']
        sql_results = [len(fetch_all(sql)) for sql in statements((root/'database/audit.sql').read_text(encoding='utf-8'))]
        data.update(source_sha=sha, python=platform.python_version(), os=platform.platform(),
                    database=app.config['DB_NAME'], trigger_count=triggers, sql_audit_row_counts=sql_results)
    data['passed'] = (data['matches_expected_counts'] and triggers == 9 and len(sql_results) == 10
                      and not any(sql_results) and not any(data['findings'].values()))
    payload = json.dumps(data, ensure_ascii=False, indent=2, default=str)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x', encoding='utf-8') as stream:
            stream.write(payload + '\n')
    print(payload)
    return 0 if data['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
