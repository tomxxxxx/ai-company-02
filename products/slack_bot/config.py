import os
from dotenv import load_dotenv

load_dotenv()

# Slack Configuration
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")
SLACK_SIGNING_SECRET = os.environ.get("SLACK_SIGNING_SECRET")

# Database Configuration
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///taskmaster.db")

# App Configuration
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"
PORT = int(os.environ.get("PORT", 3000))
HOST = os.environ.get("HOST", "0.0.0.0")

# Socket Mode (for development)
SOCKET_MODE = os.environ.get("SOCKET_MODE", "True").lower() == "true"

# Task Configuration
MAX_TASKS_PER_CHANNEL = int(os.environ.get("MAX_TASKS_PER_CHANNEL", 100))
TASK_DESCRIPTION_MAX_LENGTH = int(os.environ.get("TASK_DESCRIPTION_MAX_LENGTH", 500))

# Validation
required_vars = ["SLACK_BOT_TOKEN"]
if SOCKET_MODE:
    required_vars.append("SLACK_APP_TOKEN")
else:
    required_vars.append("SLACK_SIGNING_SECRET")

missing_vars = [var for var in required_vars if not os.environ.get(var)]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")