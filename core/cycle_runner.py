"""
Cycle Runner v2 — The autonomous Company OS loop.

Phases:
1. READ   — parse tickets, scorecards, policies (no LLM, $0)
2. EVAL   — apply rules engine to determine actions (no LLM, $0)
3. EXEC   — execute actions, use LLM only for code generation
4. WRITE  — update tickets, scorecards, logs
5. NOTIFY — write HUMAN_ACTION_NEEDED.md if escalation needed

Usage:
    python -m core.cycle_runner           # Single cycle
    python -m core.cycle_runner --loop    # Daily loop
    python -m core.cycle_runner --dry-run # Show what would happen, change nothing
"""

import json
import logging
import argparse
import time
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Optional

from core.ticket_parser import load_all_tickets, get_ready_tickets, get_blocked_tickets
from core.scorecard_parser import load_all_scorecards, evaluate_experiment
from core.policy_engine import evaluate_ticket, evaluate_experiment_lifecycle, check_constraints
from core.ticket_executor import TicketExecutor

logger = logging.getLogger(__name__)

ROOT = Path(__file__).parent.parent
COMPANY_OS = ROOT / "company-os"
LOGS_DIR = COMPANY_OS / "logs"
HUMAN_FILE = ROOT / "HUMAN_ACTION_NEEDED.md"


class CycleResult:
    """Structured output of a single cycle."""

    def __init__(self):
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.tickets_total = 0
        self.tickets_ready = 0
        self.tickets_executed = 0
        self.experiments_evaluated = 0
        self.escalations: list[dict] = []
        self.actions_taken: list[str] = []
        self.llm_calls = 0
        self.cost_estimate_usd = 0.0
        self.errors: list[str] = []

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "tickets": {
                "total": self.tickets_total,
                "ready": self.tickets_ready,
                "executed": self.tickets_executed,
            },
            "experiments_evaluated": self.experiments_evaluated,
            "escalations": len(self.escalations),
            "actions_taken": self.actions_taken,
            "llm_calls": self.llm_calls,
            "cost_usd": self.cost_estimate_usd,
            "errors": self.errors,
        }

    def summary(self) -> str:
        lines = [
            f"=== CYCLE RESULT ({self.timestamp}) ===",
            f"Tickets: {self.tickets_ready} ready / {self.tickets_total} total / {self.tickets_executed} executed",
            f"Experiments evaluated: {self.experiments_evaluated}",
            f"Escalations: {len(self.escalations)}",
            f"LLM calls: {self.llm_calls} (~${self.cost_estimate_usd:.2f})",
        ]
        if self.actions_taken:
            lines.append("Actions:")
            for a in self.actions_taken:
                lines.append(f"  - {a}")
        if self.escalations:
            lines.append("Escalations for Thomas:")
            for e in self.escalations:
                lines.append(f"  - [{e['ticket_id']}] {e['reason']}")
        if self.errors:
            lines.append("Errors:")
            for e in self.errors:
                lines.append(f"  ! {e}")
        return "\n".join(lines)


# ── Phase 1: READ ────────────────────────────────────────────

def phase_read() -> dict:
    """Read all Company OS state. No LLM. $0."""
    logger.info("Phase 1: READ")

    tickets = load_all_tickets()
    scorecards = load_all_scorecards()

    return {
        "tickets": tickets,
        "ready_tickets": get_ready_tickets(tickets),
        "blocked_tickets": get_blocked_tickets(tickets),
        "scorecards": scorecards,
    }


# ── Phase 2: EVALUATE ───────────────────────────────────────

