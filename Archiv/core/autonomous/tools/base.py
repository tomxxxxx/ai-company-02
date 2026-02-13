"""
Tool Base — Abstract base class and registry for agent tools.

Tools are capabilities that autonomous agents can use during their work.
Each tool maps to a Claude API tool definition and has an execute method.
"""

import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class Tool(ABC):
    """Base class for tools available to autonomous agents."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique tool name (used in API calls)."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of what this tool does."""
        ...

    @property
    @abstractmethod
    def input_schema(self) -> dict:
        """JSON Schema for tool input parameters."""
        ...

    @abstractmethod
    def execute(self, **kwargs) -> str:
        """Execute the tool and return a result string."""
        ...

    def to_claude_format(self) -> dict:
        """Convert to Claude API tool definition."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
        }


class ToolRegistry:
    """Registry of available tools. Handles lookup and execution."""

    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool):
        """Register a tool."""
        self._tools[tool.name] = tool
        logger.debug(f"Registered tool: {tool.name}")

    def get(self, name: str) -> Tool | None:
        """Get a tool by name."""
        return self._tools.get(name)

    def execute(self, name: str, inputs: dict) -> str:
        """Execute a tool by name with given inputs."""
        tool = self._tools.get(name)
        if not tool:
            return f"[ERROR] Unknown tool: {name}. Available tools: {', '.join(self._tools.keys())}"
        try:
            return tool.execute(**inputs)
        except Exception as e:
            logger.error(f"Tool {name} execution failed: {e}", exc_info=True)
            return f"[ERROR] Tool {name} failed: {e}"

    def to_claude_format(self) -> list[dict]:
        """Get all tool definitions in Claude API format."""
        return [t.to_claude_format() for t in self._tools.values()]

    def get_tools_for(self, names: list[str]) -> list[dict]:
        """Get Claude API format for specific tools only."""
        return [
            self._tools[n].to_claude_format()
            for n in names
            if n in self._tools
        ]

    @property
    def tool_names(self) -> list[str]:
        return list(self._tools.keys())

    def __len__(self) -> int:
        return len(self._tools)
