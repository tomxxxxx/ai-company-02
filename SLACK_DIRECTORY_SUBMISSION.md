# SLACK APP DIRECTORY SUBMISSION — Preparation Guide

**Status:** READY TO SUBMIT (Thomas action required)  
**Date:** Feb 12, 2026  

---

## Pre-Submission Checklist

### 1. Required Assets (CEO creates / Thomas uploads)

| Asset | Status | Details |
|-------|--------|---------|
| App Icon (512x512 PNG) | NEEDED | Purple checkmark on white bg — Thomas create with Canva |
| App Name | ✅ | TaskMaster |
| Short Description | ✅ | "Simple task management inside Slack. Create, track, and complete tasks with 3 commands." |
| Long Description | ✅ | See below |
| Privacy Policy URL | ✅ | https://tomxxxxx.github.io/ai-company-02/privacy.html |
| Support URL | ✅ | mailto:support@ai-automation-lab.de |
| Landing Page URL | ✅ | https://tomxxxxx.github.io/ai-company-02/ |
| Category | ✅ | Productivity |
| Redirect URL (OAuth) | NEEDED | Setup on Railway backend |

### 2. Long Description (Copy-Paste for Slack Directory)

```
TaskMaster — Simple Task Management for Slack

Stop switching between Slack and your project management tool. TaskMaster lets you create, track, and complete tasks right inside Slack with 3 simple commands.

HOW IT WORKS:
• /task [description] — Create a new task in the current channel
• /tasks — View all open tasks in the channel
• /done [number] — Mark a task as complete

WHY TEAMS LOVE TASKMASTER:
• Zero learning curve — if you can type, you can use TaskMaster
• Per-channel organization — each channel has its own task list
• No context switching — everything stays in Slack
• 60-second setup — install, invite, start tracking

PERFECT FOR:
• Engineering teams tracking bugs and quick fixes
• Marketing teams managing campaigns and deadlines  
• Startups who need simplicity over features
• Remote teams who live in Slack

PRICING:
• Free — up to 5 team members, 3 channels
• Pro ($4/user/mo) — unlimited everything + assignments + due dates
• Team ($8/user/mo) — analytics, dashboard, export, integrations

Get started in 60 seconds. No training needed.
```

### 3. Required Scopes (Already Configured)

- `commands` — Slash commands (/task, /tasks, /done)
- `chat:write` — Send messages to channels
- `app_mentions:read` — Respond to @TaskMaster mentions

### 4. OAuth Flow (Thomas Must Setup)

The Slack App Directory requires OAuth (not Socket Mode) for public distribution.

**Steps for Thomas:**
1. In Slack API Dashboard → **OAuth & Permissions**
2. Add Redirect URL: `https://your-railway-app.railway.app/slack/oauth_redirect`
3. Under **Manage Distribution** → Activate Public Distribution
4. Set up proper OAuth install flow in the app code

**IMPORTANT:** Socket Mode works for our workspace but NOT for public distribution.
We need to add HTTP endpoint support for slash commands for public apps.

### 5. Submission Steps (Thomas, ~20 min)

1. Go to https://api.slack.com/apps → Select TaskMaster
2. Click **Manage Distribution** in the sidebar
3. Complete all checklist items:
   - ✅ OAuth Redirect URL set
   - ✅ Remove hard-coded team IDs (we don't have any)
   - ✅ Bot token scopes are minimal
   - ✅ Slash commands configured
4. Click **Activate Public Distribution**
5. Go to **Submit to App Directory**
6. Fill in:
   - Icon (512x512)
   - Short description
   - Long description (copy from above)
   - Category: Productivity
   - Landing page: https://tomxxxxx.github.io/ai-company-02/
   - Privacy policy: https://tomxxxxx.github.io/ai-company-02/privacy.html
   - Support URL
7. Submit for review (takes 1-2 weeks)

---

## BLOCKER: Socket Mode → HTTP Mode Migration

**Current state:** Bot uses Socket Mode (WebSocket connection)  
**Required for Directory:** HTTP mode with public endpoints  

This means we need to:
1. Add HTTP endpoint routes for slash commands in the Flask app
2. Configure Request URL in Slack Dashboard for each slash command
3. Set up OAuth install flow for multi-workspace support

**CEO decision:** This is a NEXT WEEK task. For THIS WEEK:
- Thomas gets 2 testers using the bot (manual install via Socket Mode)
- We collect feedback  
- Next week: migrate to HTTP mode + submit to directory

---

## Timeline

| Day | Action | Owner |
|-----|--------|-------|
| Feb 12-14 | Thomas invites 2 testers | Thomas |
| Feb 15-16 | Collect feedback from testers | CEO + Thomas |
| Feb 17 | Create app icon (Canva) | Thomas |
| Feb 17-18 | Migrate bot to HTTP mode | CEO |
| Feb 19 | Submit to Slack App Directory | Thomas |
| Feb 19+ | Wait for Slack review (1-2 weeks) | - |

---

**Next step for Thomas:** Invite 2 people to test the bot this week. That's it.
