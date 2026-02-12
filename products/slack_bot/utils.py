import re
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from slack_sdk.models.blocks import Block, SectionBlock, DividerBlock, ContextBlock
from slack_sdk.models.blocks.block_elements import PlainTextObject, MarkdownTextObject


def validate_task_description(description: str) -> bool:
    """Validate task description is not empty and within reasonable length."""
    if not description or not description.strip():
        return False
    return len(description.strip()) <= 500


def validate_task_id(task_id: str) -> bool:
    """Validate task ID is a positive integer."""
    try:
        return int(task_id) > 0
    except (ValueError, TypeError):
        return False


def format_timestamp(timestamp: datetime) -> str:
    """Format datetime to human-readable string."""
    return timestamp.strftime("%Y-%m-%d %H:%M")


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to specified length with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def escape_slack_text(text: str) -> str:
    """Escape special characters for Slack formatting."""
    # Escape &, <, >
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    return text


def create_task_block(task_id: int, description: str, created_at: datetime, 
                     created_by: str, status: str = "open") -> List[Dict[str, Any]]:
    """Create Slack block for a single task."""
    status_emoji = "✅" if status == "completed" else "🔲"
    
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"{status_emoji} *Task #{task_id}*\n{escape_slack_text(description)}"
            }
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"Created by <@{created_by}> on {format_timestamp(created_at)}"
                }
            ]
        }
    ]
    
    return blocks


def create_task_list_blocks(tasks: List[Dict[str, Any]], channel_id: str) -> List[Dict[str, Any]]:
    """Create Slack blocks for task list."""
    if not tasks:
        return [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "📋 *No open tasks in this channel*\n\nUse `/task [description]` to create a new task!"
                }
            }
        ]
    
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"📋 *Open Tasks* ({len(tasks)} total)"
            }
        },
        {"type": "divider"}
    ]
    
    for task in tasks:
        task_blocks = create_task_block(
            task["id"],
            task["description"],
            task["created_at"],
            task["created_by"],
            task["status"]
        )
        blocks.extend(task_blocks)
        blocks.append({"type": "divider"})
    
    # Remove last divider
    if blocks and blocks[-1]["type"] == "divider":
        blocks.pop()
    
    return blocks


def create_success_block(message: str) -> List[Dict[str, Any]]:
    """Create success message block."""
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"✅ {message}"
            }
        }
    ]


def create_error_block(message: str) -> List[Dict[str, Any]]:
    """Create error message block."""
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"❌ {message}"
            }
        }
    ]


def create_help_block() -> List[Dict[str, Any]]:
    """Create help message block."""
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*🤖 TaskMaster Help*"
            }
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Available Commands:*\n\n" +
                        "• `/task [description]` - Create a new task\n" +
                        "• `/tasks` - List all open tasks in this channel\n" +
                        "• `/done [task_id]` - Mark a task as complete\n\n" +
                        "*Examples:*\n" +
                        "• `/task Review pull request #123`\n" +
                        "• `/done 5`"
            }
        }
    ]


def parse_command_text(text: str) -> str:
    """Parse and clean command text."""
    if not text:
        return ""
    return text.strip()


def extract_task_id_from_text(text: str) -> Optional[int]:
    """Extract task ID from command text."""
    text = text.strip()
    if not text:
        return None
    
    # Try to parse as integer
    try:
        return int(text)
    except ValueError:
        # Try to extract number from text like "task 5" or "#5"
        match = re.search(r'#?(\d+)', text)
        if match:
            return int(match.group(1))
    
    return None


def is_valid_channel_id(channel_id: str) -> bool:
    """Validate Slack channel ID format."""
    if not channel_id:
        return False
    return channel_id.startswith('C') and len(channel_id) >= 9


def is_valid_user_id(user_id: str) -> bool:
    """Validate Slack user ID format."""
    if not user_id:
        return False
    return user_id.startswith('U') and len(user_id) >= 9


def sanitize_input(text: str, max_length: int = 500) -> str:
    """Sanitize user input."""
    if not text:
        return ""
    
    # Strip whitespace and limit length
    text = text.strip()[:max_length]
    
    # Remove any potential harmful characters
    text = re.sub(r'[^\w\s\-.,!?@#$%^&*()+=\[\]{}|;:\'\"<>/\\`~]', '', text)
    
    return text


def format_error_response(error_message: str, include_help: bool = False) -> Dict[str, Any]:
    """Format error response for Slack."""
    blocks = create_error_block(error_message)
    
    if include_help:
        blocks.extend([{"type": "divider"}])
        blocks.extend(create_help_block())
    
    return {
        "response_type": "ephemeral",
        "blocks": blocks
    }


def format_success_response(message: str, blocks: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """Format success response for Slack."""
    if blocks is None:
        blocks = create_success_block(message)
    
    return {
        "response_type": "in_channel",
        "blocks": blocks
    }


def log_command_usage(command: str, user_id: str, channel_id: str, timestamp: datetime = None):
    """Log command usage for analytics (placeholder for future implementation)."""
    if timestamp is None:
        timestamp = datetime.utcnow()
    
    # This could be extended to log to a file or analytics service
    print(f"[{timestamp}] Command: {command}, User: {user_id}, Channel: {channel_id}")