#!/usr/bin/env python3
"""Build the demo's law-schedule.json from law-quiz-sets.csv + legal-quiz-bank.csv.

law-quiz-sets.csv is the single source for which 3 law questions each day uses (style-memory
§23). The demo (lume-demo/alarm-demo) fetches law-schedule.json on open and loads that day's
set into its law script on every phone. After changing the CSV: run this, then deploy the
demo (lume-demo/alarm-demo/deploy.bat).

Usage:  python3 scripts/law_schedule.py            # write the JSON
        python3 scripts/law_schedule.py 2026-10-16 # also print that day's set
"""
import csv, json, os, sys
from collections import Counter
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(os.path.dirname(ROOT), "lume-demo", "alarm-demo", "law-schedule.json")
BANNED = {"L31", "L32"}  # real case names - law niche "avoid" list


def main():
    bank = {r["id"]: r for r in csv.DictReader(open(os.path.join(ROOT, "legal-quiz-bank.csv"), encoding="utf-8"))}
    sets = list(csv.DictReader(open(os.path.join(ROOT, "law-quiz-sets.csv"), encoding="utf-8")))
    days, seen, fail = [], Counter(), False
    for row in sets:
        ids = [x.strip() for x in row["question_ids"].split("|") if x.strip()]
        lines = []
        for i in ids:
            q = bank.get(i)
            if q is None or i in BANNED:
                print(f"FAIL {row['batch_date']}: {i} not usable"); fail = True; continue
            seen[i] += 1
            first = q["answer"].strip()
            first = first[0].upper() + first[1:]
            alts = [a.strip() for a in q["accepted_answers"].split("|") if a.strip() and a.strip().lower() != first.lower()]
            lines += [f"Q: {q['question']}", "A: " + " | ".join([first] + alts)]
        diffs = sorted(bank[i]["difficulty"] for i in ids if i in bank)
        if len(ids) != 3 or diffs != ["easy", "easy", "medium"]:
            print(f"NOTE {row['batch_date']}: expected 2 easy + 1 medium, got {diffs}")
        days.append({"date": row["batch_date"], "ids": ids, "text": "\n".join(lines)})
    reused = [i for i, n in seen.items() if n > 1]
    if reused:
        print("NOTE reused before the bank ran out:", ", ".join(sorted(reused)))
    if fail:
        return 1
    json.dump({"updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "days": days},
              open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    left = sorted(i for i in bank if i not in seen and i not in BANNED)
    print(f"wrote {OUT} - {len(days)} days, {days[0]['date']} -> {days[-1]['date']}. Unused questions left: {left or 'none (start a new rotation)'}")
    if len(sys.argv) > 1:
        d = next((x for x in days if x["date"] == sys.argv[1]), None)
        print(d["text"] if d else f"no set for {sys.argv[1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
