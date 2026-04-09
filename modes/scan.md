# Career-Ops: scan — Job Portal Scraper Mode

**Purpose:** Scan careers portals for new job postings matching target criteria.  
**Input:** `config/portals.yml` (or `templates/portals.example.yml`), `config/profile.yml`  
**Output:** New job leads appended to `data/scan-history.tsv`, deduped

---

## Pre-flight

Load `config/profile.yml` for: `target_roles[]`, `preferences.remote`, `work_authorization`.

Check for `config/portals.yml`. If missing, use `templates/portals.example.yml` and warn user to copy it.

---

## Process

For each company in portals config:

1. **Launch Playwright** → navigate to company careers page
2. **Apply search filters:** role keywords from `target_roles[]`
3. **Extract job listings:** title, URL, location, date posted
4. **Check against scan history:** `data/scan-history.tsv`
5. **Dedup:** skip if same company+title already in history
6. **Append new leads** to scan history

---

## Scan History Format

`data/scan-history.tsv` columns:
```
Scan Date \t Company \t Role Title \t URL \t Location \t Date Posted \t Status
```

---

## Output

After scan completes:

**New leads found: [N]**

| Company | Role | Location | Date Posted | URL |
|---------|------|----------|-------------|-----|
| [row] | | | | |

**Next steps:**
- Run `oferta` mode on promising leads
- Filter by archetype and remote preference
- Prioritize tier-1/tier-2 targets first
