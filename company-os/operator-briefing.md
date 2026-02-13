# Operator-Briefing für die Leitebene

Dieses Dokument wird von Thomas (dem Operator) geschrieben und von der Leitebene
zu Beginn jeder Iteration gelesen. Es enthält Feedback, Beobachtungen und Richtungsvorgaben.

Die Leitebene MUSS dieses Dokument lesen und die Inhalte in ihre Analyse einbeziehen.
Einträge die als "erledigt" markiert sind, können von der Leitebene gelöscht werden.

---

## Aktuelle Hinweise

### [2026-02-12] Grundsätzliche Unternehmensrichtung

Das Unternehmen ist ein **autonomes, KI-gesteuertes Betriebssystem**. Der Fokus liegt auf dem Aufbau und der Verbesserung dieses Systems — NICHT auf der schnellstmöglichen Monetarisierung eines einzelnen Produkts.

Produkte sind Outputs des Systems. Das System selbst ist das Kernprodukt.

### [2026-02-12] Iterationen dürfen klein sein

Iterationen dürfen kleine Schritte sein. "Legacy aufräumen", "eine Datei verbessern", "einen Prompt optimieren" — das ist völlig okay. Große Ziele erreicht man nach hunderten kleiner Iterationen. Nicht alles in eine Iteration packen.

### [2026-02-13] Iteration #4 — Externer Abbruch, kein Systemfehler

Iteration #4 wurde nach der Leitebene abgebrochen, weil das Anthropic API-Guthaben aufgebraucht war. Das ist **kein Fehler im System** — die Leitebene hat korrekt gearbeitet und den Backlog sinnvoll aktualisiert. Keine Fehlersuche nötig, einfach weiterarbeiten.

### [2026-02-13] Iteration #6 — Externer Abbruch (Rate Limit)

Iteration #6 brach wegen API Rate Limit ab. **Kein Systemfehler** — Rate-Limit-Retry mit exponentiellem Backoff (60s, 120s, 240s...) wurde inzwischen im LLM-Client implementiert. Keine Fehlersuche nötig.

### [2026-02-13] Allgemeines Feedback zu den bisherigen Iterationen

- Iterationen #3 und #5 liefen erfolgreich alle 6 Ebenen durch — die Architektur funktioniert.
- Evaluationsebene hat jetzt Commit/Revert/Continue-Empfehlungen — wurde in Iteration #5 vom System selbst implementiert.
- Die Leitebene soll erledigte Einträge in diesem Briefing aktiv löschen.

### [2026-02-12] Thomas' persönliche Kontakte

Thomas' private Kontakte werden NICHT für Business genutzt.
