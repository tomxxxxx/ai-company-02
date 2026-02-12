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

### [2026-02-12] Feedback aus Iteration #1 und #2

1. **Iteration #1**: Leitebene hat zu viel selbst umgesetzt (30 Turns). Strategieebene hat sich sofort auf TaskMaster gestürzt statt Systemreife. Planungsebene hat gut funktioniert.

2. **Iteration #2**: Leitebene besser (6 Turns). ABER: wieder bei Planungsebene blockiert — nie zur Ausführung gekommen. Das System hat externe API-Abhängigkeiten eingeplant die nicht existieren (SendGrid, Mixpanel) und sich mit einem Blocking-Task selbst blockiert. Iterationen MÜSSEN die Ausführungsebene erreichen.

### [2026-02-13] Feedback aus Iteration #3

**Das war die erste Iteration, die alle 6 Ebenen durchlaufen hat — ein Durchbruch!**

Positiv:
- Leitebene hat die ideas-backlog sauber gepflegt und sich auf ihre Rolle beschränkt.
- Strategieebene hat eine realistische, kleine Aufgabe gewählt (Legacy-Cleanup) — genau richtig.
- Planungsebene hat konkrete, machbare Tasks formuliert, keine externen Abhängigkeiten.
- Ausführungsebene hat autonom 15+ Legacy-Dateien identifiziert und gelöscht.
- Das System hat bewiesen, dass es eigenständig sinnvolle Arbeit leisten kann.

Verbesserungspotential:
- Die Evaluationsebene war noch oberflächlich — soll künftig konkreter bewerten und Commit/Revert empfehlen (siehe nächster Eintrag).

Insgesamt: Iteration #3 ist der Beweis, dass die Architektur funktioniert. Weiter so!

### [2026-02-13] Iteration #4 — Externer Abbruch, kein Systemfehler

Iteration #4 wurde nach der Leitebene abgebrochen, weil das Anthropic API-Guthaben aufgebraucht war. Das ist **kein Fehler im System** — die Leitebene hat korrekt gearbeitet und den Backlog sinnvoll aktualisiert. Das Guthaben wurde nachgeladen und Auto-Reload aktiviert. Keine Fehlersuche nötig, einfach weiterarbeiten.

### [2026-02-12] Thomas' persönliche Kontakte

Thomas' private Kontakte werden NICHT für Business genutzt.

### [2026-02-13] Evaluationsebene soll Commit/Revert-Empfehlung aussprechen

Die Evaluationsebene soll am Ende jeder Iteration bewerten, ob die Iteration einen **Fortschritt oder Rückschritt** darstellt, und eine von drei Empfehlungen aussprechen:

1. **Änderungen akzeptieren und committen** — Iteration war produktiv, Ergebnis sichern.
2. **Änderungen rückgängig machen** — Iteration hat Schaden angerichtet, zurückrollen.
3. **Weitere Iteration auf bestehenden Änderungen** — Ergebnis ist unvollständig, weitermachen bevor committed wird.

Aktuell soll das nur eine Empfehlung sein — Thomas entscheidet. Später kann das automatisiert werden.

Diese Änderung soll das System selbst in der nächsten Iteration umsetzen: Evaluations-Prompt anpassen und ggf. den Runner erweitern.
