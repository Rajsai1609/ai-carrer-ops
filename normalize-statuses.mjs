#!/usr/bin/env node
/**
 * normalize-statuses.mjs
 * Reads data/applications.md and maps all status variants to canonical
 * states defined in templates/states.yml. Overwrites the file in place.
 */

import { readFileSync, writeFileSync, existsSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

const APPLICATIONS_MD = resolve(__dirname, 'data/applications.md');
const STATES_YML      = resolve(__dirname, 'templates/states.yml');

// ── Build alias → canonical map from states.yml ──────────────────────────────
function buildAliasMap(statesYml) {
  const map = new Map();
  let currentStatus = null;
  let inAliases = false;

  for (const line of statesYml.split('\n')) {
    const nameMatch = line.match(/^\s+- name:\s+(.+)$/);
    if (nameMatch) {
      currentStatus = nameMatch[1].trim();
      map.set(currentStatus.toLowerCase(), currentStatus);
      inAliases = false;
      continue;
    }

    if (line.includes('aliases:')) {
      inAliases = true;
      continue;
    }

    if (inAliases && currentStatus) {
      const aliasMatch = line.match(/^\s+- (.+)$/);
      if (aliasMatch) {
        const alias = aliasMatch[1].trim();
        map.set(alias.toLowerCase(), currentStatus);
      } else if (line.trim() && !line.trim().startsWith('-')) {
        inAliases = false;
      }
    }
  }

  return map;
}

// ── Normalize a single status string ────────────────────────────────────────
function normalize(raw, aliasMap) {
  const lower = raw.trim().toLowerCase();
  return aliasMap.get(lower) || raw.trim();
}

// ── Process MD table ─────────────────────────────────────────────────────────
function normalizeMD(content, aliasMap) {
  const lines = content.split('\n');
  let inTable = false;
  let headerPassed = false;
  let changed = 0;

  const result = lines.map(line => {
    if (!line.startsWith('|')) {
      inTable = false;
      headerPassed = false;
      return line;
    }

    const cells = line.split('|');

    // Header row detection: look for "Date" or "Company"
    if (cells.some(c => c.trim().toLowerCase() === 'date' || c.trim().toLowerCase() === 'company')) {
      inTable = true;
      headerPassed = false;
      return line;
    }

    // Separator row
    if (cells.slice(1, -1).every(c => /^[-:\s]+$/.test(c))) {
      headerPassed = true;
      return line;
    }

    if (!inTable || !headerPassed) return line;

    // Data row: status is in column index 5 (0-indexed from split)
    // | # | Date | Company | Role | Score | Status | ...
    // cells[0] = '' (before first |), cells[6] = Status
    if (cells.length >= 7) {
      const original = cells[6].trim();
      const normalized = normalize(original, aliasMap);
      if (original !== normalized) {
        changed++;
        cells[6] = ` ${normalized} `;
        return cells.join('|');
      }
    }

    return line;
  });

  return { content: result.join('\n'), changed };
}

// ── Main ────────────────────────────────────────────────────────────────────
function main() {
  if (!existsSync(APPLICATIONS_MD)) {
    console.error('Error: data/applications.md not found.');
    process.exit(1);
  }

  if (!existsSync(STATES_YML)) {
    console.error('Error: templates/states.yml not found.');
    process.exit(1);
  }

  const statesContent = readFileSync(STATES_YML, 'utf-8');
  const aliasMap = buildAliasMap(statesContent);
  console.log(`Loaded ${aliasMap.size} status mappings from states.yml`);

  const mdContent = readFileSync(APPLICATIONS_MD, 'utf-8');
  const { content: normalized, changed } = normalizeMD(mdContent, aliasMap);

  if (changed === 0) {
    console.log('✅ All statuses already canonical — no changes needed.');
    return;
  }

  writeFileSync(APPLICATIONS_MD, normalized, 'utf-8');
  console.log(`✅ Normalized ${changed} status value(s) in data/applications.md`);
}

main();
