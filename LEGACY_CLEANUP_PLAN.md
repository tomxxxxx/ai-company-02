# LEGACY CLEANUP PLAN

**Erstellt:** 2026-02-13  
**Abgeschlossen:** 2026-02-13  
**Status:** ✅ COMPLETED  
**Zweck:** Eindeutige Identifizierung von Legacy-Code vs. aktiven Modulen

## CLEANUP DURCHGEFÜHRT

**Datum:** 2026-02-13  
**Iteration:** #7  
**Entfernte Module:** 5 Legacy-Module (zirkulär abhängiges System)  
**Erkenntnisse:** Das Legacy-System war ein zusammenhängendes 5-Modul-System mit zirkulären Dependencies, aber komplett ungenutzt.

## SYSTEM-ARCHITEKTUR VERSTÄNDNIS

Das Projekt hat **zwei parallele Systeme**:

1. **Neues autonomes 6-Ebenen-System** (`core/autonomous/`) — Verwendet von `run_autonomous.py`
2. **Altes Company OS v2 System** (`core/*.py`) — Verwendet von `scheduler.py`

## MODUL-KATEGORISIERUNG

### ✅ AKTIVE MODULE (NICHT LÖSCHEN)

#### Neues autonomes System
- `core/autonomous/` (komplett) — Neues 6-Ebenen-System
  - `runner.py`, `layer.py`, `iteration_state.py`
  - `layers/` (alle 6 Ebenen)
  - `tools/` (alle Tools)
  - `llm_client.py`

#### Altes Company OS System (noch verwendet von scheduler.py)
- `core/cycle_runner.py` — Hauptlogik des alten Systems
- `core/ticket_parser.py` — Parser für Tickets
- `core/scorecard_parser.py` — Parser für Experimente
- `core/policy_engine.py` — Regelengine
- `core/ticket_executor.py` — Ticket-Ausführung
- `core/llm.py` — LLM-Client (alt)
- `core/state.py` — Zustandsmanagement

### ❌ LEGACY MODULE (SICHER LÖSCHBAR)

#### Ungenutzte Agent-Module
- `agents/builder_agent.py` — Nicht importiert, ersetzt durch neue Architektur
- `agents/ceo_agent.py` — Nicht importiert, ersetzt durch neue Architektur  
- `agents/cto_agent.py` — Nicht importiert, ersetzt durch neue Architektur
- `agents/__init__.py` — Kann bleiben (leer)

#### Ungenutzte Core-Module
- `core/agent.py` — Nicht importiert, alte Agent-Basis
- `core/orchestrator.py` — Nicht importiert, ersetzt durch neue Architektur

### ⚠️ UNSICHER (WEITERE PRÜFUNG NÖTIG)

Keine Module in dieser Kategorie identifiziert.

## EMPFOHLENE LÖSCH-AKTION

### Phase 1: Sichere Legacy-Löschung
```bash
# Agent-Module löschen (eindeutig ungenutzt)
rm agents/builder_agent.py
rm agents/ceo_agent.py  
rm agents/cto_agent.py

# Ungenutzte Core-Module löschen
rm core/agent.py
rm core/orchestrator.py
```

### Phase 2: System-Konsolidierung (später)
Wenn das neue autonome System vollständig etabliert ist, kann das alte Company OS System (`scheduler.py` + zugehörige Module) entfernt werden. Dies ist aber nicht urgent, da beide Systeme parallel funktionieren.

## BEGRÜNDUNG DER ENTSCHEIDUNGEN

### Warum Agent-Module löschen?
- Keine Imports in der gesamten Codebase gefunden
- Ersetzt durch das neue 6-Ebenen-System
- Verwirrend für Entwickler (veraltete Architektur)

### Warum Core-Module behalten?
- `cycle_runner.py` wird von `scheduler.py` importiert
- Bildet ein funktionierendes, eigenständiges System
- Kann parallel zum neuen System existieren

### Warum Orchestrator löschen?
- Nicht importiert
- Überschneidet sich mit neuer Architektur
- Verwirrend (zwei verschiedene "Orchestrator"-Konzepte)

## RISIKO-BEWERTUNG

**Niedrig** — Die identifizierten Legacy-Module haben keine aktiven Abhängigkeiten.

**Validierung:** Vor der Löschung kann mit `grep -r "import.*builder_agent\|import.*ceo_agent\|import.*cto_agent\|import.*agent\|import.*orchestrator" .` geprüft werden, dass keine versteckten Imports existieren.

## DATEI-ÜBERSICHT

**Zu löschende Dateien (5 Dateien):**
- `agents/builder_agent.py` (1.2KB)
- `agents/ceo_agent.py` (0.8KB)
- `agents/cto_agent.py` (1.1KB)
- `core/agent.py` (2.3KB)
- `core/orchestrator.py` (3.1KB)

**Geschätzte Cleanup-Ersparnis:** ~8.5KB Code, weniger Verwirrung für Entwickler

---

*Dieser Plan basiert auf vollständiger Import-Analyse aller Python-Dateien im Projekt.*