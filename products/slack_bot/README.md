# TaskMaster - Slack Task Management Bot

A minimal Slack bot for managing tasks within channels using slash commands.

## Features

- `/task [description]` — Create a new task in the current channel
- `/tasks` — List all open tasks in the current channel  
- `/done [task_id]` — Mark a task as complete
- `@TaskMaster help` — Show available commands
- Per-channel task storage with SQLite
- Socket Mode (dev) + HTTP mode (prod)

## Tech Stack

- Python 3.11 + Flask + Gunicorn
- `slack-bolt` for Slack integration
- SQLite for data persistence (zero-config)
- Deployable on Railway / Render / Heroku

## Quick Setup (15 minutes)

### 1. Create Slack App

1. Go to https://api.slack.com/apps → **Create New App** → **From Scratch**
2. Name: `TaskMaster`, pick your workspace
3. **Socket Mode** → Enable → create an App-Level Token (name: `socket`, scope: `connections:write`) → copy `xapp-...` token
4. **OAuth & Permissions** → add Bot Token Scopes:
   - `commands`
   - `chat:write`
   - `app_mentions:read`
5. **Install to Workspace** → copy `xoxb-...` Bot Token
6. **Slash Commands** → create three:
   - `/task` — "Create a new task" — no URL needed (Socket Mode)
   - `/tasks` — "List open tasks"
   - `/done` — "Complete a task"
7. **Event Subscriptions** → Subscribe to `app_mention`

### 2. Local Development

```bash
cd products/slack_bot
pip install -r requirements.txt
cp .env.example .env
# Fill in SLACK_BOT_TOKEN and SLACK_APP_TOKEN in .env
python app.py
```

### 3. Environment Variables

| Variable | Required | Example |
|----------|----------|---------|
| `SLACK_BOT_TOKEN` | Yes | `xoxb-123...` |
| `SLACK_APP_TOKEN` | Socket Mode | `xapp-1-...` |
| `SLACK_SIGNING_SECRET` | HTTP mode | `abc123...` |
| `DATABASE_PATH` | No (default: `taskmaster.db`) | `/data/tasks.db` |
| `SOCKET_MODE` | No (default: `True`) | `False` for prod |
| `PORT` | No (default: `3000`) | `5000` |

## Deployment (Railway — recommended)

1. Push code to GitHub
2. https://railway.app → New Project → Deploy from GitHub
3. Add environment variables:
   - `SLACK_BOT_TOKEN=xoxb-...`
   - `SLACK_SIGNING_SECRET=...`
   - `SOCKET_MODE=False`
4. Railway auto-detects Procfile → deploys
5. Copy the public URL → set as Request URL in Slack:
   - Event Subscriptions: `https://your-app.railway.app/slack/events`
   - Slash Commands: same URL

## Project Structure

```
slack_bot/
├── app.py              # Entry point (Socket Mode or HTTP)
├── config.py           # Config class (env vars)
├── database.py         # SQLite database manager
├── models.py           # Task dataclass
├── task_manager.py     # Business logic layer
├── slack_handlers.py   # All slash-command & event handlers
├── utils.py            # Validation helpers
├── requirements.txt    # Python dependencies
├── Procfile            # Production: gunicorn
└── runtime.txt         # Python version
```

## Database Schema

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK | Auto-increment |
| `channel_id` | TEXT | Slack channel |
| `description` | TEXT | Task text |
| `status` | TEXT | `open` or `completed` |
| `created_by` | TEXT | Slack user ID |
| `created_at` | TIMESTAMP | Auto |
| `completed_at` | TIMESTAMP | Nullable |
| `completed_by` | TEXT | Nullable |

## License

MIT