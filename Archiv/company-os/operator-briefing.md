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

### [2026-02-13] Systemänderungen — Rate-Limit Retry, Stopp-Mechanismus, keine Blockierung

Folgende Änderungen wurden vom Operator vorgenommen:

1. **Rate-Limit Retry**: Der LLM-Client hat jetzt automatisches Retry mit exponentiellem Backoff (60s, 120s, 240s, 480s, 960s) bei API-Fehlern (429, 5xx). Das System muss hierfür keine eigene Lösung implementieren.

2. **Keine blockierenden Tasks mehr**: Thomas-Tasks blockieren den Loop NICHT mehr. Der Loop läuft immer weiter. Thomas erledigt Tasks, wenn er Zeit hat. Das `blocking`-Feld im `create_thomas_task`-Tool wird ignoriert.
Wenn Thomas-Tasks in `HUMAN_ACTION_NEEDED.md` durch spätere Iterationen **obsolet** geworden sind (z.B. das System hat das Problem selbst gelöst, oder die Aufgabe ist nicht mehr relevant), soll die Leitebene diese Tasks aus der Datei **löschen**. Veraltete Tasks sind Verwirrung.

3. **`.stop`-Datei zum Anhalten**: Eine Datei `.stop` im Workspace-Root wird vor jeder neuen Iteration geprüft. Existiert sie, stoppt der Loop sauber nach der aktuellen Iteration. Der Inhalt der Datei wird als Grund geloggt. Das System kann sich so auch selbst anhalten, indem es `write_file(".stop", "Grund...")` aufruft.

4. **`--max-iterations N`**: Neuer CLI-Parameter zum Begrenzen der Iterationsanzahl.

### [2026-02-13] Feedback: Iteration #7 — Parser-Bug und Junk-Dateien

Iteration #7 lief **10 Mal durch alle 6 Ebenen**, wurde aber nie als abgeschlossen gespeichert, weil der Recommendation-Parser im Runner crashte. **Dieser Bug wurde vom Operator gefixt**. Keine Fehlersuche nötig.

Probleme:
- **Junk-Dateien im Root**: Das System hat ~10 Analyse-Dokumente im Root erstellt (ITERATION_7_*.md, LEGACY_*.md, TOKEN_EFFICIENT_STRATEGIES.md, temp_module_analysis.md) und ein `docs/` Verzeichnis.
- **Wiederholte Arbeit**: Weil die Iteration nie gespeichert wurde, hat das System 10 Mal dieselbe Legacy-Analyse gemacht. Die Leitebene konnte die vorherige Iteration nicht sehen.

### [2026-02-13] KRITISCHES FEEDBACK: Workspace-Chaos, Leitebene und Evaluationsebene

#### Workspace ist ein Chaos

Es liegen immer noch viele **veraltete Dateien im Root**, die nichts mit dem autonomen System zu tun haben und die Agenten verwirren. Beispiele:

- `OUTREACH_STRATEGY.md`, `outreach-templates.md` — veraltete Marketing-Dokumente, irrelevant
- `privacy.html`, `terms.html`, `styles.css` — Slack-Bot-Website-Dateien, gehören nach `products/slack_bot/` oder gelöscht
- `SLACK_BOT_SPEC.md`, `SLACK_DIRECTORY_SUBMISSION.md` — Slack-Bot-Doku, gehört nach `products/slack_bot/`
- `business-playbook.md`, `VALIDATION_PLAYBOOK.md`, `TASK_TODAY.md`, `THOMAS_NEXT_SESSION.md` — veraltete Planungsdokumente
- `scheduler.py`, `taskmaster.db` — alter Code/Daten
- `company_state.json` im Root — Duplikat, die echte liegt in `data/company_state.json`
- `docs/` — existiert noch mit alten Analyse-Dateien

**Das Problem**: Wenn die Agenten den Workspace sehen, entsteht der Eindruck dass der Slack-Bot das Hauptprojekt ist. Das ist FALSCH. Das Hauptprojekt ist das autonome System. Der Slack Bot ist ein Experiment, an dem das System sich ausprobieren kann, wenn es der Meinung ist, dass wir das System an einem Projekt ausprobieren sollen. Alles was im Root liegt und nicht direkt zum Hauptsystem gehört, lenkt ab.

**Die Leitebene hätte das selbst erkennen müssen.** Das ist genau ihre Aufgabe: Probleme in den Arbeitsabläufen identifizieren. Stattdessen hat sie Token-Awareness als "Idee" aus dem Backlog genommen und nicht gemerkt, dass das schon implementiert war. Die Leitebene muss **aktiver beobachten** und **kritischer denken**.

#### Priorität: Aufräumen JETZT

Die Leitebene soll das Root-Verzeichnis aufräumen als **höchste Priorität** in den Backlog aufnehmen. Nicht "irgendwann", nicht "wenn Zeit ist" — JETZT. Jede Iteration in der die Agenten durch irrelevante Dateien verwirrt werden, ist verschwendetes Geld.

### [2026-02-12] Thomas' persönliche Kontakte

Thomas' private Kontakte werden NICHT für Business genutzt.
