# Experiment Brief — EXP-001 TaskMaster Slack Bot

> Retroactively captured from pre-Company-OS work. Original build: Cycles #2–#7.

---

## Metadata

| Field | Value |
|-------|-------|
| **Experiment ID** | EXP-001 |
| **Name** | TaskMaster Slack Bot |
| **Status** | `VALIDATING` |
| **Owner** | System Architect + Thomas |
| **Created** | 2026-02-12 |
| **Approved** | 2026-02-12 (retroactive — approved via EXECUTIVE_DECISION.md) |
| **Kill Date** | 2026-03-26 (6 weeks from launch) |
| **Category** | SaaS |
| **Investment Cap** | €100 (currently at €0 marginal cost) |

---

## 1. Hypothesis

> "We believe small teams using Slack will adopt a lightweight task bot because existing project management tools are too heavy for simple task tracking, measurable by organic installs from the Slack App Directory."

**Target User:** Small teams (5–20 people) using Slack daily
**Problem:** Full PM tools (Jira, Asana) are overkill for simple task tracking
**Proposed Solution:** 3-command Slack bot: `/task`, `/tasks`, `/done`
**Why Now:** Slack marketplace has low-competition niches; AI-powered bots trending

---

## 2. Success Criteria (Go/Kill)

| Metric | Kill Threshold | Continue Threshold | Scale Threshold |
|--------|---------------|-------------------|-----------------|
| Installs by kill date | < 5 | 5–50 | > 50 |
| Paying customers by kill date | 0 | 1–5 | > 5 |
| MRR by kill date | €0 | €1–€50 | > €50 |
| CAC | > €20 | €5–€20 | < €5 (organic) |
| Organic signups/week | 0 | 1–5 | > 5 |

---

## 3. MVP Scope

**Core Features (3):**
1. `/task [description]` — Create a task
2. `/tasks` — List all open tasks
3. `/done [task_id]` — Mark task complete

**Explicitly Out of Scope:**
- Team management / permissions
- Integrations with external tools
- AI-powered features (prioritization, summaries)
- Recurring tasks
- File attachments

**Tech Stack:**
- Python 3.11 + Slack Bolt SDK
- SQLite (via Railway persistent storage)
- Railway (free tier) for hosting

**Estimated Build Time:** 7 days (actual: ~2 days with AI agents)

---

## 4. Distribution Plan

| Channel | Action | Timeline |
|---------|--------|----------|
| Slack App Directory | Submit listing (requires HTTP mode migration) | Week 3–4 |
| Product Hunt | Launch post | After App Directory approval |
| SEO | Landing page on GitHub Pages | ✅ Done |
| Hacker News | Show HN post | After 10+ users |

---

## 5. Cost Estimate

| Item | One-time | Monthly | Notes |
|------|----------|---------|-------|
| Hosting (Railway) | €0 | €0 | Free tier |
| Domain | €2.55 | €0 | Already purchased |
| API costs | €0 | €0 | No AI API calls in bot |
| **Total** | €2.55 | €0/mo | Marginal cost = zero |

---

## 6. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| No organic installs from directory | High | High | SEO, Product Hunt as backup channels |
| HTTP migration breaks bot | Low | Medium | Test in staging first |
| Slack rejects directory submission | Medium | Medium | Follow their guidelines precisely |
| Free tier limits hit | Low | Low | Upgrade to $5/mo Railway plan |

**Approval Level:** AUTO-APPROVED (total cost < €50, existing accounts only)

---

## 7. Timeline

| Phase | Duration | Deliverable | Status |
|-------|----------|-------------|--------|
| Build MVP | 2 days | Working bot on Railway | ✅ DONE |
| Landing page | 1 day | GitHub Pages site | ✅ DONE |
| Legal pages | 1 day | Privacy + Terms | ✅ DONE |
| HTTP migration | 2–3 days | Bot works in HTTP mode | ⬜ TODO |
| App Directory submission | 1 day | Listing submitted | ⬜ TODO |
| Validate | 6 weeks | Kill/continue decision | ⬜ RUNNING |
| Scale (if approved) | ongoing | Growth targets | ⬜ PENDING |

---

## 8. Decision Log

| Date | Decision | By | Rationale |
|------|----------|-----|-----------|
| 2026-02-12 | Selected Slack Bot as first product | Thomas (EXECUTIVE_DECISION.md) | Fastest path to revenue, lowest risk, organic distribution |
| 2026-02-12 | Built MVP via AI builder agents | System | 14 files generated, deployed to Railway |
| 2026-02-12 | Created landing page, privacy, terms | System | Required for App Directory submission |
| 2026-02-12 | Pivoted to Company OS model | Thomas + System Architect | Stop CEO-mode, build systematic experiment engine |
| 2026-02-12 | Retroactively captured as EXP-001 | System Architect | First experiment in Company OS |

---

## Current State (as of 2026-02-12)

```json
{
  "id": "EXP-001",
  "name": "TaskMaster Slack Bot",
  "status": "VALIDATING",
  "created": "2026-02-12",
  "kill_date": "2026-03-26",
  "category": "SaaS",
  "hypothesis": "Small Slack teams will adopt a 3-command task bot over heavyweight PM tools",
  "investment": {
    "cap_eur": 100,
    "spent_eur": 2.55,
    "monthly_cost_eur": 0
  },
  "thresholds": {
    "kill": { "users": 5, "paying_customers": 0, "mrr_eur": 0 },
    "scale": { "users": 50, "paying_customers": 5, "mrr_eur": 50 }
  },
  "metrics_current": {
    "users_free": 0,
    "users_paid": 0,
    "mrr_eur": 0,
    "signups_this_week": 0,
    "churn_rate": 0
  },
  "distribution_channels": ["slack_app_directory", "github_pages_seo", "product_hunt"],
  "tech_stack": ["python", "slack_bolt", "sqlite", "railway"]
}
```
