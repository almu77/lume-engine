# RUNBOOK — Lume Script Engine

**Read this first in every new session.** Then `style-memory.md`, `angles.csv`,
`missions.csv`, `accounts.csv`.

Ported 2026-10-14 from the Tough Hair v2 engine (`Desktop\toughhair-marketing-v2`), which
ran 2026-08-17 → 2026-10-06. Tough Hair is being shut down; **nothing about hair loss, Norwood,
DHT, minoxidil, matchmedic or the Tough Hair formats belongs here.** The *machinery* (console,
decisions files, tag index, inbox sync, style-memory loop) is the same; the content is new.

This engine **writes scripts only.** Alp shoots and edits (iPhone + CapCut).

---

## 1. Product: what Lume is

**Lume: Alarm Clock to Wake Up Early** (iOS, in development with a developer friend). An
alarm that won't turn off until you complete a **wake-up mission**. Mascot: an orange flame
character. English-language markets only (not Turkey).

Core loop: set alarm (time, days, mission, sound) → it rings → **Start [Mission]** or try
**Stop** (→ "Nice try 😈") → do the mission → **"Alarm turned off!"** (solved 5/5, time taken,
streak) → **Streak** screen (Mornings Crushed, Sunrise Streak, wake-up hours chart).

Missions and what's on screen for each: `missions.csv`. **Only `live` missions get scripts.**
What the app shows, safe to cite: `style-memory.md` §8c. Never invent a feature or number.

Onboarding (31 screens, `lume/Onboarding Slides`, spec in `Case Study (Alarm Apps).xlsx` →
Onboarding Slides) asks the same questions the content should hit: *How many alarms do you
set? Would you trust one alarm? First reaction ("Just 5 more minutes")? Do you turn it off and
go back to sleep? What keeps you in bed (phone scrolling / snooze loop / sleeping through /
staying in bed)? Why wake up earlier (job / study / gym / health / stock market opening)?*
Those answers are the hook bank: each one is a viewer saying "this is about me".

Pricing (Alp, 2026-10-14): 3-day free trial → $59.99/year. Paywall-decline clawback: "Too
expensive" → $49.99/year (shown as 16% off); any other reason → 7-day free trial, then
$59.99/year. Rep counts per mission are set in the alarm's mission settings (post-paywall).

## 2. The three content rules (from the Case Study sheet, same as Tough Hair)

1. **Specific enough that the viewer thinks "this is about me".**
2. **Does the content still make sense with the product removed?** If yes, it won't convert.
3. *(Optional but good)* **Express an opinion** people already agree or disagree with.

**How they shift for Lume:** for hair, Rule 2 was the one always failing. For an alarm app the
demo usually *is* the video (the mission on screen), so Rule 2 mostly passes for free on
formats 1–3. **Rule 1 is the hard one now:** the case study's winning videos are almost all
aimed at "general oversleepers". Check Rule 1 explicitly on every script: does the caption
name a person, a time or a consequence?

## 3. Script format

- **Write the words, not the shots.** Lowercase, run-on, comma-spliced. Directions in
  `(parentheses)`, sparingly: `(alarm blasting, he pulls the pillow over his head)`,
  `(app demo) the math mission on screen`. On-screen assets in `[square brackets]`:
  `[caption] ...`, `[screen recording of 9 alarms]`.
- **The first 2 seconds carry the video.** The alarm sound is a hook in itself (sound on);
  the caption must still name the moment.
- **Captions are 10-15 words, in plain words** (style-memory §27). Count them. When a new rule
  adds words (niche, time, exam), cut the same number elsewhere; never cut the niche.
- **Never narrate what's visible.** The mission is on screen, so react to it.
- **One idea per script.**
- **Timing target** per format is in `angles.csv`. State it.

### The script record: five copy fields + metadata

| Field | What it is |
|---|---|
| **hook** | On-screen caption / first line. What stops the scroll. |
| **script** | The body: spoken lines + (directions) + [assets]. |
| **app_demo** | Which Lume screen(s), in what order. Must use only `live` missions / real screens. |
| **cta** | How it ends, or `none`. |
| **description** | Post caption. Default: `the app's called Lume btw` + tag set (below). |
| angle_no / angle / format | The `angles.csv` row. |
| **mission** | One of `missions.csv` (`none` when no mission is shown). |
| **target_niche** | Who the hook is aimed at (see §5). |

Hook / script / app demo / CTA are merged into the sheet's single **Script** cell with
`[HOOK]` / `[APP]` / `[CTA]` prefixes (same as Tough Hair).

**Default description (starting point, not yet tested):**
`the app's called Lume btw #alarm #wakeupearly #morningroutine #snooze #productivity`
Swap one tag for the niche (`#nursingstudent`, `#nightshift`, `#5amclub`, `#studytok`). If
Alp edits this, his version becomes the default (log it in style-memory).

