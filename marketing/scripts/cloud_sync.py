#!/usr/bin/env python3
"""Move the Lume engine between the console's database and a working folder.

Code and instructions live in the GitHub repo almu77/lume-engine (this file's repo): every
.py script, RUNBOOK.md, START-HERE.md, sheets-sync/. Only DATA lives in the console database
(style-memory, csv tables, the script log, the console's batch/status/config, decisions).
`pull` copies the repo's marketing/ folder into the work folder first, then writes the data
documents on top; a database copy of a repo file is ignored (the repo wins). `push` never
writes repo files back to the database. Code changes go through git commits only.

The engine's source of truth is the Lume Script Console artifact database (from 2026-10-19),
so the nightly and processing runs work in the cloud with Alp's PC off. The existing scripts
(add_drafts, make_review_json, apply_decisions, ...) still work on plain files, so a run:

  1. dumps the database with ArtifactData `list` + `out_dir` into DUMP (one call per
     collection: engine, log, console, decisions)
  2. `python3 <repo>/marketing/scripts/cloud_sync.py pull DUMP WORK` -> rebuilds lume/marketing/ under WORK
  3. runs the normal scripts inside WORK/marketing
  4. `cloud_sync.py push WORK OUT`    -> writes one JSON body per CHANGED document under OUT
     and prints the write plan (op, collection, doc_id, file). The run sends those with one
     ArtifactData `batch`, pinning each existing document to the version the list showed.

Database layout
  engine/<path with / as ~>   {path, content}       every engine text file
  log/<batch_date>            {batch_date, rows}    script-log.csv, one document per batch
  console/current             review.json + shoot_sheet + approved (post-list.json)
  console/status              {state, message, batch_date, updated_at}
  console/config              {process_trigger_id, nightly_trigger_id}
  decisions/<save_id>         the console save (same shape as decisions-<id>.json) + processed

Usage
  python3 cloud_sync.py pull DUMP WORK
  python3 cloud_sync.py push WORK OUT
"""
import csv
import hashlib
import io
import json
import os
import shutil
import sys

REPO_MK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # <repo>/marketing


def repo_paths():
    """Engine paths (relative to lume/, e.g. marketing/scripts/x.py) that the repo owns."""
    out = set()
    for base, dirs, files in os.walk(REPO_MK):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for f in files:
            if not f.endswith(".pyc"):
                out.add("marketing/" + os.path.relpath(os.path.join(base, f), REPO_MK).replace(os.sep, "/"))
    return out

STATE = ".cloud-sync-state.json"
SKIP_DIRS = {"__pycache__", "decisions-archive", "drafts"}
SKIP_FILES = {"script-log.csv", "review.json", STATE}


