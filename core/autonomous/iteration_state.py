"""
Iteration State — Tracks the state of a single iteration through all layers.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

ITERATIONS_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "iterations"


class IterationState:
    """State object that flows through all layers of one iteration."""

    def __init__(self, iteration_id: int, company_state: dict, history: list[dict] = None):
        self.iteration_id = iteration_id
        self.started_at = datetime.now(timezone.utc).isoformat()
        self.company_state = company_state
        self.history = history or []
        self.layer_outputs: dict[str, dict] = {}
        self.thomas_tasks: list[dict] = []
        self.blocked = False
        self.blocking_reason = ""
        self.completed_at: str | None = None
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost_usd = 0.0

    def add_layer_output(self, layer_name: str, output: dict):
        """Record output from a layer."""
        self.layer_outputs[layer_name] = output
        self.total_input_tokens += output.get("input_tokens", 0)
        self.total_output_tokens += output.get("output_tokens", 0)
        # Approximate cost (Claude Sonnet pricing: $3/MTok in, $15/MTok out)
        self.total_cost_usd += (
            output.get("input_tokens", 0) * 3.0 / 1_000_000
            + output.get("output_tokens", 0) * 15.0 / 1_000_000
        )

    def add_thomas_task(self, task: dict):
        """Add a task for Thomas. If blocking=True, marks iteration as blocked."""
        task.setdefault("created_at", datetime.now(timezone.utc).isoformat())
        task.setdefault("blocking", False)
        self.thomas_tasks.append(task)
        if task.get("blocking", False):
            self.blocked = True
            self.blocking_reason = task.get("title", "Blocking task for Thomas")

    def get_layer_summary(self) -> str:
        """Get a text summary of all layer outputs so far in this iteration."""
        parts = []
        for name, output in self.layer_outputs.items():
            parts.append(f"=== {name.upper()} ===")
            parts.append(output.get("output", "(no output)"))
            if output.get("tool_calls"):
                parts.append(f"[{len(output['tool_calls'])} tool calls made]")
            parts.append("")
        return "\n".join(parts)

    def to_dict(self) -> dict:
        """Serialize to dict for persistence."""
        return {
            "iteration_id": self.iteration_id,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "blocked": self.blocked,
            "blocking_reason": self.blocking_reason,
            "layers_completed": list(self.layer_outputs.keys()),
            "layer_outputs": {
                name: {
                    "output": out.get("output", ""),
                    "tool_calls_count": len(out.get("tool_calls", [])),
                    "tool_calls": out.get("tool_calls", []),
                    "turns": out.get("turns", 0),
                    "input_tokens": out.get("input_tokens", 0),
                    "output_tokens": out.get("output_tokens", 0),
                }
                for name, out in self.layer_outputs.items()
            },
            "thomas_tasks": self.thomas_tasks,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_cost_usd": round(self.total_cost_usd, 4),
            "company_state_snapshot": {
                "current_capital": self.company_state.get("financials", {}).get("current_capital", 0),
                "mrr": self.company_state.get("metrics", {}).get("mrr", 0),
                "products": list(self.company_state.get("products", {}).keys()),
                "current_phase": self.company_state.get("current_phase", "unknown"),
            },
        }

    def to_summary(self) -> dict:
        """Create a compact summary for history (used by future iterations)."""
        return {
            "iteration_id": self.iteration_id,
            "date": self.started_at,
            "blocked": self.blocked,
            "layers_completed": list(self.layer_outputs.keys()),
            "thomas_tasks_count": len(self.thomas_tasks),
            "cost_usd": round(self.total_cost_usd, 4),
            "layer_summaries": {
                name: out.get("output", "")[:500]
                for name, out in self.layer_outputs.items()
            },
        }

    def save(self):
        """Persist iteration to disk."""
        ITERATIONS_DIR.mkdir(parents=True, exist_ok=True)
        path = ITERATIONS_DIR / f"iteration_{self.iteration_id:04d}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        logger.info(f"Iteration #{self.iteration_id} saved to {path}")


def load_history(max_items: int = 10) -> list[dict]:
    """Load summaries of past iterations for context."""
    if not ITERATIONS_DIR.exists():
        return []

    files = sorted(ITERATIONS_DIR.glob("iteration_*.json"), reverse=True)
    history = []
    for f in files[:max_items]:
        try:
            with open(f, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            # Create a compact summary
            history.append({
                "iteration_id": data.get("iteration_id"),
                "date": data.get("started_at"),
                "blocked": data.get("blocked", False),
                "layers_completed": data.get("layers_completed", []),
                "thomas_tasks": data.get("thomas_tasks", []),
                "cost_usd": data.get("total_cost_usd", 0),
                "layer_summaries": {
                    name: info.get("output", "")[:800]
                    for name, info in data.get("layer_outputs", {}).items()
                },
            })
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to load {f}: {e}")

    return list(reversed(history))  # Oldest first


def get_iteration_count() -> int:
    """Get the number of completed iterations."""
    if not ITERATIONS_DIR.exists():
        return 0
    return len(list(ITERATIONS_DIR.glob("iteration_*.json")))
