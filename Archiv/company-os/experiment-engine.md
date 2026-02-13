# Experiment Engine — How the Company OS Generates and Evaluates Businesses

> This is the core loop of AI Automation Lab. Without this, we're just building one product.

---

## Overview

The Experiment Engine is a repeatable process that:
1. **Generates** new business experiment ideas (AI-assisted)
2. **Scores** them against objective criteria
3. **Selects** the best candidates for validation
4. **Tracks** running experiments via scorecards
5. **Kills or scales** based on data, not feelings

---

## 1. Idea Generation

### Input Sources
| Source | Method | Frequency |
|--------|--------|-----------|
| Market signals | Scrape Product Hunt, Hacker News, Indie Hackers trending | Weekly |
| Platform opportunities | Check Slack/Discord/Shopify app marketplaces for gaps | Bi-weekly |
| Existing experiment data | What adjacent problems do current users have? | Per experiment |
| AI brainstorm | Structured prompt with constraints → 10 ideas | On demand |

### Generation Prompt Template
```
Generate 10 SaaS micro-product ideas that meet ALL of these constraints:
- Can be built by 1 developer + AI agents in ≤ 7 days
- Has a built-in anonymous distribution channel (marketplace, SEO, directory)
- No personal outreach or sales calls required
- Monthly cost to operate < €20
- Target market: small teams or solo users
- Can charge $5-20/month
- Not in direct competition with [list of known giants]

For each idea, provide:
1. One-line description
2. Target user
3. Distribution channel
4. Why it could work (1 sentence)
5. Why it might fail (1 sentence)
6. Estimated build time
```

---

## 2. Idea Scoring Matrix

Each idea is scored 1–5 on these criteria. **Minimum total score to proceed: 24/35.**

| Criterion | Weight | 1 (worst) | 5 (best) | Score |
|-----------|--------|-----------|----------|-------|
| **Build Speed** | 1x | > 30 days | < 3 days | |
| **Distribution** | 2x | Needs outreach | Built-in marketplace | |
| **Cost to Operate** | 1x | > €50/mo | €0/mo | |
| **Revenue Potential** | 1x | < €100/mo | > €1k/mo at scale | |
| **Constraint Fit** | 2x | Violates constraints | Perfect fit | |
| **Competitive Gap** | 1x | Red ocean | Blue ocean | |
| **Reusability** | 1x | One-off | Builds on existing infra | |

**Weighted total = sum of (score × weight). Max = 45. Threshold = 28.**

### Auto-Reject Filters (instant kill)
- Requires personal outreach → REJECT
- Requires Thomas as salesperson → REJECT
- Monthly cost > €50 before validation → REJECT
- Build time > 14 days → REJECT
- No anonymous distribution channel → REJECT
- Violates Konkurrenzklausel → REJECT

---

## 3. Selection & Approval

| Scenario | Action |
|----------|--------|
| Score ≥ 28, cost < €50 | AUTO — start experiment brief |
| Score ≥ 28, cost ≥ €50 | HUMAN — Thomas approves budget |
| Score 24–27 | PARK — revisit next generation cycle |
| Score < 24 | KILL — do not pursue |
| Multiple ideas score ≥ 28 | Pick highest score first. Max 2 active experiments. |

**Active experiment cap:** 2 concurrent experiments maximum.
- Reason: Thomas has ~1h/day. More than 2 = context switching death.

---

## 4. Experiment Lifecycle

```
IDEA → [Score ≥ 28] → BRIEF → [Approved] → BUILD → LAUNCH → VALIDATE → KILL or SCALE
                                   ↑                              |
                                   └──── PIVOT (new hypothesis) ──┘
```

| Phase | Duration | Key Activity | Exit Criteria |
|-------|----------|-------------|---------------|
| BRIEF | 1 day | Fill experiment-brief.md | Brief complete, approved |
| BUILD | 3–7 days | MVP code, landing page | Working product deployed |
| LAUNCH | 1–3 days | Submit to distribution channel | Discoverable by users |
| VALIDATE | 4–6 weeks | Track scorecard weekly | Hit kill or scale thresholds |
| KILL | 1 day | Document learnings, archive | Post-mortem written |
| SCALE | ongoing | Increase investment | Revenue growing month-over-month |

---

## 5. Weekly Review Process

**Every Monday, the System Architect runs this checklist:**

### Per Active Experiment:
- [ ] Update scorecard with this week's numbers
- [ ] Check kill/continue/scale thresholds
- [ ] Apply verdict (auto per policy, or escalate)
- [ ] Update action items

### System-Level:
- [ ] Any experiment at kill threshold for 2+ weeks? → Auto-kill, notify Thomas
- [ ] Active experiments < 2 and no tickets in progress? → Run idea generation
- [ ] Total monthly burn still < runway threshold? → OK
- [ ] Any policy violations this week? → Document in drift check

### Output:
Weekly summary committed to `company-os/logs/YYYY-MM-DD-weekly-review.md`

---

## 6. Post-Mortem Template (for killed experiments)

```markdown
# Post-Mortem — EXP-XXX [Name]

**Duration:** [start] → [kill date]
**Total Investment:** €XX
**Peak Users:** X
**Revenue:** €X

## What we hypothesized
> [original hypothesis]

## What actually happened
> [data summary]

## Why it failed
> [root cause — be specific]

## What we'd do differently
> [actionable learnings]

## Reusable assets
- [code, templates, channels that transfer to future experiments]
```

---

## 7. Current State

| Slot | Experiment | Status | Health |
|------|-----------|--------|--------|
| 1 | EXP-001 TaskMaster Slack Bot | VALIDATING | 🟡 Waiting on distribution |
| 2 | (empty) | — | — |

**Next idea generation:** After TICKET-001 (HTTP migration) is complete and EXP-001 has an active distribution channel. No point starting EXP-002 while we can't even distribute EXP-001.
