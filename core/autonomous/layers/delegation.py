"""Delegationsebene — Prepare execution by structuring actions."""

from core.autonomous.layer import Layer


class DelegationLayer(Layer):
    name = "delegation"
    prompt_file = "delegation.md"

    def get_tools(self) -> list[str]:
        """Delegation layer reads files for preparation and can create Thomas tasks."""
        return ["read_file", "list_directory", "create_thomas_task"]
