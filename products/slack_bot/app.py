"""TaskMaster Slack Bot — entry point.

Socket Mode (development):  python app.py
HTTP Mode   (production):   gunicorn app:flask_app
"""

import os
import logging
from flask import Flask, request
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_bolt.adapter.socket_mode import SocketModeHandler

from config import Config
from database import init_db
from slack_handlers import register_handlers

# ── Logging ──────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(name)-20s  %(levelname)-7s  %(message)s",
)
logger = logging.getLogger(__name__)

# ── Validate env ─────────────────────────────────────────────
Config.validate()

# ── Slack Bolt app ───────────────────────────────────────────
if Config.USE_SOCKET_MODE:
    slack_app = App(token=Config.SLACK_BOT_TOKEN)
else:
    slack_app = App(
        token=Config.SLACK_BOT_TOKEN,
        signing_secret=Config.SLACK_SIGNING_SECRET,
    )

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


@flask_app.route("/", methods=["GET"])
def health_check():
    return {"status": "healthy", "app": "TaskMaster"}, 200


# ── Main ─────────────────────────────────────────────────────
if __name__ == "__main__":
    if Config.USE_SOCKET_MODE:
        logger.info("Starting TaskMaster in Socket Mode (dev) ...")
        sm = SocketModeHandler(slack_app, Config.SLACK_APP_TOKEN)
        sm.start()
    else:
        port = int(os.environ.get("PORT", 5000))
        logger.info("Starting TaskMaster in HTTP mode on port %s ...", port)
        flask_app.run(host="0.0.0.0", port=port, debug=Config.DEBUG)