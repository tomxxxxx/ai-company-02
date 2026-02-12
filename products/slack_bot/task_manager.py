from datetime import datetime
from typing import List, Optional, Dict, Any
from models import Task
from database import get_db_connection
import logging

logger = logging.getLogger(__name__)

class TaskManager:
    def __init__(self):
        self.db_connection = get_db_connection()
    
    def create_task(self, channel_id: str, user_id: str, description: str) -> Task:
        """Create a new task in the specified channel."""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute(
                """
                INSERT INTO tasks (channel_id, user_id, description, status, created_at)
                VALUES (?, ?, ?, 'open', ?)
                """,
                (channel_id, user_id, description, datetime.utcnow())
            )
            task_id = cursor.lastrowid
            self.db_connection.commit()
            
            # Return the created task
            return self.get_task(task_id)
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            self.db_connection.rollback()
            raise
    
    def get_task(self, task_id: int) -> Optional[Task]:
        """Get a task by its ID."""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute(
                "SELECT * FROM tasks WHERE id = ?",
                (task_id,)
            )
            row = cursor.fetchone()
            
            if row:
                return Task(
                    id=row[0],
                    channel_id=row[1],
                    user_id=row[2],
                    description=row[3],
                    status=row[4],
                    created_at=row[5],
                    completed_at=row[6]
                )
            return None
        except Exception as e:
            logger.error(f"Error getting task {task_id}: {e}")
            return None
    
    def get_channel_tasks(self, channel_id: str, status: str = 'open') -> List[Task]:
        """Get all tasks for a specific channel with given status."""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute(
                """
                SELECT * FROM tasks 
                WHERE channel_id = ? AND status = ?
                ORDER BY created_at DESC
                """,
                (channel_id, status)
            )
            rows = cursor.fetchall()
            
            tasks = []
            for row in rows:
                tasks.append(Task(
                    id=row[0],
                    channel_id=row[1],
                    user_id=row[2],
                    description=row[3],
                    status=row[4],
                    created_at=row[5],
                    completed_at=row[6]
                ))
            
            return tasks
        except Exception as e:
            logger.error(f"Error getting channel tasks for {channel_id}: {e}")
            return []
    
    def complete_task(self, task_id: int, completed_by: str) -> Optional[Task]:
        """Mark a task as completed."""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute(
                """
                UPDATE tasks 
                SET status = 'completed', completed_at = ?, completed_by = ?
                WHERE id = ? AND status = 'open'
                """,
                (datetime.utcnow(), completed_by, task_id)
            )
            
            if cursor.rowcount == 0:
                return None
            
            self.db_connection.commit()
            return self.get_task(task_id)
        except Exception as e:
            logger.error(f"Error completing task {task_id}: {e}")
            self.db_connection.rollback()
            return None
    
    def delete_task(self, task_id: int, channel_id: str) -> bool:
        """Delete a task (only if it belongs to the channel)."""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute(
                "DELETE FROM tasks WHERE id = ? AND channel_id = ?",
                (task_id, channel_id)
            )
            
            deleted = cursor.rowcount > 0
            self.db_connection.commit()
            return deleted
        except Exception as e:
            logger.error(f"Error deleting task {task_id}: {e}")
            self.db_connection.rollback()
            return False
    
    def get_task_stats(self, channel_id: str) -> Dict[str, int]:
        """Get task statistics for a channel."""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute(
                """
                SELECT status, COUNT(*) as count
                FROM tasks 
                WHERE channel_id = ?
                GROUP BY status
                """,
                (channel_id,)
            )
            rows = cursor.fetchall()
            
            stats = {'open': 0, 'completed': 0}
            for row in rows:
                stats[row[0]] = row[1]
            
            return stats
        except Exception as e:
            logger.error(f"Error getting task stats for {channel_id}: {e}")
            return {'open': 0, 'completed': 0}
    
    def format_task_blocks(self, tasks: List[Task]) -> List[Dict[str, Any]]:
        """Format tasks as Slack blocks for display."""
        if not tasks:
            return [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "📝 No open tasks found in this channel."
                    }
                }
            ]
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"📋 Open Tasks ({len(tasks)})"
                }
            },
            {
                "type": "divider"
            }
        ]
        
        for task in tasks:
            created_date = task.created_at.strftime("%m/%d %H:%M") if task.created_at else "Unknown"
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*#{task.id}* {task.description}\n_Created: {created_date} by <@{task.user_id}>_"
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "✅ Complete"
                    },
                    "value": str(task.id),
                    "action_id": f"complete_task_{task.id}"
                }
            })
        
        return blocks
    
    def format_task_created_block(self, task: Task) -> List[Dict[str, Any]]:
        """Format a newly created task as Slack blocks."""
        return [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"✅ *Task #{task.id} created*\n{task.description}"
                }
            }
        ]
    
    def format_task_completed_block(self, task: Task) -> List[Dict[str, Any]]:
        """Format a completed task as Slack blocks."""
        return [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"🎉 *Task #{task.id} completed!*\n~{task.description}~"
                }
            }
        ]

# Global instance
task_manager = TaskManager()