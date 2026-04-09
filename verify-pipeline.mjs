#!/usr/bin/env node
/**
 * verify-pipeline.mjs
 * Checks that all required files and tools exist for career-ops to function.
 */

import { existsSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';
import { execSync } from 'child_process';

const __dirname = dirname(fileURLToPath(import.meta.url));

let systemPassed = true;
let warnings = 0;

function check(label, passed, hint = '', warn = false) {
  const icon = passed ? '✅' : (warn ? '⚠️ ' : '❌');
  const msg = passed ? label : `${label}${hint ? ` — ${hint}` : ''}`;
  console.log(`  ${icon}  ${msg}`);
  if (!passed) {
    if (warn) warnings++;
    else systemPassed = false;
  }
}

function checkFile(label, relPath, hint = '', warn = false) {
  const abs = resolve(__dirname, relPath);
  check(label, existsSync(abs), hint || `expected at ${relPath}`, warn);
}

function commandExists(cmd) {
  try {
    execSync(`${cmd} --version`, { stdio: 'pipe' });
    return true;
  } catch {
    return false;
  }
}

function checkCommand(label, cmd, hint = '', warn = false) {
  check(label, commandExists(cmd), hint, warn);
}

console.log('\nCareer-Ops Pipeline Verification\n' + '─'.repeat(40));

// ── System Files (must exist — written during setup) ─────────────────────────
console.log('\n📁 System Files:');
checkFile('templates/cv-template.html',    'templates/cv-template.html');
checkFile('templates/states.yml',          'templates/states.yml');
checkFile('templates/portals.example.yml', 'templates/portals.example.yml');

// ── User Files (warn only — user creates these) ───────────────────────────────
console.log('\n👤 User Files (create these to start using Career-Ops):');
checkFile('cv.md',              'cv.md',              'Copy examples/cv-example.md → cv.md', true);
checkFile('config/profile.yml', 'config/profile.yml', 'Copy config/profile.example.yml → config/profile.yml', true);

// ── Optional Data Files ───────────────────────────────────────────────────────
console.log('\n📋 Data Files (auto-created on first run):');
checkFile('data/applications.md', 'data/applications.md', 'Created by merge-tracker.mjs automatically', true);
checkFile('config/portals.yml',   'config/portals.yml',   'Copy templates/portals.example.yml → config/portals.yml', true);

// ── Required Tools ────────────────────────────────────────────────────────────
console.log('\n🔧 Required Tools:');
checkCommand('Node.js', 'node', 'Install from https://nodejs.org');
checkCommand('npx',     'npx',  'Comes with Node.js');

// Check Playwright
let playwrightOk = false;
try {
  const result = execSync('npx playwright --version', { stdio: 'pipe' }).toString().trim();
  playwrightOk = result.includes('Version');
  check('Playwright installed', playwrightOk);
} catch {
  check('Playwright installed', false, 'Run: npm install');
}

// Check chromium
const chromiumDirs = [
  `${process.env.LOCALAPPDATA || ''}\\ms-playwright`,
  `${process.env.HOME || ''}/.cache/ms-playwright`,
];
let chromiumFound = false;
for (const dir of chromiumDirs) {
  if (existsSync(dir)) {
    chromiumFound = true;
    break;
  }
}
check('Playwright chromium', chromiumFound, 'Run: npx playwright install chromium');

// ── Optional Tools ────────────────────────────────────────────────────────────
console.log('\n🐹 Optional Tools:');
checkCommand('Go (TUI dashboard)', 'go', 'Install Go 1.21+ from https://golang.org/dl/', true);

// ── Mode Files ────────────────────────────────────────────────────────────────
console.log('\n🎯 Mode Files:');
const modes = [
  'modes/_shared.md',
  'modes/oferta.md',
  'modes/ofertas.md',
  'modes/pdf.md',
  'modes/scan.md',
  'modes/batch.md',
  'modes/tracker.md',
  'modes/apply.md',
  'modes/pipeline.md',
  'modes/contacto.md',
  'modes/deep.md',
  'modes/training.md',
  'modes/project.md',
  'modes/patterns.md',
  'modes/auto-pipeline.md',
];
for (const mode of modes) {
  checkFile(mode, mode);
}

// ── Summary ───────────────────────────────────────────────────────────────────
console.log('\n' + '─'.repeat(40));
if (systemPassed && warnings === 0) {
  console.log('✅ Pipeline healthy — all checks passed.\n');
} else if (systemPassed) {
  console.log(`✅ System healthy — ${warnings} setup step(s) remaining (see ⚠️  above).\n`);
} else {
  console.log('❌ System check failed — fix ❌ errors before using Career-Ops.\n');
  process.exit(1);
}
