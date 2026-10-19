"""Read/write helpers for script-log.csv. Writes go to a temp file then replace, so a crash
mid-write can never leave a half-written log on Alp's disk."""
import csv
import os

from schema import LOG_COLUMNS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, "script-log.csv")


def read_log():
    if not os.path.exists(LOG):
        return []
    with open(LOG, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def write_log(rows):
    tmp = LOG + ".tmp"
    with open(tmp, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=LOG_COLUMNS, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in LOG_COLUMNS})
    os.replace(tmp, LOG)
