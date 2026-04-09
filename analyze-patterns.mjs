#!/usr/bin/env node
/**
 * analyze-patterns.mjs
 * Reads all reports in reports/ and applications.md to identify
 * rejection patterns, response rates, and actionable insights.
 */

import { readFileSync, readdirSync, existsSync } from 'fs';
import { resolve, dirname, join } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const REPORTS_DIR     = resolve(__dirname, 'reports');
const APPLICATIONS_MD = resolve(__dirname, 'data/applications.md');

// ── Parse applications.md ────────────────────────────────────────────────────
function parseApplications() {
  if (!existsSync(APPLICATIONS_MD)) return [];

  const content = readFileSync(APPLICATIONS_MD, 'utf-8');
  const rows = [];
  let headerDone = false;

  for (const line of content.split('\n')) {
    if (!line.startsWith('|')) continue;
    const cells = line.split('|').map(c => c.trim()).filter((_, i, a) => i > 0 && i < a.length - 1);
    if (cells.length < 5) continue;
    if (cells.some(c => c.toLowerCase() === 'date' || c.toLowerCase() === 'company')) continue;
    if (cells.every(c => /^[-:]+$/.test(c))) { headerDone = true; continue; }
    if (!headerDone) continue;

    rows.push({
      date:    cells[1] || '',
      company: cells[2] || '',
      role:    cells[3] || '',
      score:   parseFloat(cells[4]) || 0,
      status:  cells[5] || '',
    });
  }
  return rows;
}

// ── Parse reports for stage info ─────────────────────────────────────────────
function parseReports() {
  if (!existsSync(REPORTS_DIR)) return [];

  const files = readdirSync(REPORTS_DIR).filter(f => f.endsWith('.md'));
  const reports = [];

  for (const file of files) {
    const content = readFileSync(join(REPORTS_DIR, file), 'utf-8');
    const report = { file };

    // Extract grade
    const gradeMatch = content.match(/Grade[:\s]+([A-F][+-]?)/i);
    if (gradeMatch) report.grade = gradeMatch[1];

    // Extract company
    const companyMatch = content.match(/Company[:\s]+([^\n]+)/i);
    if (companyMatch) report.company = companyMatch[1].trim();

    // Extract rejection stage
    if (content.toLowerCase().includes('rejected')) {
      if (content.toLowerCase().includes('phone') || content.toLowerCase().includes('recruiter')) {
        report.rejectionStage = 'Phone Screen';
      } else if (content.toLowerCase().includes('technical') || content.toLowerCase().includes('coding')) {
        report.rejectionStage = 'Technical Screen';
      } else if (content.toLowerCase().includes('onsite') || content.toLowerCase().includes('loop')) {
        report.rejectionStage = 'Onsite';
      } else if (content.toLowerCase().includes('offer') || content.toLowerCase().includes('comp')) {
        report.rejectionStage = 'Offer Stage';
      } else {
        report.rejectionStage = 'Unknown Stage';
      }
    }

    reports.push(report);
  }
  return reports;
}

// ── Compute analytics ────────────────────────────────────────────────────────
function computeAnalytics(apps) {
  const total = apps.length;
  if (total === 0) return null;

  const byStatus = {};
  for (const app of apps) {
    const s = app.status || 'Unknown';
    byStatus[s] = (byStatus[s] || 0) + 1;
  }

  const responseCount = (byStatus['Screening'] || 0) + (byStatus['Interview'] || 0) +
                        (byStatus['Offer'] || 0) + (byStatus['Rejected'] || 0);
  const responseRate = ((responseCount / total) * 100).toFixed(1);
  const offerRate    = (((byStatus['Offer'] || 0) / total) * 100).toFixed(1);

  // Score distribution
  const scored = apps.filter(a => a.score > 0);
  const avgScore = scored.length > 0
    ? (scored.reduce((s, a) => s + a.score, 0) / scored.length).toFixed(2)
    : 'N/A';

  // Company frequency
  const companyCounts = {};
  for (const app of apps) {
    companyCounts[app.company] = (companyCounts[app.company] || 0) + 1;
  }

  // Applications over time (monthly buckets)
  const monthly = {};
  for (const app of apps) {
    const month = (app.date || '').slice(0, 7);
    if (month) monthly[month] = (monthly[month] || 0) + 1;
  }

  return { total, byStatus, responseRate, offerRate, avgScore, monthly };
}

