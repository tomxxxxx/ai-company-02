"""Git Tools — Commit changes and check repo status."""

import logging
import subprocess
from pathlib import Path

from system.tools.base import Tool

logger = logging.getLogger(__name__)


class GitStatusTool(Tool):
    """Check git repository status."""

    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root

    @property
    def name(self):
        return "git_status"

    @property
    def description(self):
        return "Show current git status: modified, staged, and untracked files."

    @property
    def input_schema(self):
        return {"type": "object", "properties": {}}

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
            return output if output else "Working tree clean — no changes."
        except Exception as e:
            return f"[ERROR] git status failed: {e}"


class GitCommitTool(Tool):
    """Stage all changes and commit (with auto-push)."""

    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root

    @property
    def name(self):
        return "git_commit"

    @property
    def description(self):
        return (
            "Stage all changes (git add -A) and commit with the given message. "
            "Automatically pushes to remote after commit."
        )

    @property
    def input_schema(self):
        return {
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "Commit message"},
            },
            "required": ["message"],
        }

    def execute(self, message: str, **kwargs) -> str:
        try:
            # Stage
            add = subprocess.run(
                "git add -A", shell=True,
                cwd=str(self.workspace_root),
                capture_output=True, text=True, timeout=10,
            )
            if add.returncode != 0:
                return f"[ERROR] git add failed: {add.stderr}"

            # Check if anything to commit
            status = subprocess.run(
                "git status --porcelain", shell=True,
                cwd=str(self.workspace_root),
                capture_output=True, text=True, timeout=10,
            )
            if not status.stdout.strip():
                return "Nothing to commit — working tree clean."

            # Commit
            commit = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=str(self.workspace_root),
                capture_output=True, text=True, timeout=10,
            )
            if commit.returncode != 0:
                return f"[ERROR] git commit failed: {commit.stderr}"

            # Push
            push = subprocess.run(
                "git push", shell=True,
                cwd=str(self.workspace_root),
                capture_output=True, text=True, timeout=30,
            )
            push_msg = "\nPushed to remote." if push.returncode == 0 else f"\n[WARNING] Push failed: {push.stderr}"

            return f"Committed: {message}\n{commit.stdout.strip()}{push_msg}"
        except Exception as e:
            return f"[ERROR] git commit failed: {e}"
