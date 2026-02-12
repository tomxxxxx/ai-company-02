"""
Agent Base Class - Foundation for all specialized agents.

Each agent has:
- A role (what it does)
- Access to LLM
- Access to company state
- A run() method that performs its work
- Logging and decision tracking
"""

import logging
from abc import ABC, abstractmethod
from typing import Optional
from core.llm import LLM
from core.state import load_state, save_state, log_decision

logger = logging.getLogger(__name__)


class Agent(ABC):
    """Base class for all company agents."""

    def __init__(self, name: str, role: str, llm: Optional[LLM] = None):
        self.name = name
        self.role = role
        self.llm = llm or LLM()
        self.logger = logging.getLogger(f"agent.{name}")

    @abstractmethod
    def run(self, state: dict) -> dict:
        """
        Execute the agent's primary function.
        
        Args:
            state: Current company state dict
            
        Returns:
            Updated state dict with any changes
        """
        pass

    def decide(self, decision: str, reasoning: str, data: dict = None):
        """Log a decision made by this agent."""
        log_decision(decision, reasoning, agent=self.name, data=data)
        self.logger.info(f"DECISION: {decision}")

    def think(self, prompt: str, system: str = None) -> str:
        """Use LLM to reason about something."""
        if not system:
            system = f"You are {self.name}, the {self.role} of AI Automation Lab. Think step by step. Be concise and actionable."
        return self.llm.ask(prompt, system=system)

    def analyze_json(self, prompt: str) -> dict:
        """Use LLM to analyze something and return structured data."""
        system = f"You are {self.name}, the {self.role} of AI Automation Lab. Respond only with valid JSON."
        return self.llm.ask_json(prompt, system=system)

    def __repr__(self):
        return f"<Agent: {self.name} ({self.role})>"
