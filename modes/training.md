# Career-Ops: training — Course & Certification ROI Evaluator

**Purpose:** Evaluate whether a course, bootcamp, or certification is worth the investment given target roles.  
**Input:** Course/cert name or URL  
**Output:** ROI analysis and go/no-go recommendation

---

## Pre-flight

Load `config/profile.yml` for: `target_roles[]`, `archetypes`, `skills`, `interview_prep.weak_areas`.

---

## Evaluation Framework

### 1. Content Analysis

Extract from the course page/description:
- Topics covered
- Duration / time investment
- Cost (money + time)
- Prerequisites

### 2. Gap Bridge Analysis

Cross-reference against profile:
- Does this course address a `weak_areas` item from profile?
- Does it add a skill that appears in target JDs but not in CV?
- Does it reinforce existing strengths (generally lower ROI)?

### 3. Signal Value

Research:
- Is this cert recognized by target employers?
- Does it appear in job descriptions for target roles?
- Web search: `[cert name] value for [role type]`
- Web search: `[cert name] worth it 2024 2025`

### 4. Opportunity Cost

Calculate:
- Time: hours × your hourly value (estimate from target salary)
- Money: course fee
- Total cost in "opportunity days"
- Could that time be better spent on: interview prep / side projects / networking?

---

## Output

```markdown
# Training Evaluation: [Course/Cert Name]

## Quick Verdict
[Go ✅ / No-Go ❌ / Conditional ⚠️]

## ROI Analysis
| Factor | Assessment |
|--------|-----------|
| Addresses profile gaps | Yes/No/Partially |
| Appears in target JDs | Frequently/Sometimes/Rarely |
| Employer recognition | High/Medium/Low |
| Time investment | X hours |
| Cost | $X |
| Signal vs. experience | Adds signal / Redundant |

## Recommendation
[2-3 sentences: specific go/no-go with reasoning]

## Better Alternatives (if No-Go)
- [alternative 1]
- [alternative 2]
```
