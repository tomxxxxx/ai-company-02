# AI Automation Lab

Ein autonomes KI-System für Geschäftsentwicklung und Produktvalidierung.

## System-Architektur

Dieses Projekt enthält **zwei parallele Systeme**:

### 1. Autonomes 6-Ebenen-System (Hauptsystem)
**Zweck**: Geschäftsstrategie, Produktentwicklung und autonome Entscheidungsfindung

**Ebenen-Struktur**:
- **Leitebene** (`core/autonomous/leitebene_prompt.txt`) - Systemzustand bewerten, Ideen-Backlog verwalten
- **Strategieebene** (`core/autonomous/strategie_prompt.txt`) - Strategische Fokussierung und Priorisierung  
- **Planungsebene** (`core/autonomous/planung_prompt.txt`) - Konkrete Aufgaben und Machbarkeitsprüfung
- **Delegationsebene** (`core/autonomous/delegation_prompt.txt`) - Aktionslisten für Ausführung
- **Ausführungsebene** (`core/autonomous/ausfuehrung_prompt.txt`) - Tool-Nutzung und Implementierung
- **Evaluationsebene** (`core/autonomous/evaluation_prompt.txt`) - Bewertung und Commit/Revert-Empfehlungen

**Core-Module**:
- `core/cycle_runner.py` - Hauptsteuerung der Ebenen-Zyklen
- `core/llm.py` - LLM-Integration mit Rate-Limit-Management
- `core/state.py` - Zustandsverwaltung und Persistierung
- `core/token_manager.py` - Token-Optimierung und Kostenmanagement

### 2. Slack-Bot-System (Produktvalidierung)
**Zweck**: MVP für Slack-Integration und Kundenvalidierung

**Module**:
- `slack_bot/` - Slack-Bot Implementation
- Eigenständiges System für Produkttests

## Aktueller Status
- **Phase**: VALIDATE
- **Kapital**: €9,607.45
- **MRR**: €0.00
- **Produkte**: slack_bot

## Entwicklung

### Autonomes System starten
```bash
python -m core.cycle_runner
```

### Slack-Bot testen
```bash
cd slack_bot
python app.py
```

## Architektur-Prinzipien

1. **Autonomie**: Das 6-Ebenen-System trifft eigenständige Geschäftsentscheidungen
2. **Validierung**: Der Slack-Bot dient als MVP für Marktvalidierung  
3. **Trennung**: Beide Systeme sind unabhängig und können parallel entwickelt werden
4. **Evolution**: Das System lernt aus jeder Iteration und verbessert sich selbst

## Nächste Schritte
- Slack-Bot Marktvalidierung durchführen
- Autonome Geschäftsentscheidungen optimieren
- Integration zwischen beiden Systemen evaluieren