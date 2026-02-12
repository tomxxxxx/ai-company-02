# Work Ticket — TICKET-001 HTTP Mode Migration + OAuth Flow

---

## Metadata

| Field | Value |
|-------|-------|
| **Ticket ID** | TICKET-001 |
| **Experiment** | EXP-001 (TaskMaster Slack Bot) |
| **Title** | Migrate to HTTP Mode + Add OAuth Install Flow |
| **Status** | `DONE` |
| **Priority** | `P1-HIGH` (blocks App Directory = blocks all distribution) |
| **Assignee** | `builder-agent` |
| **Created** | 2026-02-12 |
| **Due** | 2026-02-19 |
| **Depends On** | None |
| **Blocks** | TICKET-002 (App Directory Submission) |

---

## 1. Objective

Bot runs in HTTP mode with OAuth install flow so any Slack workspace can install it via the App Directory.

---

## 2. Context

Bot already has HTTP mode support in `app.py` (Flask routes, `SOCKET_MODE` env toggle). What's missing:
- OAuth callback endpoint (`/slack/oauth_redirect`)
- Install endpoint (`/slack/install`)
- Railway env var `SOCKET_MODE=False` + `SLACK_SIGNING_SECRET` set
- Slack Dashboard: Redirect URL + Request URL configured

See: `SLACK_DIRECTORY_SUBMISSION.md` sections 4–5.

---

## 3. Acceptance Criteria

- [ ] `SOCKET_MODE=False` on Railway, bot still responds to `/task`, `/tasks`, `/done`
- [ ] `/slack/install` serves "Add to Slack" OAuth redirect
- [ ] `/slack/oauth_redirect` handles OAuth callback, stores workspace tokens
- [ ] Bot works in at least 2 workspaces simultaneously (multi-tenant)
- [ ] Health check (`/`) still returns 200
- [ ] No downtime — deploy alongside existing Socket Mode, then switch

---

## 4. Scope & Constraints

**In Scope:**
- OAuth endpoints in `app.py`
- Token storage (SQLite table `installations`)
- Railway env var changes
- Slack Dashboard Request URL + Redirect URL

**Out of Scope:**
- New features (no AI, no assignments, no due dates)
- Pricing/payment integration
- Landing page changes

**Constraints:**
- Zero additional cost (Railway free tier)
- Don't break existing workspace install
- Thomas must set Redirect URL in Slack Dashboard (HUMAN task)

---

## 5. Approach

1. Add `slack_bolt.oauth` with SQLite `InstallationStore`
2. Add `/slack/install` and `/slack/oauth_redirect` routes
3. Create `installations` table in existing SQLite DB
4. Test locally with `SOCKET_MODE=False`
5. Deploy to Railway with new env vars
6. Thomas: update Slack Dashboard URLs

---

## 6. Approval Required?

| Check | Result |
|-------|--------|
| Spending > €0? | No |
| New external account needed? | No |
| Breaking change to live system? | Yes — mode switch |
| **Approval level** | AUTO (code only — deploy config split to TICKET-003) |

---

## 7. Output

- Modified files: `app.py`, `database.py` (installations table)
- New env vars: `SLACK_SIGNING_SECRET`, `SLACK_CLIENT_ID`, `SLACK_CLIENT_SECRET`
- Slack Dashboard config changes (documented steps for Thomas)

---

## 8. Log

| Date | Update | By |
|------|--------|-----|
| 2026-02-12 | Created — code already partially exists | System Architect |