// ── Print report ─────────────────────────────────────────────────────────────
function printReport(analytics, reports) {
  console.log('\n📊 Career-Ops Pattern Analysis\n' + '═'.repeat(44));

  if (!analytics) {
    console.log('No application data found. Add entries to data/applications.md\n');
    return;
  }

  const { total, byStatus, responseRate, offerRate, avgScore, monthly } = analytics;

  console.log(`\n📋 Pipeline Overview (${total} total applications)`);
  console.log('─'.repeat(40));
  const statusOrder = ['Applied','Screening','Interview','Offer','Rejected','Withdrawn','Ghosted','Pipeline'];
  for (const s of statusOrder) {
    const count = byStatus[s] || 0;
    if (count > 0) {
      const bar = '█'.repeat(Math.round(count / total * 20));
      console.log(`  ${s.padEnd(12)} ${String(count).padStart(3)}  ${bar}`);
    }
  }

  console.log(`\n📈 Key Metrics`);
  console.log('─'.repeat(40));
  console.log(`  Response Rate:  ${responseRate}%`);
  console.log(`  Offer Rate:     ${offerRate}%`);
  console.log(`  Avg JD Score:   ${avgScore}`);

  // Monthly activity
  const months = Object.entries(monthly).sort(([a], [b]) => a.localeCompare(b));
  if (months.length > 0) {
    console.log(`\n📅 Monthly Application Activity`);
    console.log('─'.repeat(40));
    for (const [month, count] of months) {
      const bar = '▪'.repeat(count);
      console.log(`  ${month}  ${String(count).padStart(3)}  ${bar}`);
    }
  }

  // Report patterns
  if (reports.length > 0) {
    const rejections = reports.filter(r => r.rejectionStage);
    if (rejections.length > 0) {
      const stageCounts = {};
      for (const r of rejections) {
        stageCounts[r.rejectionStage] = (stageCounts[r.rejectionStage] || 0) + 1;
      }
      console.log(`\n❌ Rejection Stage Breakdown (from ${rejections.length} reports)`);
      console.log('─'.repeat(40));
      for (const [stage, count] of Object.entries(stageCounts).sort((a, b) => b[1] - a[1])) {
        console.log(`  ${stage.padEnd(20)} ${count}`);
      }
    }

    // Grade distribution
    const gradeCounts = {};
    for (const r of reports.filter(r => r.grade)) {
      gradeCounts[r.grade] = (gradeCounts[r.grade] || 0) + 1;
    }
    if (Object.keys(gradeCounts).length > 0) {
      console.log(`\n🎓 JD Match Grade Distribution`);
      console.log('─'.repeat(40));
      for (const [grade, count] of Object.entries(gradeCounts).sort()) {
        console.log(`  ${grade.padEnd(5)} ${count}`);
      }
    }
  }

  // Actionable insights
  console.log(`\n💡 Insights`);
  console.log('─'.repeat(40));

  const ghostedPct = ((byStatus['Ghosted'] || 0) / total * 100);
  if (ghostedPct > 30) {
    console.log(`  ⚠️  High ghost rate (${ghostedPct.toFixed(0)}%) — consider narrowing target list`);
  }

  const screeningPct = ((byStatus['Screening'] || 0) + (byStatus['Interview'] || 0)) / total * 100;
  if (screeningPct < 10) {
    console.log(`  ⚠️  Low screen rate (${screeningPct.toFixed(0)}%) — revisit CV keywords and targeting`);
  }

  const offerPctNum = parseFloat(offerRate);
  if (offerPctNum > 5) {
    console.log(`  ✅  Strong offer conversion (${offerRate}%) — maintain current approach`);
  }

  console.log('');
}

// ── Main ────────────────────────────────────────────────────────────────────
const apps    = parseApplications();
const reports = parseReports();
const analytics = computeAnalytics(apps);
printReport(analytics, reports);
