"""Thin task-management layer on top of DatabaseManager."""

from typing import List, Dict, Optional
from database import db
import logging

logger = logging.getLogger(__name__)


class TaskManager:
    """All task operations go through here so handlers stay thin."""

    def __init__(self):
        self.db = db

    # ── Core operations ─────────────────────────────────────

    def create_task(self, channel_id: str, description: str, created_by: str) -> Dict:
        return self.db.create_task(channel_id, description, created_by)

    def get_tasks(self, channel_id: str, status: str = "open") -> List[Dict]:
        return self.db.get_tasks(channel_id, status)

    def complete_task(self, task_id: int, channel_id: str, completed_by: str) -> bool:
        return self.db.complete_task(task_id, channel_id, completed_by)

    def get_task(self, task_id: int) -> Optional[Dict]:
        return self.db.get_task(task_id)

    def task_count(self, channel_id: str, status: Optional[str] = None) -> int:
        return self.db.task_count(channel_id, status)


# Global convenience instance
task_manager = TaskManager()