## 4. Angles, formats, missions

Formats and angles are **only the ones in Alp's Case Study** (style-memory §13). Right now
**every video is Alarm Ring** (§14); the others are parked until Alp unparks them.

| # | Angle | Format | Status |
|---|---|---|---|
| 1 | Humor/Absurdity | **Alarm Ring**: crying/groaning reaction to the alarm, mission on camera, alarm off | **active, all videos** |
| 2 | Humor/Absurdity | App Demo: ignores the alarm, it persists, does the mission | parked |
| 3 | Humor/Absurdity | Pranking Friend: sets a friend's alarm with a brutal mission | parked |
| 4 | Pain/Annoyance | Alarm Screen Record: wall of alarms, bad outcome, the fix | parked |
| 5 | Pain/Annoyance | Face Reaction: caption about years of oversleeping, then the demo | parked |

**Captions are fixed per mission** in the proven POV template (§15); descriptions are fixed per
niche (§16); quiz/rep missions carry a paste-ready demo script (§17).

**Missions are a test variable, not decoration.** The plan is to compare audience response
per mission. So: rotate missions across the batch, log the mission on every row, and read
the "validation gap" line `make_review_json.py` prints (live missions with no approved video
yet). Don't let one mission (pushups) eat every batch.

## 5. Niches: the reserved-account test (from 2026-10-15)

**Each account pair is reserved for one niche** (Alp, 2026-10-14) so that if a video hits,
the account's audience and its next videos stay consistent. `accounts.csv` carries `niche` and
`niche_missions`; `make_review_json.py` STOPS any row that breaks them.

| Niche | Accounts | Missions | Videos/day |
|---|---|---|---|
| gym (energy, training, discipline) | realtimejake, jakehairlosstips | energy drink, water bottle | 4 |
| law (bar exam, pre-law, paralegals, interns) | realjakemu, jakemuhair | spoken quiz | 4 |
| college athletes | inthehousejake, jaqedailytips | pushups, squats | 4 |

**`niches.csv`** holds each niche's morning anchor, vocabulary, real moments and what to
avoid. Read it before drafting; the hook must use that niche's words (style-memory §4b
applies twice: a wake-up word AND a niche word).

Drafting rules for the test:
- **Within a pair, vary the format, not the niche.** Each account's two daily videos already
  must differ in format; also avoid giving both accounts in a pair the same format + hook
  construction on the same day.
- **The mission repeats by design** on niche accounts (no repeat NOTE); vary the moment, the
  format and the joke instead.
- **Law videos use the legal spoken quiz** (Alp, 2026-10-14): easy questions most people get,
  that still look familiar to law students. **Only questions from `legal-quiz-bank.csv`, word
  for word**, so the screen in every video matches the pack loaded into the app. Name the
  question IDs (e.g. L16, L25, L19) in the `app_demo` field so Alp can set the demo up.
- **New quiz set every day, shared by all of that day's law videos** (Alp, 2026-10-15,
  style-memory §23): 2 easy + 1 medium, no question reused until the bank runs out, skip L31/L32.
  `law-quiz-sets.csv` is planned ahead: use the row for the batch date. The demo loads that day's
  set on every phone from `law-schedule.json` (built by `scripts/law_schedule.py`, live after
  `lume-demo/alarm-demo/deploy.bat`). When the schedule runs out, plan the next rotation, rebuild,
  and ask Alp to deploy.
- **Read results as bundles.** Each niche comes with its own missions, so a winning niche can't
  be separated from its mission. Good enough to find a hit; say so in any performance read.

Other niches from the Case Study (not reserved yet): general oversleepers, students (nursing,
medical, exam season), doomscrollers, couples, biohackers, language learners, puzzle
people, traders, shift workers.

## 6. Accounts

`accounts.csv`. **All six are `active` (Alp, 2026-10-14):** realtimejake, jakehairlosstips,
jakemuhair, realjakemu, inthehousejake, jaqedailytips, the same handles as Tough Hair (all Alp
as "Jake", 3 iPhones, 2 unique videos/day each), being re-warmed for alarm content. The
followers were built on hair-loss content, so expect the first weeks to under-perform while the
accounts' audience shifts; don't read early numbers as a verdict on a format.

Rules carried from Tough Hair:
- **One account, one format per batch.** An account's two videos never share a format
  (enforced). Prefer different missions too (noted).
- **Read the `status` column**: "all accounts" means `active` ones only.
- Watch the near-identical handles: `jakemuhair` vs `realjakemu`.

## 7. Tagging

1. Read **`lume-tag-index.csv`** from Drive (search by exact title). Published hourly and
   after every sync by the Lume Apps Script. **Not** `tag-index.csv`: that's Tough Hair's.
