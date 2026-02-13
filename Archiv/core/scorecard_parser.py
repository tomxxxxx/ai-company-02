"""
Scorecard Parser — reads company-os/experiments/*-scorecard.md into structured data.

No LLM calls. Pure file parsing.
"""

import re
import logging
from pathlib import Path
from datetime import date, datetime
from typing import Optional

logger = logging.getLogger(__name__)

EXPERIMENTS_DIR = Path(__file__).parent.parent / "company-os" / "experiments"


def parse_scorecard(filepath: Path) -> Optional[dict]:
    """Parse a scorecard markdown file into structured data."""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        logger.error(f"Failed to read scorecard {filepath}: {e}")
        return None

    metadata = _parse_metadata_table(content)

    scorecard = {
        "id": metadata.get("experiment_id", ""),
        "name": metadata.get("name", ""),
        "status": metadata.get("current_status", "").strip("`"),
        "kill_date": _parse_date(metadata.get("kill_date", "")),
        "week": _parse_int(metadata.get("week", "0")),
        "thresholds": _parse_thresholds(content),
        "current_verdict": _parse_verdict(content),
        "source_file": str(filepath),
    }

    return scorecard


def _parse_metadata_table(content: str) -> dict:
    """Extract key-value pairs from metadata table."""
    metadata = {}
    pattern = r"\|\s*\*\*(.+?)\*\*\s*\|\s*(.+?)\s*\|"
    for match in re.finditer(pattern, content):
        key = match.group(1).strip().lower().replace(" ", "_")
        value = match.group(2).strip()
        metadata[key] = value
    return metadata


def _parse_date(date_str: str) -> Optional[date]:
    """Parse a date string, return None if invalid."""
    date_str = date_str.strip()
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    return None


def _parse_int(value: str) -> int:
    """Parse an integer, default to 0."""
    try:
        return int(re.sub(r"[^\d]", "", value) or "0")
    except ValueError:
        return 0


def _parse_thresholds(content: str) -> dict:
    """Parse the Kill/Continue/Scale Assessment table."""
    thresholds = {}
    # Look for rows in the assessment table
    # Format: | Criterion | Kill Threshold | Scale Threshold | Actual | Verdict |
    pattern = r"\|\s*(.+?)\s*\|\s*[<>]?\s*(\d+)\s*\|\s*[<>]?\s*(\d+)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|"
    for match in re.finditer(pattern, content):
        criterion = match.group(1).strip()
        if criterion.lower() in ("criterion", "---"):
            continue
        thresholds[criterion] = {
            "kill": _parse_int(match.group(2)),
            "scale": _parse_int(match.group(3)),
            "actual": match.group(4).strip(),
            "verdict": match.group(5).strip(),
        }
    return thresholds


def _parse_verdict(content: str) -> str:
    """Extract the overall verdict (KILL/CONTINUE/SCALE)."""
    verdict_match = re.search(
        r"\*\*This Week's Verdict:\*\*\s*(.*)", content
    )
    if verdict_match:
        text = verdict_match.group(1).strip()
        if "KILL" in text.upper():
            return "KILL"
        if "SCALE" in text.upper():
            return "SCALE"
        if "CONTINUE" in text.upper():
            return "CONTINUE"
    return "UNKNOWN"


def load_all_scorecards() -> list[dict]:
    """Load and parse all scorecards."""
    if not EXPERIMENTS_DIR.exists():
        logger.warning(f"Experiments directory not found: {EXPERIMENTS_DIR}")
        return []

    scorecards = []
    for f in sorted(EXPERIMENTS_DIR.glob("*-scorecard.md")):
        sc = parse_scorecard(f)
        if sc:
            scorecards.append(sc)
            logger.debug(f"Parsed scorecard: {sc['id']} ({sc['status']})")

    logger.info(f"Loaded {len(scorecards)} scorecards")
    return scorecards


def evaluate_experiment(scorecard: dict, today: Optional[date] = None) -> str:
    """
    Evaluate experiment health based on scorecard data and kill date.
    
    Returns: "KILL" | "CONTINUE" | "SCALE" | "TOO_EARLY"
    """
    today = today or date.today()
    kill_date = scorecard.get("kill_date")

    # If no kill date, can't auto-evaluate
    if not kill_date:
        return "CONTINUE"

    # If past kill date, check thresholds
    if today >= kill_date:
        verdict = scorecard.get("current_verdict", "UNKNOWN")
        if verdict == "SCALE":
            return "SCALE"
        # At or past kill date without SCALE verdict = KILL
        return "KILL"

    # Before kill date — use current verdict
    verdict = scorecard.get("current_verdict", "UNKNOWN")
    if verdict in ("KILL", "SCALE"):
        return verdict

    return "CONTINUE"
