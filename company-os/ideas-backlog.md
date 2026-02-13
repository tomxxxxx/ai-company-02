# Ideas Backlog

Persistenter Ideenspeicher des Unternehmens. Wird von der Leitebene gepflegt.
Die Strategieebene wählt aus diesem Backlog den Fokus für die aktuelle Iteration.

## Format

Jede Idee hat:
- **Kategorie**: system | produkt | prozess | experiment
- **Priorität**: hoch | mittel | niedrig
- **Datum**: Wann hinzugefügt
- **Beschreibung**: Was genau und warum

## Regeln

- Maximal 20 aktive Einträge. Wenn voll: niedrigste Priorität entfernen.
- Erledigte Ideen werden gelöscht, nicht archiviert.
- Die Leitebene aktualisiert diesen Backlog jede Iteration.

---

## Aktive Ideen

### [system | hoch | 2026-02-13] Planungsebene Token-Awareness einbauen
Die Planungsebene muss lernen, Tasks unter Token-Limits zu planen. Statt 7 Aktionen → max 3 Aktionen pro Iteration. Oder sogar Task-Splitting: "Analysiere nur 2 Dateien, dokumentiere Ergebnisse, nächste Iteration macht weiter". Verhindert Rate-Limit-Failures. DRINGEND nach Iteration #6 Failure.

### [system | hoch | 2026-02-13] Token-bewusste Legacy-Analyse (Mini-Iteration)
Nach Planungsebene-Fix: Mini-Iteration mit nur 1-2 Legacy-Dateien analysieren (z.B. nur core/agent.py und core/orchestrator.py), Ergebnisse dokumentieren, dann in nächster Iteration fortsetzen. Beweist token-effiziente Arbeitsweise.

### [system | hoch | 2026-02-12] Dokumentation konsolidieren
company_state.json enthält veraltete Felder. ONBOARDING.md wurde gestrafft aber referenziert noch alte Strukturen. Saubere Dokumentation = bessere Iterationen.

### [system | mittel | 2026-02-12] REVERT-Funktionalität implementieren
Das neue Evaluations-System kann REVERT empfehlen, aber der Runner loggt nur ein Warning. Git-Revert-Funktionalität für fehlerhafte Iterationen nachrüsten.

### [system | mittel | 2026-02-12] Lokale Tool-Alternativen entwickeln
Statt externe APIs: lokale Email-Queue, file-basierte Analytics, Python-Web-Scraping ohne Services. System muss mit vorhandenen Tools arbeiten können.

### [produkt | mittel | 2026-02-12] TaskMaster HTTP-Migration abschließen
TICKET-001 Code wurde generiert aber nie getestet/deployt. Thomas muss Slack Dashboard URLs konfigurieren (TICKET-003) und App Directory Submission machen (TICKET-002).

### [system | niedrig | 2026-02-12] Tool-Fähigkeiten erweitern (später)
Mittelfristig: HTTP-Requests, Email-Versand, Web-Scraping. Aber erst wenn System ohne externe Dependencies arbeiten kann.

### [system | niedrig | 2026-02-13] .stop-Datei Self-Shutdown nutzen
Thomas hat eine .stop-Datei-Mechanismus implementiert. Das System kann sich selbst anhalten mit `write_file(".stop", "Grund...")`. Nützlich für Self-Diagnosis: wenn das System erkennt, dass es in Loops läuft oder kritische Fehler macht, kann es sich selbst stoppen und Thomas informieren.

### [system | niedrig | 2026-02-13] Robustheit-Features erweitern
Nach erfolgreichem Rate-Limit-Retry: weitere Robustheit-Features wie automatische Backup-Erstellung vor riskanten Operationen, System-Health-Monitoring, oder Rollback-Mechanismen für fehlerhafte Commits.
