import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""

    # Slack Configuration
    SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN", "")
    SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN", "")
    SLACK_SIGNING_SECRET = os.environ.get("SLACK_SIGNING_SECRET", "")
    SLACK_CLIENT_ID = os.environ.get("SLACK_CLIENT_ID", "")
    SLACK_CLIENT_SECRET = os.environ.get("SLACK_CLIENT_SECRET", "")

    # Database
    DATABASE_PATH = os.environ.get("DATABASE_PATH", "taskmaster.db")

    # App Configuration
    DEBUG = os.environ.get("DEBUG", "False").lower() == "true"
    PORT = int(os.environ.get("PORT", 3000))
    HOST = os.environ.get("HOST", "0.0.0.0")

    # Socket Mode (for development — set to False for HTTP/production)
    USE_SOCKET_MODE = os.environ.get("SOCKET_MODE", "True").lower() == "true"

    # Task limits
    MAX_TASKS_PER_CHANNEL = int(os.environ.get("MAX_TASKS_PER_CHANNEL", 100))
    TASK_DESCRIPTION_MAX_LENGTH = int(os.environ.get("TASK_DESCRIPTION_MAX_LENGTH", 500))

    @classmethod
    def validate(cls):
        """Validate that all required env vars are present."""
        missing = []
        if cls.USE_SOCKET_MODE:
            if not cls.SLACK_BOT_TOKEN:
                missing.append("SLACK_BOT_TOKEN")
            if not cls.SLACK_APP_TOKEN:
                missing.append("SLACK_APP_TOKEN")
        else:
            if not cls.SLACK_SIGNING_SECRET:
                missing.append("SLACK_SIGNING_SECRET")
            if not cls.SLACK_CLIENT_ID:
                missing.append("SLACK_CLIENT_ID")
            if not cls.SLACK_CLIENT_SECRET:
                missing.append("SLACK_CLIENT_SECRET")
        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}"
            )