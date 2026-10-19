# Daily start: Lume (cloud loop, from 2026-10-19)

**Nothing to type in the morning.** Tomorrow's scripts are drafted around 22:45 Istanbul time
by the scheduled task "Lume nightly scripts". Open the **Lume Script Console**
(https://claude.ai/artifact/HQFsRTN5tF99DxAAXWJrgB), judge the cards, press
**Submit & process**. Approved scripts go to the sheet; rewrites come back to the console.

- **Shoot sheet** tab: every take grouped by prop, with the variation per account.
- **Post** tab: final caption + description per tag, with copy buttons, for scheduling.
- **Steering tomorrow's batch** (niche, missions, formats, notes): tell Claude in any chat
  before 22:45. It writes the steer to `console/config.next_batch_notes` (same fields as the
  full version below); the nightly run applies it once, then clears it.
- If the console says the processing run didn't start: paste `Process Lume decisions` into a chat.

The engine's files live in the console's database now (RUNBOOK §12). The PC folder is an
archive copy from 2026-10-19.

---

## Previous manual flow (still works in a chat, against the console db)


Copy one of these into a new chat with the `lume` folder attached. Everything else (product
facts, formats, missions, accounts, tag numbers, past corrections) I read from
`lume\marketing`. Don't re-explain it.

---

## The short version

```
Run Lume scripts.
```

I'll read the RUNBOOK, style-memory, angles, missions and accounts, pull live tag numbers from
`lume-tag-index.csv`, and draft 2 per **active** account: two different formats each, missions
rotated across the batch.

## The full version (when you want to steer)

```
Run Lume scripts. Batch 2026-10-15.

Formats: balanced
Missions: rotate
Niche:
Accounts: all
Skip:
Reference:
Notes:
```

| Field | What it does | Blank gives you |
|---|---|---|
| **Formats** | `balanced` · numbers `1,2,4` · `dawn` (1,2,3,6: needs a real wake-up) · `anytime` (4,5: shoot whenever) | balanced, weighted to 1 and 2 |
| **Missions** | `rotate` · specific `math, spoken quiz` · `untested` (only missions with no approved video yet) | rotate |
| **Niche** | one niche for the whole batch, e.g. `nursing students` | mixed |
| **Accounts** | `all` · `realtimejake x2, realjakemu x1` | all active, 2 each |
| **Skip** | accounts to leave out | none |
| **Reference** | a tag to write in the style of | none |
| **Notes** | "shooting alone", "no second phone", "lean meaner" | — |

---

## Mid-flow commands

| Say this | When |
|---|---|
| `process decisions` | after Save in the console and the green banner |
| `push to sheet` | when the approved rows should go to Lume - Video Data |
| `tags only. x2 per account` | just the next tags |
| `redraft <tag>` | one script needs another pass outside the console |
| `account <handle> is live` | flip a pending account to active (after a rename, give the new handle) |

## The rhythm

**you:** `Run Lume scripts.` → **me:** drafts + console → **you:** judge, reason on every
edit, Save → **you:** `process decisions` → **me:** apply, learn, redraft rewrites → repeat →
**you:** `push to sheet` → **me:** verify tags, upload, confirm the index moved.

> The console is `lume\marketing\script-console.html`. Open it in Chrome or Edge and connect
> the `marketing` folder (not the Tough Hair one: it'll refuse).

## File names (CapCut, exports, desktop)

Sheet tags restart at 1 (`realtimejake1`), but Tough Hair already used those exact names, so
**every CapCut project and exported file is `lume_<tag>`**: `lume_realtimejake1`,
`lume_jakehairlosstips1`. The console card shows the file name to copy. Moving the old Tough
Hair CapCut projects and exports into a "Tough Hair archive" folder avoids picking up an old
`realtimejake1` by mistake.
