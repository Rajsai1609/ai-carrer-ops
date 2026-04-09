#!/usr/bin/env node
/**
 * merge-tracker.mjs
 * Reads TSV files from batch/tracker-additions/ and appends new rows
 * to data/applications.md, deduplicating by Company+Role+Date.
 */

import { readFileSync, writeFileSync, readdirSync, renameSync, existsSync, mkdirSync } from 'fs';
import { resolve, dirname, join } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const PROJECT_ROOT = __dirname;

const TRACKER_DIR     = resolve(PROJECT_ROOT, 'batch/tracker-additions');
const ARCHIVE_DIR     = resolve(PROJECT_ROOT, 'batch/logs/archived-tsv');
const APPLICATIONS_MD = resolve(PROJECT_ROOT, 'data/applications.md');

// Expected TSV columns (0-indexed)
const COL = {
  NUMBER:  0,
  DATE:    1,
  COMPANY: 2,
  ROLE:    3,
  SCORE:   4,
  STATUS:  5,
  PDF:     6,
  REPORT:  7,
  NOTES:   8,
};

const MD_HEADER = `# Job Applications Tracker

| # | Date | Company | Role | Score | Status | PDF | Report | Notes |
|---|------|---------|------|-------|--------|-----|--------|-------|
`;

// ── Parse TSV ────────────────────────────────────────────────────────────────
function parseTSV(filePath) {
  const text = readFileSync(filePath, 'utf-8');
  const lines = text.split('\n').filter(l => l.trim());
  const rows = [];

  for (const line of lines) {
    if (line.startsWith('#') || line.startsWith('//')) continue; // skip comments
    const cells = line.split('\t').map(c => c.trim());
    if (cells.length < 3) continue; // skip malformed rows

    rows.push({
      number:  cells[COL.NUMBER]  || '',
      date:    cells[COL.DATE]    || '',
      company: cells[COL.COMPANY] || '',
      role:    cells[COL.ROLE]    || '',
      score:   cells[COL.SCORE]   || '-',
      status:  cells[COL.STATUS]  || 'Applied',
      pdf:     cells[COL.PDF]     || '-',
      report:  cells[COL.REPORT]  || '-',
      notes:   cells[COL.NOTES]   || '',
    });
  }

  return rows;
}

// ── Parse existing MD table ──────────────────────────────────────────────────
function parseExistingMD(filePath) {
  if (!existsSync(filePath)) return [];

  const text = readFileSync(filePath, 'utf-8');
  const rows = [];

  for (const line of text.split('\n')) {
    if (!line.startsWith('|')) continue;
    const cells = line.split('|').map(c => c.trim()).filter(Boolean);
    if (cells.length < 6) continue;
    if (cells[0] === '#' || cells[0].startsWith('-')) continue; // header / separator

    rows.push({
      number:  cells[0] || '',
      date:    cells[1] || '',
      company: cells[2] || '',
      role:    cells[3] || '',
      score:   cells[4] || '-',
      status:  cells[5] || '',
      pdf:     cells[6] || '-',
      report:  cells[7] || '-',
      notes:   cells[8] || '',
    });
  }

  return rows;
}

// ── Deduplication key ────────────────────────────────────────────────────────
function dedupKey(row) {
  return `${row.company.toLowerCase()}|${row.role.toLowerCase()}|${row.date}`;
}

// ── Format row as MD table row ───────────────────────────────────────────────
function toMDRow(row) {
  const n = row.number || '-';
  return `| ${n} | ${row.date} | ${row.company} | ${row.role} | ${row.score} | ${row.status} | ${row.pdf} | ${row.report} | ${row.notes} |`;
}

// ── Renumber rows ────────────────────────────────────────────────────────────
function renumber(rows) {
  return rows.map((r, i) => ({ ...r, number: String(i + 1) }));
}

// ── Main ────────────────────────────────────────────────────────────────────
async function main() {
  // Ensure directories exist
  mkdirSync(TRACKER_DIR,  { recursive: true });
  mkdirSync(ARCHIVE_DIR,  { recursive: true });
  mkdirSync(resolve(PROJECT_ROOT, 'data'), { recursive: true });

  // Find TSV files
  const tsvFiles = readdirSync(TRACKER_DIR).filter(f => f.endsWith('.tsv'));

  if (tsvFiles.length === 0) {
    console.log('No TSV files found in batch/tracker-additions/ — nothing to merge.');
    return;
  }

  console.log(`Found ${tsvFiles.length} TSV file(s) to merge...`);

  // Load existing entries
  const existing = parseExistingMD(APPLICATIONS_MD);
  const seen = new Set(existing.map(dedupKey));
  const allRows = [...existing];
  let added = 0;
  let dupes = 0;

  // Process each TSV
  for (const file of tsvFiles) {
    const filePath = join(TRACKER_DIR, file);
    const newRows = parseTSV(filePath);
    console.log(`  Processing ${file}: ${newRows.length} row(s)`);

    for (const row of newRows) {
      const key = dedupKey(row);
      if (seen.has(key)) {
        dupes++;
        continue;
      }
      seen.add(key);
      allRows.push(row);
      added++;
    }

    // Archive processed TSV
    const archivePath = join(ARCHIVE_DIR, file);
    renameSync(filePath, archivePath);
    console.log(`  Archived: ${file} → batch/logs/archived-tsv/${file}`);
  }

  // Sort by date descending
  allRows.sort((a, b) => {
    const da = new Date(a.date || '2000-01-01');
    const db = new Date(b.date || '2000-01-01');
    return db - da;
  });

  // Renumber
  const numbered = renumber(allRows);

  // Write output
  const mdLines = numbered.map(toMDRow).join('\n');
  const output = MD_HEADER + mdLines + '\n';
  writeFileSync(APPLICATIONS_MD, output, 'utf-8');

  console.log(`\n✅ Merge complete:`);
  console.log(`   Added:      ${added} new entries`);
  console.log(`   Duplicates: ${dupes} skipped`);
  console.log(`   Total:      ${numbered.length} entries in tracker`);
  console.log(`   Output:     data/applications.md`);
}

main().catch(err => {
  console.error('Fatal error:', err.message);
  process.exit(1);
});
