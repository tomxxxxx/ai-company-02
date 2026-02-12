"""
State Management - Persistent state for the AI company.

Tracks:
- Financial state (capital, revenue, costs)
- Business metrics (customers, MRR, churn)
- Agent task history
- Decision log
"""

import json
import os
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent / "data"
STATE_FILE = DATA_DIR / "company_state.json"
DECISION_LOG = DATA_DIR / "decisions.jsonl"
METRICS_LOG = DATA_DIR / "metrics.jsonl"


def _ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# === DEFAULT STATE ===

DEFAULT_STATE = {
    "company": {
        "name": "AI Automation Lab",
        "founded": "2026-02-11",
        "status": "active",
    },
    "financials": {
        "starting_capital": 10000.00,
        "current_capital": 9602.42,  # 10000 - 390 (Copilot) - 2.55 (domain) - 5.03 (Anthropic API)
        "monthly_costs": {
            "copilot_pro": 32.50,
            "infrastructure": 0.00,
            "api_costs": 0.00,
            "total": 32.50,
        },
        "monthly_revenue": 0.00,
        "total_spent": 392.55,
        "total_earned": 0.00,
    },
    "products": {
        "slack_bot": {
            "name": "TaskMaster Slack Bot",
            "status": "building",  # idea | building | launched | active | retired
            "phase": "mvp",
            "customers": 0,
            "mrr": 0.00,
            "started": "2026-02-12",
            "launched": None,
        }
    },
    "metrics": {
        "mrr": 0.00,
        "customers_total": 0,
        "customers_paying": 0,
        "churn_rate": 0.00,
        "outreach_sent": 0,
        "outreach_responses": 0,
    },
    "current_phase": "build",  # research | build | launch | grow | scale
    "last_updated": None,
    "cycle_count": 0,
}


def load_state() -> dict:
    """Load company state from disk, or create default."""
    _ensure_data_dir()
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to load state: {e}")
    return DEFAULT_STATE.copy()


def save_state(state: dict):
    """Persist company state to disk."""
    _ensure_data_dir()
    state["last_updated"] = _now()
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
    logger.info("State saved")


def log_decision(decision: str, reasoning: str, agent: str = "ceo", data: Optional[dict] = None):
    """Append a decision to the decision log."""
    _ensure_data_dir()
    entry = {
        "timestamp": _now(),
        "agent": agent,
        "decision": decision,
        "reasoning": reasoning,
        "data": data or {},
    }
    with open(DECISION_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    logger.info(f"Decision logged: {decision}")


def log_metric(metric_name: str, value: Any, context: str = ""):
    """Append a metric data point."""
    _ensure_data_dir()
    entry = {
        "timestamp": _now(),
        "metric": metric_name,
        "value": value,
        "context": context,
    }
    with open(METRICS_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def get_status_report(state: dict) -> str:
    """Generate a human-readable status report."""
    fin = state["financials"]
    met = state["metrics"]
    products = state["products"]

    report = f"""
=== AI AUTOMATION LAB - STATUS REPORT ===
Generated: {_now()}
Phase: {state['current_phase'].upper()}
Cycle: #{state['cycle_count']}

=== FINANCIALS ===
Capital: €{fin['current_capital']:.2f}
Monthly Revenue: €{fin['monthly_revenue']:.2f}
Monthly Costs: €{fin['monthly_costs']['total']:.2f}
Net Monthly: €{fin['monthly_revenue'] - fin['monthly_costs']['total']:.2f}
Runway: {'∞' if fin['monthly_costs']['total'] <= 0 else f"{fin['current_capital'] / fin['monthly_costs']['total']:.0f} months"}

=== METRICS ===
MRR: €{met['mrr']:.2f}
Customers (total): {met['customers_total']}
Customers (paying): {met['customers_paying']}
Churn Rate: {met['churn_rate']:.1%}

=== PRODUCTS ==="""

    for pid, prod in products.items():
        report += f"""
  [{pid}] {prod['name']}
    Status: {prod['status']}
    Phase: {prod['phase']}
    Customers: {prod['customers']}
    MRR: €{prod['mrr']:.2f}"""

    report += "\n" + "=" * 45
    return report
