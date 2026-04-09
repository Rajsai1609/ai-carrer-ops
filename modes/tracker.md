# Career-Ops: tracker — Pipeline Status Display Mode

**Purpose:** Read `data/applications.md` and display a formatted pipeline summary.  
**Input:** `data/applications.md`  
**Output:** Console-rendered pipeline dashboard

---

## Pre-flight

Check that `data/applications.md` exists. If not, offer to create it.

---

## Display Format

### Pipeline Overview

```
═══════════════════════════════════════
  Career-Ops Pipeline — [N] applications
═══════════════════════════════════════

  📤 Applied:    [N]   █████
  📞 Screening:  [N]   ███
  🎯 Interview:  [N]   ██
  🎉 Offer:      [N]   █
  ❌ Rejected:   [N]   ████
  👻 Ghosted:    [N]   ███
  🚫 Withdrawn:  [N]   █
  🔭 Pipeline:   [N]   ██████
```

### Key Metrics

```
  Response Rate:    XX.X%
  Offer Rate:       XX.X%
  Ghost Rate:       XX.X%
  Avg JD Score:     X.X / 5
```

### Recent Activity (last 10 entries)

| # | Date | Company | Role | Status | Grade |
|---|------|---------|------|--------|-------|

### Insights

Based on pipeline state:
- If ghost rate > 30%: "Consider narrowing your target list"
- If response rate < 10%: "Review CV keywords — ATS may be filtering"
- If offer stage > 0: "You have active offers — run `ofertas` to compare"
- If pipeline is empty: "Run `scan` to find new leads"

---

## Commands Available After Display

Suggest relevant next actions based on current pipeline state:
- `oferta [URL]` — Evaluate a new job posting
- `ofertas` — Compare active offers
- `scan` — Find new leads
- `patterns` — Analyze rejection patterns
