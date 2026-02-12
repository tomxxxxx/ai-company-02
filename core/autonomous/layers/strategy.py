"""Strategieebene — Choose ONE focus for this iteration."""

from pathlib import Path

from core.autonomous.layer import Layer

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent.parent


class StrategyLayer(Layer):
    name = "strategie"
    prompt_file = "strategy.md"

    def get_tools(self) -> list[str]:
        """Strategy layer reads the backlog and context. Minimal tools."""
        return ["read_file", "list_directory"]

    def build_context(self, iteration_state) -> str:
        """Strategy layer gets ideas backlog injected for decision-making."""
        base_context = super().build_context(iteration_state)

        extra = []

        # Inject ideas backlog
        backlog_path = WORKSPACE_ROOT / "company-os" / "ideas-backlog.md"
        if backlog_path.exists():
            backlog_content = backlog_path.read_text(encoding="utf-8")
            extra.append("\n## 📝 IDEEN-BACKLOG (WÄHLE EINEN FOKUS!)")
            extra.append("")
            extra.append(backlog_content)
            extra.append("")
            extra.append("Wähle EIN Thema oder EINE Idee als Fokus für diese Iteration.")
            extra.append("")

        extra.append("ERINNERUNG: Dein Output ist KURZ. Ein Fokus, eine Begründung, eine Abgrenzung. Maximal ein Absatz.")
        extra.append("")

        return base_context + "\n" + "\n".join(extra)
