#!/usr/bin/env python3
"""Append a batch of draft scripts to script-log.csv from a JSON file.

Claude writes the drafts as a JSON list (one object per script) and runs this, rather than
hand-editing the CSV - multi-line script cells are easy to corrupt by hand.

Each object needs: batch_date, account, video_tag, angle_no, angle, format, mission,
target_niche, timing_target, rationale, hook, script, app_demo, cta, description.
row_id is generated as <video_tag>-<nn>.

A REWRITE round uses --rewrite: objects carry row_id + the five copy fields, and the
existing row's proposed_* fields are replaced, finals cleared, status set back to draft.

Usage:
  python3 scripts/add_drafts.py drafts.json
  python3 scripts/add_drafts.py redrafts.json --rewrite
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schema import COPY_FIELDS  # noqa: E402
from log_io import read_log, write_log  # noqa: E402

REQUIRED = ["batch_date", "account", "video_tag", "angle_no", "angle", "format", "mission",
            "target_niche", "timing_target", "rationale"] + COPY_FIELDS


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    items = json.load(open(sys.argv[1], encoding="utf-8"))
    rewrite = "--rewrite" in sys.argv
    rows = read_log()

    if rewrite:
        by_id = {r["row_id"]: r for r in rows}
        for it in items:
            r = by_id.get(it.get("row_id"))
            if r is None:
                print(f"FAIL: row_id {it.get('row_id')!r} not in script-log.csv")
                return 1
            if r.get("status") != "rewrite":
                print(f"FAIL: {r['row_id']} has status {r.get('status')!r}, expected 'rewrite'")
                return 1
            prior = (r.get("notes") or "").strip()
            r["notes"] = (prior + " | " if prior else "") + \
                f"round redraft; prior reason: {r.get('reason', '')}"
            for f in COPY_FIELDS:
                if f in it:
                    r[f"proposed_{f}"] = it[f]
                r[f"final_{f}"] = ""
                r[f"{f}_edited"] = ""
            for k in ("rationale", "mission", "target_niche", "timing_target"):
                if k in it:
                    r[k] = it[k]
            r["status"] = "draft"
            r["action"] = ""
        write_log(rows)
        print(f"redrafted {len(items)} row(s); now re-run make_review_json.py")
        return 0

    existing_tags = {r.get("video_tag") for r in rows if r.get("status") != "killed"}
    new = []
    for i, it in enumerate(items, 1):
        miss = [k for k in REQUIRED if str(it.get(k, "")).strip() == ""]
        if miss:
            print(f"FAIL: item {i} ({it.get('video_tag')}) missing: {', '.join(miss)} "
                  "(use 'none' for an intentionally empty CTA/mission)")
            return 1
        if it["video_tag"] in existing_tags:
            print(f"FAIL: tag {it['video_tag']} already in script-log.csv")
            return 1
        existing_tags.add(it["video_tag"])
        r = {k: str(it[k]) for k in REQUIRED if k not in COPY_FIELDS}
        r["row_id"] = f"{it['video_tag']}-{i:02d}"
        for f in COPY_FIELDS:
            r[f"proposed_{f}"] = it[f]
        r["status"] = "draft"
        new.append(r)
    write_log(rows + new)
    print(f"appended {len(new)} draft row(s) for batch {new[0]['batch_date'] if new else '?'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
