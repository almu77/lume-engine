#!/usr/bin/env python3
"""Write post-list.json: the batch's approved scripts in their FINAL wording, for the console's
Post tab (Alp copies the caption + description from it while scheduling on the phones).

Run after apply_decisions.py and after mark_synced.py.
Usage:  python3 scripts/make_post_list.py <batch_date>
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from log_io import ROOT, read_log  # noqa: E402


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    batch = sys.argv[1]
    out = []
    for r in read_log():
        if r.get("batch_date") != batch or r.get("status") not in ("approved", "synced"):
            continue
        out.append({
            "row_id": r["row_id"], "video_tag": r["video_tag"], "account": r["account"],
            "mission": r.get("mission", ""), "target_niche": r.get("target_niche", ""),
            "file_name": "lume_" + r["video_tag"],
            "hook": r.get("final_hook") or r.get("proposed_hook", ""),
            "description": r.get("final_description") or r.get("proposed_description", ""),
            "status": r["status"], "synced_at": r.get("synced_at", ""),
        })
    out.sort(key=lambda x: (x["account"], x["video_tag"]))
    json.dump(out, open(os.path.join(ROOT, "post-list.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"post-list.json: {len(out)} approved script(s) for {batch}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
