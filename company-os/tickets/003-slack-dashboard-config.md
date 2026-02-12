# Work Ticket — TICKET-003 Configure Slack Dashboard for HTTP Mode

---

## Metadata

| Field | Value |
|-------|-------|
| **Ticket ID** | TICKET-003 |
| **Experiment** | EXP-001 (TaskMaster Slack Bot) |
| **Title** | Set Redirect URL + Request URL in Slack Dashboard |
| **Status** | `BLOCKED` |
| **Priority** | `P1-HIGH` |
| **Assignee** | `thomas` |
| **Created** | 2026-02-12 |
| **Due** | 2026-02-19 |
| **Depends On** | TICKET-001 (HTTP Mode Migration code) |
| **Blocks** | TICKET-002 (App Directory Submission) |

---

## 1. Objective

Slack Dashboard configured with correct Request URL and OAuth Redirect URL so the bot works in HTTP mode publicly.

---

## 2. Context

After TICKET-001 deploys the code, Thomas needs to update 3 settings in the Slack API Dashboard. ~5 minutes.

---

## 3. Acceptance Criteria

- [ ] Slack Dashboard → Interactivity & Shortcuts → Request URL set to Railway URL
- [ ] Slack Dashboard → OAuth & Permissions → Redirect URL set
- [ ] Slack Dashboard → Slash Commands → each command Request URL updated
- [ ] Railway env var `SOCKET_MODE=False` set
- [ ] Bot still responds to commands

---

## 4. Scope & Constraints

**In Scope:**
- Slack API Dashboard config changes
- Railway environment variable change

**Out of Scope:**
- Code changes (done in TICKET-001)

---

## 5. Approach

Step-by-step instructions (generated after TICKET-001 provides the exact URLs):
1. Go to https://api.slack.com/apps → Select TaskMaster
2. OAuth & Permissions → Add Redirect URL: `https://<railway-url>/slack/oauth_redirect`
3. Slash Commands → Update each command Request URL to `https://<railway-url>/slack/events`
4. Interactivity → Set Request URL to `https://<railway-url>/slack/events`
5. Railway Dashboard → Set `SOCKET_MODE=False`
6. Verify bot responds to `/task test`

---

## 6. Approval Required?

| Check | Result |
|-------|--------|
| Spending > €0? | No |
| New external account needed? | No |
| Breaking change to live system? | Yes — mode switch |
| **Approval level** | HUMAN (Thomas must execute) |

---

## 7. Output

Slack Dashboard correctly configured. Bot serving via HTTP.

---

## 8. Log

| Date | Update | By |
|------|--------|-----|
| 2026-02-12 | Created — split from TICKET-001 | System Architect |
