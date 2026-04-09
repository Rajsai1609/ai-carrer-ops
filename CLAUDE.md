# Career-Ops — Claude Code Agent Instructions

**Version:** 1.0.0  
**Stack:** Node.js (ESM), Go 1.21+, Playwright 1.58.1, Bubble Tea TUI  
**Purpose:** Job search operating system — evaluate offers, generate CVs, track pipeline, run research

---

## Quick Start

```bash
# 1. Install dependencies
npm install
npx playwright install chromium

# 2. Set up your profile
cp config/profile.example.yml config/profile.yml
# Edit config/profile.yml with your details

# 3. Create your CV
cp examples/cv-example.md cv.md
# Edit cv.md with your actual experience

# 4. Run doctor check
node doctor.mjs

# 5. Start using career-ops
# Paste a job URL and ask Claude to run /career-ops oferta [URL]
```

---

## Available Commands

### Evaluate a Job

```
/career-ops oferta [URL]
```

Paste a job posting URL. Claude will:
1. Fetch and parse the job description
2. Compare against your `cv.md` and `config/profile.yml`
3. Score across 10 dimensions → letter grade (A+ to F)
4. Generate personalization plan, level strategy, comp research, STAR stories
5. Save report to `reports/` and suggest PDF generation

### Compare Multiple Offers

```
/career-ops ofertas [URL1] [URL2] [URL3...]
```

Side-by-side comparison. Outputs ranked priority table.

### Generate CV PDF

```
node generate-pdf.mjs --company [Name]
node generate-pdf.mjs --company [Name] --jd-file jds/[company-slug].txt
```

Or via mode:
```
/career-ops pdf --company [Name]
```

### View Pipeline Status

```
/career-ops tracker
```

Reads `data/applications.md` and renders pipeline summary.

### Scan Job Portals

```
/career-ops scan
```

Uses Playwright to scrape portals in `config/portals.yml` for new postings matching your target roles.

### Process Multiple JDs (Batch)

```bash
# Create a file with one URL per line
echo "https://company.com/job1" > urls.txt
echo "https://company.com/job2" >> urls.txt

# Run batch processor
bash batch/batch-runner.sh urls.txt --workers 3
```

### Evaluate All Pipeline URLs

```
/career-ops pipeline
```

Reads `data/pipeline.md` (one URL per line) and evaluates each sequentially.

### Apply to a Job

```
/career-ops apply [URL]
```

Generates pre-filled form values + cover letter from `config/profile.yml`.

### LinkedIn Outreach

```
/career-ops contacto [Company] [Person Name (optional)]
```

Generates connection request, follow-up messages, and referral request templates.

### Company Research

```
/career-ops deep [Company Name]
```

Full intelligence report: funding, culture, tech stack, recent news.

### Analyze Rejection Patterns

```
/career-ops patterns
```

Runs `analyze-patterns.mjs` with AI interpretation of results.

### Evaluate Training ROI

```
/career-ops training [Course/Cert Name or URL]
```

### Evaluate Portfolio Project

```
/career-ops project [Project Name or GitHub URL]
```

### Master Mode (Interactive Menu)

```
/career-ops
```

Shows interactive menu and routes to the right mode.

---

## Setup Details

### Required Files (create these)

| File | How to Create |
|------|---------------|
| `cv.md` | Copy `examples/cv-example.md`, fill in your experience |
| `config/profile.yml` | Copy `config/profile.example.yml`, fill in your details |

### Optional Files

| File | Purpose |
|------|---------|
| `config/portals.yml` | Copy `templates/portals.example.yml`, add target companies |
| `data/pipeline.md` | List of JD URLs to evaluate in batch |

### Files Created Automatically

| File | Created By |
|------|-----------|
| `data/applications.md` | `merge-tracker.mjs` |
| `data/scan-history.tsv` | scan mode |
| `reports/*.md` | oferta mode |
| `output/*.pdf` | `generate-pdf.mjs` |
| `jds/*.txt` | oferta mode (JD cache) |

---

## Scoring Rubric

### 10 Evaluation Dimensions

| # | Dimension | Weight | What It Measures |
|---|-----------|--------|-----------------|
| 1 | Role–Archetype Fit | 20% | Does role match your `archetypes` in profile? |
| 2 | CV–JD Keyword Match | 15% | % of JD requirements found in cv.md |
| 3 | Seniority Alignment | 15% | Level match (Junior/Mid/Senior/Staff) |
| 4 | Compensation Fit | 10% | JD comp vs `salary_range` in profile |
| 5 | Remote/Location Fit | 10% | JD remote policy vs `preferences.remote` |
| 6 | Company Quality Signal | 10% | Funding, stability, reputation |
| 7 | Industry Fit | 5% | JD domain vs `preferences.industries` |
| 8 | Tech Stack Overlap | 10% | JD tech vs `skills` in profile |
| 9 | Growth Potential | 3% | Long-term career trajectory signal |
| 10 | Interview Difficulty | 2% | Realistic difficulty estimate |

### Grade Scale

| Score | Grade | Action |
|-------|-------|--------|
| ≥ 4.5 | A+ | Apply immediately, top priority |
| ≥ 4.0 | A  | Apply now |
| ≥ 3.5 | B+ | Apply with targeted CV customization |
| ≥ 3.0 | B  | Apply this week |
| ≥ 2.5 | C+ | Apply if pipeline is thin |
| ≥ 2.0 | C  | Consider only if desperate |
| ≥ 1.5 | D  | Significant mismatch |
| < 1.5 | F  | Skip |

---

## Customization Guide

### Adjusting Scoring Weights

The default weights in `modes/_shared.md` can be overridden per-profile.
Add a `scoring_overrides` section to `config/profile.yml`:

