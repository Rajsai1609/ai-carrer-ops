# Career-Ops: pdf — ATS CV PDF Generation Mode

**Purpose:** Generate a tailored, ATS-optimized PDF CV for a specific company/role.  
**Input:** Company name + optional JD file  
**Output:** PDF at `output/cv-{lastname}-{company}-{YYYY-MM-DD}.pdf`

---

## Pre-flight

Load `config/profile.yml`, `cv.md`.

---

## Process

1. **Extract candidate name** from `config/profile.yml`
2. **Extract JD keywords** if `--jd-file` provided (or from `jds/{company-slug}.txt`)
3. **Identify top 10 keywords** from JD not already prominent in CV
4. **Run generator:**
   ```bash
   node generate-pdf.mjs --company "{Company}" --jd-file jds/{company-slug}.txt
   ```

## Keyword Injection Strategy

From the JD, extract:
- Required technical skills not in CV → inject into ATS hidden div
- Role-specific verbs ("architect", "design", "scale") → surface in summary
- Domain keywords ("distributed", "real-time", "ML") → note for manual CV edit

## Output Confirmation

After generation, confirm:
- ✅ File path: `output/cv-{lastname}-{company-slug}-{YYYY-MM-DD}.pdf`
- ✅ File size (should be 80–300 KB for A4 single page)
- ✅ ATS keywords injected: [list top 10]

## Manual Customization Notes

Suggest 3 quick CV tweaks for this specific JD that would improve ATS score:
1. [tweak 1]
2. [tweak 2]  
3. [tweak 3]
