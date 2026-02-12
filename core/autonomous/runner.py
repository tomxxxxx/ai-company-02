"""
Autonomous Runner — The main continuous loop of AI Automation Lab.

Runs through all layers sequentially, continuously,
until a blocking Thomas-task stops the loop.
"""

import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path

from core.autonomous.llm_client import ToolUseClient
from core.autonomous.iteration_state import IterationState, load_history, get_iteration_count
from core.autonomous.tools import (
    ToolRegistry,
    ReadFileTool,
    WriteFileTool,
    EditFileTool,
    ListDirectoryTool,
    RunCommandTool,
    GitCommitTool,
    GitStatusTool,
    CreateThomasTaskTool,
)
from core.autonomous.layers import (
    LeitLayer,
    StrategyLayer,
    PlanningLayer,
    DelegationLayer,
    ExecutionLayer,
    EvaluationLayer,
)
from core.state import load_state, save_state

logger = logging.getLogger(__name__)

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent
HUMAN_FILE = WORKSPACE_ROOT / "HUMAN_ACTION_NEEDED.md"


class AutonomousRunner:
    """
    Main entry point for the autonomous company loop.

    Runs iterations continuously. Each iteration passes through all 6 layers:
    Leitebene → Strategie → Planung → Delegation → Ausführung → Evaluation

    Stops only when a blocking Thomas-task is created.
    """

    def __init__(self, delay_between_iterations: float = 5.0):
        self.delay = delay_between_iterations
        self.llm = ToolUseClient()
        self.thomas_tool = CreateThomasTaskTool()
        self.tools = self._init_tools()
        self.layers = self._init_layers()

    def _init_tools(self) -> ToolRegistry:
        """Initialize all available tools."""
        registry = ToolRegistry()
        registry.register(ReadFileTool(WORKSPACE_ROOT))
        registry.register(WriteFileTool(WORKSPACE_ROOT))
        registry.register(EditFileTool(WORKSPACE_ROOT))
        registry.register(ListDirectoryTool(WORKSPACE_ROOT))
        registry.register(RunCommandTool(WORKSPACE_ROOT, timeout=120))
        registry.register(GitCommitTool(WORKSPACE_ROOT))
        registry.register(GitStatusTool(WORKSPACE_ROOT))
        registry.register(self.thomas_tool)
        logger.info(f"Initialized {len(registry)} tools: {', '.join(registry.tool_names)}")
        return registry

    def _init_layers(self) -> list:
        """Initialize all layers in execution order."""
        layers = [
            LeitLayer(self.llm, self.tools),
            StrategyLayer(self.llm, self.tools),
            PlanningLayer(self.llm, self.tools),
            DelegationLayer(self.llm, self.tools),
            ExecutionLayer(self.llm, self.tools),
            EvaluationLayer(self.llm, self.tools),
        ]
        names = [l.name for l in layers]
        logger.info(f"Initialized {len(layers)} layers: {' → '.join(names)}")
        return layers

    def run_iteration(self) -> IterationState:
        """Run a single iteration through all layers."""
        iteration_id = get_iteration_count() + 1
        company_state = load_state()
        history = load_history(max_items=10)

        state = IterationState(
            iteration_id=iteration_id,
            company_state=company_state,
            history=history,
        )

        logger.info(f"\n{'#'*70}")
        logger.info(f"# ITERATION #{iteration_id}")
        logger.info(f"# Started: {state.started_at}")
        logger.info(f"{'#'*70}\n")

        for layer in self.layers:
            try:
                output = layer.run(state)
                state.add_layer_output(layer.name, output)

                # Check for pending Thomas tasks
                for task in self.thomas_tool.drain_tasks():
                    state.add_thomas_task(task)
                    logger.info(
                        f"Thomas task: {task['title']} "
                        f"(blocking={task.get('blocking', False)})"
                    )

                # If blocked, stop iteration
                if state.blocked:
                    logger.info(f"BLOCKED: {state.blocking_reason}")
                    break

            except Exception as e:
                logger.error(f"Layer {layer.name} failed: {e}", exc_info=True)
                state.add_layer_output(layer.name, {
                    "layer": layer.name,
                    "output": f"[ERROR] Layer failed: {e}",
                    "tool_calls": [],
                    "turns": 0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "error": str(e),
                })
                # Continue to next layer? Or stop?
                # For now, stop the iteration on layer failure
                logger.warning(f"Stopping iteration due to layer failure: {layer.name}")
                break

        # Finalize iteration
        state.completed_at = datetime.now(timezone.utc).isoformat()
        state.save()

        # Log summary
        logger.info(f"\n{'='*70}")
        logger.info(f"ITERATION #{iteration_id} COMPLETE")
        logger.info(f"Layers completed: {', '.join(state.layer_outputs.keys())}")
        logger.info(f"Thomas tasks: {len(state.thomas_tasks)}")
        logger.info(f"Blocked: {state.blocked}")
        logger.info(f"Cost: ${state.total_cost_usd:.4f}")
        logger.info(f"Tokens: {state.total_input_tokens} in / {state.total_output_tokens} out")
        logger.info(f"{'='*70}\n")

        return state

    def _write_human_action_needed(self, state: IterationState):
        """Write HUMAN_ACTION_NEEDED.md with current Thomas tasks."""
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        lines = [
            "# HUMAN ACTION NEEDED",
            "",
            f"*Generated by Iteration #{state.iteration_id} — {now}*",
            "",
            "Items below need your attention. The autonomous loop is paused.",
            "After handling all blocking items, restart the loop: `python run_autonomous.py`",
            "",
            "---",
            "",
        ]

        blocking = [t for t in state.thomas_tasks if t.get("blocking")]
        non_blocking = [t for t in state.thomas_tasks if not t.get("blocking")]

        if blocking:
            lines.append("## ⛔ BLOCKING (Loop ist pausiert)")
            lines.append("")
            for i, task in enumerate(blocking, 1):
                lines.append(f"### {i}. {task['title']}")
                lines.append(f"**Priorität:** {task.get('priority', 'medium')}")
                if task.get("estimated_minutes"):
                    lines.append(f"**Geschätzte Zeit:** {task['estimated_minutes']} Min.")
                lines.append("")
                lines.append(task.get("description", ""))
                lines.append("")
                lines.append("- [ ] Erledigt")
                lines.append("")

        if non_blocking:
            lines.append("## 📋 NON-BLOCKING (Wenn du Zeit hast)")
            lines.append("")
            for i, task in enumerate(non_blocking, 1):
                lines.append(f"### {i}. {task['title']}")
                lines.append(f"**Priorität:** {task.get('priority', 'medium')}")
                if task.get("estimated_minutes"):
                    lines.append(f"**Geschätzte Zeit:** {task['estimated_minutes']} Min.")
                lines.append("")
                lines.append(task.get("description", ""))
                lines.append("")
                lines.append("- [ ] Erledigt")
                lines.append("")

        HUMAN_FILE.write_text("\n".join(lines), encoding="utf-8")
        logger.info(f"Wrote HUMAN_ACTION_NEEDED.md ({len(blocking)} blocking, {len(non_blocking)} non-blocking)")

    def run_continuous(self):
        """
        Main entry point: run iterations continuously until blocked.

        This is the heart of the autonomous company.
        """
        logger.info("=" * 70)
        logger.info("AUTONOMOUS LOOP STARTED")
        logger.info(f"Workspace: {WORKSPACE_ROOT}")
        logger.info(f"Delay between iterations: {self.delay}s")
        logger.info("=" * 70)

        iteration_number = 0

        while True:
            iteration_number += 1

            try:
                state = self.run_iteration()
            except KeyboardInterrupt:
                logger.info("Interrupted by user (Ctrl+C). Shutting down.")
                break
            except Exception as e:
                logger.error(f"Iteration failed with unhandled error: {e}", exc_info=True)
                logger.info("Waiting 30s before retrying...")
                time.sleep(30)
                continue

            if state.blocked:
                self._write_human_action_needed(state)
                logger.info("")
                logger.info("=" * 70)
                logger.info("LOOP PAUSED — Thomas has blocking tasks")
                logger.info(f"See: {HUMAN_FILE}")
                logger.info("Restart with: python run_autonomous.py")
                logger.info("=" * 70)
                break

            if state.thomas_tasks:
                # Non-blocking tasks exist — write them but continue
                self._write_human_action_needed(state)

            # Brief pause between iterations
            if self.delay > 0:
                logger.info(f"Next iteration in {self.delay}s...")
                time.sleep(self.delay)

    def run_single(self):
        """Run exactly one iteration (useful for testing)."""
        state = self.run_iteration()
        if state.thomas_tasks:
            self._write_human_action_needed(state)
        return state
