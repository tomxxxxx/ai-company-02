"""
LLM Client with Tool Use — Agentic loop over Claude API.

Handles the multi-turn tool-use pattern:
1. Send message to Claude with available tools
2. If Claude calls tools, execute them and send results back
3. Repeat until Claude stops calling tools
4. Return final text output + all tool call logs
"""

import os
import json
import logging
import time
from typing import Callable, Optional

from core.autonomous.tools.token_utils import estimate_tokens, is_text_too_large

logger = logging.getLogger(__name__)


class ToolUseClient:
    """Claude API client with tool-use support for the autonomous loop."""

    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY", "")
        self._client = None

        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY required for autonomous loop. "
                "Set it in .env file."
            )

        try:
            import anthropic
            self._client = anthropic.Anthropic(api_key=self.api_key)
            logger.info("Anthropic Claude initialized for tool-use")
        except ImportError:
            raise ImportError(
                "anthropic package required: pip install 'anthropic>=0.42.0'"
            )

    def _content_to_dicts(self, content_blocks) -> list[dict]:
        """Convert SDK ContentBlock objects to plain dicts for message history."""
        result = []
        for block in content_blocks:
            if block.type == "text":
                result.append({"type": "text", "text": block.text})
            elif block.type == "tool_use":
                result.append({
                    "type": "tool_use",
                    "id": block.id,
                    "name": block.name,
                    "input": block.input,
                })
        return result

    def run_agent_loop(
        self,
        system_prompt: str,
        user_message: str,
        tools: list[dict],
        tool_executor: Callable[[str, dict], str],
        model: str = "claude-sonnet-4-20250514",
        max_tokens: int = 8192,
        max_turns: int = 30,
        temperature: float = 0.7,
    ) -> dict:
        """
        Run an agentic tool-use loop until the model stops calling tools.

        Args:
            system_prompt: System prompt for the agent
            user_message: Initial user message with context
            tools: Tool definitions in Claude API format
            tool_executor: func(tool_name, tool_input) -> result string
            model: Claude model to use
            max_tokens: Max tokens per response
            max_turns: Safety limit on conversation turns
            temperature: Sampling temperature

        Returns:
            {
                "text": str,            # Final text output (all text from all turns)
                "tool_calls": list,      # All tool calls made
                "turns": int,            # Number of turns taken
                "input_tokens": int,     # Total input tokens
                "output_tokens": int,    # Total output tokens
            }
        """
        messages = [{"role": "user", "content": user_message}]
        all_tool_calls = []
        all_text = []
        total_input_tokens = 0
        total_output_tokens = 0
        turn = 0

        while turn < max_turns:
            turn += 1
            logger.debug(f"Agent turn {turn}/{max_turns}")

            try:
                kwargs = {
                    "model": model,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "system": system_prompt,
                    "messages": messages,
                }
                if tools:
                    kwargs["tools"] = tools

                response = self._call_with_retry(kwargs)
            except Exception as e:
                logger.error(f"Claude API error on turn {turn}: {e}")
                raise

            total_input_tokens += response.usage.input_tokens
            total_output_tokens += response.usage.output_tokens

            # Extract text and tool-use blocks
            text_blocks = []
            tool_use_blocks = []
            for block in response.content:
                if block.type == "text":
                    text_blocks.append(block.text)
                elif block.type == "tool_use":
                    tool_use_blocks.append(block)

            if text_blocks:
                all_text.extend(text_blocks)

            # If no tool calls, we're done
            if not tool_use_blocks:
                return {
                    "text": "\n".join(all_text),
                    "tool_calls": all_tool_calls,
                    "turns": turn,
                    "input_tokens": total_input_tokens,
                    "output_tokens": total_output_tokens,
                }

            # Execute each tool call
            tool_results = []
            for block in tool_use_blocks:
                tool_name = block.name
                tool_input = block.input

                input_preview = json.dumps(tool_input, ensure_ascii=False)
                if len(input_preview) > 300:
                    input_preview = input_preview[:300] + "..."
                logger.info(f"Tool call: {tool_name}({input_preview})")

                try:
                    result = tool_executor(tool_name, tool_input)
                    result_str = str(result)
                except Exception as e:
                    result_str = f"[ERROR] Tool execution failed: {e}"
                    logger.error(f"Tool {tool_name} failed: {e}")

                all_tool_calls.append({
                    "tool": tool_name,
                    "input": tool_input,
                    "output_preview": result_str[:500],
                })

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result_str,
                })

            # Append assistant response and tool results to message history
            messages.append({
                "role": "assistant",
                "content": self._content_to_dicts(response.content),
            })
            messages.append({
                "role": "user",
                "content": tool_results,
            })

        # Hit max turns
        logger.warning(f"Agent loop hit max turns ({max_turns})")
        return {
            "text": "\n".join(all_text) if all_text else "[Max turns reached without final output]",
            "tool_calls": all_tool_calls,
            "turns": turn,
            "input_tokens": total_input_tokens,
            "output_tokens": total_output_tokens,
        }

    def _call_with_retry(
        self,
        kwargs: dict,
        max_retries: int = 5,
        initial_wait: float = 60.0,
    ):
        """
        Call Claude API with retry on rate-limit (429) and server errors (5xx).
        Uses exponential backoff: 60s, 120s, 240s, 480s, 960s.
        On rate limits, also tries to reduce message size if possible.
        """
        original_kwargs = kwargs.copy()
        
        for attempt in range(max_retries + 1):
            try:
                return self._client.messages.create(**kwargs)
            except Exception as e:
                error_str = str(e)
                is_rate_limit = "429" in error_str or "rate_limit" in error_str.lower()
                is_server_error = any(f"{code}" in error_str for code in [500, 502, 503, 529])
                is_overloaded = "overloaded" in error_str.lower()

                if (is_rate_limit or is_server_error or is_overloaded) and attempt < max_retries:
                    wait_time = initial_wait * (2 ** attempt)
                    
                    # On rate limit, try to reduce message size for next attempt
                    if is_rate_limit and attempt == 0:
                        kwargs = self._reduce_message_size(kwargs)
                        if kwargs != original_kwargs:
                            logger.info("Rate limit detected - trying with reduced message size")
                    
                    logger.warning(
                        f"API error (attempt {attempt + 1}/{max_retries + 1}): "
                        f"{error_str[:200]}. Retrying in {wait_time:.0f}s..."
                    )
                    time.sleep(wait_time)
                else:
                    raise

    def _reduce_message_size(self, kwargs: dict) -> dict:
        """
        Try to reduce the size of messages to avoid rate limits.
        Returns modified kwargs if reduction was possible, otherwise original kwargs.
        """
        try:
            messages = kwargs.get("messages", [])
            if not messages:
                return kwargs
            
            # Find the largest message content and try to truncate it
            max_size = 0
            largest_msg_idx = -1
            
            for i, msg in enumerate(messages):
                content = msg.get("content", "")
                if isinstance(content, str):
                    size = estimate_tokens(content)
                    if size > max_size and size > 1000:  # Only truncate if > 1000 tokens
                        max_size = size
                        largest_msg_idx = i
            
            if largest_msg_idx >= 0:
                # Truncate the largest message to ~80% of its size
                msg = messages[largest_msg_idx]
                content = msg["content"]
                if isinstance(content, str):
                    target_length = int(len(content) * 0.8)
                    truncated = content[:target_length] + "\n\n[MESSAGE TRUNCATED DUE TO RATE LIMITS]"
                    
                    # Create new kwargs with truncated message
                    new_kwargs = kwargs.copy()
                    new_messages = messages.copy()
                    new_messages[largest_msg_idx] = {**msg, "content": truncated}
                    new_kwargs["messages"] = new_messages
                    
                    logger.info(f"Truncated message {largest_msg_idx} from {len(content)} to {len(truncated)} chars")
                    return new_kwargs
            
            return kwargs
        except Exception as e:
            logger.warning(f"Failed to reduce message size: {e}")
            return kwargs
