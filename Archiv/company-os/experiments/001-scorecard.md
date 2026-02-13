# KPI Scorecard — EXP-001 TaskMaster Slack Bot

---

## Metadata

| Field | Value |
|-------|-------|
| **Experiment ID** | EXP-001 |
| **Name** | TaskMaster Slack Bot |
| **Scorecard Start** | 2026-02-12 |
| **Current Status** | `VALIDATING` |
| **Kill Date** | 2026-03-26 |
| **Week** | 1 |

---

## Core Metrics (Weekly)

| Week | Date | Users (free) | Users (paid) | MRR (€) | Signups | Churn | CAC (€) | Notes |
|------|------|-------------|-------------|---------|---------|-------|---------|-------|
| 0 (pre-launch) | 2026-02-12 | 0 | 0 | 0 | 0 | 0 | 0 | Bot live, no distribution yet |
| 1 | 2026-02-19 | | | | | | | |
| 2 | 2026-02-26 | | | | | | | |
| 3 | 2026-03-05 | | | | | | | |
| 4 | 2026-03-12 | | | | | | | |
| 5 | 2026-03-19 | | | | | | | |
| 6 | 2026-03-26 | | | | | | | KILL DATE — decision required |

---

## Health Indicators

### Traffic & Awareness
| Metric | This Week | Last Week | Trend |
|--------|-----------|-----------|-------|
| Landing page visits | unknown | — | — |
| Unique visitors | unknown | — | — |
| Bounce rate | unknown | — | — |
| Referral source breakdown | — | — | — |

### Activation & Engagement
| Metric | This Week | Last Week | Trend |
|--------|-----------|-----------|-------|
| Installs | 0 | — | — |
| Activation rate (install→first /task) | 0% | — | — |
| DAU / WAU | 0 | — | — |
| Tasks created | 0 | — | — |

### Revenue & Monetization
| Metric | This Week | Last Week | Trend |
|--------|-----------|-----------|-------|
| MRR (€) | 0 | — | — |
| New paying customers | 0 | — | — |
| Trial→Paid conversion rate | 0% | — | — |
| ARPU (€) | 0 | — | — |
| Churn rate (%) | 0% | — | — |

### Cost & Efficiency
| Metric | This Week | Last Week | Trend |
|--------|-----------|-----------|-------|
| Hosting cost (€) | 0 | — | — |
| API cost (€) | 0 | — | — |
| Total experiment cost (€) | 2.55 | — | — |
| Thomas time invested (h) | ~3h | — | — |

---

## Kill/Continue/Scale Assessment

| Criterion | Kill Threshold | Scale Threshold | Actual | Verdict |
|-----------|---------------|-----------------|--------|---------|
| Installs by 2026-03-26 | < 5 | > 50 | 0 | 🟡 Too early |
| Paying customers by 2026-03-26 | 0 | > 5 | 0 | 🟡 Too early |
| MRR by 2026-03-26 | €0 | > €50 | €0 | 🟡 Too early |
| CAC | > €20 | < €5 | €0 (organic) | 🟢 |
| Organic growth | 0/week | > 5/week | 0/week | 🟡 Too early |

### Overall Verdict

**This Week's Verdict:** 🟡 CONTINUE — Week 0, no distribution channel active yet. Assessment meaningful from Week 2+.

**Blocker:** App Directory submission requires HTTP mode migration. Without it, there is no anonymous distribution channel. Personal outreach is not an option (constraint).

---

## Action Items (This Week)

| # | Action | Owner | Due | Status |
|---|--------|-------|-----|--------|
| 1 | HTTP mode migration (App Directory blocker) | System Architect | 2026-02-19 | ⬜ |
| 2 | Add analytics endpoint (install count) | System Architect | 2026-02-19 | ⬜ |
| 3 | App Icon (512x512 PNG) | Thomas | after migration | ⬜ |
| 4 | Submit to Slack App Directory | Thomas (review) | after migration | ⬜ |

---

## Cumulative Investment

| Category | Total to Date (€) |
|----------|--------------------|
| Hosting | 0 |
| API costs | 0 |
| Domain | 2.55 |
| Thomas time (~3h × €0) | 0 |
| **Total** | **2.55** |
