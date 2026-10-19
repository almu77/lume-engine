#!/usr/bin/env python3
"""Write lume-video-data-inbox.csv for the bound Apps Script to insert into "Lume - Video Data".

One row per APPROVED script in the batch. Claude then uploads it to Drive (connector
create_file) with the exact name `lume-video-data-inbox.csv`.

  *** NEVER name it video-data-inbox.csv - that is the Tough Hair inbox, and the Tough Hair
      Apps Script (still installed) would insert these rows into the Tough Hair sheet. ***

  *** BEFORE UPLOADING: re-read lume-tag-index.csv and pass --verify-tags. Tags reserved at
      draft time can be consumed by another batch before this one syncs; the sync dedupes by
      tag and would silently skip the colliding rows (bit Tough Hair twice, 06-21 and 06-22). ***

Usage:
  python3 scripts/make_sheet_inbox.py <batch_date> --verify-tags realtimejake=0,realjakemu=4
"""
import csv
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schema import INBOX_COLUMNS, INBOX_FILE  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, "script-log.csv")
OUT = os.path.join(ROOT, INBOX_FILE)
TAG_RE = re.compile(r"^([a-z][a-z0-9_.]*?)(\d+)$")


def parse_tag(tag):
    m = TAG_RE.match((tag or "").strip())
    return (m.group(1), int(m.group(2))) if m else (None, None)


def build_script_cell(r):
    """Hook + body + app demo + CTA collapse into the one Script cell, newline separated,
    each part [TAG]-prefixed so the cell is scannable on a shoot day and can be split back
    into columns programmatically later."""
    parts = []
    hook = r.get("final_hook") or r.get("proposed_hook", "")
    if hook:
        parts.append("[HOOK] " + hook.strip())
    body = r.get("final_script") or r.get("proposed_script", "")
    # the script's own first "[caption] ..." line repeats the hook: drop it, [HOOK] already carries it
    lines = body.strip().split("\n")
    if hook and lines and lines[0].strip().lower().startswith("[caption]") and \
            lines[0].split("]", 1)[1].strip() == hook.strip():
        body = "\n".join(lines[1:])
    if body:
        parts.append(body.strip())
    demo = r.get("final_app_demo") or r.get("proposed_app_demo", "")
    if demo:
        parts.append("[APP] " + demo.strip())
    cta = r.get("final_cta") or r.get("proposed_cta", "")
    if cta and cta.strip().lower() != "none":
        parts.append("[CTA] " + cta.strip())
    return "\n".join(parts)


def main():
    if len(sys.argv) < 2:
        print("usage: make_sheet_inbox.py <batch_date> [--verify-tags acct=max,acct=max]")
        return 1
    batch = sys.argv[1]
    live_max = {}
    if "--verify-tags" in sys.argv:
        for part in sys.argv[sys.argv.index("--verify-tags") + 1].split(","):
            acct, _, val = part.partition("=")
            live_max[acct.strip()] = int(val or 0)

    with open(LOG, newline="", encoding="utf-8") as fh:
        rows = [r for r in csv.DictReader(fh)
                if r.get("batch_date") == batch and r.get("status") == "approved"]
    if not rows:
        print(f"FAIL: no approved rows for batch {batch}.")
        return 1

    collisions, seen = [], set()
    for r in rows:
        acct, num = parse_tag(r.get("video_tag"))
        if acct is None:
            print(f"FAIL: unparseable tag {r.get('video_tag')!r} on row {r['row_id']}")
            return 1
        if r["video_tag"] in seen:
            collisions.append((r["row_id"], r["video_tag"], "duplicate inside this batch"))
        seen.add(r["video_tag"])
        if acct in live_max and num <= live_max[acct]:
            collisions.append((r["row_id"], r["video_tag"], f"live max is {live_max[acct]}"))
    if collisions:
        print("STOP - tag collisions:")
        for rid, tag, why in collisions:
            print(f"  {rid}: {tag} ({why})")
        print("Bump these tags in script-log.csv and re-run. Do NOT upload as-is.")
        return 2
    if not live_max:
        print("WARNING: ran without --verify-tags. Re-read lume-tag-index.csv and re-run with it.")

    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=INBOX_COLUMNS)
        w.writeheader()
        for r in rows:
            w.writerow({
                "video_tag": r.get("video_tag", ""),
                "format": r.get("format", ""),
                "angle": r.get("angle", ""),
                "script": build_script_cell(r),
                "description": r.get("final_description") or r.get("proposed_description", ""),
                "mission": r.get("mission", ""),
                "target_niche": r.get("target_niche", ""),
                "posted_to_account": r.get("account", ""),
            })
    print(f"wrote {OUT} - {len(rows)} rows for batch {batch}")
    print(f"Next: upload to Drive via create_file, exact title '{INBOX_FILE}', "
          "contentMimeType text/csv, disableConversionToGoogleType true.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
