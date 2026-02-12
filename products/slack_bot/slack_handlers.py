"""Slack event & command handlers for TaskMaster."""

import logging
from slack_bolt import App
from task_manager import TaskManager

logger = logging.getLogger(__name__)

HELP_TEXT = (
    "*TaskMaster Help* :clipboard:\n\n"
    "Available commands:\n"
    "• `/task [description]` — Create a new task\n"
    "• `/tasks` — List all open tasks in this channel\n"
    "• `/done [task_id]` — Mark a task as complete\n"
    "• Mention me with *help* for this message"
)


def _fmt_error(msg: str) -> str:
    return f":x: {msg}"


def register_handlers(app: App):
    """Wire every slash-command and event to the Slack app."""
    tm = TaskManager()

    # ── /task [description] ──────────────────────────────────

    @app.command("/task")
    def handle_create_task(ack, respond, command):
        ack()
        description = (command.get("text") or "").strip()
        if not description:
            respond(_fmt_error("Please provide a task description.\nUsage: `/task Buy more coffee`"))
            return
        if len(description) > 500:
            respond(_fmt_error("Description too long (max 500 chars)."))
            return

        try:
            task = tm.create_task(
                channel_id=command["channel_id"],
                description=description,
                created_by=command["user_id"],
            )
            respond(
                {
                    "response_type": "in_channel",
                    "blocks": [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f":white_check_mark: *Task #{task['id']} created*\n{task['description']}",
                            },
                        }
                    ],
                }
            )
        except Exception as e:
            logger.error("Error creating task: %s", e)
            respond(_fmt_error("Failed to create task. Please try again."))

    # ── /tasks ───────────────────────────────────────────────

    @app.command("/tasks")
    def handle_list_tasks(ack, respond, command):
        ack()
        try:
            tasks = tm.get_tasks(channel_id=command["channel_id"])
            if not tasks:
                respond(":clipboard: No open tasks in this channel. Use `/task` to create one!")
                return

            lines = [f":clipboard: *Open Tasks* ({len(tasks)} total)\n"]
            for t in tasks:
                lines.append(f"• *#{t['id']}* — {t['description']}  (by <@{t['created_by']}>)")
            respond({"response_type": "in_channel", "text": "\n".join(lines)})
        except Exception as e:
            logger.error("Error listing tasks: %s", e)
            respond(_fmt_error("Failed to list tasks."))

    # ── /done [id] ───────────────────────────────────────────

    @app.command("/done")
    def handle_complete_task(ack, respond, command):
        ack()
        raw = (command.get("text") or "").strip()
        if not raw:
            respond(_fmt_error("Usage: `/done [task_id]`"))
            return
        try:
            task_id = int(raw)
        except ValueError:
            respond(_fmt_error("Invalid task ID — please provide a number."))
            return

        try:
            ok = tm.complete_task(task_id, command["channel_id"], command["user_id"])
            if ok:
                respond(
                    {
                        "response_type": "in_channel",
                        "text": f":tada: Task #{task_id} marked as complete!",
                    }
                )
            else:
                respond(_fmt_error(f"Task #{task_id} not found in this channel or already completed."))
        except Exception as e:
            logger.error("Error completing task: %s", e)
            respond(_fmt_error("Failed to complete task."))

    # ── @mention ─────────────────────────────────────────────

    @app.event("app_mention")
    def handle_mention(event, say):
        text = (event.get("text") or "").lower()
        if "help" in text:
            say(HELP_TEXT)
        else:
            say("Hi there! :wave: Type `@TaskMaster help` for available commands.")