```yaml
scoring_overrides:
  compensation_weight: 0.20   # increase from 10% to 20% if comp is critical
  remote_weight: 0.15         # increase if remote is non-negotiable
  archetype_weight: 0.15      # decrease if open to role stretching
```

### Adding Company Portals

Edit `config/portals.yml` (copy from `templates/portals.example.yml`):

```yaml
- company: YourTargetCompany
  url: "https://company.com/careers"
  selector: ".job-listing"
  title_selector: "h3"
  pagination: none
```

### Localization

Use German, French, or Portuguese modes:

```
/career-ops de/angebot [URL]    # German evaluation
/career-ops fr/offre [URL]      # French evaluation
/career-ops pt/oferta [URL]     # Portuguese evaluation
```

---

## Data Contract (Summary)

**System layer** (don't edit): `modes/`, `templates/`, `*.mjs`, `batch/`, `dashboard/`  
**User layer** (yours): `config/`, `data/`, `cv.md`, `reports/`, `output/`, `jds/`

See `DATA_CONTRACT.md` for full details.

---

## Go Dashboard

The TUI dashboard requires Go 1.21+:

```bash
# Install Go: https://golang.org/dl/

cd dashboard
go mod tidy
go build ./
./dashboard
# or on Windows:
# dashboard.exe
```

Set environment variable if needed:
```bash
export CAREER_OPS_ROOT=/path/to/career-ops
```

---

## Troubleshooting

### doctor.mjs fails
```bash
node doctor.mjs
```
Follow the ❌ items. Most common issues:
- `cv.md` not created → copy from `examples/cv-example.md`
- `config/profile.yml` not created → copy from `config/profile.example.yml`
- Playwright chromium not installed → `npx playwright install chromium`

### PDF generation fails
- Check `templates/cv-template.html` exists
- Check `output/` directory exists (created automatically)
- Check Playwright chromium is installed: `npx playwright install chromium`

### Go dashboard fails to compile
- Requires Go 1.21+: `go version`
- Run `go mod tidy` inside `dashboard/`
- Check `CAREER_OPS_ROOT` env var points to project root

### Tracker shows no data
- Check `data/applications.md` exists
- Run `node merge-tracker.mjs` after adding TSV files to `batch/tracker-additions/`
- Or create `data/applications.md` manually with the header format

### Batch runner fails
- Check `claude` CLI is installed and authenticated
- Verify URLs in input file are accessible
- Check `batch/logs/` for per-worker error logs

---

## File Structure Reference

```
career-ops/
├── CLAUDE.md               ← You are here
├── DATA_CONTRACT.md        ← System vs. user layer
├── VERSION                 ← 1.0.0
├── package.json
├── .gitignore
│
├── config/
│   ├── profile.example.yml ← Copy → profile.yml
│   └── portals.yml         ← (copy from templates/)
│
├── cv.md                   ← YOUR CV (create this)
│
├── modes/                  ← Agent instruction files
│   ├── _shared.md
│   ├── oferta.md           ← Single job eval (MOST USED)
│   ├── ofertas.md
│   ├── pdf.md
│   ├── scan.md
│   ├── batch.md
│   ├── tracker.md
│   ├── apply.md
│   ├── pipeline.md
│   ├── contacto.md
│   ├── deep.md
│   ├── training.md
│   ├── project.md
│   ├── patterns.md
│   ├── auto-pipeline.md
│   ├── de/                 ← German localization
│   ├── fr/                 ← French localization
│   └── pt/                 ← Portuguese localization
│
├── templates/
│   ├── cv-template.html    ← ATS-optimized HTML CV
│   ├── states.yml          ← Canonical pipeline statuses
│   └── portals.example.yml ← 45+ company portal registry
│
├── batch/
│   ├── batch-runner.sh     ← Parallel batch processor
│   ├── batch-prompt.md     ← Machine-readable eval prompt
│   ├── logs/               ← (gitignored)
│   └── tracker-additions/  ← (gitignored)
│
├── dashboard/              ← Go TUI dashboard
│   ├── main.go
│   ├── go.mod
│   └── internal/
│       ├── data/career.go
│       ├── model/career.go
│       ├── theme/
│       └── ui/screens/
│
├── *.mjs                   ← Node.js utility scripts
│   ├── generate-pdf.mjs
│   ├── merge-tracker.mjs
│   ├── verify-pipeline.mjs
│   ├── normalize-statuses.mjs
│   ├── dedup-tracker.mjs
│   ├── doctor.mjs
│   └── analyze-patterns.mjs
│
├── data/                   ← (gitignored) YOUR APPLICATION DATA
├── reports/                ← (gitignored) YOUR EVALUATION REPORTS
├── output/                 ← (gitignored) YOUR GENERATED PDFs
├── jds/                    ← (gitignored) CACHED JOB DESCRIPTIONS
│
├── examples/
│   ├── cv-example.md
│   └── sample-report.md
│
└── interview-prep/
    └── story-bank.md
```

---

## Agent Behavior Notes

When Claude Code executes career-ops modes:

1. **Always load context first:** `config/profile.yml` + `cv.md` before any evaluation
2. **Never guess profile data:** If profile.yml is missing a field, ask the user rather than assuming
3. **Save reports automatically** for grades B+ and above
4. **Suggest PDF generation** after any successful evaluation
5. **Keep tracker updated** — always output TSV rows at end of evaluation
6. **Respect the data contract** — never write to `modes/` or `templates/` during normal operation
7. **Use web search** for comp research (section D) and company research (deep mode)
8. **Flag visa issues** if `needs_sponsorship: true` and company is known non-sponsor

---

*Career-Ops v1.0.0 — Built with Claude Code*
