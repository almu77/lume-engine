"""Shared column definitions for the Lume script engine.

One place to change the shape of a script record. Everything else imports from here.
Ported from the Tough Hair v2 engine (toughhair-marketing-v2/scripts/schema.py) on 2026-10-14.
Differences: every row also carries a `mission` (which Lume wake-up mission the video shows)
and a `target_niche` (which audience it is aimed at). Both are what the mission-by-mission
validation reads back, so they are first-class fields, not notes.
"""

# The five editable copy fields, in render/log order. Must match FIELDS in script-console.html.
COPY_FIELDS = ["hook", "script", "app_demo", "cta", "description"]

# script-log.csv - the permanent record. Append-only; never rewritten in place.
LOG_COLUMNS = (
    ["row_id", "batch_date", "account", "video_tag",
     "angle_no", "angle", "format", "mission", "target_niche",
     "timing_target", "rationale"]
    + [f"{p}_{f}" for f in COPY_FIELDS for p in ("proposed", "final")]
    + [f"{f}_edited" for f in COPY_FIELDS]
    + ["action", "edit_reason", "reason", "status", "synced_at", "notes"]
)

# lume-video-data-inbox.csv -> Apps Script -> "Lume - Video Data" sheet, tab "Video Data".
# Left side = inbox csv header, right side = sheet header it maps to.
# Live headers read from the sheet 2026-10-14: # | Video Tag | Format | Angle | Date Published |
# Script | Description. Mission / Target Niche / Posted to which account do NOT exist yet - the
# Apps Script skips any column it can't find (and logs it), so these are written the moment
# the columns are added (run addMissingColumns() once in the Apps Script editor).
INBOX_TO_SHEET = {
    "video_tag":         "Video Tag",
    "format":            "Format",
    "angle":             "Angle",
    "script":            "Script",          # hook + body + app demo + CTA, newline separated
    "description":       "Description",
    "mission":           "Mission",
    "target_niche":      "Target Niche",
    "posted_to_account": "Posted to which account",
}
INBOX_COLUMNS = list(INBOX_TO_SHEET.keys())

# Drive filenames. These MUST differ from the Tough Hair ones (video-data-inbox.csv,
# tag-index.csv, sheet-schema.csv): the Tough Hair Apps Script is still installed and polls
# Drive every minute for `video-data-inbox.csv` - a Lume inbox under that name would be
# inserted into the Tough Hair sheet.
INBOX_FILE = "lume-video-data-inbox.csv"
TAG_INDEX_FILE = "lume-tag-index.csv"
SCHEMA_FILE = "lume-sheet-schema.csv"

STATUSES = ["draft", "approved", "rewrite", "killed", "synced"]
