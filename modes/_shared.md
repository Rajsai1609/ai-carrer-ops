# Career-Ops Shared Rules
# All modes inherit these rules. Do not modify unless updating the system.

---

## 1. Context Loading Protocol

At the start of EVERY mode execution:

1. **Load `config/profile.yml`** — Extract: name, target_roles, salary_range, archetypes, preferences, work_authorization, narrative, skills
2. **Load `cv.md`** — Extract: experience timeline, titles, companies, tech stack, achievements, education
3. **Apply `modes/_shared.md`** — These rules

If either file is missing, STOP and prompt the user to create it.

---

## 2. Scoring System

### 10 Evaluation Dimensions

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

**Total weight: 100%**

### Scoring Scale (per dimension)

| Score | Meaning |
|-------|---------|
| 5 | Perfect match / strong positive signal |
| 4 | Good match with minor gaps |
| 3 | Adequate match, some concerns |
| 2 | Weak match, significant gaps |
| 1 | Poor match or blocking issue |

### Letter Grade Thresholds

| Weighted Score | Grade |
|----------------|-------|
| ≥ 4.5 | A+ |
| ≥ 4.0 | A  |
| ≥ 3.5 | B+ |
| ≥ 3.0 | B  |
| ≥ 2.5 | C+ |
| ≥ 2.0 | C  |
| ≥ 1.5 | D  |
| < 1.5 | F  |

**Recommendation by grade:**
- **A+/A** → Apply immediately, prioritize
- **B+/B** → Apply with targeted CV customization
- **C+/C** → Apply only if pipeline is thin; note gaps
- **D/F** → Skip or archive

---

## 3. Output Format Standards

### Report Header (mandatory)

```markdown
# [Company] — [Role Title]
**Date:** YYYY-MM-DD  
**URL:** [job posting URL]
**Grade:** [letter grade]  
**Score:** [X.X/5]  
**Recommendation:** [Apply Now / Apply with Prep / Hold / Skip]
```

### Tracker Row (TSV format for batch)

```
[#]\t[Date]\t[Company]\t[Role]\t[Score]\t[Status]\t[PDF]\t[Report]\t[Notes]
```

---

## 4. File Naming Conventions

| File Type | Pattern |
|-----------|---------|
| PDF | `output/cv-{lastname}-{company-slug}-{YYYY-MM-DD}.pdf` |
| Report | `reports/{company-slug}-{role-slug}-{YYYY-MM-DD}.md` |
| JD cache | `jds/{company-slug}.txt` |
| Tracker | `data/applications.md` |
| Scan history | `data/scan-history.tsv` |

**Slug rules:** lowercase, hyphens only, no spaces or special chars.

---

## 5. Profile Reading Guide

From `config/profile.yml`, extract:

- **Archetype match:** Compare JD role type against `archetypes` map. Use weighted scoring.
- **Seniority:** Compare JD level signals (years, title) against candidate's current level.
- **Compensation:** Compare JD comp signals against `salary_range.min`/`max`.
- **Remote:** Compare JD remote policy against `preferences.remote`.
- **Tech stack:** Compare JD requirements against `skills.*` lists.
- **Visa:** If `work_authorization.needs_sponsorship: true`, flag companies unlikely to sponsor.

---

## 6. CV Reading Guide

From `cv.md`, extract:

- **Experience timeline:** Start/end dates, companies, titles
- **Tech used per role:** Languages, frameworks, infra mentioned
- **Scale signals:** Team size, traffic, data volume, system complexity
- **Achievement quality:** Look for quantified impact (%, $, x improvement)
- **Gaps:** Missing tech from JD not present in CV

---

## 7. Auto-Actions

After any evaluation producing a grade of B or higher:
1. Suggest generating PDF: `node generate-pdf.mjs --company [name]`
2. Suggest adding to tracker
3. If report file does not exist, offer to save it

---

## 8. Tone & Style

- Direct and analytical — no corporate fluff
- Flag blockers clearly with ❌
- Flag strengths clearly with ✅
- Use tables for structured data
- Keep narrative sections concise (3–5 sentences max per section)
- Always end with a clear `**Recommendation:**` line
