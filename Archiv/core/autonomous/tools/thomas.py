"""
Thomas Task Tool — Create tasks for the human operator.

Tasks can be blocking (loop pauses until Thomas handles them)
or non-blocking (noted for Thomas, but loop continues).
"""

import logging
from datetime import datetime, timezone

from core.autonomous.tools.base import Tool

logger = logging.getLogger(__name__)


class CreateThomasTaskTool(Tool):
    """Create a task that requires Thomas's attention."""

    def __init__(self):
        self._pending_tasks: list[dict] = []

    @property
    def name(self) -> str:
        return "create_thomas_task"

    @property
    def description(self) -> str:
        return (
            "Create a task for Thomas (the human operator). "
            "Tasks are always non-blocking — the loop continues regardless. "
            "Thomas will handle tasks when he has time. "
            "Thomas has ~1h/day, is a developer (not a salesperson), "
            "and cannot appear publicly (Konkurrenzklausel). "
            "Do NOT create tasks for things you can do yourself."
        )

    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Short title of the task",
                },
                "description": {
                    "type": "string",
                    "description": "Detailed description of what Thomas needs to do",
                },
                "blocking": {
                    "type": "boolean",
                    "description": "If true, the autonomous loop pauses until Thomas completes this task. Only use for truly blocking tasks.",
                },
                "estimated_minutes": {
                    "type": "integer",
                    "description": "Estimated time for Thomas to complete this task (in minutes)",
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "critical"],
                    "description": "Priority level of the task",
                },
            },
            "required": ["title", "description", "blocking"],
        }

    def execute(
        self,
        title: str,
        description: str,
        blocking: bool = False,
        estimated_minutes: int = None,
        priority: str = "medium",
        **kwargs,
    ) -> str:
        task = {
            "title": title,
            "description": description,
            "blocking": blocking,
            "estimated_minutes": estimated_minutes,
            "priority": priority,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self._pending_tasks.append(task)

        status = "BLOCKING" if blocking else "non-blocking"
        logger.info(f"Thomas task created ({status}): {title}")
        return f"Task created for Thomas ({status}): {title}"

    def drain_tasks(self) -> list[dict]:
        """Return and clear all pending tasks. Called by runner after each layer."""
        tasks = self._pending_tasks[:]
        self._pending_tasks.clear()
        return tasks
