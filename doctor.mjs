#!/usr/bin/env node
/**
 * doctor.mjs
 * Comprehensive diagnostic tool for career-ops setup.
 * Checks Node.js version, Go, Playwright, profile.yml, cv.md, and more.
 */

import { existsSync, readdirSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';
import { execSync } from 'child_process';

const __dirname = dirname(fileURLToPath(import.meta.url));

let passed = 0;
let failed = 0;
let warned = 0;

function ok(label, detail = '') {
  console.log(`  ✅  ${label}${detail ? ` (${detail})` : ''}`);
  passed++;
}

function fail(label, fix = '') {
  console.log(`  ❌  ${label}${fix ? `\n       Fix: ${fix}` : ''}`);
  failed++;
}

function warn(label, hint = '') {
  console.log(`  ⚠️   ${label}${hint ? `\n       Hint: ${hint}` : ''}`);
  warned++;
}

function runCmd(cmd) {
  try {
    return execSync(cmd, { stdio: 'pipe', timeout: 5000 }).toString().trim();
  } catch {
    return null;
  }
}

function semverAtLeast(version, major, minor = 0) {
  if (!version) return false;
  const match = version.match(/(\d+)\.(\d+)/);
  if (!match) return false;
  const [, maj, min] = match.map(Number);
  return maj > major || (maj === major && min >= minor);
}

// ── Section: Node.js ─────────────────────────────────────────────────────────
function checkNode() {
  console.log('\n🟢 Node.js');
  const version = runCmd('node --version');
  if (!version) {
    fail('Node.js not found', 'Install from https://nodejs.org (v18+)');
    return;
  }
  const isv18Plus = semverAtLeast(version, 18);
  if (isv18Plus) {
    ok(`Node.js ${version}`);
  } else {
    fail(`Node.js ${version} — requires v18+`, 'Upgrade: https://nodejs.org');
  }

  const npmVersion = runCmd('npm --version');
  if (npmVersion) {
    ok(`npm ${npmVersion}`);
  } else {
    warn('npm not found (expected with Node.js)');
  }
}

// ── Section: Go ──────────────────────────────────────────────────────────────
function checkGo() {
  console.log('\n🐹 Go (for TUI Dashboard)');
  const version = runCmd('go version');
  if (!version) {
    warn('Go not installed', 'Optional: install Go 1.21+ from https://golang.org/dl/ to run the dashboard');
    return;
  }
  const isv121Plus = semverAtLeast(version, 1, 21);
  if (isv121Plus) {
    ok(`${version}`);
  } else {
    fail(`${version} — requires Go 1.21+`, 'Upgrade: https://golang.org/dl/');
  }
}

// ── Section: Playwright ──────────────────────────────────────────────────────
function checkPlaywright() {
  console.log('\n🎭 Playwright');

  const nodeModulesPlaywright = resolve(__dirname, 'node_modules/playwright');
  if (!existsSync(nodeModulesPlaywright)) {
    fail('Playwright package not installed', 'Run: npm install');
    return;
  }
  ok('Playwright package installed');

  const version = runCmd('npx playwright --version');
  if (version) {
    ok(`${version}`);
  } else {
    warn('Could not read Playwright version');
  }

  // Check chromium browser
  const localAppData = process.env.LOCALAPPDATA || '';
  const home = process.env.HOME || process.env.USERPROFILE || '';
  const possibleDirs = [
    resolve(localAppData, 'ms-playwright'),
    resolve(home, '.cache', 'ms-playwright'),
    resolve(home, 'AppData', 'Local', 'ms-playwright'),
  ];

  let chromiumFound = false;
  for (const dir of possibleDirs) {
    if (existsSync(dir)) {
      try {
        const entries = readdirSync(dir);
        if (entries.some(e => e.startsWith('chromium'))) {
          chromiumFound = true;
          ok(`Chromium browser found in ${dir}`);
          break;
        }
      } catch {
        // ignore read errors
      }
    }
  }

  if (!chromiumFound) {
    fail('Chromium browser not installed', 'Run: npx playwright install chromium');
  }
}

// ── Section: Project Files ───────────────────────────────────────────────────
function checkProjectFiles() {
  console.log('\n📄 Project Files');

  const requiredFiles = [
    ['templates/cv-template.html', 'HTML CV template'],
    ['templates/states.yml',       'Status definitions'],
    ['templates/portals.example.yml', 'Portal registry example'],
    ['modes/_shared.md',           'Shared mode rules'],
    ['modes/oferta.md',            'Single job eval mode'],
  ];

  for (const [relPath, label] of requiredFiles) {
    const abs = resolve(__dirname, relPath);
    if (existsSync(abs)) {
      ok(`${label} (${relPath})`);
    } else {
      fail(`Missing: ${label}`, `Expected at: ${relPath}`);
    }
  }

  const userFiles = [
    ['cv.md',               'Your CV (Markdown)', true],
    ['config/profile.yml',  'Your profile config', true],
    ['data/applications.md', 'Applications tracker', false],
    ['config/portals.yml',  'Your portal config',   false],
  ];

  console.log('\n👤 User Data Files');
  for (const [relPath, label, required] of userFiles) {
    const abs = resolve(__dirname, relPath);
    if (existsSync(abs)) {
      ok(`${label} (${relPath})`);
    } else if (required) {
      fail(`Missing: ${label}`, `Create at: ${relPath} (see examples/)`);
    } else {
      warn(`Optional: ${label} not yet created`, `Will be created automatically or copy from templates/`);
    }
  }
}

// ── Section: Mode Files ──────────────────────────────────────────────────────
function checkModes() {
  console.log('\n🎯 Mode Files');

  const modeFiles = [
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

  let modesMissing = 0;
  for (const f of modeFiles) {
    const abs = resolve(__dirname, f);
    if (existsSync(abs)) {
      ok(f);
    } else {
      fail(`Missing: ${f}`);
      modesMissing++;
    }
  }

  if (modesMissing === 0) {
    // ok already printed above
  }
}

// ── Section: Scripts ─────────────────────────────────────────────────────────
function checkScripts() {
  console.log('\n🔧 Utility Scripts');

  const scripts = [
    'generate-pdf.mjs',
    'merge-tracker.mjs',
    'verify-pipeline.mjs',
    'normalize-statuses.mjs',
    'dedup-tracker.mjs',
    'doctor.mjs',
    'analyze-patterns.mjs',
  ];

  for (const s of scripts) {
    const abs = resolve(__dirname, s);
    existsSync(abs) ? ok(s) : fail(`Missing: ${s}`);
  }
}

// ── Summary ──────────────────────────────────────────────────────────────────
function printSummary() {
  const total = passed + failed + warned;
  console.log('\n' + '─'.repeat(44));
  console.log(`Diagnostic complete: ${total} checks`);
  console.log(`  ✅  Passed:   ${passed}`);
  if (warned > 0)  console.log(`  ⚠️   Warnings: ${warned}`);
  if (failed > 0)  console.log(`  ❌  Failed:   ${failed}`);
  console.log('');

  if (failed === 0 && warned === 0) {
    console.log('🚀 Career-Ops is ready to use!\n');
  } else if (failed === 0) {
    console.log('✅ Core setup is complete. Review warnings above.\n');
  } else {
    console.log('⚠️  Fix the issues above before using Career-Ops.\n');
    process.exit(1);
  }
}

// ── Main ────────────────────────────────────────────────────────────────────
console.log('\nCareer-Ops Doctor — System Diagnostic');
console.log('═'.repeat(44));

checkNode();
checkGo();
checkPlaywright();
checkProjectFiles();
checkModes();
checkScripts();
printSummary();
