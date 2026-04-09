# Career-Ops Batch Prompt — Machine-Readable Evaluation

**MODE:** batch  
**OUTPUT:** TSV row ONLY. No markdown, no explanations, no headers.

---

## Instructions

You are processing a job posting URL as part of a batch evaluation pipeline.

1. Load `config/profile.yml` for scoring context
2. Load `cv.md` for skills comparison
3. Fetch the job posting at the provided URL
4. Evaluate using the 5 compressed scoring dimensions below
5. Output EXACTLY ONE TSV row — nothing else

---

## Compressed Scoring (5 dimensions for batch mode)

| # | Dimension | Weight |
|---|-----------|--------|
| 1 | Role–Archetype Fit | 30% |
| 2 | CV–JD Keyword Match | 25% |
| 3 | Seniority Alignment | 20% |
| 4 | Compensation Fit | 15% |
| 5 | Remote/Location Fit | 10% |

Score each 1–5. Compute weighted average. Map to letter grade (see shared rules).

---

## Output Format

Output EXACTLY this TSV row (tab-separated, no header):

```
{YYYY-MM-DD}\t{Company}\t{Role Title}\t{score}\tPipeline\t-\t-\t{one-sentence note}
```

Where:
- `{YYYY-MM-DD}` = today's date
- `{Company}` = company name from job posting
- `{Role Title}` = exact role title from posting
- `{score}` = weighted score as decimal e.g. `3.8`
- `{one-sentence note}` = top reason for score (e.g. "Strong archetype fit, weak on Rust requirement")

**Example output:**
```
2025-04-08	Stripe	Senior Software Engineer	3.9	Pipeline	-	-	Strong backend fit, requires Rust experience not in CV
```

---

## CRITICAL RULES

- Output ONLY the TSV row
- NO markdown formatting
- NO explanations before or after
- NO extra lines
- If the URL cannot be fetched, output: `{date}\tERROR\t{url}\t0\tFailed\t-\t-\tURL fetch failed`
