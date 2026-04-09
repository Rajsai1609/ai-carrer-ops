#!/usr/bin/env node
/**
 * dedup-tracker.mjs
 * Reads data/applications.md, removes duplicate rows (same Company + Role),
 * keeps the most recent entry, and writes back.
 */

import { readFileSync, writeFileSync, existsSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const APPLICATIONS_MD = resolve(__dirname, 'data/applications.md');

// ── Parse markdown table rows ────────────────────────────────────────────────
function parseMDTable(content) {
  const lines = content.split('\n');
  const header = [];
  const rows = [];
  let headerParsed = false;

  for (const line of lines) {
    if (!line.startsWith('|')) {
      header.push({ type: 'text', value: line });
      continue;
    }

    const cells = line.split('|').map(c => c.trim()).filter((_, i, arr) => i > 0 && i < arr.length - 1);

    // Separator row
    if (cells.every(c => /^[-:\s]+$/.test(c))) {
      header.push({ type: 'separator', value: line });
      headerParsed = true;
      continue;
    }

    // Header row
    if (!headerParsed) {
      header.push({ type: 'header', value: line, cells });
      continue;
    }

    // Data row
    if (cells.length >= 4) {
      rows.push({ cells, raw: line });
    }
  }

  return { header, rows };
}

// ── Dedup key: Company + Role (normalized) ───────────────────────────────────
function dedupKey(cells) {
  const company = (cells[2] || '').toLowerCase().trim();
  const role    = (cells[3] || '').toLowerCase().trim();
  return `${company}||${role}`;
}

// ── Parse date from cells ────────────────────────────────────────────────────
function parseDate(cells) {
  const raw = (cells[1] || '').trim();
  const d = new Date(raw);
  return isNaN(d.getTime()) ? new Date(0) : d;
}

// ── Rebuild markdown from rows ───────────────────────────────────────────────
function buildMD(header, rows) {
  // Renumber
  const numbered = rows.map((r, i) => {
    const cells = [...r.cells];
    cells[0] = String(i + 1);
    const formatted = cells.map(c => ` ${c} `).join('|');
    return `|${formatted}|`;
  });

  const headerLines = header.map(h => h.value);
  return headerLines.join('\n') + '\n' + numbered.join('\n') + '\n';
}

// ── Main ────────────────────────────────────────────────────────────────────
function main() {
  if (!existsSync(APPLICATIONS_MD)) {
    console.error('Error: data/applications.md not found.');
    process.exit(1);
  }

  const content = readFileSync(APPLICATIONS_MD, 'utf-8');
  const { header, rows } = parseMDTable(content);

  console.log(`Total rows before dedup: ${rows.length}`);

  // Group by dedup key, keep most recent
  const byKey = new Map();
  for (const row of rows) {
    const key = dedupKey(row.cells);
    const existing = byKey.get(key);
    if (!existing) {
      byKey.set(key, row);
    } else {
      // Keep more recent
      const existingDate = parseDate(existing.cells);
      const newDate      = parseDate(row.cells);
      if (newDate > existingDate) {
        byKey.set(key, row);
      }
    }
  }

  const deduped = [...byKey.values()];
  const removed = rows.length - deduped.length;

  if (removed === 0) {
    console.log('✅ No duplicates found — tracker is clean.');
    return;
  }

  // Sort by date descending
  deduped.sort((a, b) => parseDate(b.cells) - parseDate(a.cells));

  const output = buildMD(header, deduped);
  writeFileSync(APPLICATIONS_MD, output, 'utf-8');

  console.log(`✅ Removed ${removed} duplicate(s). ${deduped.length} entries remain.`);
}

main();
