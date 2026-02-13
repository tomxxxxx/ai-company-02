"""Tool Base — Abstract base class and registry for agent tools."""

import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class Tool(ABC):
    """Base class for tools available to agents."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique tool name (used in API calls)."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description."""
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
        self._tools[tool.name] = tool
        logger.debug(f"Registered tool: {tool.name}")

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def execute(self, name: str, inputs: dict) -> str:
        tool = self._tools.get(name)
        if not tool:
            return f"[ERROR] Unknown tool: {name}. Available: {', '.join(self._tools.keys())}"
        try:
            return tool.execute(**inputs)
        except Exception as e:
            logger.error(f"Tool {name} failed: {e}", exc_info=True)
            return f"[ERROR] Tool {name} failed: {e}"

    def to_claude_format(self) -> list[dict]:
        return [t.to_claude_format() for t in self._tools.values()]

    @property
    def tool_names(self) -> list[str]:
        return list(self._tools.keys())

    def __len__(self) -> int:
        return len(self._tools)
