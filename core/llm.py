"""
LLM Interface - Abstraction layer for AI model calls.

Supports Anthropic Claude and OpenAI GPT.
Falls back gracefully if one API is unavailable.
"""

import os
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class LLM:
    """Unified interface for LLM calls."""

    def __init__(self):
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.openai_key = os.getenv("OPENAI_API_KEY", "")
        self._anthropic_client = None
        self._openai_client = None

        if self.anthropic_key:
            try:
                import anthropic
                self._anthropic_client = anthropic.Anthropic(api_key=self.anthropic_key)
                logger.info("Anthropic Claude initialized")
            except ImportError:
                logger.warning("anthropic package not installed")
        
        if self.openai_key:
            try:
                import openai
                self._openai_client = openai.OpenAI(api_key=self.openai_key)
                logger.info("OpenAI GPT initialized")
            except ImportError:
                logger.warning("openai package not installed")

        if not self._anthropic_client and not self._openai_client:
            logger.warning("No LLM API configured. Set ANTHROPIC_API_KEY or OPENAI_API_KEY in .env")

    def ask(
        self,
        prompt: str,
        system: str = "You are a helpful business assistant.",
        model: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> str:
        """
        Send a prompt to the best available LLM and return the response.
        
        Priority: Claude > GPT
        """
        # Try Claude first
        if self._anthropic_client:
            try:
                response = self._anthropic_client.messages.create(
                    model=model or "claude-sonnet-4-20250514",
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system,
                    messages=[{"role": "user", "content": prompt}],
                )
                return response.content[0].text
            except Exception as e:
                logger.error(f"Claude API error: {e}")

        # Fallback to GPT
        if self._openai_client:
            try:
                response = self._openai_client.chat.completions.create(
                    model=model or "gpt-4o",
                    max_tokens=max_tokens,
                    temperature=temperature,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt},
                    ],
                )
                return response.choices[0].message.content
            except Exception as e:
                logger.error(f"OpenAI API error: {e}")

        return "[ERROR] No LLM available. Configure API keys in .env"

    def ask_json(
        self,
        prompt: str,
        system: str = "You are a helpful assistant. Always respond with valid JSON.",
        **kwargs,
    ) -> dict:
        """Ask LLM and parse response as JSON."""
        response = self.ask(prompt, system=system, **kwargs)
        try:
            # Try to extract JSON from response
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]
            return json.loads(response.strip())
        except (json.JSONDecodeError, IndexError) as e:
            logger.error(f"Failed to parse JSON: {e}")
            return {"error": str(e), "raw_response": response}

    @property
    def available(self) -> bool:
        """Check if any LLM is available."""
        return bool(self._anthropic_client or self._openai_client)

    @property
    def provider(self) -> str:
        """Return the name of the active LLM provider."""
        if self._anthropic_client:
            return "anthropic"
        if self._openai_client:
            return "openai"
        return "none"
