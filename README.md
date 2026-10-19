# lume-engine

Code and instructions for the Lume short-form script engine (Alp, Match Medic).

- `marketing/RUNBOOK.md` — how the engine works; §12 is the cloud loop.
- `marketing/START-HERE.md` — Alp's daily flow.
- `marketing/scripts/` — the Python tools. `cloud_sync.py` moves DATA between the
  Lume Script Console database (https://claude.ai/artifact/HQFsRTN5tF99DxAAXWJrgB) and a work folder.

Data (style-memory, csv tables, the script log, batches, decisions) lives in the console
database, not here. Code lives only here: change it with commits, never by writing it to the db.
Two scheduled tasks use this repo: "Lume nightly scripts" (22:45 Istanbul) and
"Lume process decisions" (fired by the console's Submit button).
