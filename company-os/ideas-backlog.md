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

### [system | hoch | 2026-02-13] Core-Module Legacy-Analyse fortsetzen
Iteration #3 wurde bei der Core-Module-Analyse unterbrochen. Identifizieren welche Module in core/ und agents/ noch aktiv genutzt werden vs. Legacy-Code der entfernt werden kann.

### [system | mittel | 2026-02-12] REVERT-Funktionalität implementieren
Das neue Evaluations-System kann REVERT empfehlen, aber der Runner loggt nur ein Warning. Git-Revert-Funktionalität für fehlerhafte Iterationen nachrüsten.

### [system | hoch | 2026-02-12] Dokumentation konsolidieren
company_state.json enthält veraltete Felder. ONBOARDING.md wurde gestrafft aber referenziert noch alte Strukturen. Saubere Dokumentation = bessere Iterationen.

### [system | mittel | 2026-02-12] Lokale Tool-Alternativen entwickeln
Statt externe APIs: lokale Email-Queue, file-basierte Analytics, Python-Web-Scraping ohne Services. System muss mit vorhandenen Tools arbeiten können.

### [produkt | mittel | 2026-02-12] TaskMaster HTTP-Migration abschließen
TICKET-001 Code wurde generiert aber nie getestet/deployt. Thomas muss Slack Dashboard URLs konfigurieren (TICKET-003) und App Directory Submission machen (TICKET-002).

### [system | niedrig | 2026-02-12] Tool-Fähigkeiten erweitern (später)
Mittelfristig: HTTP-Requests, Email-Versand, Web-Scraping. Aber erst wenn System ohne externe Dependencies arbeiten kann.

### [experiment | niedrig | 2026-02-12] Neue Produkt-Hypothesen evaluieren
5 SaaS-Ideen wurden bereits analysiert (TOP_5_SAAS_IDEAS.json). Sobald das System reif genug ist, können wir systematisch neue Experimente starten.
