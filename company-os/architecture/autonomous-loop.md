# Company OS — Autonomous Loop Architecture

> This spec defines how the Company OS runs WITHOUT human prompting.
> Thomas starts the scheduler once. The system runs itself.

---

## Current State (broken)

```
scheduler.py --loop
  └→ orchestrator.run_cycle()
       └→ CEO Agent (LLM prompt → prose narrative)
       └→ CTO Agent (LLM prompt → prose narrative)
       └→ Builder Agent (LLM prompt → maybe writes files)
       └→ Save state + generate thomas_tasks.md
```

**Problems:**
1. Agents produce free-form narrative, not structured actions
2. No connection to Company OS artifacts (tickets, scorecards, policies)
3. Each cycle costs ~$0.10–0.30 in API calls with no clear output
4. Thomas still has to read output and decide what to do
5. Nothing actually gets done autonomously

---

## Target State (v2)

```
scheduler.py --loop --interval 86400   (runs daily)
  └→ orchestrator_v2.run_cycle()
       │
       ├→ Phase 1: READ STATE (no LLM, no cost)
       │    ├→ Read all tickets from company-os/tickets/
       │    ├→ Read all scorecards from company-os/experiments/
       │    ├→ Read risk-approval.md policies
       │    └→ Parse → structured data
       │
       ├→ Phase 2: EVALUATE (rules engine, no LLM)
       │    ├→ Any ticket READY with no blockers? → queue for execution
       │    ├→ Any scorecard past kill date? → auto-kill per policy
       │    ├→ Any experiment below threshold 2+ weeks? → auto-kill
       │    ├→ Active experiments < 2 and no work? → flag for idea generation
       │    └→ Any escalation needed? → queue for human packet
       │
       ├→ Phase 3: EXECUTE (LLM only for code generation)
       │    ├→ For each queued ticket:
       │    │    ├→ assignee = builder-agent? → LLM generates code
       │    │    ├→ assignee = system-architect? → LLM generates artifact
       │    │    ├→ assignee = thomas? → add to escalation queue
       │    │    └→ Mark ticket IN-PROGRESS → DONE or BLOCKED
       │    └→ For idea generation:
       │         └→ LLM brainstorm → score via matrix → file as DRAFT briefs
       │
       ├→ Phase 4: WRITE (no LLM)
       │    ├→ Update ticket statuses
       │    ├→ Update scorecards
       │    ├→ Write weekly review log
       │    ├→ Generate decision packets for Thomas (if any)
       │    └→ Git commit all changes
       │
       └→ Phase 5: NOTIFY (optional, no LLM)
            └→ If escalation queue non-empty → write HUMAN_ACTION_NEEDED.md
```

---

## Key Design Principles

### 1. LLM calls are expensive — rules are free
- Phase 1 (read) and Phase 2 (evaluate) use ZERO LLM calls
- Parse markdown files with regex/structured parsing
- Only call LLM when generating new code or content (Phase 3)
- Target: most daily cycles cost $0 (nothing to do = no LLM calls)

### 2. Tickets drive everything
- No agent does anything without a ticket
- Ticket = input specification + acceptance criteria
- Agent output = files in the repo + ticket status update
- If there's no ticket in READY state, the cycle does nothing (and costs nothing)

### 3. Policies are code, not prompts
- `risk-approval.md` rules → Python `if/else` in evaluator
- Kill thresholds → parsed from scorecard, compared numerically
- No LLM needed to decide "should we kill this experiment?"

### 4. Human-in-the-loop, not human-in-the-prompt
- Thomas checks `HUMAN_ACTION_NEEDED.md` when he has time
- He responds by editing the file or creating/updating tickets
- The system picks up his changes on the next cycle
- No chat session required

---

## File Structure Changes

