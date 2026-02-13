# Legacy-Analyse — Iteration #7

**Datum**: 2026-02-13  
**Ziel**: Core-Module Legacy-Analyse durchführen — Unterscheiden zwischen dem neuen autonomen 6-Ebenen-System und dem alten Agent-basierten System

---

## EXECUTIVE SUMMARY

Das AI Automation Lab hat **zwei vollständige, parallele Systeme**:

1. **NEUES AUTONOMES SYSTEM** (`core/autonomous/`) — 6-Ebenen-Architektur, vollständig funktional
2. **ALTES LEGACY-SYSTEM** (`core/` Root-Level) — Agent-basiertes Company OS, nicht mehr aktiv genutzt

**Empfehlung**: Legacy-System kann sicher entfernt werden. Nur das autonome System wird aktiv verwendet.

---

## SYSTEMVERGLEICH

### NEUES AUTONOMES SYSTEM (AKTIV)

**Architektur**: 6-Ebenen-Loop
- **Leitebene** (`core/autonomous/layers/control.py`) — Systemreflexion, Ideen-Management
- **Strategieebene** (`core/autonomous/layers/strategy.py`) — Strategische Richtung
- **Planungsebene** (`core/autonomous/layers/planning.py`) — Konkrete Aktionspläne
- **Delegationsebene** (`core/autonomous/layers/delegation.py`) — Ausführungsvorbereitung
- **Ausführungsebene** (`core/autonomous/layers/execution.py`) — Plan-Umsetzung
- **Evaluationsebene** (`core/autonomous/layers/evaluation.py`) — Ergebnis-Bewertung

**Entry Point**: `run_autonomous.py`  
**Runner**: `core/autonomous/runner.py`  
**Tools**: Modular in `core/autonomous/tools/` (filesystem, git, shell, thomas)  
**State Management**: `core/autonomous/iteration_state.py`  
**LLM Client**: `core/autonomous/llm_client.py`

**Status**: ✅ **VOLLSTÄNDIG AKTIV** — Wird in allen erfolgreichen Iterationen verwendet

### ALTES LEGACY-SYSTEM (INAKTIV)

**Architektur**: 5-Phasen-Cycle
- **READ** — Tickets und Scorecards parsen
- **EVALUATE** — Regel-Engine anwenden
- **EXECUTE** — Aktionen ausführen
- **WRITE** — Updates schreiben
- **NOTIFY** — Human-Escalations

**Entry Point**: `scheduler.py`  
**Runner**: `core/cycle_runner.py`  
**Components**:
- `core/policy_engine.py` — Regelengine für Ticket-Approval
- `core/scorecard_parser.py` — Experiment-Scorecard-Parsing
- `core/ticket_executor.py` — Ticket-Ausführung via LLM
- `core/ticket_parser.py` — Company-OS Ticket-Parsing
- `core/llm.py` — Legacy LLM-Client

**Status**: ❌ **LEGACY/UNUSED** — Wird nicht mehr verwendet

---

## KATEGORISIERTE MODULE-LISTE

### ✅ AKTIV (Neues System)
- `core/autonomous/` (gesamtes Verzeichnis)
- `run_autonomous.py`
- `core/state.py` (wird von beiden Systemen verwendet)

### ❌ LEGACY (Altes System)
- `core/cycle_runner.py`
- `core/policy_engine.py`
- `core/scorecard_parser.py`
- `core/ticket_executor.py`
- `core/ticket_parser.py`
- `core/llm.py`
- `scheduler.py`

### 🟡 UNKLAR/SHARED
- `core/__init__.py` — Verweist auf Legacy-System, aber könnte auch für neue Imports verwendet werden
- `agents/` — Nur leere `__init__.py`, praktisch bereits aufgeräumt

---

## IMPORT-DEPENDENCY-ANALYSE

### Aktive Abhängigkeiten (Neues System)
```python
# run_autonomous.py
from core.autonomous.runner import AutonomousRunner  # ✅ AKTIV

# core/autonomous/runner.py
from core.autonomous.layers import *  # ✅ AKTIV
from core.autonomous.tools import *   # ✅ AKTIV
from core.state import load_state     # ✅ SHARED (OK)
```

### Legacy-Abhängigkeiten (Altes System)
```python
# scheduler.py
from core.cycle_runner import run_cycle  # ❌ LEGACY

# core/cycle_runner.py
from core.ticket_parser import *         # ❌ LEGACY
from core.scorecard_parser import *      # ❌ LEGACY
from core.policy_engine import *         # ❌ LEGACY
from core.ticket_executor import *       # ❌ LEGACY
```

**Ergebnis**: Keine Cross-Dependencies zwischen alt und neu. Systeme sind vollständig getrennt.

---

## AGENTS-VERZEICHNIS ANALYSE

**Status**: ✅ **BEREITS AUFGERÄUMT**
- Nur `agents/__init__.py` vorhanden (leer)
- Keine Agent-Dateien mehr vorhanden
- Vermutlich in Iteration #3 bereits entfernt

**Empfehlung**: `agents/` Verzeichnis kann komplett entfernt werden.

---

## CLEANUP-EMPFEHLUNGEN

### SICHER ENTFERNBAR (100% Legacy)
1. **Legacy Core-Module**:
   - `core/cycle_runner.py`
   - `core/policy_engine.py`
   - `core/scorecard_parser.py`
   - `core/ticket_executor.py`
   - `core/ticket_parser.py`
   - `core/llm.py`

2. **Legacy Entry Points**:
   - `scheduler.py`

3. **Leere Verzeichnisse**:
   - `agents/` (komplett)

### VORSICHTIG PRÜFEN
1. **`core/__init__.py`** — Aktualisieren um nur auf neues System zu verweisen
2. **Dokumentation** — Veraltete Referenzen auf Agents oder altes System entfernen

### BEHALTEN (Aktiv genutzt)
- `core/autonomous/` (gesamtes Verzeichnis)
- `run_autonomous.py`
- `core/state.py` (wird von beiden Systemen verwendet)

---

## RISIKO-BEWERTUNG

**Risiko: NIEDRIG**
- Beide Systeme sind vollständig getrennt
- Keine Cross-Dependencies
- Neues System ist bewiesen stabil (Iterationen #3, #5, #7 erfolgreich)
- Legacy-System wird nachweislich nicht verwendet

**Empfohlenes Vorgehen**:
1. Legacy-Module in ein `legacy/` Verzeichnis verschieben (statt löschen)
2. Nach 2-3 erfolgreichen Iterationen ohne Probleme → Legacy endgültig löschen
3. `core/__init__.py` aktualisieren

---

## ERKENNTNISSE

1. **Klare Systemtrennung**: Das neue 6-Ebenen-System ist vollständig unabhängig vom alten Agent-System
2. **Erfolgreiche Migration**: Das neue System funktioniert stabil und produziert bessere Ergebnisse
3. **Legacy-Code-Ballast**: Das alte System verwirrt das aktuelle System nicht, aber verbraucht Speicher und könnte Verwirrung stiften
4. **Agents bereits entfernt**: Das Agents-Verzeichnis wurde bereits in früheren Iterationen aufgeräumt

**Fazit**: Das AI Automation Lab kann sicher auf Legacy-Code verzichten. Das neue autonome System ist die Zukunft.