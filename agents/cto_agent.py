"""
CTO Agent - Technical decision maker & builder.

Responsibilities:
- Evaluate technical status of products
- Decide what to build next
- Generate code tasks
- Monitor technical health
- Make build vs buy decisions
"""

import logging
from core.agent import Agent

logger = logging.getLogger(__name__)


class CTOAgent(Agent):
    def __init__(self, **kwargs):
        super().__init__(
            name="cto",
            role="CTO & Technical Architect",
            **kwargs,
        )

    def run(self, state: dict) -> dict:
        """Run CTO evaluation cycle."""
        self.logger.info("CTO cycle starting...")

        products = state.get("products", {})
        phase = state.get("current_phase", "build")

        # Evaluate each product
        for product_id, product in products.items():
            if product["status"] in ("building", "launched", "active"):
                assessment = self.think(f"""
Product: {product['name']}
Status: {product['status']}
Phase: {product['phase']}
Customers: {product['customers']}
MRR: €{product['mrr']}
Company Phase: {phase}

As CTO:
1. What is the next technical task for this product?
2. What is blocking progress?
3. What technical debt exists?
4. Is the architecture right for current scale?
5. What should be automated?

Be specific. Give concrete next steps.
""")
                self.logger.info(f"CTO Assessment [{product_id}]:\n{assessment}")
                state["products"][product_id]["_cto_assessment"] = assessment

        # Generate build priorities
        build_plan = self.analyze_json(f"""
Products: {list(products.keys())}
Product details: {products}
Company phase: {phase}

Generate the build priority list. Return JSON:
{{
    "build_priorities": [
        {{
            "product": "product_id",
            "task": "specific technical task",
            "complexity": "low|medium|high",
            "estimated_hours": 4,
            "blocks_revenue": true
        }}
    ],
    "tech_debt": ["list of technical debt items"],
    "automation_opportunities": ["things that should be automated"],
    "infrastructure_needs": ["what infra changes needed"]
}}
""")

        state["_cto_build_plan"] = build_plan
        return state
