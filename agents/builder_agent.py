"""
Builder Agent - Writes code, creates files, runs commands.

This is the agent that actually DOES things instead of just analyzing.
It can:
- Generate code using LLM
- Write files to disk
- Run shell commands
- Test code
- Deploy applications
"""

import logging
import os
import subprocess
import json
from pathlib import Path
from typing import Optional
from core.agent import Agent

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent


class BuilderAgent(Agent):
    def __init__(self, **kwargs):
        super().__init__(
            name="builder",
            role="Software Engineer - Builds and deploys products",
            **kwargs,
        )
        self.workspace = PROJECT_ROOT

    def run(self, state: dict) -> dict:
        """Run builder cycle: check what needs building, build it."""
        self.logger.info("Builder cycle starting...")

        products = state.get("products", {})
        cto_plan = state.get("_cto_build_plan", {})

        for product_id, product in products.items():
            if product["status"] == "building":
                self.logger.info(f"Building product: {product_id}")
                state = self._build_product(product_id, product, state, cto_plan)

        return state

    def _build_product(self, product_id: str, product: dict, state: dict, cto_plan: dict) -> dict:
        """Build a specific product."""
        product_dir = self.workspace / "products" / product_id

        if not product_dir.exists():
            # New product - generate from scratch
            self.logger.info(f"Generating new product: {product_id}")
            self._generate_product(product_id, product, product_dir)
        else:
            # Existing product - check what needs doing
            self.logger.info(f"Product exists, checking for tasks: {product_id}")
            self._iterate_product(product_id, product, product_dir, cto_plan)

        return state

    def _generate_product(self, product_id: str, product: dict, product_dir: Path):
        """Generate a complete product from scratch using LLM, file by file."""
        product_dir.mkdir(parents=True, exist_ok=True)

        # Step 1: Get file list
        file_list_response = self.analyze_json("""
You are building a Slack Bot MVP called "TaskMaster" using Python.

List ALL files needed for the MVP. Return ONLY a JSON array of filenames:
{
    "files": [
        "app.py",
        "database.py",
        "requirements.txt",
        ".env.example",
        "README.md",
        "Procfile"
    ],
    "setup_commands": ["pip install -r requirements.txt"],
    "env_vars_needed": ["SLACK_BOT_TOKEN", "SLACK_SIGNING_SECRET", "SLACK_APP_TOKEN"]
}

Just the file list, nothing else.
""")

        if "files" not in file_list_response or "error" in file_list_response:
            self.logger.error(f"Failed to get file list: {file_list_response}")
            return

        files = file_list_response["files"]
        self.logger.info(f"Will generate {len(files)} files: {files}")

        # Step 2: Generate each file individually (avoids JSON-in-JSON issues)
        for filename in files:
            self.logger.info(f"Generating: {filename}")
            content = self._generate_single_file(filename, files)
            if content and not content.startswith("[ERROR]"):
                file_path = product_dir / filename
                file_path.parent.mkdir(parents=True, exist_ok=True)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                self.logger.info(f"Created: {file_path}")
            else:
                self.logger.error(f"Failed to generate {filename}")

        self.decide(
            decision=f"Generated product {product_id} with {len(files)} files",
            reasoning="MVP generation file-by-file to avoid JSON parsing issues",
            data={"files": files},
        )

    def _generate_single_file(self, filename: str, all_files: list) -> str:
        """Generate content for a single file."""
        return self.think(f"""
Generate the COMPLETE content for the file: {filename}

This is part of a Slack Bot MVP called "TaskMaster".
Other files in this project: {all_files}

Tech stack:
- Python 3.14 + Flask
- slack_bolt library for Slack integration
- SQLite for storage
- Deployable on Railway/Heroku

Features:
1. /task [description] - creates a task in the current channel
2. /tasks - lists all open tasks in the current channel
3. /done [task_id] - marks a task as complete
4. Tasks stored per-channel in SQLite
5. Clean Slack message formatting with blocks

IMPORTANT:
- Output ONLY the raw file content, no markdown code fences
- No explanations, just the file content
- Make it production-ready but minimal
- Use slack_bolt (not raw Slack API)
- Use Socket Mode for development (easier setup)
""")

    def _iterate_product(self, product_id: str, product: dict, product_dir: Path, cto_plan: dict):
        """Iterate on existing product based on CTO plan."""
        # List current files
        existing_files = []
        for f in product_dir.rglob("*"):
            if f.is_file() and "__pycache__" not in str(f):
                rel = f.relative_to(product_dir)
                existing_files.append(str(rel))

        self.logger.info(f"Existing files in {product_id}: {existing_files}")

        # Check if there are build priorities from CTO
        if isinstance(cto_plan, dict) and "build_priorities" in cto_plan:
            for priority in cto_plan["build_priorities"]:
                if priority.get("product") == product_id:
                    self.logger.info(f"Working on: {priority.get('task', 'unknown')}")
                    # TODO: Implement specific task execution

    def write_file(self, path: str, content: str) -> bool:
        """Write a file to disk."""
        try:
            file_path = Path(path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            self.logger.info(f"File written: {path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to write file {path}: {e}")
            return False

    def run_command(self, command: str, cwd: Optional[str] = None, timeout: int = 120) -> dict:
        """Run a shell command and return output."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd or str(self.workspace),
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            output = {
                "returncode": result.returncode,
                "stdout": result.stdout[-2000:] if result.stdout else "",  # Truncate
                "stderr": result.stderr[-2000:] if result.stderr else "",
                "success": result.returncode == 0,
            }
            self.logger.info(f"Command: {command} -> exit {result.returncode}")
            return output
        except subprocess.TimeoutExpired:
            self.logger.error(f"Command timed out: {command}")
            return {"returncode": -1, "stdout": "", "stderr": "TIMEOUT", "success": False}
        except Exception as e:
            self.logger.error(f"Command failed: {command}: {e}")
            return {"returncode": -1, "stdout": "", "stderr": str(e), "success": False}

    def install_dependencies(self, product_dir: Path) -> bool:
        """Install Python dependencies for a product."""
        req_file = product_dir / "requirements.txt"
        if req_file.exists():
            result = self.run_command(
                f"python -m pip install -r {req_file} --quiet",
                cwd=str(product_dir),
            )
            return result["success"]
        return True

    def run_tests(self, product_dir: Path) -> dict:
        """Run tests for a product."""
        result = self.run_command(
            "python -m pytest -v --tb=short 2>&1 || python -m unittest discover -v 2>&1",
            cwd=str(product_dir),
        )
        return result

    def git_commit(self, message: str) -> bool:
        """Commit all changes to git."""
        self.run_command("git add .")
        result = self.run_command(f'git commit -m "{message}"')
        if result["success"]:
            self.run_command("git push")
        return result["success"]
