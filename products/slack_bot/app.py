import os
import logging
from flask import Flask, request
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from config import Config
from database import init_db
from slack_handlers import register_handlers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
flask_app = Flask(__name__)

# Initialize Slack app with Socket Mode
slack_app = App(
    token=Config.SLACK_BOT_TOKEN,
    signing_secret=Config.SLACK_SIGNING_SECRET,
    socket_mode=True,
    app_token=Config.SLACK_APP_TOKEN
)

# Initialize database
init_db()

# Register Slack handlers
register_handlers(slack_app)

# Create Flask request handler
handler = SlackRequestHandler(slack_app)

@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)

@flask_app.route("/", methods=["GET"])
def health_check():
    return {"status": "healthy", "app": "TaskMaster"}, 200

def start_socket_mode():
    """Start the app in Socket Mode (for development)"""
    try:
        logger.info("Starting TaskMaster in Socket Mode...")
        slack_app.start(port=int(os.environ.get("PORT", 3000)))
    except Exception as e:
        logger.error(f"Failed to start Socket Mode: {e}")
        raise

if __name__ == "__main__":
    if Config.USE_SOCKET_MODE:
        start_socket_mode()
    else:
        # HTTP mode for production deployment
        port = int(os.environ.get("PORT", 5000))
        flask_app.run(host="0.0.0.0", port=port, debug=Config.DEBUG)