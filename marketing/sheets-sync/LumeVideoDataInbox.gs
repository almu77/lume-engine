/**
 * Lume Video Data inbox sync  (bound Apps Script for the "Lume - Video Data" Google Sheet)
 * -----------------------------------------------------------------------------------------
 * Ported 2026-10-14 from the Tough Hair v2 script (toughhair-marketing-v2/sheets-sync/
 * VideoDataInbox.gs). Same behaviour, with these differences:
 *
 *   - DIFFERENT DRIVE FILENAMES: lume-video-data-inbox.csv / lume-tag-index.csv /
 *     lume-sheet-schema.csv. The Tough Hair script is still installed on the Tough Hair sheet
 *     and polls Drive every minute for "video-data-inbox.csv" - sharing that name would send
 *     Lume rows into the Tough Hair sheet (and vice versa).
 *   - Refuses to run unless the spreadsheet's name contains "Lume", so pasting it into the
 *     wrong sheet fails loudly instead of writing.
 *   - Header row is row 1 (no Baseline block above it like Tough Hair had).
 *   - Fills the "#" column with a running number.
 *   - Writes Mission / Target Niche / Posted to which account IF those columns exist.
 *     addMissingColumns() adds them once, at the right edge of the header.
 *
 * Every minute syncInbox():
 *   1. finds lume-video-data-inbox.csv in Drive,
 *   2. locates the "Video Data" tab and its header row,
 *   3. inserts every row whose Video Tag isn't already present directly under the header
 *      (newest first; dedupe by tag), mapping fields to columns BY HEADER NAME,
 *   4. trashes the CSV so it isn't processed twice,
 *   5. refreshes lume-tag-index.csv and lume-sheet-schema.csv.
 *
 * One-time setup is in SETUP.md.
 */

const CONFIG = {
  INBOX_FILE_NAME:  'lume-video-data-inbox.csv',
  INDEX_FILE_NAME:  'lume-tag-index.csv',
  SCHEMA_FILE_NAME: 'lume-sheet-schema.csv',
  REQUIRE_NAME:     'Lume',          // spreadsheet name must contain this
  TActiveOverride:  'Video Data',    // the tab to write to; '' = auto-detect

  COL_TAG:     'Video Tag',
  COL_NUM:     '#',
  ANCHORS:     ['Script', 'Description', 'Format'],  // tab = COL_TAG + any one of these
  COL_FORMAT:  'Format',
  COL_ANGLE:   'Angle',
  COL_SCRIPT:  'Script',
  COL_DESC:    'Description',
  COL_MISSION: 'Mission',
  COL_NICHE:   'Target Niche',
  COL_ACCOUNT: 'Posted to which account',
};

const BACKUP = { FOLDER_NAME: 'Lume Video Data Backups', KEEP: 30 };

/** Map inbox-CSV column -> sheet header. Only columns found in the sheet are written. */
function fieldMap() {
  return {
    video_tag:         CONFIG.COL_TAG,
    format:            CONFIG.COL_FORMAT,
    angle:             CONFIG.COL_ANGLE,
    script:            CONFIG.COL_SCRIPT,
    description:       CONFIG.COL_DESC,
    mission:           CONFIG.COL_MISSION,
    target_niche:      CONFIG.COL_NICHE,
    posted_to_account: CONFIG.COL_ACCOUNT,
  };
}

function guard_(ss) {
  if (ss.getName().indexOf(CONFIG.REQUIRE_NAME) === -1) {
    throw new Error('This is the LUME sync script but this spreadsheet is "' + ss.getName() +
                    '". Paste it into "Lume - Video Data" only.');
  }
}

/** Find the tab + header row: needs Video Tag plus any one of CONFIG.ANCHORS. Header cells
 *  are trimmed before matching (a trailing newline in a header cell bit Tough Hair). */
function findTarget_(ss) {
  const sheets = ss.getSheets();
  for (let s = 0; s < sheets.length; s++) {
    const sheet = sheets[s];
    if (CONFIG.TActiveOverride && sheet.getName() !== CONFIG.TActiveOverride) continue;
    const data = sheet.getDataRange().getValues();
    for (let r = 0; r < Math.min(data.length, 20); r++) {
      const row = data[r].map(function (c) { return String(c).trim(); });
      const hasAnchor = CONFIG.ANCHORS.some(function (a) { return row.indexOf(a) !== -1; });
      if (row.indexOf(CONFIG.COL_TAG) !== -1 && hasAnchor) {
        const colMap = {};
        row.forEach(function (c, i) { if (c && colMap[c] === undefined) colMap[c] = i; });
        return { sheet: sheet, headerRow: r, colMap: colMap, data: data };
      }
    }
  }
  return null;
}

function findFile_(name) {
  const files = DriveApp.getFilesByName(name);
  let file = null, latest = 0;
  while (files.hasNext()) {
    const f = files.next();
    if (f.isTrashed()) continue;
    const t = f.getLastUpdated().getTime();
    if (t > latest) { latest = t; file = f; }
  }
  return file;
}

