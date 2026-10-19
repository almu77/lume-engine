#!/usr/bin/env python3
"""Feedback-loop guard: prove that Alp's edit/rewrite reasons actually reached style-memory.

Ported from the Tough Hair v2 engine. Corrections are captured twice - raw in script-log.csv
(edit_reason / reason, per row) and distilled into style-memory.md as numbered rules. Drafting
reads the DISTILLED rules, so a reason that never gets promoted silently stops influencing
future batches. This flags those.

  CAPTURED  - quoted (near-)verbatim in style-memory.md.
  LIKELY    - strong keyword overlap with style-memory; skim to be sure.
  MISSING   - little/no overlap: promote it into style-memory or consciously skip it.

  exit 0 -> nothing MISSING      exit 3 -> at least one MISSING (advisory)

Usage:
  python3 scripts/check_reasons.py                 # last 2 batches (default)
  python3 scripts/check_reasons.py --batches 3
  python3 scripts/check_reasons.py --since 2026-10-20
"""
import argparse
import csv
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, "script-log.csv")
STYLE = os.path.join(ROOT, "style-memory.md")

STOP = set("""a an the this that these those and or but so if then of to in on for with your you you're
i im i'm it its it's is are was were be been being as at by from more less not no yes we our my me he
his him she her they them make made made it too very much need needs used use using new same into
onto than then just like about really actually genuinely thing things bit bits way ways one two
""".split())
WORD = re.compile(r"[a-z0-9']+")


def norm(s):
    return " ".join(WORD.findall((s or "").lower()))


def keywords(s):
    return [w for w in norm(s).split() if len(w) > 3 and w not in STOP]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batches", type=int, default=2)
    ap.add_argument("--since", default=None)
    ap.add_argument("--threshold", type=float, default=0.5)
    args = ap.parse_args()

    for p in (LOG, STYLE):
        if not os.path.exists(p):
            print(f"FAIL: {p} not found.")
            return 1

    style_norm = norm(open(STYLE, encoding="utf-8").read())
    style_words = set(style_norm.split())
    with open(LOG, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    all_batches = sorted({r.get("batch_date", "") for r in rows if r.get("batch_date")})
    scan = [b for b in all_batches if b >= args.since] if args.since else all_batches[-args.batches:]
    if not scan:
        print("No batches logged yet - nothing to check.")
        return 0

    seen, items = set(), []
    for r in rows:
        if r.get("batch_date") not in scan:
            continue
        reason = (r.get("edit_reason") or r.get("reason") or "").strip()
        if not reason or norm(reason) in seen:
            continue
        seen.add(norm(reason))
        items.append((r.get("batch_date", ""), r.get("video_tag", ""), reason))

    captured, likely, missing = [], [], []
    for batch, tag, reason in items:
        rn = norm(reason)
        head = " ".join(rn.split()[:10])
        if rn and (rn in style_norm or (len(head.split()) >= 5 and head in style_norm)):
            captured.append((batch, tag, reason))
            continue
        kw = keywords(reason)
        ratio = (sum(1 for w in kw if w in style_words) / len(kw)) if kw else 0.0
        (likely if ratio >= args.threshold else missing).append((batch, tag, reason, ratio))

    print(f"Feedback-loop check - batches scanned: {', '.join(scan)}")
    print(f"  {len(items)} distinct reasons  |  CAPTURED {len(captured)}  LIKELY {len(likely)}  MISSING {len(missing)}\n")
    if missing:
        print("MISSING - not reflected in style-memory.md (promote or consciously skip):")
        for batch, tag, reason, _ in missing:
            print(f"  [{batch} {tag}] {reason}")
        print()
    if likely:
        print("LIKELY - overlaps an existing rule but not quoted; skim to confirm:")
        for batch, tag, reason, ratio in likely:
            print(f"  [{batch} {tag}] ({ratio:.0%}) {reason}")
        print()
    if not missing and not likely:
        print("All scanned reasons are quoted in style-memory.md. Loop is intact.")
    return 3 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
