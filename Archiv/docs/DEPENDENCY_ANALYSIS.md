# DEPENDENCY-ANALYSE — AI Automation Lab

*Analyse aller Import-Dependencies zur Bestätigung der Legacy-Module-Entfernung*

## IMPORT-ANALYSE DURCHGEFÜHRT

### Suchbefehle ausgeführt:
1. `grep -r "from core\." --include="*.py" .`
2. `grep -r "import core\." --include="*.py" .`
3. `grep -r "from agents\." --include="*.py" .`
4. `grep -r "import agents\." --include="*.py" .`

## ERGEBNISSE

### 1. CORE-MODULE DEPENDENCIES

#### AKTIVE CORE-MODULE (werden verwendet):
- `core.llm` — Verwendet von `core/agent.py`, `core/orchestrator.py`, `core/ticket_executor.py`
- `core.state` — Verwendet von `core/agent.py`, `core/orchestrator.py`, `core/autonomous/runner.py`, `agents/ceo_agent.py`, `core/ticket_executor.py`
- `core.autonomous.*` — Gesamtes autonomes System (interne Imports)

#### LEGACY CORE-MODULE (werden NUR von anderen Legacy-Modulen verwendet):

| Legacy-Modul | Verwendet von | Status |
|--------------|---------------|--------|
| `core.agent` | `agents/builder_agent.py`, `agents/ceo_agent.py`, `agents/cto_agent.py` | ✅ **SAFE TO REMOVE** |
| `core.orchestrator` | Keine aktiven Imports gefunden | ✅ **SAFE TO REMOVE** |
| `core.policy_engine` | `core/cycle_runner.py` | ✅ **SAFE TO REMOVE** |
| `core.ticket_executor` | `core/cycle_runner.py` | ✅ **SAFE TO REMOVE** |
| `core.ticket_parser` | `core/cycle_runner.py` | ✅ **SAFE TO REMOVE** |
| `core.scorecard_parser` | `core/cycle_runner.py` | ✅ **SAFE TO REMOVE** |
| `core.cycle_runner` | `scheduler.py` | ⚠️ **CHECK SCHEDULER** |

### 2. AGENTS-MODULE DEPENDENCIES

#### AGENTS VERWENDET VON:
- `agents.ceo_agent` — Verwendet von `core/orchestrator.py` (Legacy)
- `agents.cto_agent` — Verwendet von `core/orchestrator.py` (Legacy)
- `agents.builder_agent` — Verwendet von `core/orchestrator.py` (Legacy)

**Fazit**: Alle agents-Imports kommen nur von `core/orchestrator.py`, welches selbst Legacy ist.

## DEPENDENCY-KETTE ANALYSE

### Legacy-Kette 1: Agent-System
```
core/orchestrator.py → agents/*.py → core/agent.py → core/llm.py, core/state.py
                    ↓
              scheduler.py
```

### Legacy-Kette 2: Cycle-Runner-System
```
core/cycle_runner.py → core/ticket_parser.py
                    → core/scorecard_parser.py
                    → core/policy_engine.py
                    → core/ticket_executor.py
```

### Aktive Kette: Autonomes System
```
run_autonomous.py → core/autonomous/runner.py → core/autonomous/layers/*.py
                                             → core/autonomous/tools/*.py
                                             → core/state.py, core/llm.py
```

## SICHERE ENTFERNUNG BESTÄTIGT

### ✅ KOMPLETT SICHER ZU ENTFERNEN:
```
agents/builder_agent.py
agents/ceo_agent.py  
agents/cto_agent.py
agents/__init__.py
core/agent.py
core/policy_engine.py
core/ticket_executor.py
core/ticket_parser.py
core/scorecard_parser.py
```
**Begründung**: Diese Module werden nur voneinander oder von `core/orchestrator.py` verwendet.

### ⚠️ PRÜFUNG ERFORDERLICH:
```
core/orchestrator.py  — Wird nur von scheduler.py verwendet
core/cycle_runner.py  — Wird nur von scheduler.py verwendet
```
**Begründung**: Müssen `scheduler.py` prüfen — ist das noch aktiv?

### ✅ BEHALTEN (AKTIV):
```
core/llm.py          — Verwendet vom autonomen System
core/state.py        — Verwendet vom autonomen System  
core/autonomous/     — Gesamtes aktives System
```

## SCHEDULER.PY PRÜFUNG

<function_calls>
<invoke name="read_file">
<parameter name="path">scheduler.py