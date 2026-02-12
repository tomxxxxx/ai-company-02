"""
Orchestrator - Main coordination loop for the AI company.

This is the entry point. It:
1. Loads company state
2. Runs all agents in sequence
3. Generates a consolidated report
4. Saves state
5. Creates task list for Thomas (COO)

Usage:
    python -m core.orchestrator           # Single cycle
    python -m core.orchestrator --loop    # Continuous (hourly)
    python -m core.orchestrator --status  # Just print status
"""

import sys
import os
import time
import logging
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from core.llm import LLM
from core.state import load_state, save_state, get_status_report, log_decision
from agents.ceo_agent import CEOAgent
from agents.cto_agent import CTOAgent
from agents.builder_agent import BuilderAgent

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(
            Path(__file__).parent.parent / "data" / "orchestrator.log",
            encoding="utf-8",
        ),
    ],
)
logger = logging.getLogger("orchestrator")


def ensure_data_dir():
    """Ensure data directory exists."""
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)


def run_cycle():
    """Run one complete orchestration cycle."""
    ensure_data_dir()
    logger.info("=" * 50)
    logger.info("ORCHESTRATION CYCLE STARTING")
    logger.info("=" * 50)

    # Load state
    state = load_state()
    state["cycle_count"] = state.get("cycle_count", 0) + 1

    # Initialize LLM
    llm = LLM()

    if not llm.available:
        logger.error("No LLM available! Configure API keys in .env")
        logger.error("Copy .env.example to .env and add your API key")
        print("\n❌ ERROR: No API key configured.")
        print("   1. Copy .env.example to .env")
        print("   2. Add ANTHROPIC_API_KEY or OPENAI_API_KEY")
        print("   3. Run again")
        return state

    logger.info(f"LLM Provider: {llm.provider}")
    logger.info(f"Cycle #{state['cycle_count']}")

    # Run agents
    agents = [
        CEOAgent(llm=llm),
        CTOAgent(llm=llm),
        BuilderAgent(llm=llm),
    ]

    for agent in agents:
        try:
            logger.info(f"Running agent: {agent.name}")
            state = agent.run(state)
            logger.info(f"Agent {agent.name} completed")
        except Exception as e:
            logger.error(f"Agent {agent.name} failed: {e}", exc_info=True)

    # Generate consolidated report
    report = generate_report(state, llm)

    # Save state
    save_state(state)

    # Print report
    print(report)

    # Save report to file
    report_file = Path(__file__).parent.parent / "data" / "latest_report.txt"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)

    # Generate Thomas task file
    generate_thomas_tasks(state, llm)

    logger.info("ORCHESTRATION CYCLE COMPLETE")
    return state


def generate_report(state: dict, llm: LLM) -> str:
    """Generate consolidated status report."""
    status = get_status_report(state)
    ceo_analysis = state.get("_ceo_analysis", "No CEO analysis available")
    ceo_tasks = state.get("_ceo_tasks", {})
    cto_plan = state.get("_cto_build_plan", {})

    report = f"""
{'=' * 60}
  AI AUTOMATION LAB - BUSINESS REPORT
  Cycle #{state.get('cycle_count', 0)}
{'=' * 60}

{status}

=== CEO ANALYSIS ===
{ceo_analysis}

=== CEO PRIORITIES ===
{format_dict(ceo_tasks)}

=== CTO BUILD PLAN ===
{format_dict(cto_plan)}

=== NEXT ACTIONS ===
Check data/thomas_tasks.md for operator tasks.
{'=' * 60}
"""
    return report


def generate_thomas_tasks(state: dict, llm: LLM):
    """Generate clear task list for Thomas (COO)."""
    ceo_tasks = state.get("_ceo_tasks", {})
    cto_plan = state.get("_cto_build_plan", {})

    # Use LLM to generate clear human-readable tasks
    if llm.available:
        task_prompt = f"""
Based on these agent outputs:

CEO priorities: {ceo_tasks}
CTO build plan: {cto_plan}
Current phase: {state.get('current_phase', 'unknown')}

Generate a clear task list for Thomas (the human operator/COO).

Rules:
- Thomas is a developer, not a salesperson
- Thomas has ~1 hour/day
- Tasks must be specific, actionable, no interpretation needed
- Only include tasks that REQUIRE a human (accounts, payments, testing, deployment)
- If no human tasks needed, say so

Format as Markdown with checkboxes.
"""
        tasks_md = llm.ask(task_prompt)
    else:
        tasks_md = "# No LLM available - cannot generate tasks\n\nConfigure API keys in .env"

    tasks_file = Path(__file__).parent.parent / "data" / "thomas_tasks.md"
    with open(tasks_file, "w", encoding="utf-8") as f:
        f.write(f"# Tasks for Thomas (COO)\n")
        f.write(f"# Generated: Cycle #{state.get('cycle_count', 0)}\n\n")
        f.write(tasks_md)

    logger.info("Thomas tasks generated")


def format_dict(d: dict, indent: int = 0) -> str:
    """Format a dict for human-readable output."""
    if not isinstance(d, dict):
        return str(d)
    lines = []
    for key, value in d.items():
        if key.startswith("_"):
            continue
        if isinstance(value, dict):
            lines.append(f"{'  ' * indent}{key}:")
            lines.append(format_dict(value, indent + 1))
        elif isinstance(value, list):
            lines.append(f"{'  ' * indent}{key}:")
            for item in value:
                if isinstance(item, dict):
                    lines.append(format_dict(item, indent + 1))
                else:
                    lines.append(f"{'  ' * (indent + 1)}- {item}")
        else:
            lines.append(f"{'  ' * indent}{key}: {value}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="AI Company Orchestrator")
    parser.add_argument("--loop", action="store_true", help="Run continuously")
    parser.add_argument("--interval", type=int, default=3600, help="Loop interval in seconds (default: 3600)")
    parser.add_argument("--status", action="store_true", help="Just print current status")
    args = parser.parse_args()

    if args.status:
        state = load_state()
        print(get_status_report(state))
        return

    if args.loop:
        logger.info(f"Starting continuous loop (interval: {args.interval}s)")
        while True:
            try:
                run_cycle()
            except Exception as e:
                logger.error(f"Cycle failed: {e}", exc_info=True)
            logger.info(f"Sleeping {args.interval}s until next cycle...")
            time.sleep(args.interval)
    else:
        run_cycle()


if __name__ == "__main__":
    main()
