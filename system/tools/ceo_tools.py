"""CEO-specific tools — run_department and consult_expert."""

import json
import logging
from datetime import datetime
from pathlib import Path

from system.tools.base import Tool
from system.config import COST_PER_INPUT_TOKEN, COST_PER_OUTPUT_TOKEN

logger = logging.getLogger(__name__)


class RunDepartmentTool(Tool):
    """Spawn a department to execute an assignment."""

    def __init__(self, workspace_root: Path, llm_client):
        self.workspace_root = workspace_root
        self.llm = llm_client
        self.total_cost = 0.0
        self.departments_called = []

    @property
    def name(self):
        return "run_department"

    @property
    def description(self):
        return (
            "Gründe eine Abteilung und gib ihr einen Auftrag. "
            "Die Abteilung arbeitet sofort und liefert einen Report zurück. "
            "Du bestimmst Name, Auftrag, erlaubte Tools und Budget."
        )

    @property
    def input_schema(self):
        return {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name der Abteilung (z.B. 'market_research', 'engineering', 'analytics')",
                },
                "objective": {
                    "type": "string",
                    "description": "Klarer Auftrag: Was soll die Abteilung erreichen?",
                },
                "context": {
                    "type": "string",
                    "description": "Zusätzlicher Kontext für die Abteilung (optional)",
                },
                "budget_usd": {
                    "type": "number",
                    "description": "Maximales Budget in USD (default: 1.0)",
                },
                "allowed_tools": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "Tools die die Abteilung nutzen darf. "
                        "Verfügbar: read_file, write_file, edit_file, list_directory, "
                        "run_command, git_status, git_commit. "
                        "Default: read_file, write_file, edit_file, list_directory, run_command"
                    ),
                },
            },
            "required": ["name", "objective"],
        }

    def reset(self):
        """Reset tracking for a new CEO cycle."""
        self.total_cost = 0.0
        self.departments_called = []

    def execute(self, name: str, objective: str, context: str = "",
                budget_usd: float = 1.0, allowed_tools: list = None, **kw) -> str:
        try:
            # Lazy import to avoid circular dependency
            from system.department.runner import Department

            dept = Department(
                llm_client=self.llm,
                workspace_root=self.workspace_root,
                name=name,
                objective=objective,
                context=context,
                budget_usd=budget_usd,
                allowed_tools=allowed_tools,
            )

            report = dept.execute()

            # Track costs
            self.total_cost += report.get("cost_usd", 0)
            self.departments_called.append(name)

            # Save report to state/reports/
            reports_dir = self.workspace_root / "state" / "reports"
            reports_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = reports_dir / f"{name}_{timestamp}.json"
            report_file.write_text(
                json.dumps(report, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            return json.dumps(report, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error(f"Department '{name}' failed: {e}", exc_info=True)
            error_report = {
                "department": name,
                "objective": objective,
                "status": "failed",
                "error": str(e),
                "cost_usd": 0,
            }
            return json.dumps(error_report, ensure_ascii=False, indent=2)


class ConsultExpertTool(Tool):
    """Get an independent expert opinion."""

    def __init__(self, llm_client):
        self.llm = llm_client
        self.total_cost = 0.0
        self.count = 0

    @property
    def name(self):
        return "consult_expert"

    @property
    def description(self):
        return (
            "Hole eine unabhängige Expertenmeinung. "
            "Der Experte hat keine eigene Agenda und gibt ehrliches Feedback. "
            "Nutze das für Zweitmeinungen, technische Bewertungen, oder Strategiekritik."
        )

    @property
    def input_schema(self):
        return {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "Die konkrete Frage an den Experten",
                },
                "context": {
                    "type": "string",
                    "description": "Relevanter Kontext (Report, Entscheidung, Daten)",
                },
                "expertise": {
                    "type": "string",
                    "description": "Fachgebiet (z.B. 'Technologie', 'Marketing', 'Finanzen', 'Strategie')",
                },
            },
            "required": ["question"],
        }

    def reset(self):
        """Reset tracking for a new CEO cycle."""
        self.total_cost = 0.0
        self.count = 0

    def execute(self, question: str, context: str = "", expertise: str = "Allgemein", **kw) -> str:
        system_prompt = (
            f"Du bist ein unabhängiger Berater mit Expertise in: {expertise}.\n"
            "Du gibst eine ehrliche, kritische Zweitmeinung.\n"
            "Sei direkt, konkret, und scheue nicht vor negativem Feedback zurück.\n"
            "Halte deine Antwort kurz und actionable."
        )

        user_message = f"Frage: {question}"
        if context:
            user_message += f"\n\nKontext:\n{context}"

        try:
            result = self.llm.run_agent_loop(
                system_prompt=system_prompt,
                user_message=user_message,
                tools=[],
                tool_executor=lambda n, i: "",
                max_tokens=2048,
            )

            cost = round(
                result["input_tokens"] * COST_PER_INPUT_TOKEN +
                result["output_tokens"] * COST_PER_OUTPUT_TOKEN,
                4,
            )
            self.total_cost += cost
            self.count += 1

            logger.info(f"Consultant ({expertise}): ${cost}")
            return result["text"]

        except Exception as e:
            logger.error(f"Consultant failed: {e}", exc_info=True)
            return f"[ERROR] Consultant-Anfrage fehlgeschlagen: {e}"
