#!/usr/bin/env python3
"""AI Company v2 — CEO-gesteuertes autonomes Unternehmen."""

import argparse
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser(description="AI Company v2 — CEO Cycle")
    parser.add_argument("--max-cycles", type=int, default=1, help="Anzahl CEO-Zyklen (default: 1)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Debug-Logging aktivieren")
    args = parser.parse_args()

    # Load environment
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )

    from system.ceo.runner import CEO
    ceo = CEO(workspace_root=ROOT)

    for i in range(args.max_cycles):
        print(f"\n{'='*60}")
        print(f"  CEO ZYKLUS #{i + 1}")
        print(f"{'='*60}\n")

        result = ceo.run_cycle()

        print(f"\n--- CEO Output ---")
        print(result["text"])
        print(f"\n{'='*60}")
        print(f"  ZYKLUS #{i + 1} ABGESCHLOSSEN")
        print(f"  Kosten:       ${result['cost_usd']:.4f}")
        print(f"  Tool-Calls:   {result['tool_calls_count']}")
        print(f"  Turns:        {result['turns']}")
        print(f"  Abteilungen:  {', '.join(result['departments']) or 'keine'}")
        print(f"  Consultants:  {result['consultations']}")
        print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
