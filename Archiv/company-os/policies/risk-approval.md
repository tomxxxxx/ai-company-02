# Risk & Approval Policy — AI Automation Lab

> Version: 1.0 | Effective: 2026-02-12 | Owner: System Architect + Thomas

---

## Purpose

Defines which decisions can be made automatically by AI agents and which require human approval. Every decision must be traceable to a rule in this document or an explicit human override.

---

## 1. Spending Decisions

| Action | Limit | Approval | Examples |
|--------|-------|----------|---------|
| Free-tier service signup | €0 | AUTO | Railway free tier, GitHub Pages |
| One-time tool purchase | < €20 | AUTO | Domain, icon assets |
| One-time tool purchase | €20–€100 | HUMAN | Premium tool licenses |
| One-time tool purchase | > €100 | HUMAN + JUSTIFICATION | Hardware, annual subscriptions |
| Monthly recurring cost | < €10/mo | AUTO | Small API usage |
| Monthly recurring cost | €10–€50/mo | HUMAN | New SaaS tools |
| Monthly recurring cost | > €50/mo | HUMAN + ROI CALC | Infrastructure scaling |
| Experiment total budget | < €50 | AUTO (within experiment cap) | MVP hosting, domain |
| Experiment total budget | €50–€200 | HUMAN | Extended validation |
| Experiment total budget | > €200 | HUMAN + BUSINESS CASE | Scaling investment |

---

## 2. Experiment Lifecycle Decisions

| Decision | Criteria | Approval |
|----------|----------|----------|
| **START** new experiment | Brief completed, < €50 initial cost | AUTO |
| **START** new experiment | Brief completed, ≥ €50 initial cost | HUMAN |
| **CONTINUE** experiment | Between kill and scale thresholds | AUTO (weekly review) |
| **KILL** experiment | Below kill thresholds for 2 consecutive weeks | AUTO (notify Thomas) |
| **KILL** experiment | Above kill thresholds but strategic concern | HUMAN |
| **SCALE** experiment (increase spend) | Above scale thresholds | HUMAN |
| **PIVOT** experiment (change hypothesis) | Any | HUMAN |
| **PAUSE** experiment | Operational issue, no spend impact | AUTO (notify Thomas) |

---

## 3. Technical Decisions

| Decision | Approval | Notes |
|----------|----------|-------|
| Choose tech stack for new experiment | AUTO | Must use free/cheap tiers |
| Deploy to production (new experiment) | AUTO | If experiment is APPROVED |
| Deploy update to live experiment | AUTO | If tests pass, no breaking changes |
| Deploy breaking change | HUMAN | Migration plan required |
| Create new external account | HUMAN | Thomas must register |
| Change pricing model | HUMAN | Always |
| Delete/archive user data | HUMAN | Always |
| Add new dependency > 10MB | AUTO with note | Document rationale |

---

## 4. Communication & Distribution

| Decision | Approval | Notes |
|----------|----------|-------|
| Submit to app marketplace (Slack, etc.) | HUMAN | Thomas must review listing |
| Post on Product Hunt | HUMAN | Timing matters |
| SEO optimization (meta tags, content) | AUTO | No personal info |
| Create anonymous social account | HUMAN | Thomas must approve platform |
| Cold outreach to individuals | BLOCKED | Violates constraints |
| Use Thomas's personal contacts | BLOCKED | Violates constraints |
| Respond to inbound support requests | AUTO | Template responses, escalate edge cases |

---

## 5. Data & Privacy

| Decision | Approval | Notes |
|----------|----------|-------|
| Collect anonymous usage metrics | AUTO | Must comply with privacy policy |
| Collect PII (email, name) | HUMAN | Privacy policy update required |
| Share data with third parties | BLOCKED | Never without explicit consent |
| Process payments | HUMAN | Stripe setup by Thomas |

---

## 6. Company OS Changes

| Decision | Approval | Notes |
|----------|----------|-------|
| Update templates | AUTO | Git-tracked, reversible |
| Update policies | HUMAN | This document included |
| Change agent roles/permissions | HUMAN | Architecture change |
| Add new agent type | HUMAN | Architecture review required |
| Modify scoring/threshold formulas | HUMAN | Affects experiment lifecycle |

---

## 7. Escalation Format

When a decision requires HUMAN approval, the System Architect provides:

```markdown
## Decision Packet

**Decision ID:** DEC-YYYY-MM-DD-XX
**Category:** [Spending / Experiment / Technical / Distribution]
**Summary:** One sentence

### Options
| Option | Pro | Con | Cost | Risk |
|--------|-----|-----|------|------|
| A | | | | |
| B | | | | |

### Recommendation
Option X because [rationale].

### Deadline
[Date] — if no response, [default action per policy].

### Default if No Response (72h)
[Most conservative option] will be auto-applied.
```

---

## 8. Override Mechanism

Thomas can override ANY policy decision by:
1. Stating the override in the chat or committing a `HUMAN_OVERRIDE.md`
2. The override is logged in `data/decisions.jsonl`
3. The policy is updated if the override represents a permanent change

---

## 9. Review Schedule

- **Weekly:** Experiment kill/continue/scale assessments (AUTO)
- **Monthly:** Policy review — are thresholds still appropriate? (HUMAN)
- **Per Cycle:** Drift check — did any agent exceed its authority? (AUTO)

---

## Changelog

| Date | Change | By |
|------|--------|-----|
| 2026-02-12 | Initial policy created | System Architect |
