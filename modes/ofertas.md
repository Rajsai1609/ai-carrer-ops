# Career-Ops: ofertas — Multi-Offer Comparison Mode

**Purpose:** Side-by-side comparison of 2–5 job offers to identify the best strategic choice.  
**Input:** 2–5 job posting URLs or report files  
**Output:** Ranked comparison table + decision recommendation

---

## Pre-flight

Load `config/profile.yml`, `cv.md`, `modes/_shared.md`.

---

## Process

For each offer provided:
1. Run the full `oferta.md` evaluation pipeline (abbreviated — no full report)
2. Extract: Company, Role, Grade, Score breakdown, Comp estimate, Remote, Level, Key pros/cons

---

## Comparison Output

### Summary Table

| | Offer 1 | Offer 2 | Offer 3 | Offer 4 | Offer 5 |
|-|---------|---------|---------|---------|---------|
| Company | | | | | |
| Role | | | | | |
| Level | | | | | |
| Grade | | | | | |
| Score | | | | | |
| Est. Base | | | | | |
| Equity | | | | | |
| Remote | | | | | |
| Archetype Fit | | | | | |
| Tech Stack Fit | | | | | |
| Visa Sponsor | | | | | |
| Upside/Risk | | | | | |

### Dimension-by-Dimension Comparison

For each of the 10 scoring dimensions, show scores side by side in a table.

### Recommendation

**Ranked choice:**
1. [Company A] — [reason in one sentence]
2. [Company B] — [reason in one sentence]
...

**Strategic advice:**
- If offers include both high-comp/low-fit and low-comp/high-fit: [negotiation strategy]
- If multiple offers are similar: [differentiating factors to investigate]
- Visa/sponsorship considerations: [if relevant from profile]

**Decision framework:**
Apply this weighted priority from profile:
1. Archetype fit (most important for long-term career)
2. Compensation vs target range
3. Remote preference
4. Level/growth trajectory
5. Company stability signal
