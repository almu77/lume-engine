#!/usr/bin/env python3
"""Regenerate review.json (what the console reads) from script-log.csv.

Run after drafting a batch, and again after processing a rewrite round. Only rows whose
status is `draft` or `rewrite` are shown - approved, killed and synced rows drop out.

Guards (all ported from Tough Hair, plus the Lume mission checks):
  STOP  account not `active` in accounts.csv          (no drafting for unconfirmed handles)
  STOP  account running a format not in allowed_angles
  NOTE  same format twice on one account (allowed: Alarm Ring on everything, Alp 2026-10-14)
  STOP  a mission that isn't `live` in missions.csv   (never script a mission the app lacks)
  STOP  a niche-reserved account (accounts.csv `niche`) given another niche or a mission
        outside its `niche_missions`
  NOTE  same mission twice on one account in one batch
  NOTE  same format as that account's previous batch
  NOTE  caption (hook) over 15 words                  (style-memory §27, Alp 2026-10-16)
  INFO  mission x format coverage for the batch       (feeds the mission validation test)

Usage:  python3 scripts/make_review_json.py <batch_date>
"""
import csv
import json
import os
import sys
from collections import Counter
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schema import COPY_FIELDS  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, "script-log.csv")
OUT = os.path.join(ROOT, "review.json")


