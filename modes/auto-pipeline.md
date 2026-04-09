# Career-Ops: auto-pipeline — Master Mode Router

**Purpose:** Entry point when no mode is specified. Shows menu, routes to correct mode.  
**Input:** Optional arguments — if none, show interactive menu  
**Output:** Routes to the appropriate mode

---

## Invocation

```
/career-ops                    → show menu
/career-ops oferta [URL]       → run oferta mode
/career-ops tracker            → run tracker mode
/career-ops scan               → run scan mode
/career-ops deep [Company]     → run deep mode
```

---

## Interactive Menu (no arguments)

Display:

```
═══════════════════════════════════════════
  Career-Ops v1.0.0
  Your job search operating system
═══════════════════════════════════════════

  What would you like to do?

  📋 EVALUATE
  [1] oferta      — Evaluate a job posting (A–F grade)
  [2] ofertas     — Compare multiple offers side by side
  [3] deep        — Full company research

  📄 APPLY
  [4] pdf         — Generate ATS-optimized CV PDF
  [5] apply       — Fill application form
  [6] contacto    — Write LinkedIn outreach messages

  🔭 DISCOVER
  [7] scan        — Scan portals for new jobs
  [8] batch       — Process multiple JDs at once
  [9] pipeline    — Evaluate all pipeline URLs

  📊 TRACK
  [10] tracker    — View pipeline status
  [11] patterns   — Analyze rejection patterns

  🎓 IMPROVE
  [12] training   — Evaluate course/cert ROI
  [13] project    — Evaluate portfolio project fit

  Type a number or mode name, or paste a job URL directly.
```

---

## Smart URL Detection

If user input looks like a URL (starts with `http`):
→ Automatically route to `oferta` mode with that URL.

If user input is a company name:
→ Ask: "Would you like to (1) evaluate a specific role, (2) research the company, or (3) scan their careers page?"

---

## Pipeline Health Check (on startup)

Before showing menu, check:
- How many applications in tracker?
- Any in Interview or Offer stage? → Highlight
- Last scan date → If > 7 days: "💡 You haven't scanned portals in 7+ days"
- Grade distribution → If avg < B: "💡 Consider refining targeting"

Display brief status:
```
Pipeline: [N] tracked | [N] active | Last scan: [date]
```
