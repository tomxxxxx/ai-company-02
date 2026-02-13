"""
Filesystem Tools — Read, write, edit, and list files in the workspace.
"""

import logging
from pathlib import Path

from core.autonomous.tools.base import Tool
from core.autonomous.tools.token_utils import estimate_tokens, is_text_too_large, calculate_chunk_size

logger = logging.getLogger(__name__)


class ReadFileTool(Tool):
    """Read the contents of a file."""

    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root

    @property
    def name(self) -> str:
        return "read_file"

    @property
    def description(self) -> str:
        return (
            "Read the contents of a file. Path can be relative to workspace root "
            "or absolute. Returns the file contents as text. "
            "For large files, use start_line and end_line to read a specific range."
        )

    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "File path (relative to workspace root or absolute)",
                },
                "start_line": {
                    "type": "integer",
                    "description": "Start reading from this line (1-based, optional)",
                },
                "end_line": {
                    "type": "integer",
                    "description": "Stop reading at this line (1-based, inclusive, optional)",
                },
            },
            "required": ["path"],
        }

    def _resolve_path(self, path: str) -> Path:
        p = Path(path)
        if not p.is_absolute():
            p = self.workspace_root / p
        return p.resolve()

    def execute(self, path: str, start_line: int = None, end_line: int = None, **kwargs) -> str:
        resolved = self._resolve_path(path)
        if not resolved.exists():
            return f"[ERROR] File not found: {path}"
        if not resolved.is_file():
            return f"[ERROR] Not a file: {path}"

        try:
            text = resolved.read_text(encoding="utf-8")
            lines = text.splitlines(keepends=True)
            total_lines = len(lines)

            # If no specific range requested, check if file is too large
            if not start_line and not end_line:
                if is_text_too_large(text, max_tokens=2000):
                    # File is too large, suggest chunking
                    chunk_size = calculate_chunk_size(total_lines, max_tokens_per_chunk=2000)
                    return (f"[WARNING] File {path} is too large ({estimate_tokens(text)} tokens). "
                           f"Use start_line/end_line parameters to read in chunks. "
                           f"Suggested chunk size: {chunk_size} lines. "
                           f"Total lines: {total_lines}\n\n"
                           f"[First {chunk_size} lines preview]\n" + 
                           "".join(lines[:chunk_size]))

            if start_line or end_line:
                start = max(1, start_line or 1) - 1
                end = min(len(lines), end_line or len(lines))
                lines = lines[start:end]
                return f"[Lines {start+1}-{end} of {total_lines} in {resolved}]\n" + "".join(lines)

            return text
        except Exception as e:
            return f"[ERROR] Failed to read {path}: {e}"


class WriteFileTool(Tool):
    """Write content to a file (creates or overwrites)."""

    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root

    @property
    def name(self) -> str:
        return "write_file"

    @property
    def description(self) -> str:
        return (
            "Write content to a file. Creates the file and any parent directories "
            "if they don't exist. Overwrites existing content. "
            "Path can be relative to workspace root or absolute."
        )

    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "File path (relative to workspace root or absolute)",
                },
                "content": {
                    "type": "string",
                    "description": "Content to write to the file",
                },
            },
            "required": ["path", "content"],
        }

    def _resolve_path(self, path: str) -> Path:
        p = Path(path)
        if not p.is_absolute():
            p = self.workspace_root / p
        return p.resolve()

    def execute(self, path: str, content: str, **kwargs) -> str:
        resolved = self._resolve_path(path)
        try:
            resolved.parent.mkdir(parents=True, exist_ok=True)
            resolved.write_text(content, encoding="utf-8")
            return f"File written: {resolved} ({len(content)} bytes)"
        except Exception as e:
            return f"[ERROR] Failed to write {path}: {e}"


class EditFileTool(Tool):
    """Edit a file by replacing a specific string."""

    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root

    @property
    def name(self) -> str:
        return "edit_file"

    @property
    def description(self) -> str:
        return (
            "Edit a file by replacing an exact string with new content. "
            "The old_string must match exactly (including whitespace and indentation). "
            "Include enough context to make the match unique."
        )

    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "File path (relative to workspace root or absolute)",
                },
                "old_string": {
                    "type": "string",
                    "description": "The exact string to replace (must match uniquely)",
                },
                "new_string": {
                    "type": "string",
                    "description": "The replacement string",
                },
            },
            "required": ["path", "old_string", "new_string"],
        }

    def _resolve_path(self, path: str) -> Path:
        p = Path(path)
        if not p.is_absolute():
            p = self.workspace_root / p
        return p.resolve()

    def execute(self, path: str, old_string: str, new_string: str, **kwargs) -> str:
        resolved = self._resolve_path(path)
        if not resolved.exists():
            return f"[ERROR] File not found: {path}"

        try:
            text = resolved.read_text(encoding="utf-8")
            count = text.count(old_string)

            if count == 0:
                return f"[ERROR] old_string not found in {path}"
            if count > 1:
                return f"[ERROR] old_string matches {count} locations in {path}. Include more context to make it unique."

            new_text = text.replace(old_string, new_string, 1)
            resolved.write_text(new_text, encoding="utf-8")
            return f"File edited: {resolved} (1 replacement made)"
        except Exception as e:
            return f"[ERROR] Failed to edit {path}: {e}"


class ListDirectoryTool(Tool):
    """List contents of a directory."""

    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root

    @property
    def name(self) -> str:
        return "list_directory"

    @property
    def description(self) -> str:
        return (
            "List the contents of a directory. Returns file and folder names. "
            "Folders end with '/'. Path can be relative to workspace root."
        )

    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Directory path (relative to workspace root or absolute). Use '.' for workspace root.",
                },
                "recursive": {
                    "type": "boolean",
                    "description": "If true, list contents recursively (default: false)",
                },
            },
            "required": ["path"],
        }

    def _resolve_path(self, path: str) -> Path:
        p = Path(path)
        if not p.is_absolute():
            p = self.workspace_root / p
        return p.resolve()

    def execute(self, path: str = ".", recursive: bool = False, **kwargs) -> str:
        resolved = self._resolve_path(path)
        if not resolved.exists():
            return f"[ERROR] Directory not found: {path}"
        if not resolved.is_dir():
            return f"[ERROR] Not a directory: {path}"

        try:
            entries = []
            if recursive:
                for item in sorted(resolved.rglob("*")):
                    # Skip __pycache__ and .git
                    parts = item.relative_to(resolved).parts
                    if any(p.startswith(".") or p == "__pycache__" for p in parts):
                        continue
                    rel = item.relative_to(resolved)
                    suffix = "/" if item.is_dir() else ""
                    entries.append(f"{rel}{suffix}")
            else:
                for item in sorted(resolved.iterdir()):
                    if item.name.startswith(".") or item.name == "__pycache__":
                        continue
                    suffix = "/" if item.is_dir() else ""
                    entries.append(f"{item.name}{suffix}")

            if not entries:
                return f"Directory {path} is empty"
            return "\n".join(entries)
        except Exception as e:
            return f"[ERROR] Failed to list {path}: {e}"
