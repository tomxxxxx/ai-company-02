# SYSTEM-ARCHITEKTUR — AI Automation Lab

*Dokumentation des aktiven 6-Ebenen-Systems*

## ÜBERBLICK

Das AI Automation Lab verwendet ein **6-Ebenen-autonomes System**, das in kontinuierlichen Iterationen arbeitet. Jede Iteration durchläuft alle 6 Ebenen sequenziell, wobei jede Ebene auf den Outputs der vorherigen aufbaut.

```
ITERATION → Leitebene → Strategie → Planung → Delegation → Ausführung → Evaluation → COMMIT/CONTINUE
```

## CORE-ARCHITEKTUR

### Hauptkomponenten

| Modul | Pfad | Funktion |
|-------|------|----------|
| **Runner** | `core/autonomous/runner.py` | Hauptschleife, orchestriert alle Iterationen |
| **Layer Base** | `core/autonomous/layer.py` | Basis-Klasse für alle Ebenen |
| **Tools** | `core/autonomous/tools.py` | Alle verfügbaren Werkzeuge |
| **LLM Client** | `core/autonomous/llm_client.py` | Claude API Integration |
| **State Management** | `core/autonomous/iteration_state.py` | Iteration-Zustand und Persistierung |

### Tool-System

Das System verfügt über 8 integrierte Tools:

1. **ReadFileTool** — Dateien lesen
2. **WriteFileTool** — Dateien schreiben
3. **EditFileTool** — Dateien editieren (string replace)
4. **ListDirectoryTool** — Verzeichnisse auflisten
5. **RunCommandTool** — Shell-Befehle ausführen
6. **GitCommitTool** — Git-Commits erstellen
7. **GitStatusTool** — Git-Status prüfen
8. **CreateThomasTaskTool** — Aufgaben für Thomas erstellen

## DIE 6 EBENEN

### 1. LEITEBENE (`core/autonomous/layers/control.py`)
- **Rolle**: Systemreflexion, Ideenmanagement, Systemzustandsbewertung
- **Tools**: `read_file`, `list_directory`, `edit_file`, `write_file`
- **Input**: Operator-Briefing, Ideen-Backlog, Systemkontext
- **Output**: Systemzustands-Bewertung und Ideen-Backlog-Update
- **Prompt**: `prompts/control.md`

### 2. STRATEGIEEBENE (`core/autonomous/layers/strategy.py`)
- **Rolle**: Einen Fokus für die Iteration wählen
- **Tools**: `read_file`, `list_directory`
- **Input**: Leitebene-Output + Ideen-Backlog
- **Output**: Ein konkreter Fokus mit Begründung
- **Prompt**: `prompts/strategy.md`

### 3. PLANUNGSEBENE (`core/autonomous/layers/planning.py`)
- **Rolle**: Strategischen Fokus in konkrete Aufgaben übersetzen
- **Tools**: `read_file`, `list_directory`, `create_thomas_task`
- **Input**: Strategieebene-Output
- **Output**: Detaillierter Aufgabenplan
- **Prompt**: `prompts/planning.md`

### 4. DELEGATIONSEBENE (`core/autonomous/layers/delegation.py`)
- **Rolle**: Plan in konkrete, schrittweise Aktionen strukturieren
- **Tools**: `read_file`, `list_directory`, `create_thomas_task`
- **Input**: Planungsebene-Output
- **Output**: Schritt-für-Schritt Aktionsliste für Ausführungsebene
- **Prompt**: `prompts/delegation.md`

### 5. AUSFÜHRUNGSEBENE (`core/autonomous/layers/execution.py`)
- **Rolle**: Aktionsliste abarbeiten, konkrete Arbeit umsetzen
- **Tools**: **ALLE** (8 Tools verfügbar)
- **Input**: Delegationsebene-Aktionsliste
- **Output**: Ausführungsbericht mit Ergebnissen
- **Prompt**: `prompts/execution.md`

### 6. EVALUATIONSEBENE (`core/autonomous/layers/evaluation.py`)
- **Rolle**: Iteration bewerten, Commit/Revert/Continue empfehlen
- **Tools**: `read_file`, `list_directory`, `git_status`
- **Input**: Alle Ebenen-Outputs der Iteration
- **Output**: Bewertung + Empfehlung (COMMIT/REVERT/CONTINUE)
- **Prompt**: `prompts/evaluation.md`

## DATENFLUSS

### Iteration State
Jede Iteration hat einen `IterationState` der folgende Informationen sammelt:
- **Iteration ID** — Fortlaufende Nummer
- **Company State** — Aktueller Unternehmenszustand (Kapital, MRR, etc.)
- **History** — Outputs der letzten 10 Iterationen
- **Layer Outputs** — Output jeder Ebene in dieser Iteration
- **Thomas Tasks** — Erstellte Aufgaben für Thomas
- **Kosten/Token-Tracking** — LLM-Usage pro Iteration

### Persistierung
- **Iteration Logs**: `data/iterations/iteration_YYYY-MM-DD_ID.json`
- **Company State**: `data/company_state.json`
- **Ideas Backlog**: `company-os/ideas-backlog.md`
- **Operator Briefing**: `company-os/operator-briefing.md`

## CONTINUOUS LOOP

### Hauptschleife (`run_continuous`)
1. **Iteration starten** — Neue Iteration-ID, State laden
2. **6 Ebenen durchlaufen** — Sequenziell, jede baut auf vorheriger auf
3. **Thomas-Tasks verarbeiten** — Non-blocking sammeln
4. **Evaluation-Empfehlung umsetzen** — Auto-Commit bei COMMIT-Empfehlung
5. **State speichern** — Iteration-Log schreiben
6. **Pause** — 5s warten, dann nächste Iteration

### Stopp-Bedingungen
- **`.stop` Datei** — Graceful shutdown
- **Ctrl+C** — User interrupt
- **Layer-Fehler** — Iteration stoppt bei Layer-Failure
- **Max-Iterations** — Optional für Testing

## THOMAS-INTEGRATION

### Task-System
- **Non-Blocking Tasks** — Loop läuft weiter, Thomas arbeitet parallel
- **HUMAN_ACTION_NEEDED.md** — Automatisch generiert bei neuen Tasks
- **Priority Levels** — low, medium, high, critical

### Evaluation-Integration
- **Auto-Commit** — Bei COMMIT-Empfehlung wird automatisch committed
- **Revert** — Noch nicht implementiert
- **Continue** — Nächste Iteration läuft normal weiter

## QUALITÄTSSICHERUNG

### Error Handling
- **Layer-Failures** — Stoppen Iteration, werden geloggt
- **Rate-Limit-Retry** — Automatisches Retry bei API-Limits
- **Tool-Errors** — Werden in Layer-Output dokumentiert

### Logging
- **Structured Logging** — Alle Aktionen werden detailliert geloggt
- **Cost Tracking** — Token und Kosten pro Iteration
- **Performance Metrics** — Laufzeit, Tool-Usage, etc.

## ENTRY POINTS

### Produktiv
- `python run_autonomous.py` — Startet continuous loop
- `python -m core.autonomous.runner` — Alternative

### Testing
- `runner.run_single()` — Eine Iteration
- `runner.run_continuous(max_iterations=3)` — Begrenzte Anzahl

---

**Status**: AKTIV — Dieses System ist seit Iteration #3 produktiv im Einsatz.
**Letzte Aktualisierung**: Iteration #7 (2026-02-13)