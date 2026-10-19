# Lume Video Data sync: one-time setup (~10 min)

Approved scripts land in **Lume - Video Data** → tab **Video Data** automatically. Same
mechanism as Tough Hair: Claude drops a small CSV into your Drive, a script bound to the sheet
picks it up within a minute and inserts the rows under the header.

## ⚠️ Read this first: Tough Hair's script is still running

The Tough Hair sheet's Apps Script polls Drive every minute for `video-data-inbox.csv` and
republishes `tag-index.csv` / `sheet-schema.csv` hourly (both were refreshed this morning). Lume
uses **different names** on purpose (`lume-video-data-inbox.csv`, `lume-tag-index.csv`,
`lume-sheet-schema.csv`) so the two can never cross. Nothing to do here unless you want Tough
Hair fully off:

- **To switch Tough Hair off:** open the Tough Hair *Video Data* sheet → Extensions → Apps
  Script → Triggers (clock icon) → delete the four triggers. Its sheet and backups stay as they are.
- **Don't** paste the Lume script into the Tough Hair sheet's editor (or the reverse). The
  Lume script refuses to run in any spreadsheet whose name lacks "Lume".

## Steps

1. Open **Lume - Video Data** on the web.
2. **Extensions → Apps Script.** This is a new, empty project. Delete the placeholder code.
3. Paste the whole of **`LumeVideoDataInbox.gs`** from this folder. Save (disk icon).
4. Function dropdown → **`addMissingColumns`** → **Run** → approve the permission prompt.
   This appends three columns to the right of your header row: `Mission`, `Target Niche`,
   `Posted to which account`. They're what the mission-by-mission test reads back. (Skip this
   step if you don't want them; the sync just won't write those fields.)
5. Function dropdown → **`installTrigger`** → **Run**. This schedules the sync (every minute),
   the tag index and schema (hourly) and a daily backup (~3am, newest 30 kept in a Drive folder
   called **Lume Video Data Backups**), and publishes `lume-tag-index.csv` +
   `lume-sheet-schema.csv` straight away.
6. Tell Claude **"sheet's live"**. Claude reads `lume-sheet-schema.csv` to confirm the columns.

## What it writes

| Inbox field | Sheet column |
|---|---|
| video_tag | Video Tag |
| format | Format |
| angle | Angle |
| script | Script (`[HOOK]` / body / `[APP]` / `[CTA]` on separate lines) |
| description | Description |
| mission | Mission *(after step 4)* |
| target_niche | Target Niche *(after step 4)* |
| posted_to_account | Posted to which account *(after step 4)* |

**Date Published** is left blank. Fill it when you post.

## Behaviour (same as Tough Hair)

- **Never edits or deletes existing rows.** Inserts new rows directly under the header,
  newest first, matching columns by header name. Columns can be reordered freely; an
  unmatched field is skipped, never shifted.
- **Dedupe by Video Tag.** A tag that already exists is skipped and logged as
  `!! COLLISION` (Apps Script → Executions). Claude re-checks tags against
  `lume-tag-index.csv` before every upload so this shouldn't happen.
- **New rows have no fill and normal weight.** `insertRowsBefore` copies the formatting of the
  row above, which here is the header, so the script resets it.
- **If the inbox was converted to a Google Sheet on upload,** it's left untouched and logged.
  Claude uploads it as raw CSV.
- **To pause:** Apps Script → Triggers → delete the `syncInbox` trigger.

## The Accounts tab

The Accounts tab is not touched by the script. It currently holds the Tough Hair roster
**including plaintext logins**. Anyone the sheet is shared with can read them; consider moving
credentials to a password manager before you share it with a manager.