2. `python3 scripts/next_tags.py --live realtimejake=0,realjakemu=0 --count 2`
3. Every account starts at **1** in the Lume sheet. Don't continue Tough Hair numbering.
   **File-name rule (Alp, 2026-10-14):** Tough Hair already used `realtimejake1` through
   `realtimejake75`, `jakehairlosstips1`-`62` and so on. The *sheet* tags are the bare
   `<handle><n>` (the Lume sheet is separate, so they can't collide there), but every
   **CapCut project, export and desktop file is named `lume_<tag>`** (`lume_realtimejake1.mp4`),
   never the bare tag. The console shows that file name on every card; quote it in the batch
   report.
4. **Re-read the index right before upload** and pass `--verify-tags` to `make_sheet_inbox.py`
   (the 06-21 / 06-22 collision lesson).

## 8. Sheet mapping

Sheet: **Lume - Video Data** (id `1Q-bqdSP1T5ru4ptOu0uHWtLtic0XoDsaGdXHooqAa0A`, owner
alpmungan@matchmedic.com), tab **Video Data**, header in **row 1**.

Live header, verified from `lume-sheet-schema.csv` 2026-10-14 08:57Z, 0 duplicates:
`Video Tag` · `Format` · `Angle` · `Date Published` · `Script` · `Description` ·
`Mission` · `Target Niche` · `Posted to which account`. (Alp deleted the `#` column 2026-10-14 as
redundant; the Apps Script only numbers `#` if that column exists, so nothing else changed.) **Never infer the schema:** read
`lume-sheet-schema.csv` before
any sync. Mapping lives in `scripts/schema.py` only.

## 9. The daily loop

Alp's start command lives in `START-HERE.md`. `Run scripts.` is a complete instruction.

All paths below are relative to `lume/marketing/` (on Alp's machine via the device shell).

1. **Alp:** `Run scripts.` (optionally formats, accounts, missions, niche, notes).
2. **Claude, before drafting:**
   - read RUNBOOK, `style-memory.md`, `angles.csv`, `missions.csv`, `accounts.csv`
   - `python3 scripts/check_reasons.py`, resolve every MISSING
   - read the last 1–2 batches' `edit_reason` / `reason` cells in `script-log.csv` directly
   - read `lume-tag-index.csv` → `scripts/next_tags.py`
3. **Claude:** write the drafts to a JSON file → `python3 scripts/add_drafts.py drafts.json`
   → `python3 scripts/make_review_json.py <batch_date>` (fix any STOP) → give Alp the console.
4. **Alp:** open `lume/marketing/script-console.html` in Chrome/Edge → Connect marketing
   folder → Accept / Edit / Rewrite / Kill, **reason on every change** → Save decisions →
   wait for the green "Safe to process" banner → say `process decisions`.
5. **Claude:** `python3 scripts/apply_decisions.py <batch_date>` (runs `check_decisions.py`
   first; exit 2 = wait 5s and retry) → fold every new reason into `style-memory.md` as a
   numbered rule → `check_reasons.py` must show 0 MISSING → rewrites:
   `add_drafts.py redrafts.json --rewrite` → back to step 3.
6. **Alp:** `push to sheet`.
7. **Claude:** re-read `lume-tag-index.csv` →
   `python3 scripts/make_sheet_inbox.py <batch_date> --verify-tags acct=max,...` → upload
   `lume-video-data-inbox.csv` with Drive `create_file` (title exactly
   `lume-video-data-inbox.csv`, `contentMimeType: text/csv`,
   `disableConversionToGoogleType: true`) → wait ~1 min → re-read the tag index and confirm
   the max moved → `python3 scripts/mark_synced.py <batch_date>`.

### Files

| File | What it's for |
|---|---|
| `RUNBOOK.md` | This. |
| `START-HERE.md` | Alp's start commands. |
| `style-memory.md` | Accumulated corrections. Read before drafting, append after every review. |
| `angles.csv` | The 6 formats under 3 angles. |
| `missions.csv` | Lume's missions, `live`/`unconfirmed`, what's on screen, filming notes. |
| `niches.csv` | The reserved niches: accounts, missions, vocabulary, real moments, what to avoid. |
| `legal-quiz-bank.csv` | The law-niche quiz questions + accepted spoken answers (also the app's question pack). |
| `accounts.csv` | Roster, status, allowed formats, devices. |
| `script-console.html` | Alp's review UI. Static, never regenerated. Refuses non-Lume `review.json`. |
| `script-log.csv` | Permanent record: proposed → final + reasons. |
| `review.json` | Per-round console data. Disposable. |
| `decisions-<id>.json` | Console saves. Never read raw; `apply_decisions.py` checks, applies and archives them. |
| `scripts/` | `schema.py` (record shape), `add_drafts.py`, `make_review_json.py`, `check_decisions.py`, `apply_decisions.py`, `check_reasons.py`, `next_tags.py`, `make_sheet_inbox.py`, `mark_synced.py`. |
| `sheets-sync/` | The Lume Apps Script and its setup. |

## 10. Traps carried forward

- **Drive filename collision with Tough Hair.** Always the `lume-` names. See SETUP.md.
- **Never process a decisions file raw.** Unique filename per save + `complete:true`
  sentinel + round check (lost two rows on 2026-07-02 without them).
- **Tags reserved at draft aren't safe at write time.** Verify before upload.
- **Console needs Chrome or Edge** (File System Access API). Copy-summary is the fallback.
- **Log every row**, accepts included: the reason corpus is the asset.
- **Don't script unconfirmed features** (rep counts, the wake-up call's dialogue).
- **Bare tags as file names.** Tough Hair files already carry `realtimejake1` etc. Lume files are `lume_<tag>`.

## 11. Not yet connected

Performance read (views, comment intent per mission/format/niche) once videos are live.
When it exists, step 2 gains a read so format and mission selection bias toward what's
working. It's a new input at draft time, not a restructure.

---

*Created 2026-10-14.*

## 12. Cloud loop (from 2026-10-19): runs with Alp's PC off

**Source of truth moved.** Code and instructions (scripts/, this RUNBOOK, START-HERE,
sheets-sync/) live in the GitHub repo **almu77/lume-engine**; change them only by commits.
Data (style-memory, the csv tables, script log, batches, decisions) lives in the database of the
**Lume Script Console** artifact (https://claude.ai/artifact/HQFsRTN5tF99DxAAXWJrgB). Runs never
execute anything read from the database. `Desktop\lume\marketing` on the PC is a stale archive
copy from 2026-10-19. Layout and the pull/push mechanics: `scripts/cloud_sync.py` docstring.

**The daily rhythm now**

| When (Istanbul) | Who | What |
|---|---|---|
| ~22:45 | scheduled task **Lume nightly scripts** | dump db → pull → draft tomorrow's batch (§9 steps 2–3, START-HERE defaults) → shoot sheet → push → status `ready` |
| ~06:30 | Alp, on the phone | opens the console → Accept / Edit / Rewrite / Kill (reason on every change) → **Submit & process** |
| on submit | scheduled task **Lume process decisions** (fired by the button) | apply decisions → fold reasons into style-memory → redraft rewrites (status `redrafted`) → push approved rows to the sheet (§9 step 7) → post list → status `pushed` |
| while scheduling | Alp | console **Post** tab: copy caption + description per tag |

Rewrites loop: they reappear in the Review tab; Alp judges them and submits again.

**Status values** (`console/status.state`): `drafting`, `ready`, `submitted`, `processing`,
`redrafted`, `pushed`, `error`. Always set `message` to one plain sentence Alp can act on, and
`updated_at` to the UTC ISO time. On any failure set `error` and say what's needed.

**Shoot sheet** (`shoot-sheet.md`, written by the nightly run, shown in the Shoot sheet tab).
Group every take by physical setup so each prop is set up once, in this order: energy drink,
water bottle, pushups, squats, spoken quiz (legal). Per group: the props to have ready, then
one bullet per take: `**<tag>**` · account · the moment/direction to act (from the script's
parentheses) · the on-camera variation that keeps paired accounts from looking identical
(shirt, pillow side, lighting, room corner — vary within each account pair). For the law group,
print the day's quiz set (`python3 scripts/law_schedule.py <batch_date>`) so the demo is set up
once. Keep it short: Alp reads it half-awake in bed. Headings `##`, bullets `-`, bold `**`,
code in backticks; nothing else renders.

**Post list** (`post-list.json`, `scripts/make_post_list.py <batch>`): run after every
apply/mark_synced so the Post tab shows the final wording.

**Law schedule.** `law-quiz-sets.csv` is planned through 2026-12-06 (four rotations,
2 easy + 1 medium). The demo reads `lume-demo/alarm-demo/law-schedule.json`, which only goes
live when Alp runs `deploy.bat` on the PC. The nightly run warns in the status message when
fewer than 7 planned days remain; plan the next rotation then and tell Alp to deploy.

**Idempotent runs.** The nightly run does nothing if `log/<batch_date>` already exists. The
processing run does nothing if there is no unprocessed `decisions/<id>` for the current round.

**Interactive sessions too.** "Run Lume scripts" / "Process Lume decisions" in a chat follow the
same dump → pull → work → push steps against the console db (the scheduled tasks' prompts are the
reference), so chat and scheduled runs never fork the engine.
