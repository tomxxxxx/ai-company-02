import sqlite3
import os
from contextlib import contextmanager
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

DATABASE_PATH = os.getenv('DATABASE_PATH', 'taskmaster.db')

class DatabaseManager:
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        try:
            with self.get_connection() as conn:
                conn.execute('''
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
                ''')
                
                # Create indexes for better performance
                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_channel_status 
                    ON tasks(channel_id, status)
                ''')
                
                conn.commit()
                logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def create_task(self, channel_id: str, description: str, created_by: str) -> int:
        """Create a new task and return its ID"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute('''
                    INSERT INTO tasks (channel_id, description, created_by)
                    VALUES (?, ?, ?)
                ''', (channel_id, description, created_by))
                conn.commit()
                task_id = cursor.lastrowid
                logger.info(f"Created task {task_id} in channel {channel_id}")
                return task_id
        except Exception as e:
            logger.error(f"Failed to create task: {e}")
            raise
    
    def get_tasks_by_channel(self, channel_id: str, status: str = 'open') -> List[Dict]:
        """Get all tasks for a specific channel and status"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute('''
                    SELECT id, description, status, created_by, created_at, 
                           completed_at, completed_by
                    FROM tasks 
                    WHERE channel_id = ? AND status = ?
                    ORDER BY created_at ASC
                ''', (channel_id, status))
                
                tasks = []
                for row in cursor.fetchall():
                    tasks.append({
                        'id': row['id'],
                        'description': row['description'],
                        'status': row['status'],
                        'created_by': row['created_by'],
                        'created_at': row['created_at'],
                        'completed_at': row['completed_at'],
                        'completed_by': row['completed_by']
                    })
                
                logger.info(f"Retrieved {len(tasks)} {status} tasks for channel {channel_id}")
                return tasks
        except Exception as e:
            logger.error(f"Failed to get tasks: {e}")
            raise
    
    def complete_task(self, task_id: int, completed_by: str, channel_id: str) -> bool:
        """Mark a task as complete"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute('''
                    UPDATE tasks 
                    SET status = 'completed', 
                        completed_at = CURRENT_TIMESTAMP,
                        completed_by = ?
                    WHERE id = ? AND channel_id = ? AND status = 'open'
                ''', (completed_by, task_id, channel_id))
                
                conn.commit()
                rows_affected = cursor.rowcount
                
                if rows_affected > 0:
                    logger.info(f"Task {task_id} completed by {completed_by}")
                    return True
                else:
                    logger.warning(f"Task {task_id} not found or already completed")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to complete task {task_id}: {e}")
            raise
    
    def get_task_by_id(self, task_id: int, channel_id: str) -> Optional[Dict]:
        """Get a specific task by ID and channel"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute('''
                    SELECT id, description, status, created_by, created_at,
                           completed_at, completed_by
                    FROM tasks 
                    WHERE id = ? AND channel_id = ?
                ''', (task_id, channel_id))
                
                row = cursor.fetchone()
                if row:
                    return {
                        'id': row['id'],
                        'description': row['description'],
                        'status': row['status'],
                        'created_by': row['created_by'],
                        'created_at': row['created_at'],
                        'completed_at': row['completed_at'],
                        'completed_by': row['completed_by']
                    }
                return None
                
        except Exception as e:
            logger.error(f"Failed to get task {task_id}: {e}")
            raise
    
    def get_task_count(self, channel_id: str, status: str = None) -> int:
        """Get count of tasks for a channel"""
        try:
            with self.get_connection() as conn:
                if status:
                    cursor = conn.execute('''
                        SELECT COUNT(*) FROM tasks 
                        WHERE channel_id = ? AND status = ?
                    ''', (channel_id, status))
                else:
                    cursor = conn.execute('''
                        SELECT COUNT(*) FROM tasks 
                        WHERE channel_id = ?
                    ''', (channel_id,))
                
                return cursor.fetchone()[0]
                
        except Exception as e:
            logger.error(f"Failed to get task count: {e}")
            raise

# Global database manager instance
db = DatabaseManager()