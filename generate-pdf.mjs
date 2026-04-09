#!/usr/bin/env node
/**
 * generate-pdf.mjs
 * Generates an ATS-optimized PDF CV using Playwright + chromium.
 *
 * Usage:
 *   node generate-pdf.mjs --company <name> [--jd-file <path>] [--template <path>]
 *   node generate-pdf.mjs --help
 */

import { chromium } from 'playwright';
import { readFileSync, existsSync, mkdirSync } from 'fs';
import { resolve, dirname, basename } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

// ── Argument parsing ────────────────────────────────────────────────────────
function parseArgs(args) {
  const parsed = {
    company: null,
    jdFile: null,
    template: resolve(__dirname, 'templates/cv-template.html'),
    cvFile: resolve(__dirname, 'cv.md'),
    outputDir: resolve(__dirname, 'output'),
    help: false,
  };

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--help':
      case '-h':
        parsed.help = true;
        break;
      case '--company':
        parsed.company = args[++i];
        break;
      case '--jd-file':
        parsed.jdFile = args[++i];
        break;
      case '--template':
        parsed.template = args[++i];
        break;
      case '--cv':
        parsed.cvFile = args[++i];
        break;
      case '--output-dir':
        parsed.outputDir = args[++i];
        break;
    }
  }

  return parsed;
}

function printHelp() {
  console.log(`
career-ops: generate-pdf.mjs
Generates an ATS-optimized PDF CV tailored to a specific job description.

Usage:
  node generate-pdf.mjs --company <name> [options]

Options:
  --company <name>       Target company name (required for output filename)
  --jd-file <path>       Path to job description text file (for keyword injection)
  --template <path>      Path to HTML CV template (default: templates/cv-template.html)
  --cv <path>            Path to cv.md source file (default: ./cv.md)
  --output-dir <path>    Output directory (default: ./output)
  --help                 Show this help message

Output:
  output/cv-<candidate>-<company>-<YYYY-MM-DD>.pdf

Examples:
  node generate-pdf.mjs --company Stripe
  node generate-pdf.mjs --company Anthropic --jd-file jds/anthropic-swe.txt
`);
}

// ── JD keyword extraction ───────────────────────────────────────────────────
function extractKeywords(jdText) {
  if (!jdText) return [];

  // Common tech keywords pattern
  const techTerms = [
    /\b(Python|Go|Golang|TypeScript|JavaScript|Java|Rust|C\+\+|Scala|Kotlin)\b/gi,
    /\b(React|Next\.js|Vue|Angular|Node\.js|FastAPI|Django|Flask|Spring)\b/gi,
    /\b(AWS|GCP|Azure|Kubernetes|Docker|Terraform|CI\/CD|GitOps)\b/gi,
    /\b(PostgreSQL|MySQL|Redis|Cassandra|MongoDB|Elasticsearch|BigQuery)\b/gi,
    /\b(gRPC|REST|GraphQL|Kafka|RabbitMQ|SQS|SNS|Pub\/Sub)\b/gi,
    /\b(microservices|distributed systems?|high.availability|scalability|observability)\b/gi,
    /\b(ML|machine learning|deep learning|LLM|RAG|embeddings|vector)\b/gi,
  ];

  const found = new Set();
  for (const pattern of techTerms) {
    const matches = jdText.match(pattern) || [];
    for (const m of matches) {
      found.add(m.toLowerCase());
    }
  }
  return [...found];
}

// ── CV markdown → template fields ──────────────────────────────────────────
function loadCvFields(cvPath) {
  if (!existsSync(cvPath)) {
    console.warn(`Warning: cv.md not found at ${cvPath}. Using placeholder values.`);
    return {};
  }
  // cv.md is used as-is; the HTML template fields are already set for real usage.
  // In production, cv.md would be parsed section by section.
  // Here we just flag that the file exists.
  return { CV_LOADED: true };
}

// ── Slug helper ─────────────────────────────────────────────────────────────
function slugify(str) {
  return str.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
}

// ── Main ────────────────────────────────────────────────────────────────────
async function main() {
  const args = parseArgs(process.argv.slice(2));

  if (args.help) {
    printHelp();
    process.exit(0);
  }

  if (!args.company) {
    console.error('Error: --company is required. Run with --help for usage.');
    process.exit(1);
  }

  // Validate template exists
  if (!existsSync(args.template)) {
    console.error(`Error: template not found at ${args.template}`);
    process.exit(1);
  }

  // Ensure output directory exists
  if (!existsSync(args.outputDir)) {
    mkdirSync(args.outputDir, { recursive: true });
  }

  // Load JD keywords if provided
  let keywords = [];
  if (args.jdFile) {
    if (!existsSync(args.jdFile)) {
      console.error(`Error: JD file not found at ${args.jdFile}`);
      process.exit(1);
    }
    const jdText = readFileSync(args.jdFile, 'utf-8');
    keywords = extractKeywords(jdText);
    console.log(`Extracted ${keywords.length} ATS keywords from JD`);
  }

  loadCvFields(args.cvFile);

  // Load HTML template
  let html = readFileSync(args.template, 'utf-8');

  // Inject ATS keywords (invisible to human, visible to ATS parsers)
  html = html.replace('{{ATS_KEYWORDS}}', keywords.join(' '));

  // Build output filename
  const dateStr = new Date().toISOString().slice(0, 10);
  const candidateSlug = 'candidate'; // Replace with profile name from config/profile.yml
  const companySlug = slugify(args.company);
  const outputPath = resolve(args.outputDir, `cv-${candidateSlug}-${companySlug}-${dateStr}.pdf`);

  console.log(`Launching Playwright chromium...`);

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  // Load HTML directly as content
  await page.setContent(html, { waitUntil: 'networkidle' });

  // Wait for Google Fonts to load (if network available), or skip gracefully
  try {
    await page.waitForTimeout(1500);
  } catch {
    // ignore
  }

  // Generate PDF
  await page.pdf({
    path: outputPath,
    format: 'A4',
    printBackground: true,
    margin: {
      top: '10mm',
      right: '10mm',
      bottom: '10mm',
      left: '10mm',
    },
  });

  await browser.close();

  console.log(`✅ PDF generated: ${outputPath}`);
  if (keywords.length > 0) {
    console.log(`   ATS keywords injected: ${keywords.slice(0, 10).join(', ')}${keywords.length > 10 ? '...' : ''}`);
  }
}

main().catch((err) => {
  console.error('Fatal error:', err.message);
  process.exit(1);
});
