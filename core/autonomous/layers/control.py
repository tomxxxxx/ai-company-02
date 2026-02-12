"""Leitebene — Creative thinking, system reflection, and ideas management."""

from pathlib import Path

from core.autonomous.layer import Layer

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent.parent


class LeitLayer(Layer):
    name = "leitebene"
    prompt_file = "control.md"

    def get_tools(self) -> list[str]:
        """Leitebene can read files and update the ideas backlog."""
        return ["read_file", "list_directory", "edit_file", "write_file"]

    def build_context(self, iteration_state) -> str:
        """Leitebene gets operator briefing + ideas backlog + system context."""
        base_context = super().build_context(iteration_state)

        extra = []

        # Inject operator briefing directly into context
        briefing_path = WORKSPACE_ROOT / "company-os" / "operator-briefing.md"
        if briefing_path.exists():
            briefing_content = briefing_path.read_text(encoding="utf-8")
            extra.append("\n## ⚠️ OPERATOR-BRIEFING (HÖCHSTE PRIORITÄT)")
            extra.append("Thomas hat folgendes Feedback und folgende Vorgaben hinterlassen:")
            extra.append("")
            extra.append(briefing_content)
            extra.append("")
        else:
            extra.append("\n## Operator-Briefing")
            extra.append("Kein Briefing vorhanden. Arbeite nach bestem Wissen.")
            extra.append("")

        # Inject ideas backlog
        backlog_path = WORKSPACE_ROOT / "company-os" / "ideas-backlog.md"
        if backlog_path.exists():
            backlog_content = backlog_path.read_text(encoding="utf-8")
            extra.append("## 📝 IDEEN-BACKLOG (LESEN UND AKTUALISIEREN!)")
            extra.append("")
            extra.append(backlog_content)
            extra.append("")
            extra.append("Aktualisiere diesen Backlog mit edit_file oder write_file.")
            extra.append("")
        else:
            extra.append("## Ideen-Backlog")
            extra.append("Kein Backlog vorhanden. Erstelle company-os/ideas-backlog.md.")
            extra.append("")

        extra.append("## Systemkontext")
        extra.append("Iteration-Logs: data/iterations/")
        extra.append("Unternehmens-State: data/company_state.json")
        extra.append("")
        extra.append("ERINNERUNG: Du bist die Leitebene. Dein Job: Systemzustand bewerten + Ideen-Backlog pflegen. NICHT den Iterationsfokus setzen.")
        extra.append("")

        return base_context + "\n" + "\n".join(extra)
