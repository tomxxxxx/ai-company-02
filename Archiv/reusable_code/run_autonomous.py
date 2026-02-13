#!/usr/bin/env python3
"""
AI Automation Lab — Autonomous Loop Entry Point.

Usage:
    python run_autonomous.py              # Run continuously until blocked
    python run_autonomous.py --single     # Run one iteration only
    python run_autonomous.py --delay 10   # Set delay between iterations (seconds)

The loop runs through 6 layers per iteration:
    Leitebene → Strategie → Planung → Delegation → Ausführung → Evaluation

It continues until a blocking Thomas-task is created,
then writes HUMAN_ACTION_NEEDED.md and exits.
"""

import argparse
import logging
import sys
from pathlib import Path

# Add workspace root to Python path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from core.autonomous.runner import AutonomousRunner


def setup_logging(verbose: bool = False):
    """Configure logging to console and file."""
    log_level = logging.DEBUG if verbose else logging.INFO

    # Console handler
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(log_level)
    console_fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    console.setFormatter(console_fmt)

    # File handler
    log_dir = ROOT / "data" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(
        log_dir / "autonomous_loop.log",
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    file_handler.setFormatter(file_fmt)

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console)
    root_logger.addHandler(file_handler)

    # Reduce noise from HTTP libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("anthropic").setLevel(logging.WARNING)


def main():
    parser = argparse.ArgumentParser(
        description="AI Automation Lab — Autonomous Loop",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--single",
        action="store_true",
        help="Run one iteration only (useful for testing)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=5.0,
        help="Seconds to wait between iterations (default: 5)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable debug-level logging",
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=0,
        help="Stop after N iterations (default: 0 = unlimited)",
    )

    args = parser.parse_args()
    setup_logging(verbose=args.verbose)

    logger = logging.getLogger(__name__)
    logger.info("AI Automation Lab — Autonomous Loop")
    logger.info(f"Mode: {'single iteration' if args.single else 'continuous'}")
    if args.max_iterations > 0:
        logger.info(f"Max iterations: {args.max_iterations}")

    try:
        runner = AutonomousRunner(delay_between_iterations=args.delay)

        if args.single:
            state = runner.run_single()
            logger.info(f"Single iteration complete. Cost: ${state.total_cost_usd:.4f}")
            if state.blocked:
                logger.info(f"Blocked: {state.blocking_reason}")
        else:
            runner.run_continuous(max_iterations=args.max_iterations)

    except KeyboardInterrupt:
        logger.info("Shutdown requested. Bye.")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
