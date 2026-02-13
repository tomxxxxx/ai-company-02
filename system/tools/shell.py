"""Shell Tool — Execute shell commands in the workspace."""

import logging
import platform
import subprocess
from pathlib import Path

from system.tools.base import Tool

logger = logging.getLogger(__name__)


class RunCommandTool(Tool):
    """Run a shell command in the workspace directory."""

    def __init__(self, workspace_root: Path, timeout: int = 60):
        self.workspace_root = workspace_root
        self.timeout = timeout

    @property
    def name(self):
        return "run_command"

    @property
    def description(self):
        os_name = platform.system()
        return (
            f"Run a shell command in the workspace directory. "
            f"OS: {os_name}. Timeout: {self.timeout}s. "
            f"Returns stdout + stderr."
        )

    @property
    def input_schema(self):
        return {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Shell command to execute"},
            },
            "required": ["command"],
        }

    def execute(self, command: str, **kwargs) -> str:
        logger.info(f"Running command: {command}")

        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=str(self.workspace_root),
                capture_output=True,
                text=True,
                timeout=self.timeout,
                encoding="utf-8",
                errors="replace",
            )

            parts = []
            if result.stdout:
                parts.append(result.stdout)
            if result.stderr:
                parts.append(f"[STDERR]\n{result.stderr}")

            output = "\n".join(parts) if parts else "(no output)"

            # Truncate very long output
            if len(output) > 50000:
                output = output[:25000] + "\n\n[...truncated...]\n\n" + output[-25000:]

            if result.returncode != 0:
                return f"[EXIT CODE {result.returncode}]\n{output}"

            return output

        except subprocess.TimeoutExpired:
            return f"[ERROR] Command timed out after {self.timeout}s: {command}"
        except Exception as e:
            return f"[ERROR] Failed to run command: {e}"
