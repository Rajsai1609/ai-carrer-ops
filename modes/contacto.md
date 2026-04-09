# Career-Ops: contacto — LinkedIn Outreach Message Generator

**Purpose:** Generate personalized LinkedIn connection requests and follow-up messages.  
**Input:** Target company + role + (optional) target person's name/title  
**Output:** Ready-to-send connection request + follow-up sequence

---

## Pre-flight

Load `config/profile.yml` for narrative and target roles.

---

## Message Types

### 1. Connection Request (max 300 chars)

Template:
> "Hi [Name], I'm a [title] with [X] years in [domain]. I'm exploring [Company] and your work on [specific project/team] caught my attention. I'd love to connect."

Rules:
- ≤ 300 characters (LinkedIn limit)
- Reference something specific about their work or company
- No "I'm applying for a job" — keep it about mutual interest
- No attachments in connection request

### 2. Follow-up After Acceptance (first message)

Template (3-4 sentences):
> "Thanks for connecting, [Name]. I've been following [Company]'s work on [specific thing], especially [recent news/product]. I'm currently exploring senior engineering roles — if you're open to a brief chat about the team's direction, I'd genuinely appreciate it. No pressure either way."

### 3. Recruiter Cold Outreach

Template:
> "Hi [Name], I'm a [title] with a strong background in [top 2 skills from profile]. I noticed [Company] is growing its [team/domain] — I'd love to learn more about opportunities that might be a fit. My profile: [LinkedIn URL]. Open to connecting?"

### 4. Referral Request (after 1-2 exchanges)

> "I really appreciate the conversation, [Name]. I'm seriously considering applying to [role] on your team. Would you be comfortable providing a referral, or pointing me to the right recruiter? Totally understand if that's not something you can do — just wanted to ask directly."

---

## Personalization Data Points

For each message, Claude should use web search to find:
- Recent company news (funding, launch, blog post)
- Target person's recent LinkedIn activity or publications
- Specific team or project they work on

---

## Follow-up Sequence

If no response after 7 days:
> "Just circling back in case this got buried, [Name]. Happy to share more about my background if useful."

If no response after 14 days: Stop. Mark as Ghosted in notes.