def read_csv(name):
    p = os.path.join(ROOT, name)
    if not os.path.exists(p):
        return []
    with open(p, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def main():
    if len(sys.argv) < 2:
        print("usage: make_review_json.py <batch_date>   e.g. 2026-10-15")
        return 1
    batch = sys.argv[1]

    all_rows = read_csv("script-log.csv")
    rows = [r for r in all_rows
            if r.get("batch_date") == batch and (r.get("status") or "draft") in ("draft", "rewrite")]
    if not rows:
        print(f"FAIL: no draft/rewrite rows for batch {batch}. "
              f"Batches present: {sorted({r.get('batch_date', '') for r in all_rows})}")
        return 1

    accounts = {a["account"].strip(): a for a in read_csv("accounts.csv")}
    missions = {m["mission"].strip().lower(): m for m in read_csv("missions.csv")}
    stops = []

    for r in rows:
        acct = r.get("account", "").strip()
        a = accounts.get(acct)
        if a is None:
            stops.append(f"{r['row_id']}: account {acct!r} is not in accounts.csv (typo?)")
            continue
        if (a.get("status") or "").strip() != "active":
            stops.append(f"{r['row_id']}: account {acct} has status {a.get('status')!r} - only "
                         "`active` accounts get scripts. Confirm the handle with Alp first.")
        spec = (a.get("allowed_angles") or "").strip()
        ang = str(r.get("angle_no", "")).strip()
        if spec and ang and ang not in {x.strip() for x in spec.split(",")}:
            stops.append(f"{r['row_id']}: {acct} cannot run format {ang} (allowed: {spec})")

        # Niche reservation (Alp, 2026-10-14): an account reserved for a niche only posts that
        # niche, with that niche's missions, so a hit builds one consistent audience.
        niche = (a.get("niche") or "").strip().lower()
        if niche:
            row_niche = (r.get("target_niche") or "").strip().lower()
            if row_niche != niche:
                stops.append(f"{r['row_id']}: {acct} is reserved for the '{niche}' niche, "
                             f"row targets {r.get('target_niche')!r}")
            allowed_m = {m.strip().lower() for m in (a.get("niche_missions") or "").split(",") if m.strip()}
            m_row = (r.get("mission") or "").strip().lower()
            if allowed_m and m_row not in allowed_m | {"none"}:
                stops.append(f"{r['row_id']}: {acct}'s niche missions are {a.get('niche_missions')}, "
                             f"row uses {r.get('mission')!r}")

        mis = (r.get("mission") or "").strip().lower()
        if mis and mis != "none":
            m = missions.get(mis)
            if m is None:
                stops.append(f"{r['row_id']}: mission {r.get('mission')!r} is not in missions.csv")
            elif (m.get("status") or "").strip() != "live":
                stops.append(f"{r['row_id']}: mission {m['mission']} is {m.get('status')!r}, not live "
                             "in the app - don't script features that don't exist.")

    by_acct = {}
    for r in rows:
        by_acct.setdefault(r.get("account", "").strip(), []).append(r)
    notes = []  # noqa
    for acct, rs in by_acct.items():
        fmt_seen, mis_seen = {}, {}
        for r in rs:
            f = str(r.get("angle_no", "")).strip()
            if f in fmt_seen and f != "1":
                notes.append(f"{acct}: format {f} on both {fmt_seen[f]} and {r['row_id']} "
                             "(allowed while every video is Alarm Ring - Alp, 2026-10-14)")
            fmt_seen[f] = r["row_id"]
            m = (r.get("mission") or "").strip().lower()
            niche_acct = bool((accounts.get(acct) or {}).get("niche"))
            if m and m != "none" and not niche_acct:  # niche accounts repeat missions by design
                if m in mis_seen:
                    notes.append(f"{acct}: mission {m} on both {mis_seen[m]} and {r['row_id']} "
                                 "(allowed, but the two videos will look alike back-to-back)")
                mis_seen[m] = r["row_id"]

    if stops:
        print("STOP - fix these in script-log.csv (or accounts.csv / missions.csv) and re-run:")
        for s in stops:
            print("  " + s)
        return 2

    prev = {}
    for r in sorted(all_rows, key=lambda x: x.get("batch_date", "")):
        if r.get("batch_date") == batch or r.get("status") == "killed":
            continue
        prev.setdefault(r.get("account", "").strip(), {})[str(r.get("angle_no", "")).strip()] = r.get("batch_date")
    for r in rows:
        acct, ang = r.get("account", "").strip(), str(r.get("angle_no", "")).strip()
        if ang in prev.get(acct, {}):
            notes.append(f"{r['row_id']}: {acct} ran format {ang} on {prev[acct][ang]} too")
    for r in rows:  # style-memory §27: proven captions run 10-15 words
        hook = r.get("proposed_hook") or r.get("hook") or ""
        n_words = len([w for w in hook.split() if any(c.isalnum() for c in w)])
        if n_words > 15:
            notes.append(f"{r['row_id']}: caption is {n_words} words (target 10-15, style-memory §27)")
    if notes:
        print("NOTE (allowed, just be deliberate):")
        for n in notes:
            print("  " + n)
        print()

    cov = Counter((r.get("mission") or "none").strip().lower() for r in rows)
    print("Mission coverage this batch: " + ", ".join(f"{k} x{v}" for k, v in cov.most_common()))
    live = [m["mission"].lower() for m in missions.values()
            if (m.get("status") or "") == "live" and m["mission"].lower() != "none"]
    untested = [m for m in live if m not in {(r.get("mission") or "").strip().lower()
                                             for r in all_rows if r.get("status") in ("approved", "synced")}
                and m not in cov]
    if untested:
        print("Live missions with NO approved video yet (validation gap): " + ", ".join(untested))
    print()

    out = {"app": "lume", "batch_date": batch,
           "generated_at": datetime.now().isoformat(timespec="seconds"), "rows": []}
    for r in rows:
        row = {
            "row_id": r["row_id"], "account": r.get("account", ""), "video_tag": r.get("video_tag", ""),
            "angle_no": r.get("angle_no", ""), "angle_name": r.get("angle", ""),
            "format": r.get("format", ""), "mission": r.get("mission", ""),
            "target_niche": r.get("target_niche", ""), "timing_target": r.get("timing_target", ""),
            "rationale": r.get("rationale", ""), "status": r.get("status") or "draft",
        }
        for f in COPY_FIELDS:
            # a rewrite round carries the previous final forward as the new proposal
            row[f"proposed_{f}"] = r.get(f"final_{f}") or r.get(f"proposed_{f}", "")
        out["rows"].append(row)

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    print(f"wrote {OUT} - batch {batch}, {len(out['rows'])} rows")
    print("Now give Alp the console: lume/marketing/script-console.html")
    return 0


if __name__ == "__main__":
    sys.exit(main())
