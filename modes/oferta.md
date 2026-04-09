# Career-Ops: oferta — Single Job Evaluation Mode

**Purpose:** Full A–F pipeline evaluation of a single job description.  
**Input:** Job posting URL or pasted JD text  
**Output:** Structured report saved to `reports/`, tracker row, PDF suggestion

---

## Activation

User provides:
- A job posting URL, OR
- Pasted JD text, OR
- Path to a JD file in `jds/`

If URL is provided: fetch and extract the job description using web tools.  
Save extracted JD to `jds/{company-slug}.txt` for future reference.

---

## Pre-flight

1. Load `config/profile.yml`
2. Load `cv.md`
3. Load `modes/_shared.md` scoring rules

---

## Evaluation Pipeline

### A. Role Summary

Extract and present:

| Field | Value |
|-------|-------|
| Company | |
| Role Title | |
| Seniority Level | (IC3/IC4/L5/Senior/Staff/etc.) |
| Archetype | (Backend / Frontend / Fullstack / Platform / ML / etc.) |
| Domain | (FinTech / DevTools / Infrastructure / AI / etc.) |
| Function | (Product Eng / Platform / Research / etc.) |
| Remote Policy | (Remote / Hybrid / Onsite — location) |
| Est. Team Size | (from JD signals) |
| Visa Sponsorship | (Yes / No / Unknown) |

**Archetype detection rules:**
- "distributed systems", "backend", "API" → Backend Systems
- "platform", "infra", "SRE", "reliability" → Platform/Infrastructure
- "ML", "model", "training", "inference" → ML Platform
- "full stack", "React + backend" → Full Stack
- "data pipeline", "ETL", "Spark" → Data Engineering

---

### B. CV Match Analysis

Map every JD requirement against `cv.md`:

**Required skills matrix:**
| JD Requirement | In CV? | Match Quality | Gap Severity |
|----------------|--------|---------------|--------------|
| [req 1] | ✅/❌/~  | Strong/Partial/Missing | Critical/Medium/Low |
| [req 2] | ... | | |

**Gap mitigation strategy:**
For each Critical gap, suggest:
- Whether it can be bridged in a cover letter / narrative
- Whether it can be addressed in a STAR story
- Whether it's a dealbreaker

**Keyword density analysis:**
List top 10 JD keywords not prominent in CV. These become PDF injection targets.

---

### C. Level Strategy

**Detected JD level:** [Junior / Mid / Senior / Staff / Principal]  
**Candidate level (from profile):** [from target_roles]  
**Gap assessment:** [On level / Stretch up / Stretch down]

**Senior positioning strategy:**
If the role is below candidate's target level:
- Identify which aspects of the candidate's background translate as expertise
- Script for framing: "I'm looking for a role where I can own X while building Y"

**Downlevel negotiation script** (if role is one level below target):
> "I'm aware this role is typically leveled at [X], but given my experience with [specific system/achievement], I'd want to discuss leveling alignment during the process. I'm confident I can demonstrate [Staff/Senior] impact within [timeframe]."

---

### D. Compensation Research

Trigger web search for:
- `[Company] [Role] salary site:levels.fyi`
- `[Company] [Role] compensation Glassdoor`
- `[Company] funding stage valuation`
- `[Company] engineering culture review`

**Compensation assessment:**
| Signal | Finding |
|--------|---------|
| Reported base range | |
| Equity type | (RSUs / Options / None) |
| Vesting schedule | |
| vs. Candidate target | (Below / Within / Above range) |
| Funding/stability signal | |

**Negotiation notes:**
- If comp is below range: flag and suggest BATNA framing
- If comp is above range: note as leverage

---

### E. Personalization Plan

**Top 5 CV edits for this specific JD:**

1. **[Section to modify]:** Change "[current text]" → "[suggested text]" to mirror JD language for "[keyword]"
2. **[Bullet to strengthen]:** Add metric/context — "[suggestion]"
3. **[Skill to surface]:** Move or highlight "[skill]" which appears [N] times in JD
4. **[Gap to address]:** Add brief mention of adjacent experience in "[section]"
5. **[Summary update]:** Tailor opening sentence to mention "[company domain]"

**Top 5 LinkedIn edits:**

1. **Headline:** Update to include "[keyword from JD]"
2. **About section:** Reference "[domain/stack]" in opening paragraph
3. **Featured section:** Pin project most relevant to this role
4. **Skills section:** Add/reorder "[missing skill]" to top 10
5. **Recent activity:** Engage with company content before applying

---

### F. Interview Prep

Generate 3 STAR+Reflection stories mapped to this JD's top requirements:

**Story 1: [JD requirement mapped]**
- **Situation:** 
- **Task:** 
- **Action:** 
- **Result:** (quantified)
- **Reflection:** What I learned / would do differently

**Story 2: [JD requirement mapped]**
- [same structure]

**Story 3: [JD requirement mapped]**
- [same structure]

**Likely technical questions for this role:**
1. [question 1 based on JD tech stack]
2. [question 2 based on JD domain]
3. [question 3 based on seniority level]

---

## Score Breakdown

| # | Dimension | Weight | Score (1-5) | Weighted |
|---|-----------|--------|-------------|---------|
| 1 | Role–Archetype Fit | 20% | | |
| 2 | CV–JD Keyword Match | 15% | | |
| 3 | Seniority Alignment | 15% | | |
| 4 | Compensation Fit | 10% | | |
| 5 | Remote/Location Fit | 10% | | |
| 6 | Company Quality Signal | 10% | | |
| 7 | Industry Fit | 5% | | |
| 8 | Tech Stack Overlap | 10% | | |
| 9 | Growth Potential | 3% | | |
| 10 | Interview Difficulty Estimate | 2% | | |
| | **TOTAL** | **100%** | | **X.X/5** |

**Grade:** [letter]  
**Recommendation:** [Apply Now / Apply with Prep / Hold / Skip]

---

## Post-Evaluation Auto-Actions

If grade ≥ B:
1. Save report to `reports/{company-slug}-{role-slug}-{YYYY-MM-DD}.md`
2. Output tracker TSV row:
   ```
   -\t{YYYY-MM-DD}\t{Company}\t{Role}\t{score}\tPipeline\t-\treports/{report-filename}\t{one-line note}
   ```
3. Suggest: `node generate-pdf.mjs --company {Company} --jd-file jds/{company-slug}.txt`

If grade < B:
1. Ask user if they want to proceed anyway or skip
2. Still offer to save the report for reference
