"""Utility helpers for TaskMaster Slack Bot."""

import re
from typing import Optional


def validate_task_description(description: str, max_length: int = 500) -> bool:
    """Return True if the description is non-empty and within the limit."""
    if not description or not description.strip():
        return False
    return len(description.strip()) <= max_length


def validate_task_id(raw: str) -> Optional[int]:
    """Parse a task-id string (e.g. '5' or '#5'). Returns int or None."""
    if not raw:
        return None
    raw = raw.strip().lstrip("#")
    try:
        tid = int(raw)
        return tid if tid > 0 else None
    except ValueError:
        match = re.search(r"(\d+)", raw)
        return int(match.group(1)) if match else None


def escape_slack(text: str) -> str:
    """Escape &, <, > for Slack mrkdwn."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")