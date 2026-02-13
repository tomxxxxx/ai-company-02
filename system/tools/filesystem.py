"""Filesystem Tools — Read, write, edit, and list files."""

import logging
from pathlib import Path

from system.tools.base import Tool

logger = logging.getLogger(__name__)

MAX_FILE_CHARS = 50_000


class ReadFileTool(Tool):
    """Read file contents."""

    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root

    @property
    def name(self):
        return "read_file"

    @property
    def description(self):
        return (
            "Read a file's contents. For large files, use start_line/end_line. "
            "Path can be relative to workspace root or absolute."
        )

    @property
    def input_schema(self):
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path"},
                "start_line": {"type": "integer", "description": "Start line (1-based, optional)"},
                "end_line": {"type": "integer", "description": "End line (1-based, inclusive, optional)"},
            },
            "required": ["path"],
        }

    def _resolve(self, path: str) -> Path:
        p = Path(path)
        if not p.is_absolute():
            p = self.workspace_root / p
        return p.resolve()

    def execute(self, path: str, start_line: int = None, end_line: int = None, **kw) -> str:
        resolved = self._resolve(path)
        if not resolved.exists():
            return f"[ERROR] File not found: {path}"
        if not resolved.is_file():
            return f"[ERROR] Not a file: {path}"

        try:
            text = resolved.read_text(encoding="utf-8")
            lines = text.splitlines(keepends=True)
            total = len(lines)

            if start_line or end_line:
                s = max(1, start_line or 1) - 1
                e = min(total, end_line or total)
                return f"[Lines {s+1}-{e} of {total}]\n" + "".join(lines[s:e])

            if len(text) > MAX_FILE_CHARS:
                return (
                    f"[WARNING] File too large ({len(text)} chars, {total} lines). "
                    f"Use start_line/end_line to read in chunks.\n\n"
                    f"[First 100 lines preview]\n" + "".join(lines[:100])
                )

            return text
        except Exception as e:
            return f"[ERROR] Failed to read {path}: {e}"


class WriteFileTool(Tool):
    """Write content to a file (with path protection)."""

    def __init__(self, workspace_root: Path, protected_prefixes: list[str] = None):
        self.workspace_root = workspace_root
        self.protected_prefixes = protected_prefixes or []

    @property
    def name(self):
        return "write_file"

    @property
    def description(self):
        return "Write content to a file. Creates parent directories if needed."

    @property
    def input_schema(self):
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path"},
                "content": {"type": "string", "description": "Content to write"},
            },
            "required": ["path", "content"],
        }

    def _resolve(self, path: str) -> Path:
        p = Path(path)
        if not p.is_absolute():
            p = self.workspace_root / p
        return p.resolve()

    def _is_protected(self, resolved: Path) -> bool:
        for prefix in self.protected_prefixes:
            protected = (self.workspace_root / prefix).resolve()
            try:
                resolved.relative_to(protected)
                return True
            except ValueError:
                pass
            if protected == resolved:
                return True
        return False

    def execute(self, path: str, content: str, **kw) -> str:
        resolved = self._resolve(path)
        if self._is_protected(resolved):
            return f"[BLOCKED] Schreibzugriff auf geschützten Pfad: {path}"

        try:
            resolved.parent.mkdir(parents=True, exist_ok=True)
            resolved.write_text(content, encoding="utf-8")
            return f"File written: {resolved} ({len(content)} bytes)"
        except Exception as e:
            return f"[ERROR] Failed to write {path}: {e}"


class EditFileTool(Tool):
    """Edit a file by exact string replacement (with path protection)."""

    def __init__(self, workspace_root: Path, protected_prefixes: list[str] = None):
        self.workspace_root = workspace_root
        self.protected_prefixes = protected_prefixes or []

    @property
    def name(self):
        return "edit_file"

    @property
    def description(self):
        return "Edit a file by replacing an exact string. Include enough context for a unique match."

    @property
    def input_schema(self):
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path"},
                "old_string": {"type": "string", "description": "Exact string to replace"},
                "new_string": {"type": "string", "description": "Replacement string"},
            },
            "required": ["path", "old_string", "new_string"],
        }

    def _resolve(self, path: str) -> Path:
        p = Path(path)
        if not p.is_absolute():
            p = self.workspace_root / p
        return p.resolve()

    def _is_protected(self, resolved: Path) -> bool:
        for prefix in self.protected_prefixes:
            protected = (self.workspace_root / prefix).resolve()
            try:
                resolved.relative_to(protected)
                return True
            except ValueError:
                pass
            if protected == resolved:
                return True
        return False

    def execute(self, path: str, old_string: str, new_string: str, **kw) -> str:
        resolved = self._resolve(path)
        if self._is_protected(resolved):
            return f"[BLOCKED] Schreibzugriff auf geschützten Pfad: {path}"
        if not resolved.exists():
            return f"[ERROR] File not found: {path}"

        try:
            text = resolved.read_text(encoding="utf-8")
            count = text.count(old_string)

            if count == 0:
                return f"[ERROR] String not found in {path}"
            if count > 1:
                return f"[ERROR] String matches {count} locations. Add more context."

            new_text = text.replace(old_string, new_string, 1)
            resolved.write_text(new_text, encoding="utf-8")
            return f"File edited: {resolved} (1 replacement)"
        except Exception as e:
            return f"[ERROR] Failed to edit {path}: {e}"


class ListDirectoryTool(Tool):
    """List directory contents."""

    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root

    @property
    def name(self):
        return "list_directory"

    @property
    def description(self):
        return "List files and folders in a directory. Folders end with '/'. Use '.' for workspace root."

    @property
    def input_schema(self):
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Directory path. Use '.' for root."},
            },
            "required": ["path"],
        }

    def _resolve(self, path: str) -> Path:
        p = Path(path)
        if not p.is_absolute():
            p = self.workspace_root / p
        return p.resolve()

    def execute(self, path: str = ".", **kw) -> str:
        resolved = self._resolve(path)
        if not resolved.exists():
            return f"[ERROR] Directory not found: {path}"
        if not resolved.is_dir():
            return f"[ERROR] Not a directory: {path}"

        try:
            entries = []
            for item in sorted(resolved.iterdir()):
                if item.name.startswith(".") or item.name == "__pycache__":
                    continue
                suffix = "/" if item.is_dir() else ""
                entries.append(f"{item.name}{suffix}")
            return "\n".join(entries) if entries else "(empty directory)"
        except Exception as e:
            return f"[ERROR] Failed to list {path}: {e}"
