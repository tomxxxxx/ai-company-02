"""Simple data models for TaskMaster (no ORM needed)."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Task:
    id: int
    channel_id: str
    description: str
    status: str = "open"
    created_by: str = ""
    created_at: Optional[str] = None
    completed_at: Optional[str] = None
    completed_by: Optional[str] = None

    @property
    def is_complete(self) -> bool:
        return self.status == "completed"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "channel_id": self.channel_id,
            "description": self.description,
            "status": self.status,
            "created_by": self.created_by,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "completed_by": self.completed_by,
        }

    def __repr__(self):
        desc = self.description[:30] + "..." if len(self.description) > 30 else self.description
        return f"<Task #{self.id} '{desc}' [{self.status}]>"