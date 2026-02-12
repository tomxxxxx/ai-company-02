"""
Layer Base Class — Foundation for all autonomous loop layers.

Each layer:
1. Gets context (company state, iteration state, previous layer outputs)
2. Runs an LLM agent loop with access to tools
3. Produces structured output for the next layer
"""

import logging
from pathlib import Path

from core.autonomous.llm_client import ToolUseClient
from core.autonomous.tools.base import ToolRegistry

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).resolve().parent.parent.parent / "company-os" / "prompts"


class Layer:
    """Base class for autonomous loop layers."""

    # Subclasses must set these
    name: str = ""
    prompt_file: str = ""  # Filename in company-os/prompts/

    def __init__(self, llm: ToolUseClient, tools: ToolRegistry, config: dict = None):
        self.llm = llm
        self.tools = tools
        self.config = config or {}

    def load_system_prompt(self) -> str:
        """Load system prompt from file. Falls back to default if file missing."""
        path = PROMPTS_DIR / self.prompt_file
        if path.exists():
            return path.read_text(encoding="utf-8")
        logger.warning(f"Prompt file not found: {path}. Using default prompt.")
        return self._default_prompt()

    def _default_prompt(self) -> str:
        """Fallback prompt if file doesn't exist."""
        return f"Du bist die {self.name}-Ebene des AI Automation Lab. Führe deine Aufgabe aus."

    def get_tools(self) -> list[str]:
        """
        List of tool names this layer can use.
        Empty list = all tools available.
        Override in subclass to restrict tools.
        """
        return []

    def build_context(self, iteration_state) -> str:
        """
        Build the user message with full context for this layer.
        Override in subclass for layer-specific context assembly.
        """
        from core.autonomous.iteration_state import IterationState

        state: IterationState = iteration_state
        parts = []

        # Company state
        parts.append("## Aktueller Unternehmens-Status")
        parts.append(f"Kapital: €{state.company_state.get('financials', {}).get('current_capital', 0):,.2f}")
        parts.append(f"MRR: €{state.company_state.get('metrics', {}).get('mrr', 0):,.2f}")
        parts.append(f"Phase: {state.company_state.get('current_phase', 'unknown')}")
        products = state.company_state.get("products", {})
        if products:
            parts.append(f"Produkte: {', '.join(products.keys())}")
        parts.append("")

        # Previous layer outputs in this iteration
        if state.layer_outputs:
            parts.append("## Bisherige Ebenen-Outputs in dieser Iteration")
            parts.append(state.get_layer_summary())

        # History from past iterations
        if state.history:
            parts.append("## Vergangene Iterationen (Zusammenfassungen)")
            for h in state.history[-5:]:  # Last 5 iterations
                parts.append(f"### Iteration #{h['iteration_id']} ({h['date'][:10]})")
                for layer_name, summary in h.get("layer_summaries", {}).items():
                    parts.append(f"**{layer_name}:** {summary[:300]}")
                if h.get("thomas_tasks_count", 0) > 0:
                    parts.append(f"Thomas-Tasks: {h['thomas_tasks_count']}")
                parts.append(f"Kosten: ${h.get('cost_usd', 0):.4f}")
                parts.append("")
        else:
            parts.append("## Vergangene Iterationen")
            parts.append("Dies ist die erste Iteration. Es gibt keine Historie.")
            parts.append("")

        # Iteration metadata
        parts.append(f"## Diese Iteration: #{state.iteration_id}")
        parts.append(f"Gestartet: {state.started_at}")

        return "\n".join(parts)

    def run(self, iteration_state) -> dict:
        """Run this layer and return output."""
        logger.info(f"{'='*60}")
        logger.info(f"Layer: {self.name}")
        logger.info(f"{'='*60}")

        system_prompt = self.load_system_prompt()
        context = self.build_context(iteration_state)

        # Filter tools if layer specifies a subset
        allowed = self.get_tools()
        if allowed:
            tools = self.tools.get_tools_for(allowed)
        else:
            tools = self.tools.to_claude_format()

        result = self.llm.run_agent_loop(
            system_prompt=system_prompt,
            user_message=context,
            tools=tools,
            tool_executor=self.tools.execute,
            model=self.config.get("model", "claude-sonnet-4-20250514"),
            max_tokens=self.config.get("max_tokens", 8192),
            max_turns=self.config.get("max_turns", 30),
            temperature=self.config.get("temperature", 0.7),
        )

        output = {
            "layer": self.name,
            "output": result["text"],
            "tool_calls": result["tool_calls"],
            "turns": result["turns"],
            "input_tokens": result["input_tokens"],
            "output_tokens": result["output_tokens"],
        }

        logger.info(
            f"Layer {self.name} completed: {result['turns']} turns, "
            f"{len(result['tool_calls'])} tool calls, "
            f"{result['input_tokens']} in / {result['output_tokens']} out tokens"
        )

        return output
