# Career-Ops: patterns — Rejection Pattern Analysis Mode

**Purpose:** Run `analyze-patterns.mjs` and interpret the results with AI-driven recommendations.  
**Input:** `data/applications.md` + `reports/` directory  
**Output:** Pattern insights + actionable strategy adjustments

---

## Pre-flight

Load `config/profile.yml`.

---

## Process

1. Run `node analyze-patterns.mjs` and capture output
2. Read `data/applications.md` for full pipeline context
3. Read recent reports in `reports/` (last 10) for qualitative signals

---

## AI Interpretation Layer

After reading the raw analytics, provide:

### Pattern Recognition

Identify:
- **Stage where most rejections occur:** (Applied → no response / Phone screen / Technical / Onsite / Offer)
- **Company type pattern:** (Startups ghosting / Big tech rejecting at technical stage / etc.)
- **Role type pattern:** (Backend roles responding more than full-stack / etc.)
- **Timing pattern:** (Roles applied > 2 weeks ago have lower response rates / etc.)
- **Score vs. outcome correlation:** (High-scoring JDs → better response rate? / etc.)

### Root Cause Hypotheses

Based on patterns:
- If high ghost rate → CV/ATS issue or too many low-fit applications
- If phone screen → onsite conversion is low → technical prep gap
- If onsite → offer conversion is low → system design or cultural signal gap
- If offer → acceptance is low → compensation expectations misaligned

### Strategic Recommendations

Based on profile + patterns, suggest:
1. **Targeting adjustment:** Narrow or broaden company type
2. **CV adjustment:** Specific section to strengthen
3. **Prep adjustment:** Which interview stage to focus on
4. **Volume adjustment:** Increase/decrease application rate

### Updated Priorities

Suggest:
- Top 3 companies to prioritize in next 2 weeks
- Top 1 skill to address in next 30 days
- One metric to track improvement: "Aim for X% response rate in next 20 applications"
