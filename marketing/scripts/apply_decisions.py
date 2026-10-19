#!/usr/bin/env python3
"""Apply the newest VALIDATED console save to script-log.csv.

Always run check_decisions.py first (exit 0). This then:
  accept  -> status approved, finals = proposed
  edit    -> status approved, finals = Alp's text (unedited fields = proposed),
             <field>_edited flags + edit_reason logged
  rewrite -> status rewrite, reason logged (Claude redrafts, then add_drafts.py --rewrite)
  kill    -> status killed, reason logged
Rows with no decision are left as drafts. The processed decisions file is moved into
decisions-archive/ AFTER the log is written.

After this: fold every new reason into style-memory.md, then run check_reasons.py.

Usage:  python3 scripts/apply_decisions.py <batch_date>
"""
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from schema import COPY_FIELDS  # noqa: E402
from log_io import ROOT, read_log, write_log  # noqa: E402


def main():
    if len(sys.argv) < 2:
        print("usage: apply_decisions.py <batch_date>")
        return 1
    batch = sys.argv[1]
    chk = subprocess.run([sys.executable, os.path.join(HERE, "check_decisions.py"), batch],
                         capture_output=True, text=True)
    print(chk.stdout.strip())
    if chk.returncode != 0:
        print("Not applying - check_decisions.py did not pass.")
        return chk.returncode
    path = chk.stdout.splitlines()[0].split("OK: ", 1)[1].strip()
    obj = json.load(open(path, encoding="utf-8"))

    rows = read_log()
    by_id = {r["row_id"]: r for r in rows}
    counts = {}
    for d in obj["decisions"]:
        r = by_id.get(d["row_id"])
        if r is None:
            print(f"FAIL: {d['row_id']} not in script-log.csv")
            return 1
        act = d.get("action")
        counts[act] = counts.get(act, 0) + 1
        r["action"] = act
        if act in ("accept", "edit"):
            for f in COPY_FIELDS:
                fin = d.get(f"final_{f}")
                prop = r.get(f"proposed_{f}", "")
                edited = act == "edit" and fin is not None and fin != prop
                r[f"final_{f}"] = fin if edited else prop
                r[f"{f}_edited"] = "true" if edited else "false"
            r["edit_reason"] = (d.get("edit_reason") or "").strip()
            r["status"] = "approved"
        elif act == "rewrite":
            r["reason"] = (d.get("reason") or "").strip()
            # a rewrite can also carry inline edits + their reason (e.g. a changed rep count): keep both
            r["edit_reason"] = (d.get("edit_reason") or "").strip()
            for f in COPY_FIELDS:
                if d.get(f"final_{f}") is not None:
                    r["notes"] = ((r.get("notes") or "") + f" | rewrite-round edit {f}: {d[f'final_{f}']}").strip(" |")
            r["status"] = "rewrite"
        elif act == "kill":
            r["reason"] = (d.get("reason") or "").strip()
            r["status"] = "killed"
    write_log(rows)

    arch = os.path.join(ROOT, "decisions-archive")
    os.makedirs(arch, exist_ok=True)
    shutil.move(path, os.path.join(arch, os.path.basename(path)))
    print("applied: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))
    print("Next: fold the reasons into style-memory.md, then run check_reasons.py.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
