# Career-Ops: pipeline — Sequential Pipeline Evaluation Mode

**Purpose:** Read a list of JD URLs from `data/pipeline.md` and evaluate each one sequentially.  
**Input:** `data/pipeline.md` (one URL per line, markdown list)  
**Output:** Individual reports + consolidated priority ranking

---

## Pre-flight

Load `config/profile.yml`, `cv.md`.

Check for `data/pipeline.md`. If not found, prompt user to create it:
```
# Job Pipeline

- https://company.com/careers/job-id-1
- https://company.com/careers/job-id-2
```

---

## Process

For each URL in `data/pipeline.md`:
1. Skip blank lines and comments (`#`)
2. Run abbreviated `oferta` evaluation (Sections A, B, C, score)
3. Save individual report to `reports/`
4. Append TSV row to `batch/tracker-additions/pipeline-{date}.tsv`

---

## Consolidated Output

After processing all URLs:

### Priority Ranking

| Rank | Company | Role | Grade | Score | Key Reason |
|------|---------|------|-------|-------|------------|

### Action Plan

**Apply today (A+/A):**
- [list]

**Apply this week with prep (B+/B):**
- [list]

**Hold / deprioritize (C or below):**
- [list]

---

## Auto-Actions

After evaluation:
1. Run `node merge-tracker.mjs` to add all rows to tracker
2. Suggest generating PDFs for top-ranked roles
3. Archive `data/pipeline.md` entries that have been evaluated (move to `data/pipeline-archive.md`)
