# Career-Ops: apply — Application Form Fill Mode

**Purpose:** Assist with filling application forms using profile.yml data.  
**Input:** Application form URL or field list  
**Output:** Pre-filled field values ready to paste/type

---

## Pre-flight

Load `config/profile.yml` for all contact and work authorization fields.

---

## Standard Field Mappings

From `config/profile.yml`, map to common application fields:

| Form Field | Source | Value |
|-----------|--------|-------|
| First Name | profile.name (split) | |
| Last Name | profile.name (split) | |
| Email | profile.email | |
| Phone | profile.phone | |
| LinkedIn URL | profile.linkedin | |
| GitHub URL | profile.github | |
| Portfolio | profile.portfolio | |
| Location / City | profile.location | |
| Work Authorization | profile.work_authorization.status | |
| Requires Sponsorship | profile.work_authorization.needs_sponsorship | |
| Desired Salary | profile.salary_range.min–max | |
| Remote Preference | profile.preferences.remote | |

---

## Cover Letter Template

Generate a concise 3-paragraph cover letter using:
1. **Opening:** Role + company + why specifically this company
2. **Body:** Top 2 relevant experiences from cv.md mapped to JD requirements
3. **Close:** Enthusiasm + call to action

Tone: Direct, confident, no fluff. Max 250 words.

---

## Work Authorization Script

If `needs_sponsorship: true`, provide scripted answer for:
- "Are you authorized to work in the US?"
  > "I am currently on [status] and will require visa sponsorship. My current authorization is valid through [date]. I have successfully navigated sponsorship processes before and am happy to discuss timeline and process."

---

## Application Checklist

Before submitting:
- [ ] CV PDF attached (correct company/date version)
- [ ] Cover letter personalized
- [ ] Work authorization answered accurately
- [ ] Salary expectations within range
- [ ] LinkedIn profile updated for this role
- [ ] Applied via referral if available
