"""Global configuration for the AI Company system."""

from pathlib import Path

# Workspace root (project root directory)
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent

# Bootstrap files — nobody modifies these (keeps the system startable)
BOOTSTRAP_PROTECTED_PATHS = [
    "system/config.py",
    "system/__init__.py",
    "system/llm/__init__.py",
    "system/tools/__init__.py",
    "system/ceo/__init__.py",
    "system/department/__init__.py",
    "run.py",
]

# CEO can modify everything except bootstrap files
CEO_PROTECTED_PATHS = BOOTSTRAP_PROTECTED_PATHS

# Departments cannot touch system/, operator/, state/, or key root files
DEPARTMENT_PROTECTED_PATHS = [
    "system", "operator", "state", "Archiv",
    "ARCHITEKTUR.md", "run.py", "requirements.txt",
]

# LLM Configuration
DEFAULT_MODEL = "claude-sonnet-4-20250514"
DEFAULT_MAX_TOKENS = 8192
DEFAULT_TEMPERATURE = 0.7

# Cost estimation (Claude Sonnet pricing)
COST_PER_INPUT_TOKEN = 3.0 / 1_000_000    # $3 per MTok
COST_PER_OUTPUT_TOKEN = 15.0 / 1_000_000   # $15 per MTok

# Department defaults
DEFAULT_DEPARTMENT_MAX_TURNS = 30

# CEO defaults
CEO_MAX_TURNS = 50
