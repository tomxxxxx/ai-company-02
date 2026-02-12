"""
Ticket Executor — executes tickets by delegating to the builder agent.

Takes a structured ticket dict, reads related files for context,
generates a focused LLM prompt, and writes output files.

This is the bridge between the Company OS (tickets/policies)
and the builder agent (code generation).
"""

import re
import logging
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from core.llm import LLM
from core.state import log_decision

logger = logging.getLogger(__name__)

ROOT = Path(__file__).parent.parent


class TicketExecutor:
    """Executes a single ticket using LLM-powered code generation."""

    def __init__(self, llm: Optional[LLM] = None):
        self.llm = llm or LLM()
        self.files_written: list[str] = []
        self.errors: list[str] = []
        self.llm_calls = 0

    def execute(self, ticket: dict) -> dict:
        """
        Execute a ticket and return result.

        Returns: {"success": bool, "files_written": [...], "errors": [...], "llm_calls": int}
        """
        ticket_id = ticket.get("id", "UNKNOWN")
        title = ticket.get("title", "")
        logger.info(f"Executing ticket {ticket_id}: {title}")

        # Read the full ticket file for context
        source_file = ticket.get("source_file", "")
        ticket_content = ""
        if source_file and Path(source_file).exists():
            ticket_content = Path(source_file).read_text(encoding="utf-8")

        # Determine what kind of work this is
        assignee = ticket.get("assignee", "").lower()

        if "builder" in assignee:
            return self._execute_code_ticket(ticket, ticket_content)
        elif "architect" in assignee:
            return self._execute_artifact_ticket(ticket, ticket_content)
        else:
            self.errors.append(f"Unknown assignee type: {assignee}")
            return self._result(False)

    def _execute_code_ticket(self, ticket: dict, ticket_content: str) -> dict:
        """Execute a ticket that requires code generation."""
        if not self.llm or not self.llm.available:
            self.errors.append("No LLM available for code generation")
            return self._result(False)

        # Find which experiment/product this relates to
        experiment = ticket.get("experiment", "")
        product_dir = self._resolve_product_dir(experiment)

        # Read existing code for context
        existing_code = self._read_product_files(product_dir) if product_dir else {}

        # Build the prompt
        prompt = self._build_code_prompt(ticket, ticket_content, existing_code)

        # Call LLM
        system = (
            "You are a senior software engineer. You receive structured work tickets "
            "and produce exact file contents. Output ONLY a JSON object with this format:\n"
            '{"files": [{"path": "relative/path.py", "content": "full file content"}]}\n'
            "No explanations. No markdown. Just the JSON."
        )

        try:
            response = self.llm.ask(prompt, system=system, max_tokens=8192, temperature=0.3)
            self.llm_calls += 1
        except Exception as e:
            self.errors.append(f"LLM call failed: {e}")
            return self._result(False)

        # Parse response
        files = self._parse_file_output(response)
        if not files:
            self.errors.append("Failed to parse LLM output into files")
            logger.error(f"LLM response was: {response[:500]}")
            return self._result(False)

        # Write files
        for file_info in files:
            rel_path = file_info["path"]
            content = file_info["content"]

            if product_dir:
                full_path = product_dir / rel_path
            else:
                full_path = ROOT / rel_path

            try:
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content, encoding="utf-8")
                self.files_written.append(str(full_path))
                logger.info(f"  Wrote: {full_path}")
            except Exception as e:
                self.errors.append(f"Failed to write {full_path}: {e}")

        # Update ticket status
        self._update_ticket_status(ticket, "DONE")

        # Log decision
        log_decision(
            decision=f"Executed {ticket.get('id')}: {ticket.get('title')}",
            reasoning=f"Generated {len(self.files_written)} files via LLM",
            agent="ticket-executor",
            data={"files": self.files_written, "llm_calls": self.llm_calls},
        )

        return self._result(True)

    def _execute_artifact_ticket(self, ticket: dict, ticket_content: str) -> dict:
        """Execute a ticket that requires generating OS artifacts (templates, specs)."""
        if not self.llm or not self.llm.available:
            self.errors.append("No LLM available")
            return self._result(False)

        prompt = (
            f"Generate the artifact described in this ticket:\n\n"
            f"{ticket_content}\n\n"
            f"Output as JSON: {{\"files\": [{{\"path\": \"...\", \"content\": \"...\"}}]}}"
        )
        system = (
            "You are a system architect. Generate structured artifacts (templates, specs, policies). "
            "Output ONLY valid JSON with file paths and content."
        )

        try:
            response = self.llm.ask(prompt, system=system, max_tokens=4096, temperature=0.3)
            self.llm_calls += 1
        except Exception as e:
            self.errors.append(f"LLM call failed: {e}")
            return self._result(False)

        files = self._parse_file_output(response)
        if not files:
            self.errors.append("Failed to parse artifact output")
            return self._result(False)

        for file_info in files:
            full_path = ROOT / file_info["path"]
            try:
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(file_info["content"], encoding="utf-8")
                self.files_written.append(str(full_path))
            except Exception as e:
                self.errors.append(f"Failed to write {full_path}: {e}")

        self._update_ticket_status(ticket, "DONE")
        return self._result(True)

    def _build_code_prompt(
        self, ticket: dict, ticket_content: str, existing_code: dict
    ) -> str:
        """Build a focused prompt for code generation."""
        existing_summary = ""
        for path, content in existing_code.items():
            existing_summary += f"\n--- {path} ---\n{content}\n"

        return f"""TICKET: {ticket.get('id')} — {ticket.get('title')}

FULL TICKET SPEC:
{ticket_content}

EXISTING CODE:
{existing_summary}

INSTRUCTIONS:
1. Read the ticket's Acceptance Criteria carefully
2. Modify or create only the files needed to fulfill the ticket
3. Keep all existing functionality intact
4. For modified files, output the COMPLETE new file content (not diffs)
5. Use the existing code style and patterns

Output format — ONLY valid JSON, no markdown:
{{"files": [{{"path": "relative/filename.py", "content": "complete file content"}}]}}
"""

    def _resolve_product_dir(self, experiment: str) -> Optional[Path]:
        """Map experiment ID to product directory."""
        # Simple mapping — extend as experiments grow
        mapping = {
            "EXP-001": ROOT / "products" / "slack_bot",
            "EXP-001 (TaskMaster Slack Bot)": ROOT / "products" / "slack_bot",
        }
        for key, path in mapping.items():
            if key in experiment:
                return path
        return None

    def _read_product_files(self, product_dir: Path, max_files: int = 15) -> dict:
        """Read existing product source files for LLM context."""
        files = {}
        if not product_dir.exists():
            return files

        extensions = {".py", ".txt", ".md", ".json", ".yaml", ".yml", ".toml", ".cfg"}
        for f in sorted(product_dir.rglob("*")):
            if not f.is_file():
                continue
            if "__pycache__" in str(f):
                continue
            if f.suffix not in extensions:
                continue
            if len(files) >= max_files:
                break

            try:
                rel = f.relative_to(product_dir)
                content = f.read_text(encoding="utf-8")
                # Truncate very large files
                if len(content) > 5000:
                    content = content[:5000] + "\n... [TRUNCATED]"
                files[str(rel)] = content
            except Exception:
                continue

        return files

    def _parse_file_output(self, response: str) -> list[dict]:
        """Parse LLM JSON output into list of {path, content} dicts."""
        # Try to extract JSON from response
        response = response.strip()

        # Remove markdown code fences if present
        if response.startswith("```"):
            response = re.sub(r"^```\w*\n?", "", response)
            response = re.sub(r"\n?```$", "", response)
            response = response.strip()

        try:
            import json
            data = json.loads(response)
            if isinstance(data, dict) and "files" in data:
                return data["files"]
            return []
        except json.JSONDecodeError:
            # Try to find JSON in the response
            match = re.search(r'\{.*"files".*\}', response, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group())
                    return data.get("files", [])
                except json.JSONDecodeError:
                    pass
            return []

    def _update_ticket_status(self, ticket: dict, new_status: str):
        """Update the ticket's status in its source file."""
        source_file = ticket.get("source_file", "")
        if not source_file or not Path(source_file).exists():
            return

        try:
            content = Path(source_file).read_text(encoding="utf-8")
            # Replace status in metadata table
            content = re.sub(
                r"(\|\s*\*\*Status\*\*\s*\|\s*)`[^`]+`",
                f"\\1`{new_status}`",
                content,
            )
            Path(source_file).write_text(content, encoding="utf-8")
            logger.info(f"  Updated ticket status → {new_status}")
        except Exception as e:
            logger.error(f"  Failed to update ticket status: {e}")

    def _result(self, success: bool) -> dict:
        return {
            "success": success,
            "files_written": self.files_written,
            "errors": self.errors,
            "llm_calls": self.llm_calls,
        }
