# Career-Ops Data Contract

This document defines which files belong to the **system layer** (managed by career-ops, do not edit) 
and which belong to the **user layer** (yours to own and customize).

---

## System Layer — Do Not Edit

These files contain the operational logic of career-ops. They are updated when you upgrade career-ops.
Editing them may break the system. Contribute improvements via PRs instead.

| Path | Purpose |
|------|---------|
| `modes/*.md` | Agent mode instruction files |
| `modes/de/`, `modes/fr/`, `modes/pt/` | Localized mode files |
| `templates/cv-template.html` | Base HTML CV template |
| `templates/states.yml` | Canonical status definitions |
| `templates/portals.example.yml` | Example portal registry |
| `*.mjs` | Utility scripts (generate-pdf, merge-tracker, etc.) |
| `batch/batch-runner.sh` | Batch processing orchestrator |
| `batch/batch-prompt.md` | Machine-readable batch eval prompt |
| `dashboard/` | Go TUI dashboard source code |
| `.claude/skills/career-ops/SKILL.md` | Claude Code skill definition |
| `VERSION` | Version file |

---

## User Layer — You Own This

These files contain YOUR data, preferences, and CV content. They are yours to edit freely.
They are excluded from git by `.gitignore`.

| Path | Purpose | How to Create |
|------|---------|---------------|
| `config/profile.yml` | Your identity, targets, compensation, preferences | Copy from `config/profile.example.yml` |
| `config/portals.yml` | Your portal registry (customized for your targets) | Copy from `templates/portals.example.yml` |
| `cv.md` | Your CV in Markdown format | Copy from `examples/cv-example.md` |
| `data/applications.md` | Your job application tracker | Auto-created by `merge-tracker.mjs` |
| `data/pipeline.md` | Your list of URLs to evaluate | Create manually |
| `data/scan-history.tsv` | History of scanned portal listings | Auto-created by scan mode |
| `reports/*.md` | Evaluation reports for specific jobs | Auto-created by oferta mode |
| `output/*.pdf` | Generated CV PDFs | Auto-created by generate-pdf.mjs |
| `jds/*.txt` | Cached job description text files | Auto-created by oferta mode |
| `interview-prep/story-bank.md` | Your personal STAR story library | Editable template provided |

---

## Boundary Rules

1. **Never put secrets in `config/profile.yml`** — it contains salary info and personal data; it's gitignored but treat it with care
2. **Never commit files in `data/`, `reports/`, `output/`, `jds/`** — these are gitignored by design
3. **Never edit `modes/` files** unless you are forking career-ops for customization
4. **Do use** `config/profile.yml` to tune scoring weights toward your specific priorities
5. **Do extend** `config/portals.yml` by copying from `templates/portals.example.yml` and adding company entries

---

## Upgrade Path

When a new version of career-ops is released:
1. Update system layer files (`modes/`, `templates/`, `*.mjs`, `batch/`)
2. Your user layer files (`config/`, `data/`, `cv.md`) are untouched
3. Check `CHANGELOG.md` for any config format changes
