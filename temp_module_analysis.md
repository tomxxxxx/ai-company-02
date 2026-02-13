# MODULE USAGE ANALYSIS — ITERATION #7

*Generiert: 2026-02-13*

## METHODIK

1. **Aktive Module**: Werden vom neuen 6-Ebenen-System (`run_autonomous.py`) verwendet
2. **Legacy Module**: Gehören zum alten Company OS v2 System (`scheduler.py`)
3. **Analyse**: Import-Dependencies und Verwendung in beiden Entry-Points

---

## ENTRY POINTS

### 🆕 NEUES SYSTEM: `run_autonomous.py`
- **Architektur**: 6-Ebenen autonomes System
- **Imports**: `core.autonomous.*`
- **Status**: AKTIV, Hauptsystem

### 🗂️ ALTES SYSTEM: `scheduler.py`  
- **Architektur**: Company OS v2 mit Tickets/Policies
- **Imports**: `core.cycle_runner`
- **Status**: LEGACY, aber noch funktional

---

## MODULE KATEGORISIERUNG

| Modul | Typ | Status | Verwendet von | Beschreibung |
|-------|-----|--------|---------------|-------------|
| **core/autonomous/** | | | | |
| `autonomous/runner.py` | Core | ✅ AKTIV | run_autonomous.py | Haupt-Loop des neuen Systems |
| `autonomous/layers/` | Core | ✅ AKTIV | runner.py | 6 Ebenen (Leit, Strategie, etc.) |
| `autonomous/tools/` | Core | ✅ AKTIV | layers | Tool-System für LLM-Calls |
| `autonomous/llm_client.py` | Core | ✅ AKTIV | runner.py, layers | LLM Interface mit Tools |
| `autonomous/iteration_state.py` | Core | ✅ AKTIV | runner.py | State Management |
| **core/ (Root-Level)** | | | | |
| `cycle_runner.py` | Legacy | 🟡 LEGACY | scheduler.py | Company OS v2 Main Loop |
| `ticket_executor.py` | Legacy | 🟡 LEGACY | cycle_runner.py | Ticket-basierte Ausführung |
| `ticket_parser.py` | Legacy | 🟡 LEGACY | cycle_runner.py | Ticket Markdown Parser |
| `scorecard_parser.py` | Legacy | 🟡 LEGACY | cycle_runner.py | Experiment Scorecard Parser |
| `policy_engine.py` | Legacy | 🟡 LEGACY | cycle_runner.py | Regel-basierte Entscheidungen |
| `batch_processor.py` | Legacy | 🟡 LEGACY | cycle_runner.py | Rate-Limit Management |
| `token_manager.py` | Legacy | 🟡 LEGACY | batch_processor.py | Token Budget Management |
| `llm.py` | Legacy | 🟡 LEGACY | ticket_executor.py | Alter LLM Client |
| `state.py` | Shared | ✅ AKTIV | Beide Systeme | Company State Management |
| **agents/** | | | | |
| `agents/__init__.py` | Empty | 🔴 UNUSED | - | Leeres Verzeichnis |

---

## DEPENDENCY ANALYSIS

### NEUES SYSTEM (run_autonomous.py)
```
run_autonomous.py
├── core.autonomous.runner.AutonomousRunner
    ├── core.autonomous.llm_client.ToolUseClient
    ├── core.autonomous.iteration_state.*
    ├── core.autonomous.tools.*
    ├── core.autonomous.layers.*
    └── core.state.* (Shared)
```

### ALTES SYSTEM (scheduler.py)
```
scheduler.py
├── core.cycle_runner.run_cycle
    ├── core.ticket_parser.*
    ├── core.scorecard_parser.*
    ├── core.policy_engine.*
    ├── core.ticket_executor.*
    ├── core.batch_processor.*
    ├── core.token_manager.*
    ├── core.llm.*
    └── core.state.* (Shared)
```

---

## ERKENNTNISSE

### ✅ AKTIVE MODULE (Neues 6-Ebenen-System)
- **core/autonomous/**: Komplettes neues System
- **core/state.py**: Shared zwischen beiden Systemen

### 🟡 LEGACY MODULE (Company OS v2)
- **core/cycle_runner.py**: Alter Hauptloop
- **core/ticket_*.py**: Ticket-System
- **core/scorecard_parser.py**: Experiment Tracking
- **core/policy_engine.py**: Regelwerk
- **core/batch_processor.py**: Rate-Limit-Management
- **core/token_manager.py**: Token-Budget-System
- **core/llm.py**: Alter LLM Client

### 🔴 UNUSED MODULE
- **agents/**: Komplett leer, nur `__init__.py`

### 🤔 BESONDERHEITEN
1. **Zwei parallele Systeme**: Das neue autonome System läuft parallel zum alten Company OS
2. **Shared State**: `core/state.py` wird von beiden verwendet
3. **Verschiedene LLM Clients**: `core/llm.py` (alt) vs. `core/autonomous/llm_client.py` (neu)
4. **Rate-Limit-Strategien**: Alt (batch_processor) vs. Neu (retry in llm_client)

---

## EMPFEHLUNGEN

1. **Kurzfristig**: Beide Systeme parallel lassen — sie erfüllen verschiedene Zwecke
2. **Legacy-Cleanup**: `agents/` Verzeichnis kann entfernt werden
3. **Langfristig**: Entscheidung treffen welches System das Hauptsystem wird
4. **Integration**: Eventuell Policy Engine und Ticket System ins neue System integrieren