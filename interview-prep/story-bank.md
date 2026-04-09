# Interview Story Bank — STAR+Reflection Template

Use this file to catalog your best interview stories mapped to common competencies.
Run `oferta` mode to generate role-specific story suggestions.

---

## Template: STAR+Reflection

```markdown
### Story: [Descriptive Title]
**Competency:** [Leadership / Scale / Conflict / Technical Challenge / Ownership / etc.]
**Applicable JD keywords:** [terms this story addresses]

**Situation:**
[1-2 sentences: context, team size, business stakes]

**Task:**
[1 sentence: your specific responsibility]

**Action:**
[3-5 sentences: what YOU specifically did — use "I", not "we"]

**Result:**
[1-2 sentences: quantified outcome — %, $, x improvement, time saved]

**Reflection:**
[1 sentence: what you learned or would do differently]

---
```

---

## Story Examples

### Story: API Gateway Migration
**Competency:** Technical Leadership, Scale, Architecture  
**Applicable JD keywords:** distributed systems, high-throughput, API design, gRPC, latency

**Situation:**  
Our legacy REST monolith was processing 150K req/s and hitting p99 latency of 200ms — 3x our SLA target — causing downstream checkout failures.

**Task:**  
I was tasked with designing and leading a replacement API gateway that could handle 10x projected traffic without impacting 99.99% uptime SLA.

**Action:**  
I designed a gRPC-based gateway with per-service circuit breakers, adaptive rate limiting, and connection pooling. I built a shadow traffic system to run both gateways in parallel, routing 5% → 50% → 100% traffic over 6 weeks. I coordinated with 3 service teams to update their clients and wrote runbooks for on-call.

**Result:**  
Achieved 500K req/s capacity with p99 < 8ms — 25x improvement on latency. Zero-downtime migration. Reduced deployment cycle time by 65%.

**Reflection:**  
I would add distributed tracing from day one — we added it 3 weeks in and it would have shortened debugging cycles during the rollout.

---

### Story: Database Sharding Without Downtime
**Competency:** Ownership, Technical Risk Management, Cross-team Coordination  
**Applicable JD keywords:** PostgreSQL, data reliability, distributed systems, zero-downtime migration

**Situation:**  
Our multi-tenant PostgreSQL cluster was hitting table size limits at 500GB; queries were degrading and we had signed contracts requiring 99.9% uptime.

**Task:**  
I owned the design and execution of a sharding strategy that could be deployed without a maintenance window for our 200+ paying customers.

**Action:**  
I designed a range-based tenant sharding scheme, built a shadow-write migration harness that wrote to both old and new databases simultaneously, and validated data consistency with checksums. I coordinated with customer success, on-call, and 2 other engineering teams for the cutover weekend.

**Result:**  
10x customer growth accommodated. Zero customer-visible downtime. Migration completed in 8 hours vs. the 48-hour estimate.

**Reflection:**  
The shadow-write approach added 3 weeks of development. For the next migration, I'd evaluate using Citus or PlanetScale earlier in the product lifecycle to avoid the constraint.

---

### Story: Fraud Detection Pipeline — Batch to Real-Time
**Competency:** Impact, Business Alignment, Technical Execution  
**Applicable JD keywords:** Kafka, event streaming, real-time systems, data pipeline, Python

**Situation:**  
Our fraud detection ran batch jobs with 2-hour lag. We were losing an estimated $50K/month to fraud that our system was catching too late to reverse.

**Task:**  
Build a real-time fraud scoring pipeline to reduce detection lag from 2 hours to under 30 seconds.

**Action:**  
I designed a Kafka → Faust consumer pipeline with per-event ML model scoring, added a confidence-threshold quarantine system, and deployed via A/B rollout (10% → 50% → 100% over 2 weeks) with manual review fallback.

**Result:**  
Reduced fraud detection lag from 2 hours to < 5 seconds. Estimated $48K/month fraud reduction verified over 3 months. Pipeline now processes 2M events/day with 3 nines uptime.

**Reflection:**  
I underestimated the complexity of the replay testing infrastructure. I'd allocate a full sprint to event replay and chaos testing before going to production.

---

## Competency Coverage Tracker

| Competency | Stories Covering | Target |
|-----------|-----------------|--------|
| Technical Leadership | API Gateway Migration | ✅ |
| Scale / High-throughput | API Gateway, Fraud Pipeline | ✅ |
| Cross-team Coordination | DB Sharding | ✅ |
| Ownership / Risk | DB Sharding | ✅ |
| Business Impact | Fraud Pipeline | ✅ |
| Conflict / Disagreement | _(add story)_ | ❌ |
| Mentorship | _(add story)_ | ❌ |
| Failure / Recovery | _(add story)_ | ❌ |
| Ambiguous Problem | _(add story)_ | ❌ |

---

## How to Use This File

1. Run `oferta [URL]` — it generates 3 STAR stories mapped to the specific JD
2. Copy the generated stories here for your permanent record
3. Practice each story out loud (aim for 2–3 minutes)
4. Track which stories you've actually told in interviews by adding notes
