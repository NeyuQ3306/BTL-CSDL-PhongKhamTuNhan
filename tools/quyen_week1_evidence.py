"""Collect reproducible week-1 evidence on a disposable *_test database."""
import argparse
import json
import os
import platform
import subprocess
from pathlib import Path
from tools.quyen_db import ROOT, connect, statements

OUT = ROOT / "test-artifacts" / "quyen-week1"

def execute_file(db, name, require_empty=False):
    results = []
    with db.cursor() as cur:
        for sql in statements((ROOT / "database" / name).read_text(encoding="utf-8")):
            cur.execute(sql)
            if cur.description:
                rows = cur.fetchall()
                results.append(rows)
                if require_empty and rows:
                    raise RuntimeError(f"{name}: audit has findings: {rows}")
    return results

def collect(install=False):
    if not os.environ.get("DB_NAME", "").endswith("_test"):
        raise RuntimeError("Use a dedicated disposable database ending in _test")
    OUT.mkdir(parents=True, exist_ok=True)
    report = {
        "source_sha": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "python": platform.python_version(), "platform": platform.platform(),
        "scope": "Automated isolated acceptance; not evidence of Quyen/Trung Windows machines",
        "sequence": [], "success": False,
    }
    db = connect()
    try:
        with db.cursor() as cur:
            cur.execute("SELECT VERSION() AS version")
            report["mysql"] = cur.fetchone()["version"]
            cur.execute("SET time_zone='+07:00'")
            if install:
                cur.execute("SHOW TABLES")
                if cur.fetchall():
                    raise RuntimeError("Database must be empty; no import performed")
        if install:
            for name in ("schema.sql", "seed.sql", "audit.sql", "constraints.sql", "audit.sql", "queries.sql"):
                result = execute_file(db, name, require_empty=name == "audit.sql")
                report["sequence"].append({"file": name, "result_sets": len(result), "passed": True})
            db.commit()
        audits = execute_file(db, "audit.sql", require_empty=True)
        report["audit_query_count"] = len(audits)
        with db.cursor() as cur:
            cur.execute("SHOW TABLES")
            report["table_count"] = len(cur.fetchall())
            cur.execute("SELECT COUNT(*) AS n FROM information_schema.TRIGGERS WHERE TRIGGER_SCHEMA=DATABASE()")
            report["trigger_count"] = cur.fetchone()["n"]
        if report["table_count"] != 11 or report["trigger_count"] != 9:
            raise RuntimeError("Expected 11 tables and 9 triggers")
        # Capture actual query outputs; independent Python-oracle assertions run in pytest.
        report["queries_default"] = execute_file(db, "queries.sql")
        report["success"] = True
    finally:
        db.rollback()
        db.close()
        (OUT / ("canonical-import.json" if install else "final-audit-queries.json")).write_text(
            json.dumps(report, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k != "queries_default"}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--install", action="store_true", help="Install only into an empty *_test DB")
    collect(parser.parse_args().install)
