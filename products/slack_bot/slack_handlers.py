import logging
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from task_manager import TaskManager
from utils import format_task_list, format_task_created, format_task_completed, format_error
import os

logger = logging.getLogger(__name__)

class SlackHandlers:
    def __init__(self, app: App):
        self.app = app
        self.task_manager = TaskManager()
        self._register_handlers()
    
    def _register_handlers(self):
        """Register all Slack event handlers"""
        self.app.command("/task")(self.handle_create_task)
        self.app.command("/tasks")(self.handle_list_tasks)
        self.app.command("/done")(self.handle_complete_task)
        self.app.event("app_mention")(self.handle_app_mention)
    
    def handle_create_task(self, ack, say, command):
        """Handle /task command to create a new task"""
        ack()
        
        try:
            description = command['text'].strip()
            if not description:
                say(format_error("Please provide a task description. Usage: `/task [description]`"))
                return
            
            channel_id = command['channel_id']
            user_id = command['user_id']
            
            task = self.task_manager.create_task(
                description=description,
                channel_id=channel_id,
                created_by=user_id
            )
            
            say(blocks=format_task_created(task))
            
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            say(format_error("Failed to create task. Please try again."))
    
    def handle_list_tasks(self, ack, say, command):
        """Handle /tasks command to list all open tasks"""
        ack()
        
        try:
            channel_id = command['channel_id']
            tasks = self.task_manager.get_tasks_by_channel(channel_id)
            
            if not tasks:
                say("No open tasks in this channel! 🎉")
                return
            
            say(blocks=format_task_list(tasks))
            
        except Exception as e:
            logger.error(f"Error listing tasks: {e}")
            say(format_error("Failed to retrieve tasks. Please try again."))
    
    def handle_complete_task(self, ack, say, command):
        """Handle /done command to mark a task as complete"""
        ack()
        
        try:
            task_id_str = command['text'].strip()
            if not task_id_str:
                say(format_error("Please provide a task ID. Usage: `/done [task_id]`"))
                return
            
            try:
                task_id = int(task_id_str)
            except ValueError:
                say(format_error("Invalid task ID. Please provide a number."))
                return
            
            channel_id = command['channel_id']
            user_id = command['user_id']
            
            task = self.task_manager.complete_task(task_id, channel_id, user_id)
            
            if task:
                say(blocks=format_task_completed(task))
            else:
                say(format_error(f"Task #{task_id} not found in this channel or already completed."))
                
        except Exception as e:
            logger.error(f"Error completing task: {e}")
            say(format_error("Failed to complete task. Please try again."))
    
    def handle_app_mention(self, event, say):
        """Handle app mentions for help and interaction"""
        try:
            text = event.get('text', '').lower()
            
            if 'help' in text:
                help_message = {
                    "blocks": [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": "*TaskMaster Help* 📋\n\nAvailable commands:\n• `/task [description]` - Create a new task\n• `/tasks` - List all open tasks\n• `/done [task_id]` - Mark task as complete"
                            }
                        }
                    ]
                }
                say(blocks=help_message["blocks"])
            else:
                say("Hi there! 👋 Type `@TaskMaster help` for available commands.")
                
        except Exception as e:
            logger.error(f"Error handling app mention: {e}")
            say("Sorry, I encountered an error. Please try again.")

def create_socket_mode_handler(app: App) -> SocketModeHandler:
    """Create and return Socket Mode handler"""
    app_token = os.environ.get("SLACK_APP_TOKEN")
    if not app_token:
        raise ValueError("SLACK_APP_TOKEN environment variable is required")
    
    return SocketModeHandler(app, app_token)