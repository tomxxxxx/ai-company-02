"""
Ticket Parser — reads company-os/tickets/*.md into structured data.

No LLM calls. Pure file parsing.
"""

import re
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

TICKETS_DIR = Path(__file__).parent.parent / "company-os" / "tickets"


def parse_metadata_table(content: str) -> dict:
    """Extract key-value pairs from a Markdown metadata table."""
    metadata = {}
    # Match rows like: | **Field** | Value |
    pattern = r"\|\s*\*\*(.+?)\*\*\s*\|\s*(.+?)\s*\|"
    for match in re.finditer(pattern, content):
        key = match.group(1).strip().lower().replace(" ", "_")
        value = match.group(2).strip()
        # Clean up backtick-wrapped values
        value = value.strip("`").strip()
        metadata[key] = value
    return metadata


def parse_acceptance_criteria(content: str) -> list[dict]:
    """Extract acceptance criteria checkboxes."""
    criteria = []
    in_section = False
    for line in content.split("\n"):
        if "Acceptance Criteria" in line:
            in_section = True
            continue
        if in_section and line.startswith("#"):
            break
        if in_section:
            check = re.match(r"- \[([ xX])\] (.+)", line)
            if check:
                criteria.append({
                    "done": check.group(1).lower() == "x",
                    "text": check.group(2).strip(),
                })
    return criteria


def parse_ticket(filepath: Path) -> Optional[dict]:
    """Parse a single ticket markdown file into structured data."""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        logger.error(f"Failed to read ticket {filepath}: {e}")
        return None

    metadata = parse_metadata_table(content)

    ticket = {
        "id": metadata.get("ticket_id", filepath.stem),
        "experiment": metadata.get("experiment", ""),
        "title": metadata.get("title", ""),
        "status": metadata.get("status", "BACKLOG"),
        "priority": metadata.get("priority", "P3-LOW"),
        "assignee": metadata.get("assignee", ""),
        "created": metadata.get("created", ""),
        "due": metadata.get("due", ""),
        "depends_on": metadata.get("depends_on", "None"),
        "blocks": metadata.get("blocks", "None"),
        "approval_level": _extract_approval(content),
        "acceptance_criteria": parse_acceptance_criteria(content),
        "source_file": str(filepath),
    }

    # Normalize "None" strings
    for key in ("depends_on", "blocks"):
        if ticket[key] in ("None", "none", "—", "-", ""):
            ticket[key] = None
        elif ticket[key]:
            # Extract ticket ID from values like "TICKET-001 (HTTP Mode Migration)"
            id_match = re.match(r"(TICKET-\d+)", ticket[key])
            if id_match:
                ticket[key] = id_match.group(1)

    return ticket


def _extract_approval(content: str) -> str:
    """Determine if ticket needs AUTO or HUMAN approval."""
    if "HUMAN" in content.split("Approval")[1] if "Approval" in content else "":
        return "HUMAN"
    # Check the approval table
    approval_match = re.search(
        r"\*\*Approval level\*\*\s*\|\s*(.+?)\s*\|", content, re.IGNORECASE
    )
    if approval_match:
        level = approval_match.group(1).strip()
        if "HUMAN" in level.upper():
            return "HUMAN"
        if "AUTO" in level.upper():
            return "AUTO"
    return "AUTO"


def load_all_tickets() -> list[dict]:
    """Load and parse all tickets from the tickets directory."""
    if not TICKETS_DIR.exists():
        logger.warning(f"Tickets directory not found: {TICKETS_DIR}")
        return []

    tickets = []
    for f in sorted(TICKETS_DIR.glob("*.md")):
        ticket = parse_ticket(f)
        if ticket:
            tickets.append(ticket)
            logger.debug(f"Parsed ticket: {ticket['id']} ({ticket['status']})")

    logger.info(f"Loaded {len(tickets)} tickets")
    return tickets


def get_ready_tickets(tickets: list[dict]) -> list[dict]:
    """Return tickets that are READY or BLOCKED-but-unblocked (dependencies met)."""
    done_ids = {t["id"] for t in tickets if t["status"] == "DONE"}

    ready = []
    for t in tickets:
        if t["status"] == "DONE":
            continue
        if t["status"] not in ("READY", "BLOCKED", "BACKLOG"):
            continue

        # Check dependency
        dep = t.get("depends_on")
        if dep and dep not in done_ids:
            # Still blocked
            continue

        # Dependency met (or no dependency) → this ticket is actionable
        ready.append(t)

    return ready


def get_blocked_tickets(tickets: list[dict]) -> list[dict]:
    """Return tickets that are BLOCKED or have unmet dependencies."""
    done_ids = {t["id"] for t in tickets if t["status"] == "DONE"}
    blocked = []
    for t in tickets:
        if t["status"] == "BLOCKED":
            blocked.append(t)
        elif t["status"] == "READY":
            dep = t.get("depends_on")
            if dep and dep not in done_ids:
                blocked.append(t)
    return blocked
