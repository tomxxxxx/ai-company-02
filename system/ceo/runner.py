"""CEO Runner — The strategic brain of the AI Company."""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from system.llm.client import ToolUseClient
from system.tools.base import ToolRegistry
from system.tools.filesystem import ReadFileTool, WriteFileTool, EditFileTool, ListDirectoryTool
from system.tools.git import GitStatusTool, GitCommitTool
from system.tools.shell import RunCommandTool
from system.tools.ceo_tools import RunDepartmentTool, ConsultExpertTool
from system.config import (
    CEO_PROTECTED_PATHS,
    CEO_MAX_TURNS,
    COST_PER_INPUT_TOKEN,
    COST_PER_OUTPUT_TOKEN,
)

logger = logging.getLogger(__name__)


class CEO:
    """The CEO agent — reads state, makes decisions, delegates to departments."""

    def __init__(self, workspace_root: Path):
        self.workspace_root = Path(workspace_root)
        self.llm = ToolUseClient()

        # CEO-specific tools (kept as references for cost tracking)
        self.dept_tool = RunDepartmentTool(self.workspace_root, self.llm)
        self.consultant_tool = ConsultExpertTool(self.llm)

        self.registry = self._build_registry()
        self.prompt = self._load_prompt()

    def _build_registry(self) -> ToolRegistry:
        registry = ToolRegistry()

        # Filesystem — CEO can modify everything except bootstrap files
        registry.register(ReadFileTool(self.workspace_root))
        registry.register(WriteFileTool(self.workspace_root, protected_prefixes=CEO_PROTECTED_PATHS))
        registry.register(EditFileTool(self.workspace_root, protected_prefixes=CEO_PROTECTED_PATHS))
        registry.register(ListDirectoryTool(self.workspace_root))

        # Shell — for quick checks
        registry.register(RunCommandTool(self.workspace_root, timeout=30))

        # Git
        registry.register(GitStatusTool(self.workspace_root))
        registry.register(GitCommitTool(self.workspace_root))

        # CEO-specific
        registry.register(self.dept_tool)
        registry.register(self.consultant_tool)

        return registry

    def _load_prompt(self) -> str:
        prompt_file = Path(__file__).parent / "prompt.md"
        return prompt_file.read_text(encoding="utf-8")

    def _gather_context(self) -> str:
        """Build initial context from company state, briefing, reports, and CEO log."""
        parts = []

        # Vision
        vision_file = self.workspace_root / "operator" / "vision.md"
        if vision_file.exists():
            parts.append(f"## Vision & Ziele\n{vision_file.read_text(encoding='utf-8').strip()}")

        # Company state
        state_file = self.workspace_root / "state" / "company.json"
        if state_file.exists():
            parts.append(f"## Unternehmensstand\n```json\n{state_file.read_text(encoding='utf-8')}\n```")

        # Operator briefing
        briefing = self.workspace_root / "operator" / "briefing.md"
        if briefing.exists():
            content = briefing.read_text(encoding="utf-8").strip()
            if content:
                parts.append(f"## Operator-Briefing\n{content}")

        # Pending department reports
        reports_dir = self.workspace_root / "state" / "reports"
        if reports_dir.exists():
            for f in sorted(reports_dir.glob("*.json")):
                try:
                    parts.append(f"## Abteilungs-Report: {f.stem}\n```json\n{f.read_text(encoding='utf-8')}\n```")
                except Exception:
                    pass

        # Recent CEO log (last 10 entries)
        log_file = self.workspace_root / "state" / "ceo_log.jsonl"
        if log_file.exists():
            try:
                lines = log_file.read_text(encoding="utf-8").strip().split("\n")
                recent = [l for l in lines[-10:] if l.strip()]
                if recent:
                    parts.append("## Deine letzten Entscheidungen\n```jsonl\n" + "\n".join(recent) + "\n```")
            except Exception:
                pass

        if not parts:
            return "Dies ist dein erster CEO-Zyklus. Lies die Vision (operator/vision.md) und das Briefing (operator/briefing.md)."

        return "\n\n".join(parts)

    def run_cycle(self) -> dict:
        """Run one CEO decision cycle."""
        # Reset tracking
        self.dept_tool.reset()
        self.consultant_tool.reset()

        # Gather context
        context = self._gather_context()

        logger.info("CEO cycle starting...")

        # Run CEO agent loop
        result = self.llm.run_agent_loop(
            system_prompt=self.prompt,
            user_message=context,
            tools=self.registry.to_claude_format(),
            tool_executor=self.registry.execute,
            max_turns=CEO_MAX_TURNS,
        )

        # Calculate costs
        ceo_cost = (
            result["input_tokens"] * COST_PER_INPUT_TOKEN +
            result["output_tokens"] * COST_PER_OUTPUT_TOKEN
        )
        total_cost = round(ceo_cost + self.dept_tool.total_cost + self.consultant_tool.total_cost, 4)

        # Save CEO log
        self._save_log(result, total_cost)

        # Save operator report
        self._save_report(result, total_cost)

        # Update company state (deduct costs)
        self._update_state(total_cost)

        # Auto-commit any system/ changes (audit trail)
        self._auto_commit_system_changes()

        # Archive processed department reports
        self._archive_reports()

        logger.info(f"CEO cycle complete. Cost: ${total_cost}")

        return {
            "text": result["text"],
            "cost_usd": total_cost,
            "tool_calls_count": len(result["tool_calls"]),
            "turns": result["turns"],
            "departments": list(self.dept_tool.departments_called),
            "consultations": self.consultant_tool.count,
        }

    def _save_log(self, result: dict, total_cost: float):
        log_file = self.workspace_root / "state" / "ceo_log.jsonl"
        log_file.parent.mkdir(parents=True, exist_ok=True)

        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "summary": result["text"][:1000],
            "departments": list(self.dept_tool.departments_called),
            "consultations": self.consultant_tool.count,
            "cost_usd": total_cost,
            "tool_calls": len(result["tool_calls"]),
            "turns": result["turns"],
        }

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def _save_report(self, result: dict, total_cost: float):
        report_dir = self.workspace_root / "operator" / "reports"
        report_dir.mkdir(parents=True, exist_ok=True)

        cycle_num = self._get_cycle_count() + 1
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")

        report = {
            "cycle": cycle_num,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "summary": result["text"],
            "departments_called": list(self.dept_tool.departments_called),
            "consultations": self.consultant_tool.count,
            "cost_usd": total_cost,
            "tool_calls": len(result["tool_calls"]),
            "turns": result["turns"],
        }

        report_file = report_dir / f"cycle_{cycle_num:04d}_{timestamp}.json"
        report_file.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    def _update_state(self, cost_usd: float):
        """Update state — ONLY costs and cycle count. Revenue/products are never auto-updated."""
        state_file = self.workspace_root / "state" / "company.json"
        state = json.loads(state_file.read_text(encoding="utf-8"))

        # Only update cost tracking and cycle info — never touch revenue or products
        state["total_spent_usd"] = round(state.get("total_spent_usd", 0) + cost_usd, 4)
        state["capital_usd"] = round(state.get("capital_usd", 0) - cost_usd, 4)
        state["last_ceo_cycle"] = datetime.now(timezone.utc).isoformat()
        state["cycle_count"] = state.get("cycle_count", 0) + 1
        # mrr_usd, products, customers — NEVER modified by the system
        # Only Thomas (operator) updates revenue when real money flows

        state_file.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

    def _auto_commit_system_changes(self):
        """If CEO modified system/ files, auto-commit them for audit trail."""
        import subprocess
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "system/"],
                cwd=str(self.workspace_root),
                capture_output=True, text=True, timeout=10,
            )
            # Also check for untracked files in system/
            untracked = subprocess.run(
                ["git", "ls-files", "--others", "--exclude-standard", "system/"],
                cwd=str(self.workspace_root),
                capture_output=True, text=True, timeout=10,
            )
            changed = (result.stdout.strip() + "\n" + untracked.stdout.strip()).strip()
            if changed:
                files = [f for f in changed.split("\n") if f.strip()]
                subprocess.run(
                    ["git", "add"] + files,
                    cwd=str(self.workspace_root), timeout=10,
                )
                msg = f"[auto] CEO modified system/: {', '.join(files)}"
                subprocess.run(
                    ["git", "commit", "-m", msg],
                    cwd=str(self.workspace_root), timeout=10,
                )
                logger.info(f"Auto-committed system/ changes: {files}")
        except Exception as e:
            logger.warning(f"Auto-commit of system/ changes failed: {e}")

    def _archive_reports(self):
        """Move processed department reports to archive."""
        reports_dir = self.workspace_root / "state" / "reports"
        archive_dir = reports_dir / "archive"
        if not reports_dir.exists():
            return
        archive_dir.mkdir(parents=True, exist_ok=True)
        for f in reports_dir.glob("*.json"):
            try:
                f.rename(archive_dir / f.name)
            except Exception as e:
                logger.warning(f"Failed to archive report {f.name}: {e}")

    def _get_cycle_count(self) -> int:
        state_file = self.workspace_root / "state" / "company.json"
        if state_file.exists():
            state = json.loads(state_file.read_text(encoding="utf-8"))
            return state.get("cycle_count", 0)
        return 0
