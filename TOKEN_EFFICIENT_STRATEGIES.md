# Token-Effiziente Analyse-Strategien

**Erstellt**: 2026-02-13 — Iteration #7  
**Zweck**: Robuste Strategien für große Analyse-Tasks entwickeln, um Rate-Limit-Probleme zu vermeiden

## Problem-Analyse

**Iteration #6 Fehler**: Rate-Limit-Error trotz Retry-Mechanismus
- Error: `429 - rate_limit_error` bei 30,000 Token/Minute Limit
- Ursache: Große Legacy-Analyse versuchte zu viele Dateien auf einmal zu verarbeiten
- Aktuelles System: Hat nur einfaches Retry, aber kein intelligentes Task-Splitting

## Legacy-System Mechanismen (Erfolgreich getestet)

### 1. BatchProcessor (`core/batch_processor.py`)

**Kern-Features**:
- **Task-Splitting**: Große Analyse-Tasks werden in kleinere Sub-Tasks aufgeteilt
- **Progress-Tracking**: JSON-basierte Batch-Pläne mit Status-Verfolgung
- **Resume-Capability**: Unterbrochene Batches können fortgesetzt werden
- **Delay-Management**: Konfigurierbare Delays zwischen Sub-Tasks (Standard: 1.0s)
- **Error-Handling**: Einzelne Sub-Task-Fehler stoppen nicht den gesamten Batch

**Bewährte Strategien**:
```python
# Delay zwischen Sub-Tasks
time.sleep(self.delay_between_batches)

# Progress-Speicherung nach jeder Sub-Task
if save_progress:
    self.save_batch_plan(plan)

# Robuste Error-Isolation
try:
    output = processor_func(subtask)
    result['status'] = 'completed'
except Exception as e:
    result['status'] = 'failed'
    # Batch läuft weiter
```

### 2. TokenManager (`core/token_manager.py`)

**Kern-Features**:
- **Token-Schätzung**: Konservative Schätzung (3 Zeichen = 1 Token)
- **Intelligente Chunk-Aufteilung**: Dateien werden nach Token-Budget gruppiert
- **Große-Datei-Behandlung**: Einzelne große Dateien bekommen eigene Chunks
- **Directory-Analyse**: Rekursive Token-Schätzung für ganze Verzeichnisse

**Bewährte Algorithmen**:
```python
# Konservative Token-Schätzung
def estimate_tokens(self, text: str) -> int:
    return len(text) // 3  # Konservative Schätzung

# Intelligente Chunk-Bildung
if token_count > self.max_tokens_per_chunk:
    # Große Datei als eigener Chunk
    chunks.append({
        'files': [file_path],
        'requires_splitting': True
    })
```

## Aktuelles System Gaps

### 1. LLM Client (`core/autonomous/llm_client.py`)

**Vorhandene Features** ✅:
- Exponential Backoff Retry (60s, 120s, 240s, 480s, 960s)
- Message-Size-Reduction bei Rate-Limits
- Robuste Error-Handling für 429/5xx Errors

**Fehlende Features** ❌:
- **Kein Task-Splitting**: Große Tasks werden nicht automatisch aufgeteilt
- **Kein Progress-Tracking**: Keine Möglichkeit unterbrochene Tasks fortzusetzen
- **Kein Token-Budget-Management**: Keine proaktive Token-Schätzung vor API-Calls
- **Keine Directory-Analyse-Optimierung**: Große Verzeichnisse werden nicht intelligent aufgeteilt
- **Kein Batch-Processing**: Keine Möglichkeit mehrere kleine Tasks sequenziell zu verarbeiten

## Implementierungsplan

### Phase 1: Token-Budget-Integration (Priorität: HOCH)

**Neue Datei**: `core/autonomous/token_budget.py`
```python
class TokenBudget:
    def __init__(self, max_tokens_per_request=4000):
        self.max_tokens_per_request = max_tokens_per_request
    
    def estimate_prompt_tokens(self, system_prompt, user_message):
        # Implementiere Token-Schätzung für Prompts
    
    def can_process_files(self, file_paths):
        # Prüfe ob Dateien in einem Request verarbeitet werden können
    
    def split_file_analysis(self, file_paths):
        # Teile Datei-Listen in Token-Budget-konforme Chunks
```

**Integration in LLM Client**:
- Vor jedem API-Call: Token-Budget prüfen
- Bei Überschreitung: Automatisches Task-Splitting
- Proaktive Vermeidung von Rate-Limits

### Phase 2: Batch-Processing für Autonomes System (Priorität: HOCH)

