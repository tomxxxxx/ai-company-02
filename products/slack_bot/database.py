import sqlite3
import os
from contextlib import contextmanager
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

DATABASE_PATH = os.getenv("DATABASE_PATH", "taskmaster.db")


class DatabaseManager:
    """Simple sqlite3-based database for TaskMaster."""

    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self._init_tables()

    def _init_tables(self):
        """Create tables if they don't exist."""
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    channel_id TEXT NOT NULL,
                    description TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'open',
                    created_by TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    completed_by TEXT
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_channel_status
                ON tasks(channel_id, status)
                """
            )
            conn.commit()
            logger.info("Database initialised (%s)", self.db_path)

    @contextmanager
    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # ── CRUD ────────────────────────────────────────────────

    def create_task(self, channel_id: str, description: str, created_by: str) -> Dict:
        """Insert a task and return it as a dict."""
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO tasks (channel_id, description, created_by) VALUES (?, ?, ?)",
                (channel_id, description, created_by),
            )
            conn.commit()
            task_id = cur.lastrowid
            logger.info("Created task #%s in %s", task_id, channel_id)
            return self.get_task(task_id) or {"id": task_id, "description": description}

    def get_task(self, task_id: int) -> Optional[Dict]:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
            return dict(row) if row else None

    def get_tasks(self, channel_id: str, status: str = "open") -> List[Dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM tasks WHERE channel_id = ? AND status = ? ORDER BY created_at ASC",
                (channel_id, status),
            ).fetchall()
            return [dict(r) for r in rows]

    def complete_task(self, task_id: int, channel_id: str, completed_by: str) -> bool:
        """Mark a task as completed. Returns True if a row was updated."""
        with self._connect() as conn:
            cur = conn.execute(
                """
                UPDATE tasks
                SET status = 'completed', completed_at = CURRENT_TIMESTAMP, completed_by = ?
                WHERE id = ? AND channel_id = ? AND status = 'open'
                """,
                (completed_by, task_id, channel_id),
            )
            conn.commit()
            return cur.rowcount > 0

    def task_count(self, channel_id: str, status: Optional[str] = None) -> int:
        with self._connect() as conn:
            if status:
                row = conn.execute(
                    "SELECT COUNT(*) FROM tasks WHERE channel_id = ? AND status = ?",
                    (channel_id, status),
                ).fetchone()
            else:
                row = conn.execute(
                    "SELECT COUNT(*) FROM tasks WHERE channel_id = ?",
                    (channel_id,),
                ).fetchone()
            return row[0]


# ── Singleton used by the rest of the app ──────────────────
db = DatabaseManager()


def init_db():
    """Convenience function — tables are created on import, but callers can
    invoke this explicitly for clarity."""
    return db