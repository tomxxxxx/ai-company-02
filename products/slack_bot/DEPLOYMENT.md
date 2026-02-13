# TaskMaster Slack Bot — Deployment Guide

## Overview
TaskMaster is a Slack bot for task management that supports both Socket Mode (development) and HTTP Mode (production) deployment.

## Prerequisites
- Python 3.8+
- Slack App configured with appropriate permissions
- Database storage (SQLite supported out-of-the-box)

## Dependencies
Install all dependencies from `requirements.txt`:
```bash
pip install -r requirements.txt
```

### Required Packages
- `slack-bolt>=1.18.0` — Slack Bot framework
- `slack-sdk>=3.21.0` — Slack SDK
- `Flask>=2.3.0` — Web framework for HTTP endpoints
- `python-dotenv>=1.0.0` — Environment variable management
- `gunicorn>=21.2.0` — WSGI HTTP Server (production)
- `requests>=2.31.0` — HTTP library

## Environment Variables

### Socket Mode (Development)
For development with Socket Mode, set:
```bash
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token
SOCKET_MODE=true
DEBUG=true
```

### HTTP Mode (Production)
For production deployment with HTTP endpoints, set:
```bash
SLACK_SIGNING_SECRET=your-signing-secret
SLACK_CLIENT_ID=your-client-id
SLACK_CLIENT_SECRET=your-client-secret
SOCKET_MODE=false
DEBUG=false
PORT=5000
```

### Optional Configuration
```bash
DATABASE_PATH=taskmaster.db                # Database file path
HOST=0.0.0.0                              # Server host
MAX_TASKS_PER_CHANNEL=100                 # Task limit per channel
TASK_DESCRIPTION_MAX_LENGTH=500           # Max task description length
```

## HTTP Endpoints

The Flask app exposes the following endpoints:

### Core Slack Endpoints
- `POST /slack/events` — Slack Events API endpoint
- `GET /slack/install` — OAuth installation flow
- `GET /slack/oauth_redirect` — OAuth callback

### Health Check
- `GET /` — Health check endpoint (returns `{"status": "healthy", "app": "TaskMaster"}`)

## Deployment Options

### 1. Socket Mode (Development)
```bash
python app.py
```
- Uses WebSocket connection to Slack
- Requires `SLACK_BOT_TOKEN` and `SLACK_APP_TOKEN`
- Good for development and testing

### 2. HTTP Mode (Production)
```bash
# Using built-in Flask server (not recommended for production)
python app.py

# Using Gunicorn (recommended)
gunicorn app:flask_app --bind 0.0.0.0:5000 --workers 2
```

### 3. Platform-as-a-Service (Heroku, Railway, Render)
The app includes a `Procfile` for easy PaaS deployment:
```
web: gunicorn app:flask_app --bind 0.0.0.0:$PORT
```

## Database Setup
The app uses SQLite by default. Database initialization happens automatically when the app starts.

For production, consider:
- Setting `DATABASE_PATH` to a persistent volume
- Using PostgreSQL/MySQL (requires code modifications)

## Slack App Configuration

### Required Scopes
- `commands` — For slash commands
- `chat:write` — To send messages
- `app_mentions:read` — To respond to @mentions

### Slash Commands to Configure
- `/task` — Create new task
- `/tasks` — List open tasks  
- `/done` — Mark task complete

### Event Subscriptions
- `app_mention` — Respond to @mentions

## Testing Deployment

### 1. Syntax Check
```bash
python -m py_compile app.py
python -m py_compile config.py
```

### 2. Local Health Check
```bash
# Start the app
python app.py

# Test health endpoint (in another terminal)
curl http://localhost:3000/
# Expected: {"status": "healthy", "app": "TaskMaster"}
```

### 3. Environment Validation
The app validates required environment variables on startup and will fail fast if they're missing.

## Production Checklist

- [ ] Set `DEBUG=false`
- [ ] Set `SOCKET_MODE=false` for HTTP mode
- [ ] Configure all required environment variables
- [ ] Set up persistent database storage
- [ ] Configure reverse proxy/load balancer if needed
- [ ] Set up monitoring and logging
- [ ] Test OAuth flow (if using HTTP mode)
- [ ] Verify Slack app permissions and endpoints

## Troubleshooting

### Common Issues
1. **Missing environment variables**: Check Config.validate() error message
2. **Import errors**: Install all requirements.txt dependencies
3. **Database permissions**: Ensure write access to DATABASE_PATH location
4. **Slack API errors**: Verify bot tokens and app permissions

### Logs
The app uses Python logging. Increase log level for debugging:
```python
logging.basicConfig(level=logging.DEBUG)
```

## Security Notes
- Never commit tokens/secrets to version control
- Use environment variables or secure secret management
- In production, run behind HTTPS
- Validate Slack request signatures (handled by slack-bolt)