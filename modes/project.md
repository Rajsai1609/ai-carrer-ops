# Career-Ops: project — Portfolio Project Fit Evaluator

**Purpose:** Evaluate whether a side project or portfolio project strengthens the candidate's fit for target roles.  
**Input:** Project description or GitHub link  
**Output:** Fit analysis + improvement recommendations

---

## Pre-flight

Load `config/profile.yml` for: `target_roles[]`, `archetypes`, `skills`, `interview_prep.weak_areas`.
Load `cv.md` for existing projects listed.

---

## Evaluation Framework

### 1. Project Summary

Extract from provided info:
- What it does
- Tech stack used
- Scale / complexity signals
- Public / private
- Stars, forks, contributors (if GitHub)

### 2. Gap Bridge Analysis

Cross-reference against profile:
- Does this project demonstrate a skill in `weak_areas`?
- Does it add a tech stack item from target JDs?
- Does it show system design / architecture thinking?
- Is there a quantifiable impact / interesting metric?

### 3. Narrative Strength

Assess:
- Can this generate a STAR story for interviews?
- Is there a clear problem → solution → outcome arc?
- Does it demonstrate senior-level thinking (not just implementation)?

### 4. Visibility Assessment

- Is it on GitHub (public)?
- Is it mentioned on LinkedIn profile?
- Is it in CV `cv.md` projects section?
- Does it have a README that would impress a hiring manager?

---

## Output

```markdown
# Project Evaluation: [Project Name]

## Fit Score: [X/5]

## What This Project Demonstrates
- [strength 1]
- [strength 2]

## Gaps Not Addressed
- [gap 1]

## Interview Story Potential
[1-2 sentence STAR story arc this enables]

## Improvement Recommendations
1. [Add X to the project to demonstrate Y]
2. [Write a blog post about Z aspect]
3. [Add metrics: e.g., "handles 10k req/s"]
4. [Feature on LinkedIn / CV]

## Recommendation
[Add to CV / Featured on LinkedIn / Expand scope / Archive it]
```
