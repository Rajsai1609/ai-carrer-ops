#!/usr/bin/env node
/**
 * run-pipeline-auto.mjs
 * Batch-evaluates all URLs in data/pipeline.md against your profile and CV.
 * Usage: node run-pipeline-auto.mjs [--limit N]
 */

import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const TODAY = new Date().toISOString().split('T')[0];

// ── Arg parsing ───────────────────────────────────────────────────────────────
const args = process.argv.slice(2);
const limitIdx = args.indexOf('--limit');
const LIMIT = limitIdx !== -1 ? parseInt(args[limitIdx + 1], 10) : 92;

// ── Ensure output dirs exist ──────────────────────────────────────────────────
const reportsDir = resolve(__dirname, 'reports');
const dataDir = resolve(__dirname, 'data');
if (!existsSync(reportsDir)) mkdirSync(reportsDir, { recursive: true });
if (!existsSync(dataDir)) mkdirSync(dataDir, { recursive: true });

// ── YAML parser (handles our specific profile.yml format) ─────────────────────
function parseYaml(text) {
  const result = {};
  const lines = text.split('\n');
  let topKey = null;
  let nestedKey = null;

  for (const raw of lines) {
    if (!raw.trim() || raw.trim().startsWith('#')) continue;

    // Top-level key (no leading spaces)
    const topMatch = raw.match(/^([A-Za-z_][\w_-]*)\s*:\s*(.*)/);
    if (topMatch) {
      topKey = topMatch[1];
      nestedKey = null;
      const val = topMatch[2].trim();
      if (val) {
        result[topKey] = parseScalar(val);
      } else {
        // Placeholder: will be filled by child lines
        result[topKey] = null;
      }
      continue;
    }

    // 2-space nested key
    const nestedKeyMatch = raw.match(/^  ([A-Za-z_][\w_-]*)\s*:\s*(.*)/);
    if (nestedKeyMatch && topKey) {
      nestedKey = nestedKeyMatch[1];
      const val = nestedKeyMatch[2].trim();
      if (result[topKey] === null || typeof result[topKey] !== 'object' || Array.isArray(result[topKey])) {
        result[topKey] = {};
      }
      result[topKey][nestedKey] = val ? parseScalar(val) : null;
      continue;
    }

    // 2-space list item under top-level key
    const topListMatch = raw.match(/^  - (.*)/);
    if (topListMatch && topKey && nestedKey === null) {
      if (!Array.isArray(result[topKey])) result[topKey] = [];
      result[topKey].push(topListMatch[1].trim().replace(/^['"]|['"]$/g, ''));
      continue;
    }

    // 4-space list item under nested key
    const nestedListMatch = raw.match(/^    - (.*)/);
    if (nestedListMatch && topKey && nestedKey) {
      if (!Array.isArray(result[topKey][nestedKey])) result[topKey][nestedKey] = [];
      result[topKey][nestedKey].push(nestedListMatch[1].trim().replace(/^['"]|['"]$/g, ''));
      continue;
    }
  }
  return result;
}

function parseScalar(v) {
  const s = v.replace(/^['"]|['"]$/g, '');
  if (s === 'true') return true;
  if (s === 'false') return false;
  if (/^\d+$/.test(s)) return parseInt(s, 10);
  return s;
}

// ── Load config files ─────────────────────────────────────────────────────────
function loadProfile() {
  const path = resolve(__dirname, 'config/profile.yml');
  if (!existsSync(path)) {
    console.error('❌  config/profile.yml not found. Run: cp config/profile.example.yml config/profile.yml');
    process.exit(1);
  }
  return parseYaml(readFileSync(path, 'utf-8'));
}

function loadCV() {
  const path = resolve(__dirname, 'cv.md');
  if (!existsSync(path)) {
    console.error('❌  cv.md not found. Run: cp examples/cv-example.md cv.md');
    process.exit(1);
  }
  return readFileSync(path, 'utf-8').toLowerCase();
}

// ── Fetch job page ────────────────────────────────────────────────────────────
async function fetchJob(url) {
  const urlMatch = url.match(/jobs\.ashbyhq\.com\/([^/]+)\/([^/?#]+)/);
  const companySlug = urlMatch ? urlMatch[1] : 'unknown';

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 10000);

  try {
    const res = await fetch(url, {
      signal: controller.signal,
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
      },
    });
    clearTimeout(timer);
    const html = await res.text();
    return parseJobFromHtml(html, companySlug, url);
  } catch (err) {
    clearTimeout(timer);
    return { title: 'Fetch Error', company: companySlug, companySlug, description: '', error: err.message };
  }
}

function parseJobFromHtml(html, companySlug, url) {
  // Try __NEXT_DATA__ (Ashby uses Next.js)
  const nextMatch = html.match(/<script[^>]+id="__NEXT_DATA__"[^>]*>([\s\S]*?)<\/script>/);
  if (nextMatch) {
    try {
      const data = JSON.parse(nextMatch[1]);
      const pp = data?.props?.pageProps;
      // Multiple possible paths in Ashby's Next data
      const job = pp?.jobPosting ?? pp?.posting ?? pp?.job ?? null;
      if (job) {
        const title = job.title ?? job.jobTitle ?? 'Unknown Role';
        const orgName = job.organization?.name ?? job.company?.name ?? job.organizationName ?? companySlug;
        const descHtml = job.descriptionHtml ?? job.description ?? job.jobDescriptionHtml ?? '';
        const descText = stripHtml(descHtml).toLowerCase();
        const locName = job.locationName ?? job.location?.name ?? '';
        const isRemote = job.isRemote ?? job.remote ?? /remote/i.test(locName);
        const compRange = job.compensation ?? job.salaryRange ?? null;
        return {
          title,
          company: capitalize(orgName),
          companySlug,
          description: descText,
          location: locName,
          isRemote,
          compMin: compRange?.minValue ?? compRange?.min ?? null,
          compMax: compRange?.maxValue ?? compRange?.max ?? null,
        };
      }
    } catch { /* fall through */ }
  }

  // Fall back to meta/title tags
  const ogTitle = html.match(/<meta[^>]+property="og:title"[^>]+content="([^"]+)"/i)?.[1]
    ?? html.match(/<meta[^>]+content="([^"]+)"[^>]+property="og:title"/i)?.[1];
  const titleTag = html.match(/<title[^>]*>([^<]+)<\/title>/i)?.[1];
  const rawTitle = ogTitle ?? titleTag ?? 'Unknown Role';

  // Ashby og:title is usually "Role Title | Company"
  let title = rawTitle;
  let company = capitalize(companySlug);
  const pipeIdx = rawTitle.lastIndexOf(' | ');
  if (pipeIdx !== -1) {
    title = rawTitle.slice(0, pipeIdx).trim();
    company = rawTitle.slice(pipeIdx + 3).trim() || company;
  }

  // Strip HTML and grab body text for description
  const bodyText = stripHtml(html).toLowerCase().slice(0, 8000);
  const isRemote = /\bremote\b/i.test(bodyText.slice(0, 2000));

  return { title, company, companySlug, description: bodyText, location: '', isRemote, compMin: null, compMax: null };
}

function stripHtml(html) {
  return html.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
}

function capitalize(s) {
  if (!s) return s;
  return s.charAt(0).toUpperCase() + s.slice(1);
}

// ── Scoring engine ────────────────────────────────────────────────────────────
// Each dimension returns a score 1–5. Final = weighted sum (max 5).

const WEIGHTS = {
  archetypeFit:     0.20,
  cvKeywordMatch:   0.15,
  seniorityAlign:   0.15,
  compFit:          0.10,
  remoteFit:        0.10,
  companyQuality:   0.10,
  industryFit:      0.05,
  techStackOverlap: 0.10,
  growthPotential:  0.03,
  interviewDiff:    0.02,
};

// Known company tiers for AI/tech companies
const COMPANY_TIERS = {
  openai: 5, anthropic: 5, google: 5, deepmind: 5, meta: 5, microsoft: 5,
  cohere: 4, perplexity: 4, mistral: 4, xai: 4, databricks: 4, snowflake: 4,
  stripe: 4, notion: 4, figma: 4, ramp: 4, linear: 4, vercel: 4,
  amazon: 4, apple: 4, netflix: 4,
};

const INTERVIEW_DIFFICULTY = {
  openai: 1, anthropic: 1, google: 1, meta: 1, deepmind: 1,
  microsoft: 2, amazon: 2, apple: 2,
  cohere: 3, perplexity: 3, databricks: 3, snowflake: 3, stripe: 3,
  notion: 3, figma: 3, ramp: 3, linear: 3, vercel: 3,
};

// Role keywords that map to the candidate's archetypes
const ARCHETYPE_KEYWORDS = {
  ai_engineer:   ['ai engineer', 'artificial intelligence engineer', 'ai/ml engineer', 'ml engineer', 'machine learning engineer'],
  data_engineer: ['data engineer', 'data platform', 'etl', 'data pipeline', 'analytics engineer'],
  ml_engineer:   ['machine learning', 'ml platform', 'model training', 'inference', 'mlops', 'deep learning'],
  ai_architect:  ['ai architect', 'solutions architect', 'ai solutions', 'platform architect'],
  fullstack_ai:  ['full stack', 'fullstack', 'full-stack', 'ai developer', 'ai software engineer'],
};

// All tech keywords from profile skills (lower-cased for matching)
const PROFILE_SKILLS = [
  'python', 'node.js', 'nodejs', 'typescript', 'sql', 'claude api', 'openai api', 'openai',
  'multi-agent', 'multiagent', 'supabase', 'postgresql', 'postgres', 'gcp', 'google cloud',
  'github actions', 'machine learning', 'xgboost', 'scikit-learn', 'sklearn', 'fastapi',
  'docker', 'playwright', 'rest api', 'rest apis', 'fastapi', 'langchain', 'llm', 'llms',
  'rag', 'vector', 'embedding', 'transformer', 'pytorch', 'tensorflow', 'hugging face',
  'bigquery', 'railway', 'vercel', 'react', 'next.js', 'nextjs',
];

function scoreArchetypeFit(title, description) {
  const t = title.toLowerCase();
  const combined = `${t} ${description.slice(0, 1000)}`;
  for (const kws of Object.values(ARCHETYPE_KEYWORDS)) {
    if (kws.some(kw => combined.includes(kw))) return 5;
  }
  if (/software engineer|swe|engineer/i.test(t)) return 3;
  return 2;
}

function scoreCvKeywordMatch(description, cvText) {
  if (!description) return 3;
  const hits = PROFILE_SKILLS.filter(sk => description.includes(sk) || cvText.includes(sk));
  return Math.min(5, Math.round((hits.length / PROFILE_SKILLS.length) * 10));
}

function scoreSeniorityAlign(title, description) {
  const t = `${title} ${description.slice(0, 500)}`.toLowerCase();
  if (/\b(staff|principal|distinguished|vp|director|manager)\b/.test(t)) return 3; // stretch up
  if (/\b(senior|sr\.|lead|iii|iv)\b/.test(t)) return 5;
  if (/\b(mid|ii|intermediate)\b/.test(t) || !/\b(junior|entry|i\b|new grad)\b/.test(t)) return 4;
  return 2; // junior/entry = stretch down
}

function scoreCompFit(compMin, compMax, salMin, salMax) {
  if (!compMin && !compMax) return 3; // no data, neutral
  const midComp = compMin && compMax ? (compMin + compMax) / 2 : (compMin || compMax);
  const midTarget = (salMin + salMax) / 2;
  if (midComp >= salMin && midComp <= salMax) return 5;
  if (midComp > salMax) return 4;         // above range = good
  if (midComp >= salMin * 0.85) return 3; // slightly below
  return 2;
}

function scoreRemoteFit(isRemote, location, prefRemote) {
  const loc = (location || '').toLowerCase();
  const wantsHybrid = prefRemote === 'hybrid';
  const wantsRemote = prefRemote === 'remote' || prefRemote === 'preferred';
  if (isRemote) return wantsRemote ? 5 : 4;
  if (/hybrid/.test(loc)) return wantsHybrid ? 5 : 4;
  if (/seattle|bellevue|redmond|bothell|kirkland/.test(loc)) return 4;
  if (/remote/.test(loc)) return 5;
  if (!loc) return 3; // not specified
  return 2; // in-office elsewhere
}

function scoreCompanyQuality(companySlug) {
  return COMPANY_TIERS[companySlug.toLowerCase()] ?? 3;
}

function scoreIndustryFit(title, description) {
  const combined = `${title} ${description.slice(0, 2000)}`.toLowerCase();
  if (/\b(ai|machine learning|llm|gpt|generative|nlp|deep learning|neural)\b/.test(combined)) return 5;
  if (/\b(data|analytics|platform|infra|cloud|devtools)\b/.test(combined)) return 4;
  if (/\b(fintech|saas|b2b|developer)\b/.test(combined)) return 4;
  return 3;
}

function scoreTechStackOverlap(description) {
  if (!description) return 3;
  const hit = PROFILE_SKILLS.filter(sk => description.includes(sk)).length;
  // Normalize: 8+ hits = 5, 0 = 1
  return Math.max(1, Math.min(5, Math.round(hit / 2) + 1));
}

function scoreGrowthPotential(companySlug) {
  const tier = COMPANY_TIERS[companySlug.toLowerCase()] ?? 3;
  // Tier-5 companies = cutting-edge, great growth signal
  if (tier === 5) return 5;
  if (tier === 4) return 4;
  return 3;
}

function scoreInterviewDifficulty(companySlug) {
  // Higher score = more achievable / appropriate difficulty
  const diff = INTERVIEW_DIFFICULTY[companySlug.toLowerCase()] ?? 3;
  // Flip: difficulty 1 (very hard) → score 2 (tough but doable for strong candidate)
  //       difficulty 5 (easy) → score 4 (good fit)
  return { 1: 2, 2: 3, 3: 4, 4: 4, 5: 4 }[diff] ?? 3;
}

function scoreJob(job, profile, cvText) {
  const salMin = profile?.salary_range?.min ?? 120000;
  const salMax = profile?.salary_range?.max ?? 180000;
  const prefRemote = profile?.preferences?.remote ?? 'hybrid';

  const scores = {
    archetypeFit:     scoreArchetypeFit(job.title, job.description),
    cvKeywordMatch:   scoreCvKeywordMatch(job.description, cvText),
    seniorityAlign:   scoreSeniorityAlign(job.title, job.description),
    compFit:          scoreCompFit(job.compMin, job.compMax, salMin, salMax),
    remoteFit:        scoreRemoteFit(job.isRemote, job.location, prefRemote),
    companyQuality:   scoreCompanyQuality(job.companySlug),
    industryFit:      scoreIndustryFit(job.title, job.description),
    techStackOverlap: scoreTechStackOverlap(job.description),
    growthPotential:  scoreGrowthPotential(job.companySlug),
    interviewDiff:    scoreInterviewDifficulty(job.companySlug),
  };

  const weighted = Object.entries(WEIGHTS).reduce((sum, [k, w]) => sum + (scores[k] ?? 3) * w, 0);
  const total = Math.round(weighted * 10) / 10;
  return { scores, total };
}

function gradeFromScore(score) {
  if (score >= 4.5) return 'A+';
  if (score >= 4.0) return 'A';
  if (score >= 3.5) return 'B+';
  if (score >= 3.0) return 'B';
  if (score >= 2.5) return 'C+';
  if (score >= 2.0) return 'C';
  if (score >= 1.5) return 'D';
  return 'F';
}

function recommendation(grade) {
  if (grade === 'A+' || grade === 'A') return 'Apply Now';
  if (grade === 'B+' || grade === 'B') return 'Apply with Prep';
  if (grade === 'C+' || grade === 'C') return 'Consider if pipeline thin';
  return 'Skip';
}

// ── Slug helpers ──────────────────────────────────────────────────────────────
function toSlug(s) {
  return s.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
}

function reportFilename(companySlug, title) {
  return `${companySlug}-${toSlug(title)}-${TODAY}.md`;
}

// ── Report generator ──────────────────────────────────────────────────────────
function buildReport(job, scoreResult, url) {
  const { scores, total } = scoreResult;
  const grade = gradeFromScore(total);
  const rec = recommendation(grade);

  const dimTable = [
    ['Role–Archetype Fit',       '20%', scores.archetypeFit],
    ['CV–JD Keyword Match',      '15%', scores.cvKeywordMatch],
    ['Seniority Alignment',      '15%', scores.seniorityAlign],
    ['Compensation Fit',         '10%', scores.compFit],
    ['Remote/Location Fit',      '10%', scores.remoteFit],
    ['Company Quality Signal',   '10%', scores.companyQuality],
    ['Industry Fit',              '5%', scores.industryFit],
    ['Tech Stack Overlap',       '10%', scores.techStackOverlap],
    ['Growth Potential',          '3%', scores.growthPotential],
    ['Interview Difficulty Est',  '2%', scores.interviewDiff],
  ];

  const tableRows = dimTable.map(([dim, wt, sc]) => {
    const wtNum = parseFloat(wt) / 100;
    return `| ${dim.padEnd(28)} | ${wt.padStart(4)} | ${sc}/5 | ${(sc * wtNum).toFixed(2)} |`;
  }).join('\n');

  return `# ${job.company} — ${job.title}
**Date:** ${TODAY}
**URL:** ${url}
**Grade:** ${grade}
**Score:** ${total}/5
**Recommendation:** ${rec}

---

## Score Breakdown

| Dimension                     | Weight | Score | Weighted |
|-------------------------------|--------|-------|---------|
${tableRows}
| **TOTAL**                     | 100%   |       | **${total}/5** |

**Grade:** ${grade}
**Recommendation:** ${rec}

---

## Notes

- Company: ${job.company} (${job.companySlug})
- Location: ${job.location || 'Not specified'}
- Remote: ${job.isRemote ? 'Yes' : 'Not indicated'}
- Compensation: ${job.compMin && job.compMax ? `$${job.compMin.toLocaleString()}–$${job.compMax.toLocaleString()}` : 'Not disclosed'}
${job.error ? `\n⚠️  Fetch error: ${job.error}` : ''}
`;
}

// ── Main ──────────────────────────────────────────────────────────────────────
async function main() {
  const pipelinePath = resolve(__dirname, 'data/pipeline.md');
  if (!existsSync(pipelinePath)) {
    console.error('❌  data/pipeline.md not found.');
    process.exit(1);
  }

  const urls = readFileSync(pipelinePath, 'utf-8')
    .split('\n')
    .map(l => l.trim().replace(/^[-*] /, ''))
    .filter(l => l && !l.startsWith('#') && /^https?:\/\//.test(l));

  const subset = urls.slice(0, LIMIT);
  const total = subset.length;

  console.log(`\nCareer-Ops Pipeline Auto-Evaluator`);
  console.log(`═`.repeat(42));
  console.log(`Evaluating ${total} job(s) — ${TODAY}\n`);

  const profile = loadProfile();
  const cvText = loadCV();

  const gradeRows = [];

  for (let i = 0; i < total; i++) {
    const url = subset[i];

    // Skip if report already exists for today
    const urlMatch = url.match(/jobs\.ashbyhq\.com\/([^/]+)\//);
    const previewSlug = urlMatch ? urlMatch[1] : 'unknown';
    const existing = existsSync(resolve(reportsDir, `${previewSlug}`));
    // More precise: check if any report for this URL exists today
    // (we'll check properly after we get the title)

    process.stdout.write(`  [${i + 1}/${total}] Fetching ${previewSlug}... `);

    const job = await fetchJob(url);
    const reportFile = reportFilename(job.companySlug, job.title);
    const reportPath = resolve(reportsDir, reportFile);

    if (existsSync(reportPath)) {
      console.log(`(skipped — report exists)`);
      // Still add to grades if we can read it
      const scoreResult = scoreJob(job, profile, cvText);
      gradeRows.push({ url, company: job.company, title: job.title, ...scoreResult, reportFile });
      continue;
    }

    const scoreResult = scoreJob(job, profile, cvText);
    const grade = gradeFromScore(scoreResult.total);

    // Save report for all grades
    const report = buildReport(job, scoreResult, url);
    writeFileSync(reportPath, report, 'utf-8');

    console.log(`${job.company} — ${job.title} → ${grade} (${scoreResult.total})`);

    gradeRows.push({ url, company: job.company, title: job.title, grade, score: scoreResult.total, reportFile });
  }

  // Write data/grades.tsv
  const tsvHeader = 'url\tcompany\ttitle\tgrade\tscore\tevaluated_at';
  const tsvRows = gradeRows.map(r =>
    `${r.url}\t${r.company}\t${r.title}\t${r.grade ?? gradeFromScore(r.total)}\t${r.score ?? r.total}\t${TODAY}`
  );
  const tsvPath = resolve(dataDir, 'grades.tsv');
  writeFileSync(tsvPath, [tsvHeader, ...tsvRows].join('\n') + '\n', 'utf-8');

  // Summary
  console.log(`\n${'─'.repeat(42)}`);
  console.log(`Evaluated: ${total} jobs`);
  console.log(`Reports saved to: reports/`);
  console.log(`Grades written to: data/grades.tsv\n`);

  // Priority table
  const sorted = [...gradeRows].sort((a, b) => (b.score ?? b.total) - (a.score ?? a.total));
  console.log('Priority Ranking:');
  console.log('─'.repeat(62));
  console.log(`${'#'.padEnd(4)}${'Company'.padEnd(16)}${'Role'.padEnd(32)}${'Grade'.padEnd(6)}Score`);
  console.log('─'.repeat(62));
  sorted.forEach((r, idx) => {
    const sc = r.score ?? r.total;
    const gr = r.grade ?? gradeFromScore(sc);
    const co = (r.company ?? '').slice(0, 14).padEnd(16);
    const ti = (r.title ?? '').slice(0, 30).padEnd(32);
    console.log(`${String(idx + 1).padEnd(4)}${co}${ti}${gr.padEnd(6)}${sc}`);
  });
  console.log('');
}

main().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
