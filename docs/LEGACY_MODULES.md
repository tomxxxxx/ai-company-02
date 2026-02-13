# LEGACY-MODULE — AI Automation Lab

*Module die NICHT mehr vom aktiven 6-Ebenen-System verwendet werden*

## ÜBERBLICK

Das AI Automation Lab hat sich von einem **Agent-basierten System** zu einem **6-Ebenen-autonomen System** entwickelt. Die folgenden Module sind Legacy-Code aus der Agent-Architektur und werden nicht mehr verwendet.

## LEGACY-MODULE LISTE

### 1. CORE LEGACY-MODULE

| Datei | Zweck (ursprünglich) | Status | Begründung |
|-------|---------------------|--------|-----------|
| `core/agent.py` | Basis-Klasse für alle Agents | **LEGACY** | Ersetzt durch Layer-System in `core/autonomous/` |
| `core/orchestrator.py` | Hauptschleife für Agent-System | **LEGACY** | Ersetzt durch `core/autonomous/runner.py` |
| `core/policy_engine.py` | Rule-Engine für Entscheidungen | **LEGACY** | Policies wurden in autonome Layer integriert |
| `core/cycle_runner.py` | Alternative Hauptschleife | **LEGACY** | Ersetzt durch `core/autonomous/runner.py` |
| `core/ticket_executor.py` | Ticket-basierte Aufgabenausführung | **LEGACY** | Ersetzt durch direkte Ausführung in Execution Layer |
| `core/ticket_parser.py` | Ticket-Parsing-Logic | **LEGACY** | Nicht mehr benötigt, da keine Tickets |
| `core/scorecard_parser.py` | Scorecard-Auswertung | **LEGACY** | State-Management wurde vereinfacht |

### 2. AGENTS LEGACY-MODULE

| Datei | Zweck (ursprünglich) | Status | Begründung |
|-------|---------------------|--------|-----------|
| `agents/builder_agent.py` | Code-Generation und Deployment | **LEGACY** | Funktionalität in Execution Layer integriert |
| `agents/ceo_agent.py` | Strategische Entscheidungen | **LEGACY** | Ersetzt durch Strategy + Planning Layer |
| `agents/cto_agent.py` | Technische Entscheidungen | **LEGACY** | Ersetzt durch Planning + Execution Layer |
| `agents/__init__.py` | Agent-System Imports | **LEGACY** | Nicht mehr benötigt |

## ARCHITEKTUR-VERGLEICH

### ALT: Agent-basiertes System
```
Orchestrator → CEO Agent → CTO Agent → Builder Agent → Thomas Tasks
```
- **Problem**: Sequenziell, starr, schwer erweiterbar
- **Komplexität**: Jeder Agent musste alles können
- **State**: Verstreut über verschiedene Agent-Outputs

### NEU: 6-Ebenen-System
```
Leitebene → Strategie → Planung → Delegation → Ausführung → Evaluation
```
- **Vorteil**: Klare Trennung der Verantwortlichkeiten
- **Flexibilität**: Jede Ebene hat spezifische Tools und Aufgaben
- **State**: Zentral verwaltet in `IterationState`

## ABHÄNGIGKEITEN PRÜFEN

### Module die noch core/ verwenden könnten:
- `core/llm.py` — **AKTIV** (wird von autonomous system verwendet)
- `core/state.py` — **AKTIV** (wird von autonomous system verwendet)

### Module die agents/ verwenden könnten:
- Keine gefunden — agents/ ist vollständig isoliert

## SICHERE ENTFERNUNG

Die folgenden Module können **sicher entfernt** werden, da sie:
1. Nicht vom autonomen System importiert werden
2. Keine aktiven Dependencies haben
3. Durch das neue System ersetzt wurden

### Zu entfernende Dateien:
```
core/agent.py
core/orchestrator.py
core/policy_engine.py
core/cycle_runner.py
core/ticket_executor.py
core/ticket_parser.py
core/scorecard_parser.py
agents/builder_agent.py
agents/ceo_agent.py
agents/cto_agent.py
agents/__init__.py
```

### Zu behaltende Dateien (AKTIV):
```
core/llm.py                    # LLM-Integration
core/state.py                  # State-Management
core/autonomous/               # Gesamtes autonomes System
```

## MIGRATION COMPLETE

Das 6-Ebenen-System ist seit **Iteration #3** produktiv und hat bewiesen, dass es:
- Stabil läuft (mehrere erfolgreiche Iterationen)
- Bessere Ergebnisse liefert als das Agent-System
- Einfacher zu erweitern und zu debuggen ist
- Thomas-Integration nahtlos funktioniert

**Empfehlung**: Legacy-Module können in der nächsten Iteration entfernt werden.

---

**Erstellt**: Iteration #7 (2026-02-13)  
**Status**: BEREIT ZUR ENTFERNUNG