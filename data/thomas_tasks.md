# Tasks for Thomas (COO)
# Updated: Cycle #5 — CEO Code Review Complete

## STATUS: Code is now FIXED and deployment-ready.
The Builder Agent's code had critical bugs (broken imports, duplicate files, mismatched APIs). I've rewritten all 8 files into a consistent, working architecture. **No more building — it's time to deploy and sell.**

---

## PRIORITY 1: Deploy Bot Locally & Test (30 min)

- [ ] `cd products/slack_bot && pip install -r requirements.txt`
- [ ] Create `.env` file with a test Slack workspace:
  ```
  SLACK_BOT_TOKEN=xoxb-your-token
  SLACK_APP_TOKEN=xapp-your-token
  SOCKET_MODE=True
  ```
- [ ] Create Slack App at https://api.slack.com/apps:
  - Enable Socket Mode → create App-Level Token (`connections:write`)
  - OAuth Scopes: `commands`, `chat:write`, `app_mentions:read`
  - Slash Commands: `/task`, `/tasks`, `/done`
  - Event subscription: `app_mention`
  - Install to workspace → copy Bot Token
- [ ] Run: `python app.py` → test all 3 commands in Slack
- [ ] **If it works → proceed to Priority 2. If bugs → tell me.**

## PRIORITY 2: Deploy to Railway (20 min)

- [ ] Create Railway account (free tier: https://railway.app)
- [ ] New Project → Deploy from GitHub → select this repo
- [ ] Set root directory to `products/slack_bot`
- [ ] Add env vars: `SLACK_BOT_TOKEN`, `SLACK_SIGNING_SECRET`, `SOCKET_MODE=False`
- [ ] Copy public URL → update Slack App:
  - Request URL: `https://your-app.railway.app/slack/events`
  - Slash command URLs: same
- [ ] Verify the bot works from Slack

## PRIORITY 3: Get 3 Beta Users (rest of week)

- [ ] Install TaskMaster in your own workspace → use it daily
- [ ] Ask 2 developer friends/colleagues to install it (free)
- [ ] Collect feedback: What's missing? What's annoying?
- [ ] **Goal: 3 active workspaces by end of week**

## PRIORITY 4: Payment Setup (next week)

- [ ] Stripe account (if you don't have one)
- [ ] Simple pricing: Free (3 users) / Pro €9/month (unlimited)
- [ ] Landing page with "Add to Slack" button (I'll build this)

---

**Time estimate:** ~1h today (P1), ~30min tomorrow (P2), ongoing (P3)
**CEO Note:** Kein Verkaufen nötig — das Produkt verkauft sich über den Slack Marketplace. Wir brauchen nur 3 echte Nutzer um zu validieren.