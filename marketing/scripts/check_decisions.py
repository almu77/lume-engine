#!/usr/bin/env python3
"""Validate the newest decisions file before Claude processes it.

Ported unchanged in logic from the Tough Hair v2 engine. Why it exists: the console writes
on Alp's machine and Claude reads through a synced mount. On 2026-07-02 (Tough Hair) that
mount served a stale, partial copy of a fixed-name `decisions.json` and two rows were
silently lost. The console writes a unique `decisions-<save_id>.json` per save with a
trailing `complete:true` sentinel, and this script checks it.

  exit 0 -> safe, prints the path to process
  exit 2 -> incomplete/stale, wait ~5s and re-run (a few times) before falling back
            to the console's Copy-summary paste

Usage:  python3 scripts/check_decisions.py [batch_date]
"""
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def candidates():
    files = glob.glob(os.path.join(ROOT, "decisions-*.json"))

    def key(f):
        base = os.path.basename(f)
        try:
            return int(base.split("-")[1].split(".")[0])
        except (IndexError, ValueError):
            return int(os.path.getmtime(f) * 1000)
    return sorted(files, key=key, reverse=True)


def main():
    want_batch = sys.argv[1] if len(sys.argv) > 1 else None
    files = candidates()
    if not files:
        print("FAIL: no decisions-*.json in the lume/marketing folder. "
              "Has Alp pressed Save decisions and seen the green banner?")
        return 2

    path = files[0]
    try:
        with open(path, encoding="utf-8") as fh:
            obj = json.load(fh)
    except json.JSONDecodeError as e:
        print(f"FAIL: {os.path.basename(path)} is not valid JSON ({e}). "
              "Almost certainly a partial write - wait and re-run.")
        return 2

    if obj.get("app") not in (None, "lume"):
        print(f"FAIL: {os.path.basename(path)} was written by the {obj.get('app')!r} console, "
              "not Lume. Wrong folder connected in the console?")
        return 2

    if obj.get("complete") is not True:
        print(f"FAIL: {os.path.basename(path)} has no `complete: true` sentinel - "
              "the write was truncated. Wait ~5s and re-run.")
        return 2

    decs = obj.get("decisions", [])
    declared = obj.get("decision_count")
    if declared is not None and declared != len(decs):
        print(f"FAIL: decision_count says {declared} but found {len(decs)} decisions. "
              "Truncated - wait ~5s and re-run.")
        return 2

    if want_batch and obj.get("batch_date") != want_batch:
        print(f"FAIL: newest file is for batch {obj.get('batch_date')}, you asked for "
              f"{want_batch}. Alp may not have saved the current batch yet.")
        return 2

    # Round check: the save must belong to the CURRENT review.json, otherwise it is a replay
    # of an earlier drafting round and the judgements refer to text that no longer exists.
    rv = os.path.join(ROOT, "review.json")
    if os.path.exists(rv):
        with open(rv, encoding="utf-8") as fh:
            review = json.load(fh)
        live = {r["row_id"] for r in review.get("rows", [])}
        stale = [d["row_id"] for d in decs if d["row_id"] not in live]
        saved_round = obj.get("round")
        if saved_round and saved_round != review.get("generated_at"):
            print(f"FAIL: this save is from round {saved_round} but review.json is "
                  f"round {review.get('generated_at')}. The decisions refer to text that "
                  "has since been redrafted. Ask Alp to reload the console and re-judge.")
            return 2
        if stale:
            print(f"FAIL: {len(stale)} decision(s) reference rows not in the current "
                  f"review.json: {', '.join(stale)}. Stale round - reload and re-judge.")
            return 2

    missing = [d.get("video_tag") or d.get("row_id") for d in decs
               if (d.get("action") == "edit" and not (d.get("edit_reason") or "").strip())
               or (d.get("action") in ("rewrite", "kill") and not (d.get("reason") or "").strip())]

    print(f"OK: {path}")
    print(f"    batch {obj.get('batch_date')} - {len(decs)} decisions - saved {obj.get('saved_at')}")
    counts = {}
    for d in decs:
        counts[d.get("action", "?")] = counts.get(d.get("action", "?"), 0) + 1
    print("    " + " - ".join(f"{k}: {v}" for k, v in sorted(counts.items())))
    undecided = review.get("rows") and len(review["rows"]) - len(decs) if os.path.exists(rv) else 0
    if undecided:
        print(f"    NOTE: {undecided} row(s) in review.json have no decision yet - they stay as drafts.")
    if missing:
        print(f"    NOTE: {len(missing)} row(s) have no reason: {', '.join(map(str, missing))}")
        print("    Ask Alp for the reason before logging - a blank reason is lost learning.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
