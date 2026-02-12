#!/usr/bin/env python3
"""
Scheduler - Runs the orchestrator on a timer.

Usage:
    python scheduler.py              # Run once
    python scheduler.py --loop       # Run every INTERVAL seconds
    python scheduler.py --loop --interval 3600   # Every hour (default)

This is the entry point for autonomous operation.
Thomas starts this once, then the company runs itself.
"""

import sys
import os
import time
import logging
import argparse
import json
from pathlib import Path
from datetime import datetime, timezone

# Add project root to path
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

LOG_DIR = ROOT / "data"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_DIR / "scheduler.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("scheduler")


def run_once():
    """Run a single orchestration cycle."""
    from core.orchestrator import run_cycle

    logger.info("=" * 40)
    logger.info("SCHEDULER: Starting cycle")
    logger.info("=" * 40)

    try:
        state = run_cycle()

        # Log cycle result
        result = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "cycle": state.get("cycle_count", 0),
            "phase": state.get("current_phase", "unknown"),
            "mrr": state.get("metrics", {}).get("mrr", 0),
            "capital": state.get("financials", {}).get("current_capital", 0),
            "success": True,
        }

        with open(LOG_DIR / "cycle_history.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(result) + "\n")

        logger.info(f"SCHEDULER: Cycle #{result['cycle']} complete")
        return True

    except Exception as e:
        logger.error(f"SCHEDULER: Cycle failed: {e}", exc_info=True)

        error_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e),
            "success": False,
        }
        with open(LOG_DIR / "cycle_history.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(error_entry) + "\n")

        return False


def run_loop(interval: int = 3600, max_cycles: int = 0):
    """Run orchestrator in a loop."""
    logger.info(f"SCHEDULER: Starting loop mode (interval={interval}s)")
    cycle = 0

    while True:
        cycle += 1
        logger.info(f"SCHEDULER: Loop cycle {cycle}")

        success = run_once()

        if max_cycles > 0 and cycle >= max_cycles:
            logger.info(f"SCHEDULER: Reached max cycles ({max_cycles}), stopping")
            break

        if not success:
            # Back off on failure
            wait = min(interval * 2, 7200)  # Max 2 hours backoff
            logger.warning(f"SCHEDULER: Cycle failed, backing off {wait}s")
            time.sleep(wait)
        else:
            logger.info(f"SCHEDULER: Sleeping {interval}s until next cycle...")
            time.sleep(interval)


def main():
    parser = argparse.ArgumentParser(description="AI Company Scheduler")
    parser.add_argument("--loop", action="store_true", help="Run in continuous loop")
    parser.add_argument("--interval", type=int, default=3600, help="Seconds between cycles (default: 3600 = 1h)")
    parser.add_argument("--max-cycles", type=int, default=0, help="Max cycles before stopping (0 = infinite)")
    args = parser.parse_args()

    if args.loop:
        run_loop(interval=args.interval, max_cycles=args.max_cycles)
    else:
        run_once()


if __name__ == "__main__":
    main()
