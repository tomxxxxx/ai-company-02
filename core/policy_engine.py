"""
Policy Engine — codifies risk-approval.md rules as executable Python.

No LLM calls. Pure rule evaluation.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


# ── Spending Policies ───────────────────────────────────────

def evaluate_spending(amount_eur: float, recurring: bool = False) -> str:
    """
    Evaluate a spending decision.
    
    Returns: "AUTO" | "HUMAN" | "HUMAN_JUSTIFICATION"
    """
    if recurring:
        if amount_eur < 10:
            return "AUTO"
        elif amount_eur <= 50:
            return "HUMAN"
        else:
            return "HUMAN_JUSTIFICATION"
    else:
        if amount_eur < 20:
            return "AUTO"
        elif amount_eur <= 100:
            return "HUMAN"
        else:
            return "HUMAN_JUSTIFICATION"


# ── Experiment Lifecycle Policies ────────────────────────────

def evaluate_experiment_start(initial_cost_eur: float, brief_complete: bool) -> str:
    """
    Can we start a new experiment?
    
    Returns: "AUTO" | "HUMAN" | "BLOCKED"
    """
    if not brief_complete:
        return "BLOCKED"
    if initial_cost_eur < 50:
        return "AUTO"
    return "HUMAN"


def evaluate_experiment_lifecycle(
    weeks_below_kill: int,
    current_verdict: str,
    strategic_concern: bool = False,
) -> str:
    """
    Should we KILL, CONTINUE, or SCALE an experiment?
    
    Returns: "KILL_AUTO" | "KILL_HUMAN" | "CONTINUE" | "SCALE_HUMAN"
    """
    if current_verdict == "SCALE":
        return "SCALE_HUMAN"  # Always human approval to increase spend

    if current_verdict == "KILL":
        if strategic_concern:
            return "KILL_HUMAN"
        if weeks_below_kill >= 2:
            return "KILL_AUTO"
        return "CONTINUE"  # Give it one more week

    return "CONTINUE"


# ── Technical Policies ──────────────────────────────────────

def evaluate_technical_decision(
    decision_type: str,
    breaking_change: bool = False,
    needs_account: bool = False,
) -> str:
    """
    Evaluate a technical decision.
    
    Returns: "AUTO" | "HUMAN" | "BLOCKED"
    """
    always_human = {"pricing_change", "delete_user_data", "new_account"}
    always_blocked = {"cold_outreach", "personal_contacts"}

    if decision_type in always_blocked:
        return "BLOCKED"
    if decision_type in always_human:
        return "HUMAN"
    if breaking_change:
        return "HUMAN"
    if needs_account:
        return "HUMAN"
    return "AUTO"


# ── Distribution Policies ───────────────────────────────────

def evaluate_distribution(channel: str) -> str:
    """
    Can we use this distribution channel?
    
    Returns: "AUTO" | "HUMAN" | "BLOCKED"
    """
    auto_channels = {"seo", "meta_tags", "content_optimization", "support_response"}
    human_channels = {"app_marketplace", "product_hunt", "social_account"}
    blocked_channels = {"cold_outreach", "personal_contacts", "linkedin_personal"}

    channel_lower = channel.lower().replace(" ", "_")

    if channel_lower in blocked_channels:
        return "BLOCKED"
    if channel_lower in human_channels:
        return "HUMAN"
    if channel_lower in auto_channels:
        return "AUTO"

    # Unknown channel — default to HUMAN
    logger.warning(f"Unknown distribution channel: {channel}, defaulting to HUMAN")
    return "HUMAN"


# ── Ticket Approval ─────────────────────────────────────────

def evaluate_ticket(ticket: dict) -> str:
    """
    Should this ticket be auto-approved, need human approval, or be blocked?
    
    Uses ticket metadata to check against policies.
    
    Returns: "AUTO" | "HUMAN" | "BLOCKED"
    """
    # Check for explicit approval level in ticket
    explicit = ticket.get("approval_level", "").upper()
    if explicit in ("HUMAN", "BLOCKED"):
        return explicit

    # Check assignee — if thomas is anywhere in the assignee field, needs human
    assignee = ticket.get("assignee", "").lower()
    if "thomas" in assignee:
        return "HUMAN"

    # Pure agent tickets are auto
    if any(a in assignee for a in ("builder-agent", "system-architect")):
        return "AUTO"

    # Default
    return "AUTO"


# ── Constraint Checks ───────────────────────────────────────

HARD_CONSTRAINTS = [
    "no_personal_contacts",
    "no_cold_outreach",
    "no_public_identity",
    "no_sales_calls",
    "anonymous_distribution_only",
    "konkurrenzklausel_compliance",
]


def check_constraints(action_description: str) -> list[str]:
    """
    Check if an action description violates any hard constraints.
    Returns list of violated constraints (empty = OK).
    
    Simple keyword matching — not perfect, but catches obvious violations.
    """
    violations = []
    desc = action_description.lower()

    personal_keywords = {"personal contact", "friend", "colleague", "network",
                         "reach out to", "ask someone", "invite people"}
    if any(kw in desc for kw in personal_keywords):
        violations.append("no_personal_contacts")

    outreach_keywords = {"cold email", "cold outreach", "cold message", "dm strangers"}
    if any(kw in desc for kw in outreach_keywords):
        violations.append("no_cold_outreach")

    identity_keywords = {"real name", "linkedin profile", "public identity",
                         "thomas's name"}
    if any(kw in desc for kw in identity_keywords):
        violations.append("no_public_identity")

    sales_keywords = {"sales call", "discovery call", "sell to", "pitch to"}
    if any(kw in desc for kw in sales_keywords):
        violations.append("no_sales_calls")

    return violations
