#!/usr/bin/env python3
"""Standalone tag helper. Given the live max per account (from lume-tag-index.csv), prints the
next N sequential tags.

Tags = <account handle><number>, following the `account` column in accounts.csv ONLY. Lume
runs in its OWN sheet ("Lume - Video Data"), so every account starts at 1 there even if the
same handle had a Tough Hair sequence - do NOT continue Tough Hair numbering.
An account with no rows starts at 1, and that is reported loudly so a typo'd handle surfaces.

Usage:
  python3 scripts/next_tags.py --live realtimejake=0,realjakemu=4 --count 2
"""
import argparse
import csv
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ACCOUNTS = os.path.join(ROOT, "accounts.csv")


def accounts():
    if not os.path.exists(ACCOUNTS):
        return {}
    with open(ACCOUNTS, newline="", encoding="utf-8") as fh:
        return {r["account"].strip(): r for r in csv.DictReader(fh)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", required=True, help="account=current_max,... e.g. realtimejake=0")
    ap.add_argument("--count", type=int, default=2)
    ap.add_argument("--per-account", default="", help="overrides, e.g. realtimejake=3")
    args = ap.parse_args()

    overrides = {}
    for part in filter(None, args.per_account.split(",")):
        a, _, v = part.partition("=")
        overrides[a.strip()] = int(v)

    known = accounts()
    out, warnings = [], []
    for part in filter(None, args.live.split(",")):
        acct, _, val = part.partition("=")
        acct, mx = acct.strip(), int(val or 0)
        if known and acct not in known:
            warnings.append(f"{acct!r} is NOT in accounts.csv - typo? Refusing to guess.")
            continue
        if known and (known[acct].get("status") or "").strip() != "active":
            warnings.append(f"{acct} is {known[acct].get('status')!r}, not active - no tags issued.")
            continue
        if mx == 0:
            warnings.append(f"{acct} has no Lume tags yet - starting at {acct}1. "
                            "Confirm the handle is spelled right.")
        n = overrides.get(acct, args.count)
        out.append((acct, [f"{acct}{mx + i}" for i in range(1, n + 1)]))

    for w in warnings:
        print("WARNING: " + w)
    if warnings:
        print()
    for acct, tags in out:
        print(f"{acct}: {', '.join(tags)}")
    print(f"\n{sum(len(t) for _, t in out)} tags across {len(out)} accounts.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