def phase_evaluate(state: dict, result: CycleResult) -> dict:
    """Apply rules to determine what should happen. No LLM. $0."""
    logger.info("Phase 2: EVALUATE")

    actions = []
    escalations = []

    result.tickets_total = len(state["tickets"])
    result.tickets_ready = len(state["ready_tickets"])

    # Evaluate each ready ticket
    for ticket in state["ready_tickets"]:
        approval = evaluate_ticket(ticket)
        if approval == "AUTO":
            actions.append({"type": "execute_ticket", "ticket": ticket})
            logger.info(f"  Ticket {ticket['id']}: AUTO → queue for execution")
        elif approval == "HUMAN":
            escalations.append({
                "ticket_id": ticket["id"],
                "title": ticket.get("title", ""),
                "reason": f"Ticket needs human action (assignee: {ticket.get('assignee', '?')})",
                "action": ticket.get("title", "See ticket for details"),
            })
            logger.info(f"  Ticket {ticket['id']}: HUMAN → escalate")
        elif approval == "BLOCKED":
            logger.info(f"  Ticket {ticket['id']}: BLOCKED → skip")

    # Evaluate each experiment scorecard
    today = date.today()
    for sc in state["scorecards"]:
        verdict = evaluate_experiment(sc, today)
        result.experiments_evaluated += 1

        if verdict == "KILL":
            escalations.append({
                "ticket_id": sc["id"],
                "title": f"Experiment {sc['name']} hit KILL threshold",
                "reason": f"Kill date reached or below thresholds for 2+ weeks",
                "action": "Confirm kill or override with CONTINUE",
            })
            logger.info(f"  Experiment {sc['id']}: KILL → escalate")
        elif verdict == "SCALE":
            escalations.append({
                "ticket_id": sc["id"],
                "title": f"Experiment {sc['name']} ready to SCALE",
                "reason": "Above scale thresholds",
                "action": "Approve increased investment",
            })
            logger.info(f"  Experiment {sc['id']}: SCALE → escalate")
        else:
            logger.info(f"  Experiment {sc['id']}: {verdict} → no action")

    result.escalations = escalations

    return {
        **state,
        "actions": actions,
        "escalations": escalations,
    }


# ── Phase 3: EXECUTE ────────────────────────────────────────

def phase_execute(state: dict, result: CycleResult, dry_run: bool = False) -> dict:
    """Execute queued actions. LLM only if code generation needed."""
    logger.info("Phase 3: EXECUTE")

    for action in state.get("actions", []):
        if action["type"] == "execute_ticket":
            ticket = action["ticket"]
            assignee = ticket.get("assignee", "").lower()

            if dry_run:
                result.actions_taken.append(
                    f"[DRY RUN] Would execute {ticket['id']}: {ticket.get('title', '')}"
                )
                continue

            if any(a in assignee for a in ("builder-agent", "system-architect")):
                # Execute via TicketExecutor
                logger.info(f"  Executing {ticket['id']} via TicketExecutor...")
                executor = TicketExecutor()
                exec_result = executor.execute(ticket)

                result.llm_calls += exec_result.get("llm_calls", 0)
                result.cost_estimate_usd += exec_result.get("llm_calls", 0) * 0.10

                if exec_result["success"]:
                    files = exec_result.get("files_written", [])
                    result.actions_taken.append(
                        f"Executed {ticket['id']}: wrote {len(files)} files"
                    )
                    logger.info(f"  {ticket['id']} DONE — {len(files)} files written")
                else:
                    errors = exec_result.get("errors", [])
                    result.errors.extend(errors)
                    result.actions_taken.append(
                        f"FAILED {ticket['id']}: {'; '.join(errors)}"
                    )
                    logger.error(f"  {ticket['id']} FAILED: {errors}")

            elif "thomas" in assignee:
                # Human ticket — should have been escalated in Phase 2
                result.actions_taken.append(
                    f"Ticket {ticket['id']} is for Thomas — escalating"
                )
            else:
                result.actions_taken.append(
                    f"Ticket {ticket['id']} has unknown assignee: {assignee}"
                )

            result.tickets_executed += 1

    return state


# ── Phase 4: WRITE ──────────────────────────────────────────

def phase_write(state: dict, result: CycleResult, dry_run: bool = False):
    """Update tickets, scorecards, write logs. No LLM. $0."""
    logger.info("Phase 4: WRITE")

    if dry_run:
        logger.info("  [DRY RUN] Skipping writes")
        return

    # Write cycle log
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    today_str = date.today().isoformat()
    log_file = LOGS_DIR / f"{today_str}-cycle.json"

    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)

    result.actions_taken.append(f"Wrote cycle log: {log_file.name}")
    logger.info(f"  Wrote cycle log: {log_file}")


# ── Phase 5: NOTIFY ─────────────────────────────────────────

