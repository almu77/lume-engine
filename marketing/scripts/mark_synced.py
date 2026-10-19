#!/usr/bin/env python3
"""After the inbox upload, mark that batch's approved rows as synced (with a UTC timestamp)
so they never ship twice. Run only once lume-tag-index.csv shows the new max numbers.

Usage:  python3 scripts/mark_synced.py <batch_date>
"""
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from log_io import read_log, write_log  # noqa: E402


def main():
    if len(sys.argv) < 2:
        print("usage: mark_synced.py <batch_date>")
        return 1
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    rows = read_log()
    n = 0
    for r in rows:
        if r.get("batch_date") == sys.argv[1] and r.get("status") == "approved":
            r["status"], r["synced_at"] = "synced", stamp
            n += 1
    write_log(rows)
    print(f"marked {n} row(s) synced at {stamp}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
