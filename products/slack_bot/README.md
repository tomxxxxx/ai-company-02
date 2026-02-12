# TaskMaster - Slack Task Management Bot

A minimal Slack bot for managing tasks within channels using slash commands.

## Features

- `/task [description]` - Create a new task in the current channel
- `/tasks` - List all open tasks in the current channel  
- `/done [task_id]` - Mark a task as complete
- Per-channel task storage with SQLite
- Clean Slack message formatting with blocks
- Socket Mode support for easy development

## Tech Stack

- Python 3.14 + Flask
- slack_bolt library for Slack integration
- SQLite for data persistence
- Deployable on Railway/Heroku

## Quick Setup

### 1. Slack App Configuration

1. Create a new Slack app at https://api.slack.com/apps
2. Enable Socket Mode in your app settings
3. Add the following OAuth scopes under "OAuth & Permissions":
   - `commands` - Add slash commands
   - `chat:write` - Send messages
   - `channels:read` - Access channel information
4. Install the app to your workspace
5. Create slash commands:
   - `/task` - Create task
   - `/tasks` - List tasks
   - `/done` - Complete task

### 2. Local Development

1. Clone and install dependencies:
```bash
git clone <repository-url>
cd taskmaster
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your Slack tokens
```

3. Run the application:
```bash
python app.py
```

### 3. Environment Variables

Copy `.env.example` to `.env` and configure:

- `SLACK_BOT_TOKEN` - Bot User OAuth Token (starts with xoxb-)
- `SLACK_APP_TOKEN` - App-Level Token for Socket Mode (starts with xapp-)
- `DATABASE_URL` - SQLite database path (default: sqlite:///tasks.db)
- `PORT` - Application port (default: 3000)

## Usage

### Create a Task
```
/task Review pull request #123
```

### List Tasks
```
/tasks
```

### Complete a Task
```
/done 1
```

## Deployment

### Railway
1. Connect your GitHub repository to Railway
2. Add environment variables in Railway dashboard
3. Deploy automatically on push

### Heroku
1. Create Heroku app: `heroku create your-app-name`
2. Set environment variables: `heroku config:set SLACK_BOT_TOKEN=xoxb-...`
3. Deploy: `git push heroku main`

## Project Structure

```
taskmaster/
├── app.py              # Main Flask application
├── slack_handlers.py   # Slack event and command handlers
├── task_manager.py     # Task business logic
├── database.py         # Database connection and setup
├── models.py           # SQLAlchemy models
├── commands.py         # Slash command implementations
├── utils.py            # Utility functions
├── config.py           # Configuration management
├── requirements.txt    # Python dependencies
├── Procfile           # Heroku deployment config
├── runtime.txt        # Python version specification
└── .env.example       # Environment variables template
```

## Development

### Database Schema

Tasks are stored with the following fields:
- `id` - Unique task identifier
- `description` - Task description
- `channel_id` - Slack channel ID
- `created_by` - User who created the task
- `created_at` - Creation timestamp
- `completed` - Completion status
- `completed_at` - Completion timestamp

### Adding New Commands

1. Add command handler in `commands.py`
2. Register handler in `slack_handlers.py`
3. Update Slack app configuration with new slash command

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally
5. Submit a pull request

## License

MIT License - see LICENSE file for details