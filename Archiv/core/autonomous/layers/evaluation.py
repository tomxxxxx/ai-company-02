"""Evaluationsebene — Evaluate the iteration's results."""

from core.autonomous.layer import Layer


class EvaluationLayer(Layer):
    name = "evaluation"
    prompt_file = "evaluation.md"

    def get_tools(self) -> list[str]:
        """Evaluation layer reads files to assess results, but doesn't modify."""
        return ["read_file", "list_directory", "git_status"]
