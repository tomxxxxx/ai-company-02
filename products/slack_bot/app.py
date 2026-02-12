"""TaskMaster Slack Bot — entry point.

Socket Mode (development):  python app.py
HTTP Mode   (production):   gunicorn app:flask_app
"""

import os
import logging
from flask import Flask, request, redirect
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_bolt.oauth.oauth_settings import OAuthSettings
from slack_bolt.oauth import OAuthFlow

from config import Config
from database import init_db
from slack_handlers import register_handlers
from oauth_store import SQLiteInstallationStore, SQLiteOAuthStateStore

# ── Logging ──────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(name)-20s  %(levelname)-7s  %(message)s",
)
logger = logging.getLogger(__name__)

# ── Validate env ─────────────────────────────────────────────
Config.validate()

# ── OAuth Setup ──────────────────────────────────────────────
if not Config.USE_SOCKET_MODE:
    installation_store = SQLiteInstallationStore()
    oauth_state_store = SQLiteOAuthStateStore()
    
    oauth_settings = OAuthSettings(
        client_id=Config.SLACK_CLIENT_ID,
        client_secret=Config.SLACK_CLIENT_SECRET,
        scopes=["commands", "chat:write", "app_mentions:read"],
        installation_store=installation_store,
        state_store=oauth_state_store,
    )
    
    slack_app = App(
        signing_secret=Config.SLACK_SIGNING_SECRET,
        oauth_settings=oauth_settings,
    )
else:
    slack_app = App(token=Config.SLACK_BOT_TOKEN)

# ── Database ─────────────────────────────────────────────────
init_db()

# ── Register slash-commands & events ─────────────────────────
register_handlers(slack_app)

# ── Flask (HTTP mode / health-check) ────────────────────────
flask_app = Flask(__name__)
handler = SlackRequestHandler(slack_app)


@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)


@flask_app.route("/slack/install", methods=["GET"])
def install():
    if Config.USE_SOCKET_MODE:
        return {"error": "OAuth not available in Socket Mode"}, 400
    return slack_app.oauth_flow.handle_installation(request)


@flask_app.route("/slack/oauth_redirect", methods=["GET"])
def oauth_redirect():
    if Config.USE_SOCKET_MODE:
        return {"error": "OAuth not available in Socket Mode"}, 400
    return slack_app.oauth_flow.handle_callback(request)


@flask_app.route("/", methods=["GET"])
def health_check():
    return {"status": "healthy", "app": "TaskMaster"}, 200


# ── Main ─────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))

    if Config.USE_SOCKET_MODE:
        logger.info("Starting TaskMaster in Socket Mode ...")
        sm = SocketModeHandler(slack_app, Config.SLACK_APP_TOKEN)
        sm.connect()  # non-blocking — connects via WebSocket
        # Also serve Flask so Railway/Render get a health-check port
        logger.info("Health-check on port %s", port)
        flask_app.run(host="0.0.0.0", port=port)
    else:
        port = int(os.environ.get("PORT", 5000))
        logger.info("Starting TaskMaster in HTTP mode on port %s ...", port)
        flask_app.run(host="0.0.0.0", port=port, debug=Config.DEBUG)