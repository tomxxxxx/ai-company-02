# SLACK BOT - MVP BUILD SPECIFICATION

**Decision:** GO  
**Start:** Feb 12, 2026  
**Target Launch:** Feb 22, 2026 (10 days)  
**Budget:** ~$100/month  

---

## MVP FEATURE SET

### Core Bot Functionality
```
Slack Bot: "TaskMaster" (working name)

PURPOSE: Automate task management from Slack messages
- Slash command: /task create [task name]
- Auto-convert @mentions to task assignments
- AI summarization of task descriptions
- Daily standup summary
- Integration with Slack threads
```

### Phase 1 MVP (Week 1-2)
**Must Have:**
1. Slash command: `/task [description]` → creates task
2. Auto-assign to mentioned users
3. Store tasks in database
4. List tasks with `/tasks list`
5. Mark complete: `/task complete [id]`
6. Basic Auth (OAuth2 Slack)

**Nice to Have (but cut if not time):**
- AI summarization
- Daily standup
- Integrations beyond Slack

### Phase 2 (Post-Launch, Week 3)
- AI context understanding
- Natural language task extraction
- Slack reaction-based marking
- Team analytics dashboard

---

## TECHNICAL ARCHITECTURE

### Backend
```
Language: Python 3.11
Framework: Flask or FastAPI
Database: PostgreSQL (Railway free tier or PlanetScale)
Hosting: Vercel (serverless functions)
Queue: No queue needed initially (sync)
Logs: CloudWatch or Vercel logs
```

### API Integrations
```
1. Slack API (socket mode or webhook)
2. Claude API (summarization, optional MVP)
3. OAuth2 (Slack app auth)
4. PostgreSQL + SQLAlchemy ORM
```

### Code Structure
```
/slack-bot-mvp/
  ├── app.py (main Flask app)
  ├── slack_handlers.py (slash commands, events)
  ├── ai_engine.py (Claude calls)
  ├── db.py (database models)
  ├── auth.py (OAuth2)
  ├── requirements.txt
  ├── .env.example
  └── vercel.json
```

---

## DEVELOPMENT TIMELINE (10 DAYS)

### Day 1: Setup & Auth
- [x] Create GitHub repo
- [ ] Slack app creation (dev.slack.com)
- [ ] OAuth2 configuration
- [ ] Database schema
- [ ] Basic Flask app template

**Deliverable:** Auth flow working, can install bot in test Slack workspace

### Day 2-3: Core Commands
- [ ] `/task create` command
- [ ] Database model for tasks
- [ ] `/tasks list` retrieval
- [ ] Basic error handling
- [ ] Task ID generation

**Deliverable:** Can create and list tasks

### Day 4-5: Features
- [ ] Task completion marking
- [ ] User mention parsing (@user assigns task)
- [ ] Persisting user IDs
- [ ] Edit task command
- [ ] Delete task command

**Deliverable:** Full CRUD for tasks

### Day 6: Testing & Polish
- [ ] Error handling (bad input)
- [ ] Edge cases (duplicate tasks, invalid users)
- [ ] Response message formatting
- [ ] Slack message buttons (if time)

**Deliverable:** Robust MVP

### Day 7: Deployment
- [ ] Deploy to Vercel
- [ ] Database migration
- [ ] Environment variables setup
- [ ] Slack Marketplace submission form filled

**Deliverable:** Bot publicly accessible

### Day 8-9: Slack Marketplace Submission
- [ ] Screenshots for marketplace
- [ ] Description / feature list
- [ ] Privacy policy (template)
- [ ] Support email
- [ ] Submit to Slack review

**Deliverable:** Submitted

### Day 10: ProductHunt Prep
- [ ] Create ProductHunt account
- [ ] Write description/tagline
- [ ] Get backlinks ready
- [ ] Prepare launch day

**Deliverable:** Ready to launch Day 11

---

## COST BREAKDOWN

### Monthly Infrastructure
```
Vercel (serverless): $0-20
PostgreSQL (Railway): $7-15 or free tier
Slack API: $0 (free for development)
Claude API: $20-50 (depending on usage)
Domain: Already paid
--
TOTAL: $27-85/month
```

### One-Time Setup
```
Slack App review: $0
ProductHunt: $0
GitHub: $0
Time (10 days @ 8 hours/day): Sunk cost
```

---

## SUCCESS METRICS

### Week 1 Launch
- **Target:** 100+ Product Hunt upvotes
- **Target:** Top 5 on HN
- **Target:** 50+ app installs to submitted bot

### Week 2
- **Target:** 200+ total installs
- **Target:** 10+ paying customers (freemium → $9/month)
- **Target:** $90 MRR

### Week 3
- **Target:** 500+ installs
- **Target:** 25+ paid
- **Target:** $225 MRR

### Week 4
- **Target:** 1000+ installs
- **Target:** 50+ paid
- **Target:** $450 MRR

---

## GO-LIVE CHECKLIST

Before ProductHunt launch:
- [ ] Beta testing with 5 real users
- [ ] NPS score > 7
- [ ] Zero critical bugs
- [ ] Database backed up
- [ ] Scaling plan documented
- [ ] Support email monitored
- [ ] Pricing page ready
- [ ] Landing page ready

---

## MONETIZATION (Week 2+)

### Freemium Model
```
FREE:
- 10 tasks/month
- 1 Slack workspace
- Basic features

PAID ($9/month):
- Unlimited tasks
- Unlimited workspaces
- AI summarization
- Advanced reporting
- Priority support
```

### Payment Processing
- Stripe or Paddle
- Implement Week 2-3
- Auto-billing for Slack app

---

## CONTINGENCIES

**If behind schedule:**
1. Cut AI summarization (not MVP critical)
2. Cut analytics (nice-to-have)
3. Launch with core 3 commands only
4. Add features post-launch based on usage

**If low traction Week 1:**
1. Pivot to Email Bot (same codebase)
2. Try API Monitor angle
3. Launch Social Scheduler simultaneously
4. Analyze why traction low before pivoting

---

## NEXT ACTIONS FOR COO (Thomas)

**Thomas, I need from you (Week 1-2):**

1. **Day 8 (if on schedule):**
   - Verify bot works in your test Slack workspace
   - Report any bugs
   
2. **Day 10 (before launch):**
   - Create Stripe account (for payments)
   - Create ProductHunt account
   - Stand by for launch day support

3. **Day 11+ (operational):**
   - Monitor Slack DMs for user issues
   - Help debug any deployment problems
   - Track daily signup metrics

**Everything else is my job.**

---

**BUILD STARTING NOW**

I'm building this autonomously. You'll hear from me:
1. If I need account setup (payment, etc.)
2. On launch day (Day 11)
3. With daily metrics starting Week 2

**Current status:** Building Day 1 framework
