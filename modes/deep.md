# Career-Ops: deep — Company Deep Research Mode

**Purpose:** Full company intelligence report — funding, culture, tech stack, recent news.  
**Input:** Company name  
**Output:** Structured research report

---

## Research Checklist

Run web searches for each section below. Use multiple queries per section.

### 1. Company Fundamentals

Queries:
- `[Company] funding history Crunchbase`
- `[Company] valuation 2024 2025`
- `[Company] headcount employees`

Extract:
- Funding stage (Seed / Series A–F / Public / Acquired)
- Total raised
- Last valuation
- Key investors
- Headcount (approximate)
- Revenue signals (if available)
- Runway signals (if startup)

### 2. Engineering Culture

Queries:
- `[Company] engineering blog`
- `[Company] tech stack`
- `[Company] engineering team size`
- `[Company] site:levels.fyi`
- `[Company] Glassdoor engineering review`

Extract:
- Published tech stack (languages, frameworks, infra)
- Engineering blog posts (topics, quality signal)
- Glassdoor/Blind summary: pros/cons, comp, WLB
- Levels.fyi comp data if available

### 3. Recent News

Queries:
- `[Company] news 2024 2025`
- `[Company] layoffs OR hiring OR product launch`
- `[Company] CEO leadership change`

Extract:
- Major product launches (last 12 months)
- Funding announcements
- Layoffs or hiring freezes (risk signal)
- Leadership changes
- Regulatory/legal news (risk signal)

### 4. Technical Signals

Queries:
- `[Company] GitHub`
- `[Company] open source`
- `[Company] engineering architecture`

Extract:
- Open source contributions / repos
- Published architecture decisions
- Technical complexity signals

---

## Output Report

```markdown
# Company Research: [Company]
**Date:** YYYY-MM-DD

## Quick Summary
[3-sentence overview: what they do, stage, why relevant]

## Funding & Stability
| Metric | Value |
|--------|-------|
| Stage | |
| Total Raised | |
| Last Valuation | |
| Key Investors | |
| Headcount | |
| Stability Signal | 🟢 Strong / 🟡 Uncertain / 🔴 Risk |

## Engineering Culture
[Summary of Glassdoor/Blind signals, tech stack, engineering blog quality]

## Tech Stack
- Languages: 
- Frameworks:
- Infrastructure:
- Data:

## Recent News
- [bullet points, dated]

## Risk Flags
- [any concerning signals]

## Opportunity Signals
- [any positive differentiated signals]

## Verdict for Candidate
[2-3 sentences: why this company is/isn't a strong strategic fit based on profile.yml]
```
