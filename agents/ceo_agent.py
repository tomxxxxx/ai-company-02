"""
CEO Agent - Strategic decision maker.

Responsibilities:
- Evaluate current state
- Decide next priorities
- Allocate resources
- Make go/no-go decisions
- Generate tasks for other agents and for Thomas (COO)
"""

import logging
from core.agent import Agent
from core.state import get_status_report

logger = logging.getLogger(__name__)


class CEOAgent(Agent):
    def __init__(self, **kwargs):
        super().__init__(
            name="ceo",
            role="CEO & Strategic Decision Maker",
            **kwargs,
        )

    def run(self, state: dict) -> dict:
        """Run CEO evaluation cycle."""
        self.logger.info("CEO cycle starting...")

        status = get_status_report(state)
        phase = state["current_phase"]

        # CEO thinks about current situation
        analysis = self.think(f"""
Current company status:
{status}

Current phase: {phase}

Based on this status:
1. What is the #1 priority right now?
2. What risks do I see?
3. What should I tell Thomas (COO/operator) to do next?
4. Should we change strategy? If so, what?
5. What metrics should I watch most closely this week?

Be brutally honest. Short answers. No fluff.
""")

        self.logger.info(f"CEO Analysis:\n{analysis}")

        # Generate actionable tasks
        tasks = self.analyze_json(f"""
Based on this analysis:
{analysis}

Company status:
{status}

Generate a prioritized task list. Return JSON:
{{
    "priority_1": {{
        "task": "description",
        "owner": "ceo|cto|thomas",
        "deadline_days": 1,
        "why": "reason"
    }},
    "priority_2": {{...}},
    "priority_3": {{...}},
    "phase_recommendation": "current phase or new phase",
    "risk_level": "low|medium|high|critical",
    "capital_decision": "hold|invest|cut_costs"
}}
""")

        # Log decisions
        if isinstance(tasks, dict) and "error" not in tasks:
            self.decide(
                decision=f"Phase: {tasks.get('phase_recommendation', phase)} | Risk: {tasks.get('risk_level', 'unknown')}",
                reasoning=analysis[:500],
                data=tasks,
            )

            # Update phase if recommended
            new_phase = tasks.get("phase_recommendation", phase)
            if new_phase != phase:
                state["current_phase"] = new_phase
                self.logger.info(f"Phase changed: {phase} -> {new_phase}")

        state["_ceo_analysis"] = analysis
        state["_ceo_tasks"] = tasks

        return state
