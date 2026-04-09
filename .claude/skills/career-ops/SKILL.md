# Career-Ops Skill

**Skill name:** career-ops  
**Version:** 1.0.0  
**Description:** Job search operations system — evaluate offers, generate PDFs, track pipeline, run research.

---

## How to Invoke Career-Ops Modes

Career-Ops operates through mode files in `modes/`. Each mode is a standalone instruction set for Claude.
When a user invokes a mode, load the corresponding file and execute it against the provided inputs.

### Invocation Pattern

```
/career-ops <mode> [arguments]
```

Auto-routing (no mode specified):
```
/career-ops
```
→ Load `modes/auto-pipeline.md` which shows an interactive menu.

---

## Available Modes

| Mode | File | When to Use |
|------|------|-------------|
| `oferta` | `modes/oferta.md` | Evaluate a single job posting (A–F grade + full analysis) |
| `ofertas` | `modes/ofertas.md` | Compare 2–5 job offers side by side |
| `pdf` | `modes/pdf.md` | Generate ATS CV PDF from cv.md + JD |
| `scan` | `modes/scan.md` | Scrape portals for new job postings |
| `batch` | `modes/batch.md` | Process multiple JD URLs in parallel |
| `tracker` | `modes/tracker.md` | Display pipeline status summary |
| `apply` | `modes/apply.md` | Fill application forms with profile data |
| `pipeline` | `modes/pipeline.md` | Evaluate all URLs in pipeline.md sequentially |
| `contacto` | `modes/contacto.md` | Generate LinkedIn messages |
| `deep` | `modes/deep.md` | Full company research |
| `training` | `modes/training.md` | Evaluate course/cert ROI |
| `project` | `modes/project.md` | Evaluate portfolio project fit |
| `patterns` | `modes/patterns.md` | Analyze rejection patterns |
| `auto` | `modes/auto-pipeline.md` | Master mode with menu routing |

---

## Context Loading (CRITICAL)

Before executing any mode, Claude MUST load:

1. **`config/profile.yml`** — Candidate identity, target roles, compensation, archetypes, narrative
2. **`cv.md`** — Full CV content for gap analysis and keyword mapping
3. **Mode-specific shared rules** — `modes/_shared.md`

If `config/profile.yml` doesn't exist, prompt: *"Please copy config/profile.example.yml → config/profile.yml and fill in your details."*

If `cv.md` doesn't exist, prompt: *"Please create cv.md in the project root with your CV content."*

---

## Output Format Rules

### Report Structure (modes/oferta.md and similar)

All evaluation reports MUST follow this structure:

```
# [Company] — [Role Title]
**Date:** YYYY-MM-DD  
**Grade:** [A+/A/B+/B/C+/C/D/F]  
**Score:** [weighted numeric, e.g. 3.8/5]

## A. Role Summary
## B. CV Match Analysis  
## C. Level Strategy
## D. Compensation Research
## E. Personalization Plan
## F. Interview Prep

## Score Breakdown
| Dimension | Weight | Score | Weighted |
|-----------|--------|-------|---------|
...
**Final Score:** X.X/5  **Grade:** X
```

### File Naming Conventions

| Type | Pattern |
|------|---------|
| PDF output | `output/cv-{lastname}-{company-slug}-{YYYY-MM-DD}.pdf` |
| Report | `reports/{company-slug}-{role-slug}-{YYYY-MM-DD}.md` |
| JD file | `jds/{company-slug}.txt` |
| Tracker | `data/applications.md` |

---

## Scoring System

10 dimensions, each scored 1–5, with weights:

| # | Dimension | Weight |
|---|-----------|--------|
| 1 | Role–Archetype Fit | 20% |
| 2 | CV–JD Keyword Match | 15% |
| 3 | Seniority Alignment | 15% |
| 4 | Compensation Fit | 10% |
| 5 | Remote/Location Fit | 10% |
| 6 | Company Quality Signal | 10% |
| 7 | Industry Fit | 5% |
| 8 | Tech Stack Overlap | 10% |
| 9 | Growth Potential | 3% |
| 10 | Interview Difficulty Estimate | 2% |

**Grade thresholds:**

| Score | Grade |
|-------|-------|
| ≥ 4.5 | A+ |
| ≥ 4.0 | A  |
| ≥ 3.5 | B+ |
| ≥ 3.0 | B  |
| ≥ 2.5 | C+ |
| ≥ 2.0 | C  |
| ≥ 1.5 | D  |
| < 1.5 | F  |

---

## Localization

Localized mode files are in:
- `modes/de/` — German (angebot, bewerben, pipeline)
- `modes/fr/` — French (offre, postuler, pipeline)
- `modes/pt/` — Portuguese (oferta, aplicar, pipeline)

Default language: English (`modes/`)
