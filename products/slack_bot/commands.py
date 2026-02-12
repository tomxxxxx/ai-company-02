from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from task_manager import TaskManager
from utils import format_task_list, format_error_message, format_success_message
import logging

logger = logging.getLogger(__name__)

def register_commands(app: App, task_manager: TaskManager):
    """Register all slash commands with the Slack app"""
    
    @app.command("/task")
    def create_task_command(ack, respond, command):
        """Handle /task [description] command"""
        ack()
        
        try:
            description = command['text'].strip()
            if not description:
                respond(format_error_message("Please provide a task description. Usage: `/task Your task description`"))
                return
            
            channel_id = command['channel_id']
            user_id = command['user_id']
            
            task = task_manager.create_task(channel_id, description, user_id)
            
            if task:
                respond(format_success_message(f"Task created: #{task.id} - {task.description}"))
            else:
                respond(format_error_message("Failed to create task. Please try again."))
                
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            respond(format_error_message("An error occurred while creating the task."))
    
    @app.command("/tasks")
    def list_tasks_command(ack, respond, command):
        """Handle /tasks command"""
        ack()
        
        try:
            channel_id = command['channel_id']
            tasks = task_manager.get_tasks_by_channel(channel_id)
            
            if tasks:
                respond(format_task_list(tasks))
            else:
                respond({
                    "response_type": "ephemeral",
                    "blocks": [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": "📋 No open tasks in this channel."
                            }
                        }
                    ]
                })
                
        except Exception as e:
            logger.error(f"Error listing tasks: {e}")
            respond(format_error_message("An error occurred while retrieving tasks."))
    
    @app.command("/done")
    def complete_task_command(ack, respond, command):
        """Handle /done [task_id] command"""
        ack()
        
        try:
            task_id_str = command['text'].strip()
            if not task_id_str:
                respond(format_error_message("Please provide a task ID. Usage: `/done [task_id]`"))
                return
            
            try:
                task_id = int(task_id_str)
            except ValueError:
                respond(format_error_message("Invalid task ID. Please provide a valid number."))
                return
            
            channel_id = command['channel_id']
            user_id = command['user_id']
            
            success = task_manager.complete_task(task_id, channel_id, user_id)
            
            if success:
                respond(format_success_message(f"✅ Task #{task_id} marked as complete!"))
            else:
                respond(format_error_message(f"Task #{task_id} not found or already completed in this channel."))
                
        except Exception as e:
            logger.error(f"Error completing task: {e}")
            respond(format_error_message("An error occurred while completing the task."))