function syncInbox() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  guard_(ss);

  const file = findFile_(CONFIG.INBOX_FILE_NAME);
  if (!file) { Logger.log('No inbox file ("' + CONFIG.INBOX_FILE_NAME + '").'); return; }
  if (file.getMimeType() !== MimeType.CSV && file.getMimeType() !== MimeType.PLAIN_TEXT) {
    Logger.log('!! ' + CONFIG.INBOX_FILE_NAME + ' is a ' + file.getMimeType() + ', not a CSV ' +
               '(it was converted on upload). Re-upload with conversion disabled. Not processed.');
    return;
  }

  const csv = Utilities.parseCsv(file.getBlob().getDataAsString('UTF-8'));
  if (csv.length < 2) { Logger.log('Inbox empty; trashing.'); file.setTrashed(true); return; }

  const target = findTarget_(ss);
  if (!target) throw new Error('No tab with "' + CONFIG.COL_TAG + '" plus one of: ' + CONFIG.ANCHORS.join(', '));
  const sheet = target.sheet, colMap = target.colMap, data = target.data;

  const map = fieldMap();
  const missing = Object.keys(map).map(function (k) { return map[k]; })
    .filter(function (h) { return colMap[h] === undefined; });
  if (missing.length) {
    Logger.log('NOTE: no column for ' + missing.join(', ') + ' in "' + sheet.getName() +
               '" - those fields are not written. Run addMissingColumns() once to add them.');
  }

  const inHeader = csv[0].map(function (s) { return s.trim(); });
  const idxIn = function (name) { return inHeader.indexOf(name); };

  const tagCol = colMap[CONFIG.COL_TAG];
  const numCol = colMap[CONFIG.COL_NUM];
  const existing = {};
  let maxNum = 0;
  for (let r = target.headerRow + 1; r < data.length; r++) {
    const tag = String(data[r][tagCol]).trim();
    if (tag) existing[tag] = true;
    if (numCol !== undefined) {
      const n = parseInt(data[r][numCol], 10);
      if (!isNaN(n) && n > maxNum) maxNum = n;
    }
  }

  const width = sheet.getLastColumn();
  const toAppend = [], skipped = [];
  for (let r = 1; r < csv.length; r++) {
    const tag = (csv[r][idxIn('video_tag')] || '').trim();
    if (!tag) continue;
    if (existing[tag]) { skipped.push(tag); continue; }
    existing[tag] = true;
    const out = new Array(width).fill('');
    Object.keys(map).forEach(function (inCol) {
      const ci = colMap[map[inCol]], j = idxIn(inCol);
      if (ci !== undefined && j !== -1 && csv[r][j]) out[ci] = csv[r][j];
    });
    toAppend.push(out);
  }

  if (skipped.length) {
    Logger.log('!! COLLISION: ' + skipped.length + ' tag(s) already existed and were SKIPPED: ' +
               skipped.join(', ') + '. These scripts did NOT reach the sheet.');
  }

  if (toAppend.length) {
    // The sheet reads newest-first, so # counts DOWN the page: the top inserted row gets
    // the highest number and the block continues from the previous max.
    // Within the batch, the inbox is in tag order (realtimejake1, realtimejake2...), so
    // reverse it: the last tag lands on top, matching newest-first across batches.
    toAppend.reverse();
    if (numCol !== undefined) {
      for (let i = 0; i < toAppend.length; i++) toAppend[i][numCol] = maxNum + toAppend.length - i;
    }
    const insertAt = target.headerRow + 2; // 1-indexed row just below the header
    sheet.insertRowsBefore(insertAt, toAppend.length);
    const newRange = sheet.getRange(insertAt, 1, toAppend.length, width);
    newRange.setValues(toAppend);
    // insertRowsBefore inherits the formatting of the row above - i.e. the HEADER here.
    // Strip it so synced rows never look like headers or like Alp's manual colour flags.
    newRange.setBackground(null).setFontWeight('normal').setFontColor(null);
    newRange.setWrap(true).setVerticalAlignment('top');
    Logger.log('Inserted ' + toAppend.length + ' new row(s) under the header of "' + sheet.getName() + '".');
  } else {
    Logger.log('No new tags to append.');
  }
  file.setTrashed(true);
  writeTagIndex();
  writeSchema();
}

/** Run ONCE: appends any of the mapped columns that don't exist yet to the right of the
 *  header row (Mission, Target Niche, Posted to which account). Never moves or renames. */
function addMissingColumns() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  guard_(ss);
  const target = findTarget_(ss);
  if (!target) throw new Error('Target tab not found.');
  const map = fieldMap();
  const missing = Object.keys(map).map(function (k) { return map[k]; })
    .filter(function (h) { return target.colMap[h] === undefined; });
  if (!missing.length) { Logger.log('All mapped columns already exist.'); return; }
  const lastCol = target.sheet.getLastColumn();
  const hdr = target.sheet.getRange(target.headerRow + 1, lastCol + 1, 1, missing.length);
  hdr.setValues([missing]);
  target.sheet.getRange(target.headerRow + 1, lastCol).copyFormatToRange(
    target.sheet, lastCol + 1, lastCol + missing.length, target.headerRow + 1, target.headerRow + 1);
  Logger.log('Added columns: ' + missing.join(', '));
  writeSchema();
}

