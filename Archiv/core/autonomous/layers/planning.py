"""Planungsebene — Translate strategy into concrete plans."""

from core.autonomous.layer import Layer


class PlanningLayer(Layer):
    name = "planung"
    prompt_file = "planning.md"

    def get_tools(self) -> list[str]:
        """Planning layer reads context and can create Thomas tasks."""
        return ["read_file", "list_directory", "create_thomas_task"]