def h(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def load_dir(d):
    out = {}
    if os.path.isdir(d):
        for f in sorted(os.listdir(d)):
            if f.endswith(".json"):
                # ArtifactData out_dir spells "~" in a document id as "@" in the file name
                out[f[:-5].replace("@", "~")] = json.load(open(os.path.join(d, f), encoding="utf-8"))
    return out


def log_columns(mk):
    sys.path.insert(0, os.path.join(mk, "scripts"))
    from schema import LOG_COLUMNS  # noqa: E402
    return LOG_COLUMNS


def pull(dump, work):
    state = {}
    engine = load_dir(os.path.join(dump, "engine"))
    if not engine:
        print("FAIL: no engine data documents in the dump - did the list of `engine` run with out_dir?")
        return 1
    root = os.path.join(work, "lume")
    shutil.copytree(REPO_MK, os.path.join(root, "marketing"), dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    owned = repo_paths()
    ignored = 0
    for doc_id, body in engine.items():
        rel = body["path"]
        if rel in owned:
            state[f"engine/{doc_id}"] = h(body)   # stale db copy of a repo file: never run it
            ignored += 1
            continue
        p = os.path.join(root, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8", newline="") as fh:
            fh.write(body["content"])
        state[f"engine/{doc_id}"] = h(body)
    mk = os.path.join(root, "marketing")
    cols = log_columns(mk)

    logs = load_dir(os.path.join(dump, "log"))
    rows = []
    for doc_id in sorted(logs):
        rows.extend(logs[doc_id].get("rows", []))
        state[f"log/{doc_id}"] = h(logs[doc_id])
    with open(os.path.join(mk, "script-log.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in cols})

    console = load_dir(os.path.join(dump, "console"))
    cur = console.get("current")
    if cur:
        review = {k: v for k, v in cur.items() if k not in ("shoot_sheet", "approved")}
        json.dump(cur.get("approved", []), open(os.path.join(mk, "post-list.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        json.dump(review, open(os.path.join(mk, "review.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        with open(os.path.join(mk, "shoot-sheet.md"), "w", encoding="utf-8") as fh:
            fh.write(cur.get("shoot_sheet", ""))
        state["console/current"] = h(cur)
    for k in ("status", "config"):
        if k in console:
            json.dump(console[k], open(os.path.join(mk, f"console-{k}.json"), "w", encoding="utf-8"),
                      ensure_ascii=False, indent=1)
            state[f"console/{k}"] = h(console[k])

    pending = 0
    decs = load_dir(os.path.join(dump, "decisions"))
    for doc_id, body in decs.items():
        state[f"decisions/{doc_id}"] = h(body)
        if body.get("processed"):
            continue
        json.dump(body, open(os.path.join(mk, f"decisions-{doc_id}.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        pending += 1
    json.dump(state, open(os.path.join(mk, STATE), "w"), indent=1)
    print(f"repo code+instructions from {REPO_MK}; {ignored} db copies of repo files ignored")
    print(f"pulled {len(engine) - ignored} data files, {len(rows)} log rows in {len(logs)} batches, "
          f"console={'yes' if cur else 'empty'}, {pending} unprocessed decision save(s) -> {mk}")
    return 0


def engine_docs(mk_root):
    """Every engine text file under lume/ (marketing + the demo's law schedule)."""
    docs = {}
    for base, dirs, files in os.walk(mk_root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
        for f in files:
            full = os.path.join(base, f)
            rel = os.path.relpath(full, mk_root).replace(os.sep, "/")
            if f in SKIP_FILES or f.startswith("decisions-") or f.startswith("console-") \
                    or f in ("shoot-sheet.md", "post-list.json") or f.endswith((".pyc", ".tmp")):
                continue
            if not (rel.startswith("marketing/") or rel == "lume-demo/alarm-demo/law-schedule.json"):
                continue
            try:
                content = open(full, encoding="utf-8").read()
            except UnicodeDecodeError:
                continue
            docs[rel.replace("/", "~")] = {"path": rel, "content": content}
    return docs


def push(work, out):
    root = os.path.join(work, "lume")
    mk = os.path.join(root, "marketing")
    sp = os.path.join(mk, STATE)
    state = json.load(open(sp)) if os.path.exists(sp) else {}
    os.makedirs(out, exist_ok=True)
    want = {}

    owned = repo_paths()
    for doc_id, body in engine_docs(root).items():
        if body["path"] in owned:
            continue   # code/instructions: committed to git, never stored in the db
        want[f"engine/{doc_id}"] = body

    with open(os.path.join(mk, "script-log.csv"), newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    by_batch = {}
    for r in rows:
        by_batch.setdefault(r.get("batch_date") or "undated", []).append(r)
    for b, rs in by_batch.items():
        want[f"log/{b}"] = {"batch_date": b, "rows": rs}

    rv = os.path.join(mk, "review.json")
    if os.path.exists(rv):
        cur = json.load(open(rv, encoding="utf-8"))
        ss = os.path.join(mk, "shoot-sheet.md")
        cur["shoot_sheet"] = open(ss, encoding="utf-8").read() if os.path.exists(ss) else ""
        pl = os.path.join(mk, "post-list.json")
        cur["approved"] = json.load(open(pl, encoding="utf-8")) if os.path.exists(pl) else []
        want["console/current"] = cur
    for k in ("status", "config"):
        p = os.path.join(mk, f"console-{k}.json")
        if os.path.exists(p):
            want[f"console/{k}"] = json.load(open(p, encoding="utf-8"))

    # decisions applied by apply_decisions.py are moved into decisions-archive/: mark them processed
    arch = os.path.join(mk, "decisions-archive")
    if os.path.isdir(arch):
        for f in os.listdir(arch):
            if f.startswith("decisions-") and f.endswith(".json"):
                doc_id = f[len("decisions-"):-5]
                if f"decisions/{doc_id}" in state:
                    body = json.load(open(os.path.join(arch, f), encoding="utf-8"))
                    body["processed"] = True
                    want[f"decisions/{doc_id}"] = body

    plan = []
    for key, body in sorted(want.items()):
        if state.get(key) == h(body):
            continue
        coll, doc_id = key.split("/", 1)
        size = len(json.dumps(body, ensure_ascii=False).encode())
        if size > 250_000:
            print(f"FAIL: {key} is {size} bytes, over the 256 KiB document cap")
            return 1
        fp = os.path.join(out, key.replace("/", "__") + ".json")
        json.dump(body, open(fp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        plan.append({"op": "set", "collection": coll, "doc_id": doc_id, "file_path": fp,
                     "exists": key in state})
    json.dump(plan, open(os.path.join(out, "plan.json"), "w"), indent=1)
    if not plan:
        print("nothing changed - no writes needed")
        return 0
    print(f"{len(plan)} document(s) to write (one ArtifactData batch; pin every 'existing' entry "
          "to the version its list call showed, omit if_version for 'new'):")
    for p in plan:
        print(f"  {'existing' if p['exists'] else 'new     '}  {p['collection']}/{p['doc_id']}  {p['file_path']}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 4 or sys.argv[1] not in ("pull", "push"):
        print(__doc__)
        sys.exit(1)
    sys.exit(pull(sys.argv[2], sys.argv[3]) if sys.argv[1] == "pull" else push(sys.argv[2], sys.argv[3]))