def phase_notify(state: dict, result: CycleResult, dry_run: bool = False):
    """Write HUMAN_ACTION_NEEDED.md if escalations exist. No LLM. $0."""
    logger.info("Phase 5: NOTIFY")

    if not result.escalations:
        # Clean up old notification if nothing needed
        if HUMAN_FILE.exists() and not dry_run:
            HUMAN_FILE.unlink()
            logger.info("  No escalations — removed HUMAN_ACTION_NEEDED.md")
        return

    if dry_run:
        logger.info(f"  [DRY RUN] Would write {len(result.escalations)} escalations")
        return

    lines = [
        "# HUMAN ACTION NEEDED",
        "",
        f"*Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}*",
        "",
        "Items below need your attention. After handling, delete this file or mark items done.",
        "",
        "---",
        "",
    ]

    for i, esc in enumerate(result.escalations, 1):
        lines.extend([
            f"## {i}. [{esc['ticket_id']}] {esc.get('title', '')}",
            "",
            f"**Reason:** {esc['reason']}",
            f"**Action:** {esc['action']}",
            f"**Ticket:** `company-os/tickets/` or `company-os/experiments/`",
            "",
            f"- [ ] Done",
            "",
        ])

    content = "\n".join(lines)

    with open(HUMAN_FILE, "w", encoding="utf-8") as f:
        f.write(content)

    result.actions_taken.append(f"Wrote HUMAN_ACTION_NEEDED.md ({len(result.escalations)} items)")
    logger.info(f"  Wrote HUMAN_ACTION_NEEDED.md with {len(result.escalations)} escalations")


# ── Main Cycle ──────────────────────────────────────────────

def run_cycle(dry_run: bool = False) -> CycleResult:
    """Run one complete autonomous cycle."""
    result = CycleResult()

    logger.info("=" * 50)
    logger.info("COMPANY OS CYCLE STARTING")
    logger.info(f"  Date: {date.today().isoformat()}")
    logger.info(f"  Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    logger.info("=" * 50)

    try:
        # Phase 1: Read state (no LLM, $0)
        state = phase_read()

        # Phase 2: Evaluate rules (no LLM, $0)
        state = phase_evaluate(state, result)

        # Phase 3: Execute actions (LLM only if code gen)
        state = phase_execute(state, result, dry_run)

        # Phase 4: Write updates (no LLM, $0)
        phase_write(state, result, dry_run)

        # Phase 5: Notify human (no LLM, $0)
        phase_notify(state, result, dry_run)

    except Exception as e:
        result.errors.append(str(e))
        logger.error(f"Cycle failed: {e}", exc_info=True)

    logger.info(result.summary())
    return result


def run_loop(interval: int = 86400, max_cycles: int = 0):
    """Run cycles on a timer (default: daily)."""
    logger.info(f"Starting autonomous loop (interval={interval}s)")
    cycle = 0

    while True:
        cycle += 1
        result = run_cycle()

        # Log result
        cycle_log = {
            "cycle": cycle,
            **result.to_dict(),
        }
        log_file = ROOT / "data" / "cycle_history.jsonl"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(cycle_log) + "\n")

        if max_cycles > 0 and cycle >= max_cycles:
            logger.info(f"Reached max cycles ({max_cycles}), stopping")
            break

        logger.info(f"Sleeping {interval}s until next cycle...")
        time.sleep(interval)


# ── CLI ─────────────────────────────────────────────────────

def main():
    logging.basicConfig(
        level="INFO",
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )

    parser = argparse.ArgumentParser(description="Company OS Autonomous Cycle Runner")
    parser.add_argument("--loop", action="store_true", help="Run in continuous daily loop")
    parser.add_argument("--interval", type=int, default=86400, help="Seconds between cycles (default: 86400 = 24h)")
    parser.add_argument("--max-cycles", type=int, default=0, help="Max cycles (0 = infinite)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen, change nothing")
    args = parser.parse_args()

    if args.loop:
        run_loop(interval=args.interval, max_cycles=args.max_cycles)
    else:
        result = run_cycle(dry_run=args.dry_run)
        print(result.summary())


if __name__ == "__main__":
    main()
