"""
Git Tools — Commit changes and check repo status.
"""

import logging
import subprocess
from pathlib import Path

from core.autonomous.tools.base import Tool

logger = logging.getLogger(__name__)


class GitStatusTool(Tool):
    """Check git repository status."""

    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root

    @property
    def name(self) -> str:
        return "git_status"

    @property
    def description(self) -> str:
        return "Show the current git status: modified, staged, and untracked files."

    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {},
        }

    def execute(self, **kwargs) -> str:
        try:
            result = subprocess.run(
                "git status --short",
                shell=True,
                cwd=str(self.workspace_root),
                capture_output=True,
                text=True,
                timeout=10,
            )
            output = result.stdout.strip()
            if not output:
                return "Working tree clean — no changes."
            return output
        except Exception as e:
            return f"[ERROR] git status failed: {e}"


class GitCommitTool(Tool):
    """Stage all changes and commit."""

    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root

    @property
    def name(self) -> str:
        return "git_commit"

    @property
    def description(self) -> str:
        return (
            "Stage all current changes (git add -A) and commit with the given message. "
            "Use descriptive commit messages that explain WHY the change was made."
        )

    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Commit message describing the changes",
                },
            },
            "required": ["message"],
        }

    def execute(self, message: str, **kwargs) -> str:
        try:
            # Stage all changes
            add_result = subprocess.run(
                "git add -A",
                shell=True,
                cwd=str(self.workspace_root),
                capture_output=True,
                text=True,
                timeout=10,
            )
            if add_result.returncode != 0:
                return f"[ERROR] git add failed: {add_result.stderr}"

            # Check if there's anything to commit
            status = subprocess.run(
                "git status --porcelain",
                shell=True,
                cwd=str(self.workspace_root),
                capture_output=True,
                text=True,
                timeout=10,
            )
            if not status.stdout.strip():
                return "Nothing to commit — working tree clean."

            # Commit
            commit_result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=str(self.workspace_root),
                capture_output=True,
                text=True,
                timeout=10,
            )
            if commit_result.returncode != 0:
                return f"[ERROR] git commit failed: {commit_result.stderr}"

            return f"Committed: {message}\n{commit_result.stdout.strip()}"
        except Exception as e:
            return f"[ERROR] git commit failed: {e}"