```
core/
├── orchestrator.py      → orchestrator_v2.py (rewrite)
├── ticket_parser.py     → NEW: reads tickets/ into structured data
├── scorecard_parser.py  → NEW: reads scorecards into structured data
├── policy_engine.py     → NEW: evaluates rules from risk-approval.md
├── cycle_runner.py      → NEW: phases 1-5 execution
├── state.py             → keep (financial state)
├── llm.py               → keep (used only in Phase 3)
└── agent.py             → keep (base class)

agents/
├── builder_agent.py     → REFACTOR: takes structured ticket, produces files
├── architect_agent.py   → NEW: generates templates, specs, briefs
└── (ceo_agent.py)       → DEPRECATE: replaced by policy_engine
└── (cto_agent.py)       → DEPRECATE: replaced by ticket system
```

---

## Migration Path (incremental, not big-bang)

### Step 1: Ticket Parser (no risk, additive)
Build `core/ticket_parser.py` that reads `company-os/tickets/*.md` and returns:
```python
[
  {"id": "TICKET-001", "status": "READY", "assignee": "builder-agent", 
   "depends_on": None, "blocks": "TICKET-002", ...},
  ...
]
```

### Step 2: Scorecard Parser (no risk, additive)
Build `core/scorecard_parser.py` that reads experiment scorecards and returns:
```python
[
  {"id": "EXP-001", "status": "VALIDATING", "kill_date": "2026-03-26",
   "current_metrics": {...}, "thresholds": {...}, "verdict": "CONTINUE"},
  ...
]
```

### Step 3: Policy Engine (no risk, additive)
Build `core/policy_engine.py` that codifies `risk-approval.md` rules:
```python
def evaluate_ticket(ticket, policies) -> "AUTO" | "HUMAN" | "BLOCKED"
def evaluate_experiment(scorecard, policies) -> "KILL" | "CONTINUE" | "SCALE"
```

### Step 4: Cycle Runner v2 (replaces old orchestrator)
Wire steps 1-3 together into the 5-phase loop above.

### Step 5: Refactor Builder Agent
Input: structured ticket dict (not free-form state blob)
Output: files written + ticket status update

### Step 6: Deploy Loop
`scheduler.py --loop --interval 86400` on Railway or local cron.
Thomas starts it once. Checks `HUMAN_ACTION_NEEDED.md` daily.

---

## Cost Model

| Scenario | LLM Calls | Estimated Cost |
|----------|-----------|---------------|
| Nothing to do (no READY tickets) | 0 | $0.00 |
| Weekly scorecard review | 0 | $0.00 (pure rules) |
| Execute 1 code ticket | 1–3 | $0.05–0.15 |
| Generate 10 experiment ideas + score | 1 | $0.05–0.10 |
| Full cycle with idea gen + ticket exec | 2–5 | $0.10–0.25 |

**Monthly estimate (1 cycle/day):** $0.50–3.00 vs current ~$3–9/month

---

## What Thomas's Daily Interaction Looks Like (target)

```
Morning:
1. Open HUMAN_ACTION_NEEDED.md (if it exists)
2. See: "TICKET-002 needs you: set Redirect URL in Slack Dashboard (5 min)"
3. Do it
4. Edit ticket status → DONE
5. Delete HUMAN_ACTION_NEEDED.md
6. Done. ~10 min.

If no HUMAN_ACTION_NEEDED.md exists → nothing to do.
```

---

## Implementation Priority

| Step | Ticket | Effort | Blocks |
|------|--------|--------|--------|
| 1. Ticket Parser | TICKET-003 | 2h | Step 4 |
| 2. Scorecard Parser | TICKET-004 | 2h | Step 4 |
| 3. Policy Engine | TICKET-005 | 3h | Step 4 |
| 4. Cycle Runner v2 | TICKET-006 | 4h | Step 5, 6 |
| 5. Builder Agent refactor | TICKET-007 | 3h | Step 6 |
| 6. Deploy loop | TICKET-008 | 1h | — |

**Total: ~15h of development.** Can be done by builder agent over ~3–5 cycles, 
or by Thomas in ~2–3 sessions if he prefers to build it himself.
