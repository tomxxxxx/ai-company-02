"""Department Runner — Executes a single department assignment."""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from system.tools.base import ToolRegistry
from system.tools.filesystem import ReadFileTool, WriteFileTool, EditFileTool, ListDirectoryTool
from system.tools.git import GitStatusTool, GitCommitTool
from system.tools.shell import RunCommandTool
from system.config import (
    DEPARTMENT_PROTECTED_PATHS,
    DEFAULT_DEPARTMENT_MAX_TURNS,
    COST_PER_INPUT_TOKEN,
    COST_PER_OUTPUT_TOKEN,
)

logger = logging.getLogger(__name__)

DEPARTMENT_PROMPT = """Du bist der Leiter der Abteilung "{name}" eines KI-gesteuerten Unternehmens.

## Dein Auftrag

{objective}

## Regeln

- Arbeite NUR an deinem Auftrag. Keine Eigeninitiative darüber hinaus.
- Schreibe Dateien nach workspace/ — nicht in system/, state/ oder operator/.
- Sei effizient. Jeder Tool-Call kostet Geld.
- Wenn du blockiert bist, sage das klar.
- Erstelle KEINE Dateien die nur Pläne beschreiben. Liefere echte Ergebnisse.

## Output

Beende mit einem klaren Report:
- Was wurde erreicht?
- Was hat nicht funktioniert?
- Was sollte als nächstes passieren?"""


class Department:
    """Executes a single department assignment."""

    def __init__(self, llm_client, workspace_root, name: str, objective: str,
                 context: str = "", budget_usd: float = 1.0, allowed_tools: list = None):
        self.llm = llm_client
        self.workspace_root = Path(workspace_root)
        self.name = name
        self.objective = objective
        self.context = context
        self.budget_usd = budget_usd
        self.allowed_tools = allowed_tools or [
            "read_file", "write_file", "edit_file", "list_directory", "run_command"
        ]
        self.registry = self._build_registry()

    def _build_registry(self) -> ToolRegistry:
        registry = ToolRegistry()

        available = {
            "read_file": ReadFileTool(self.workspace_root),
            "write_file": WriteFileTool(self.workspace_root, protected_prefixes=DEPARTMENT_PROTECTED_PATHS),
            "edit_file": EditFileTool(self.workspace_root, protected_prefixes=DEPARTMENT_PROTECTED_PATHS),
            "list_directory": ListDirectoryTool(self.workspace_root),
            "run_command": RunCommandTool(self.workspace_root),
            "git_status": GitStatusTool(self.workspace_root),
            "git_commit": GitCommitTool(self.workspace_root),
        }

        for tool_name in self.allowed_tools:
            if tool_name in available:
                registry.register(available[tool_name])

        return registry

    def execute(self) -> dict:
        """Execute the assignment and return a report dict."""
        prompt = DEPARTMENT_PROMPT.format(name=self.name, objective=self.objective)

        user_message = f"Auftrag: {self.objective}"
        if self.context:
            user_message += f"\n\nKontext:\n{self.context}"

        logger.info(f"Department '{self.name}' starting: {self.objective[:100]}")

        result = self.llm.run_agent_loop(
            system_prompt=prompt,
            user_message=user_message,
            tools=self.registry.to_claude_format(),
            tool_executor=self.registry.execute,
            max_turns=DEFAULT_DEPARTMENT_MAX_TURNS,
        )

        cost = round(
            result["input_tokens"] * COST_PER_INPUT_TOKEN +
            result["output_tokens"] * COST_PER_OUTPUT_TOKEN,
            4,
        )

        report = {
            "department": self.name,
            "objective": self.objective,
            "status": "completed",
            "output": result["text"],
            "tool_calls_count": len(result["tool_calls"]),
            "tool_calls": [
                {"tool": tc["tool"], "input": tc["input"]}
                for tc in result["tool_calls"]
            ],
            "cost_usd": cost,
            "turns": result["turns"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        logger.info(f"Department '{self.name}' completed. Cost: ${cost}")
        return report