**Neue Datei**: `core/autonomous/batch_runner.py`
```python
class AutonomousBatchRunner:
    def __init__(self, llm_client, token_budget):
        self.llm_client = llm_client
        self.token_budget = token_budget
    
    def create_analysis_batch(self, task_description, target_files):
        # Erstelle Batch-Plan für große Analyse-Tasks
    
    def execute_batch(self, batch_plan):
        # Führe Batch mit autonomem LLM Client aus
    
    def resume_batch(self, batch_id):
        # Setze unterbrochene Batches fort
```

**Features**:
- JSON-basierte Batch-Pläne (kompatibel mit Legacy-System)
- Integration mit autonomem LLM Client
- Progress-Tracking und Resume-Capability

### Phase 3: Smart Directory Analysis (Priorität: MITTEL)

**Erweiterung**: `core/autonomous/tools/file_operations.py`
```python
def analyze_directory_smart(directory_path, max_tokens_per_chunk=4000):
    # Intelligente Verzeichnis-Analyse mit Token-Budget
    # Nutzt TokenBudget und BatchRunner
    # Automatisches Splitting großer Verzeichnisse
```

**Features**:
- Rekursive Token-Schätzung
- Automatische Chunk-Bildung
- Priorisierung nach Dateitypen

### Phase 4: Integration in Ebenen-System (Priorität: MITTEL)

**Ebenen-Integration**:
- **Planungsebene**: Automatische Erkennung großer Analysis-Tasks
- **Delegationsebene**: Automatische Batch-Plan-Erstellung
- **Ausführungsebene**: Nahtlose Batch-Verarbeitung

**Konfiguration**:
```python
# In config.py
TOKEN_BUDGET_CONFIG = {
    'max_tokens_per_request': 4000,
    'safety_margin': 0.8,
    'delay_between_chunks': 2.0,
    'enable_auto_batching': True
}
```

## Sofort-Maßnahmen (Für nächste Iteration)

### 1. Quick-Win: File-List-Splitting

**Problem**: Große Datei-Listen in `list_directory` Tool
**Lösung**: Automatisches Splitting bei >50 Dateien
```python
if len(files) > 50:
    return f"Directory too large ({len(files)} files). Use recursive=false or analyze subdirectories separately."
```

### 2. Quick-Win: Token-Warnung in Tools

**Problem**: Tools wissen nicht ob sie zu viel Content produzieren
**Lösung**: Token-Warnung in file-read Tools
```python
if estimate_tokens(content) > 3000:
    return content[:10000] + f"\n\n[FILE TRUNCATED - {len(content)} chars total, estimated {tokens} tokens]"
```

### 3. Quick-Win: Batch-Mode Flag

**Problem**: Keine Möglichkeit Batch-Processing zu aktivieren
**Lösung**: Umgebungsvariable für Batch-Mode
```python
ENABLE_BATCH_MODE = os.getenv("AUTONOMOUS_BATCH_MODE", "false").lower() == "true"
```

## Erfolgs-Metriken

### Quantitative Ziele:
- **Rate-Limit-Errors**: Reduktion um >90%
- **Task-Completion-Rate**: Erhöhung von ~60% auf >95%
- **Token-Effizienz**: <80% des verfügbaren Token-Budgets nutzen
- **Resume-Success-Rate**: >95% erfolgreiche Batch-Fortsetzungen

### Qualitative Ziele:
- Robuste Verarbeitung großer Verzeichnisse (>100 Dateien)
- Nahtlose Integration in bestehendes Ebenen-System
- Benutzerfreundliche Progress-Anzeige
- Kompatibilität mit Legacy-Batch-System

## Risiken & Mitigationen

### Risiko 1: Performance-Overhead
**Mitigation**: Batch-Processing nur bei großen Tasks aktivieren

### Risiko 2: Komplexität-Erhöhung
**Mitigation**: Schrittweise Integration, Legacy-Kompatibilität beibehalten

### Risiko 3: Token-Schätzung ungenau
**Mitigation**: Konservative Schätzungen + Safety-Margins verwenden

## Nächste Schritte

1. **Iteration #8**: Implementiere Phase 1 (Token-Budget-Integration)
2. **Iteration #9**: Implementiere Phase 2 (Batch-Processing)
3. **Iteration #10**: Teste mit großer Legacy-Analyse
4. **Iteration #11**: Phase 3 + 4 (Smart Directory Analysis + Ebenen-Integration)

---

**Status**: ✅ Strategien definiert, bereit für Implementierung  
**Nächste Iteration**: Token-Budget-Integration starten