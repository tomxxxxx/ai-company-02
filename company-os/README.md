# Company OS — AI Automation Lab

Operational system for spawning, validating, scaling, and killing business experiments.

## Directory Structure

```
company-os/
├── README.md                  # This file
├── experiment-engine.md       # Core loop: generate → score → build → validate → kill/scale
├── templates/                 # Reusable templates for all experiments
│   ├── experiment-brief.md    # How to define a new experiment
│   ├── kpi-scorecard.md       # How to measure an experiment
│   └── work-ticket.md         # How to define a unit of work
├── policies/                  # Decision-making rules
│   └── risk-approval.md       # What's auto-approved vs escalated
├── experiments/               # One file per experiment (numbered)
│   ├── 001-taskmaster-slack-bot.md
│   └── 001-scorecard.md
├── tickets/                   # Active work tickets
│   ├── 001-http-mode-migration.md
│   └── 002-app-directory-submission.md
├── schemas/                   # JSON schemas for structured data
│   └── experiment-state.schema.json
└── logs/                      # Cycle logs and audit trail
    └── .gitkeep
```

## How It Works

1. **New idea** → Score via `experiment-engine.md` matrix (≥28/45 to proceed)
2. **Approved idea** → Fill `templates/experiment-brief.md` → gets an experiment number
3. **Work to do** → Create `templates/work-ticket.md` → assign to agent or Thomas
4. **Running experiment** → Track via `templates/kpi-scorecard.md` weekly
5. **Decisions** → Check `policies/risk-approval.md` → auto-approve or escalate to Thomas
6. **Kill/Scale** → Policy-driven based on scorecard thresholds (2 weeks below = auto-kill)
7. **Audit** → All state changes tracked in `logs/` and git history

## Roles

| Role | Scope | Examples |
|------|-------|---------|
| System Architect (AI) | Builds OS, templates, schemas, proposes experiments | This system |
| Human Operator (Thomas) | Approves escalations, creates accounts, tests products | Stripe setup, beta testing |
| Agents (AI) | Execute tickets within defined scope | Code generation, analysis |

## Rules

- No unilateral business decisions by AI agents
- All decisions traceable to a policy or human approval
- Experiments are numbered sequentially
- Dead experiments stay in `experiments/` with status `KILLED` (never deleted)
