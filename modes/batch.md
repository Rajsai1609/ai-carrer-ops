# Career-Ops: batch — Parallel JD Processing Mode

**Purpose:** Process multiple JD URLs simultaneously using parallel workers.  
**Input:** File of JD URLs (one per line) or inline list  
**Output:** TSV rows in `batch/tracker-additions/`, merged to tracker

---

## Pre-flight

Load `config/profile.yml`, `cv.md`.

---

## Process

1. **Parse input:** Read URL list from file or stdin
2. **Spawn workers:** Use `batch/batch-runner.sh` with configurable parallelism (default: 3)
3. **Each worker runs:** `batch/batch-prompt.md` against one URL
4. **Collect outputs:** TSV rows → `batch/tracker-additions/{timestamp}-batch.tsv`
5. **Auto-merge:** Run `node merge-tracker.mjs` after all workers complete

---

## Worker Invocation

```bash
bash batch/batch-runner.sh urls.txt --workers 3
```

Or for a single URL list inline, Claude processes each sequentially with abbreviated oferta evaluation.

---

## Batch Evaluation (abbreviated oferta)

For each URL:
1. Fetch JD
2. Extract: company, role, level, remote, tech stack
3. Score against profile (compressed — 5 dimensions instead of 10)
4. Output TSV row with: date, company, role, score, status=Pipeline, notes

---

## Output Summary

After batch completes:

```
Batch processed: [N] URLs
  ✅ High priority (A/B): [N]
  ⚠️  Consider (C):       [N]
  ❌ Skip (D/F):          [N]
  
Run 'node merge-tracker.mjs' to add to tracker.
```
