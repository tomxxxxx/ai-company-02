"""OAuth installation and state stores using SQLite."""

import sqlite3
import json
import time
from typing import Optional
from slack_bolt.oauth.installation_store import InstallationStore, Installation
from slack_bolt.oauth.state_store import OAuthStateStore
from config import Config
import logging

logger = logging.getLogger(__name__)


class SQLiteInstallationStore(InstallationStore):
    """Store OAuth installations in SQLite database."""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or Config.DATABASE_PATH
    
    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def save(self, installation: Installation):
        """Save installation to database."""
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO installations (
                    client_id, enterprise_id, team_id, team_name,
                    bot_token, bot_id, bot_user_id, bot_scopes,
                    user_id, user_token, user_scopes,
                    incoming_webhook_url, incoming_webhook_channel,
                    incoming_webhook_channel_id, incoming_webhook_configuration_url,
                    is_enterprise_install, token_type
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    installation.client_id,
                    installation.enterprise_id,
                    installation.team_id,
                    installation.team_name,
                    installation.bot_token,
                    installation.bot_id,
                    installation.bot_user_id,
                    ",".join(installation.bot_scopes or []),
                    installation.user_id,
                    installation.user_token,
                    ",".join(installation.user_scopes or []),
                    installation.incoming_webhook_url,
                    installation.incoming_webhook_channel,
                    installation.incoming_webhook_channel_id,
                    installation.incoming_webhook_configuration_url,
                    installation.is_enterprise_install,
                    installation.token_type,
                )
            )
            conn.commit()
            logger.info("Saved installation for team %s", installation.team_id)
    
    def find_installation(
        self,
        *,
        enterprise_id: Optional[str],
        team_id: Optional[str],
        user_id: Optional[str] = None,
        is_enterprise_install: Optional[bool] = False,
    ) -> Optional[Installation]:
        """Find installation by team/enterprise/user."""
        with self._connect() as conn:
            if user_id:
                row = conn.execute(
                    "SELECT * FROM installations WHERE enterprise_id = ? AND team_id = ? AND user_id = ?",
                    (enterprise_id, team_id, user_id)
                ).fetchone()
            else:
                row = conn.execute(
                    "SELECT * FROM installations WHERE enterprise_id = ? AND team_id = ?",
                    (enterprise_id, team_id)
                ).fetchone()
            
            if not row:
                return None
            
            return Installation(
                client_id=row["client_id"],
                enterprise_id=row["enterprise_id"],
                team_id=row["team_id"],
                team_name=row["team_name"],
                bot_token=row["bot_token"],
                bot_id=row["bot_id"],
                bot_user_id=row["bot_user_id"],
                bot_scopes=row["bot_scopes"].split(",") if row["bot_scopes"] else [],
                user_id=row["user_id"],
                user_token=row["user_token"],
                user_scopes=row["user_scopes"].split(",") if row["user_scopes"] else [],
                incoming_webhook_url=row["incoming_webhook_url"],
                incoming_webhook_channel=row["incoming_webhook_channel"],
                incoming_webhook_channel_id=row["incoming_webhook_channel_id"],
                incoming_webhook_configuration_url=row["incoming_webhook_configuration_url"],
                is_enterprise_install=bool(row["is_enterprise_install"]),
                token_type=row["token_type"],
            )
    
    def delete_installation(
        self,
        *,
        enterprise_id: Optional[str],
        team_id: Optional[str],
        user_id: Optional[str] = None,
    ):
        """Delete installation from database."""
        with self._connect() as conn:
            if user_id:
                conn.execute(
                    "DELETE FROM installations WHERE enterprise_id = ? AND team_id = ? AND user_id = ?",
                    (enterprise_id, team_id, user_id)
                )
            else:
                conn.execute(
                    "DELETE FROM installations WHERE enterprise_id = ? AND team_id = ?",
                    (enterprise_id, team_id)
                )
            conn.commit()
            logger.info("Deleted installation for team %s", team_id)


class SQLiteOAuthStateStore(OAuthStateStore):
    """Store OAuth states in SQLite database."""
    
    def __init__(self, db_path: str = None, expiration_seconds: int = 600):
        self.db_path = db_path or Config.DATABASE_PATH
        self.expiration_seconds = expiration_seconds
    
    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def issue(self) -> str:
        """Generate and store a new OAuth state."""
        import secrets
        state = secrets.token_urlsafe(32)
        expire_at = int(time.time()) + self.expiration_seconds
        
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO oauth_states (state, expire_at) VALUES (?, ?)",
                (state, expire_at)
            )
            conn.commit()
        
        return state
    
    def consume(self, state: str) -> bool:
        """Consume (validate and delete) an OAuth state."""
        current_time = int(time.time())
        
        with self._connect() as conn:
            # Check if state exists and is not expired
            row = conn.execute(
                "SELECT expire_at FROM oauth_states WHERE state = ?",
                (state,)
            ).fetchone()
            
            if not row or row["expire_at"] < current_time:
                return False
            
            # Delete the state (consume it)
            conn.execute("DELETE FROM oauth_states WHERE state = ?", (state,))
            
            # Clean up expired states
            conn.execute("DELETE FROM oauth_states WHERE expire_at < ?", (current_time,))
            
            conn.commit()
            return True