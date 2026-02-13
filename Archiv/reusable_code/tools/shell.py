"""
Shell Tool — Execute shell commands in the workspace.
"""

import logging
import platform
import subprocess
from pathlib import Path

from core.autonomous.tools.base import Tool

logger = logging.getLogger(__name__)


class RunCommandTool(Tool):
    """Run a shell command in the workspace directory."""

    def __init__(self, workspace_root: Path, timeout: int = 60):
        self.workspace_root = workspace_root
        self.timeout = timeout

    @property
    def name(self) -> str:
        return "run_command"

    @property
    def description(self) -> str:
        os_name = platform.system()
        return (
            f"Run a shell command in the workspace directory. "
            f"Current OS: {os_name}. "
            f"Commands execute in: {self.workspace_root}. "
            f"Timeout: {self.timeout}s. "
            f"Use this for: running scripts, installing packages, testing code, "
            f"checking system state, and any other shell operations. "
            f"Returns stdout + stderr combined."
        )

    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The shell command to execute",
                },
                "working_directory": {
                    "type": "string",
                    "description": "Working directory (relative to workspace root, optional)",
                },
            },
            "required": ["command"],
        }

    def execute(self, command: str, working_directory: str = None, **kwargs) -> str:
        cwd = self.workspace_root
        if working_directory:
            cwd = Path(working_directory)
            if not cwd.is_absolute():
                cwd = self.workspace_root / cwd
            cwd = cwd.resolve()

        logger.info(f"Running command: {command} (cwd: {cwd})")

        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=self.timeout,
                encoding="utf-8",
                errors="replace",
            )

            output_parts = []
            if result.stdout:
                output_parts.append(result.stdout)
            if result.stderr:
                output_parts.append(f"[STDERR]\n{result.stderr}")

            output = "\n".join(output_parts) if output_parts else "(no output)"

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