/** account -> highest tag number. Columns: account,max_number,video_count,updated_at */
function writeTagIndex() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  guard_(ss);
  const target = findTarget_(ss);
  if (!target) { Logger.log('writeTagIndex: target tab not found.'); return; }
  const tagCol = target.colMap[CONFIG.COL_TAG];
  const maxes = {}, counts = {};
  const re = /^([a-z][a-z0-9_.]*?)(\d+)$/i;
  for (let r = target.headerRow + 1; r < target.data.length; r++) {
    const m = re.exec(String(target.data[r][tagCol]).trim());
    if (!m) continue;
    const acct = m[1], num = parseInt(m[2], 10);
    counts[acct] = (counts[acct] || 0) + 1;
    if (!(acct in maxes) || num > maxes[acct]) maxes[acct] = num;
  }
  const stamp = new Date().toISOString();
  const lines = ['account,max_number,video_count,updated_at'];
  Object.keys(maxes).sort().forEach(function (a) { lines.push([a, maxes[a], counts[a], stamp].join(',')); });
  if (lines.length === 1) lines.push('# no tags yet,0,0,' + stamp);
  putFile_(CONFIG.INDEX_FILE_NAME, lines.join('\n'));
  Logger.log(CONFIG.INDEX_FILE_NAME + ' refreshed: ' + Object.keys(maxes).length + ' accounts.');
}

/** Publish the live header row, duplicates flagged. Columns: position,header,duplicate_of */
function writeSchema() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  guard_(ss);
  const target = findTarget_(ss);
  if (!target) { Logger.log('writeSchema: target tab not found.'); return; }
  const header = target.sheet.getRange(target.headerRow + 1, 1, 1, target.sheet.getLastColumn())
    .getValues()[0].map(function (c) { return String(c).trim(); });
  const firstSeen = {};
  const lines = ['position,header,duplicate_of'];
  let dupes = 0;
  header.forEach(function (h, i) {
    if (!h) return;
    let dup = '';
    if (firstSeen[h] === undefined) firstSeen[h] = i + 1; else { dup = firstSeen[h]; dupes++; }
    lines.push([i + 1, '"' + h.replace(/"/g, '""') + '"', dup].join(','));
  });
  lines.push('# tab,"' + target.sheet.getName() + '"');
  lines.push('# header_row,' + (target.headerRow + 1));
  lines.push('# duplicates,' + dupes);
  lines.push('# updated_at,' + new Date().toISOString());
  putFile_(CONFIG.SCHEMA_FILE_NAME, lines.join('\n'));
  if (dupes) Logger.log('!! ' + dupes + ' DUPLICATE header(s). The sync writes to the FIRST one only.');
}

function putFile_(name, body) {
  const files = DriveApp.getFilesByName(name);
  let wrote = false;
  while (files.hasNext()) {
    const f = files.next();
    if (f.isTrashed()) continue;
    if (!wrote) { f.setContent(body); wrote = true; } else { f.setTrashed(true); }
  }
  if (!wrote) DriveApp.createFile(name, body, MimeType.CSV);
}

/** Timestamped full copy into "Lume Video Data Backups"; keeps the newest BACKUP.KEEP. */
function dailyBackup() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  guard_(ss);
  const file = DriveApp.getFileById(ss.getId());
  const it = DriveApp.getFoldersByName(BACKUP.FOLDER_NAME);
  const folder = it.hasNext() ? it.next() : DriveApp.createFolder(BACKUP.FOLDER_NAME);
  const stamp = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), 'yyyy-MM-dd_HH-mm');
  file.makeCopy(ss.getName() + ' BACKUP ' + stamp, folder);
  const copies = [];
  const files = folder.getFiles();
  while (files.hasNext()) copies.push(files.next());
  copies.sort(function (a, b) { return b.getDateCreated().getTime() - a.getDateCreated().getTime(); });
  for (let i = BACKUP.KEEP; i < copies.length; i++) copies[i].setTrashed(true);
}

/** Run ONCE from the editor. syncInbox every minute, tag index + schema hourly, backup ~3am. */
function installTrigger() {
  guard_(SpreadsheetApp.getActiveSpreadsheet());
  ScriptApp.getProjectTriggers().forEach(function (t) {
    const fn = t.getHandlerFunction();
    if (['syncInbox', 'dailyBackup', 'writeTagIndex', 'writeSchema'].indexOf(fn) !== -1) ScriptApp.deleteTrigger(t);
  });
  ScriptApp.newTrigger('syncInbox').timeBased().everyMinutes(1).create();
  ScriptApp.newTrigger('writeTagIndex').timeBased().everyHours(1).create();
  ScriptApp.newTrigger('writeSchema').timeBased().everyHours(1).create();
  ScriptApp.newTrigger('dailyBackup').timeBased().everyDays(1).atHour(3).create();
  writeTagIndex();
  writeSchema();
  Logger.log('Lume triggers installed; lume-tag-index.csv and lume-sheet-schema.csv published.');
}
