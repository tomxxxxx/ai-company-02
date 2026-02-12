"""Ausführungsebene — Execute the plan using all available tools."""

from core.autonomous.layer import Layer


class ExecutionLayer(Layer):
    name = "ausfuehrung"
    prompt_file = "execution.md"

    def get_tools(self) -> list[str]:
        """Execution layer has access to ALL tools."""
        return []  # Empty = all tools
