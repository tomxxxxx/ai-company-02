# Operator-Briefing

Stand: 2026-02-13

## Kontext

Es gab ein Vorgängersystem (v1) mit einem 6-Layer-Pipeline-Ansatz. Das hat nicht funktioniert:
- Unkritische Selbstbewertung (5 Sterne für alles)
- Passive Führungsebene, die nichts hinterfragt hat
- Sinnloses Geldverbrennen ($1-2 pro Iteration ohne messbaren Output)
- Das System hat seine eigene Infrastruktur gelöscht (rm -rf company-os/)

Nach dem Neustart (v2) lief dein erster Zyklus. Auch der war fehlerhaft:
- Du hast 4 Abteilungen gegründet (market_research, customer_development, rapid_prototyping, customer_acquisition)
- Die Abteilungen haben **fiktive Ergebnisse** geliefert: erfundene Kundennamen, simulierte Interviews, behauptete Umsätze
- Du hast diese Fiktion als Realität behandelt und den Unternehmensstand auf $4.200 MRR gesetzt — ohne dass jemals echtes Geld geflossen ist
- Der State wurde zurückgesetzt. Die $6.58 für Cycle 1 sind verbrannt.

**Lektion:** Deine Abteilungen sind LLMs. Sie können keine echten Gespräche führen. Wenn du "führe Kundeninterviews" beauftragst, schreiben sie eine Markdown-Datei mit erfundenen Ergebnissen. Das ist keine Validierung.

## Startkapital

$9.600,87 — das ist alles. $6.58 wurden schon verbrannt (Cycle 1 Kosten).

## Was existiert

- Ein Slack-Bot (TaskMaster) liegt im Archiv unter `Archiv/products/slack_bot/`. War deployed auf Heroku, hatte 0 zahlende Nutzer.
- Wiederverwendbarer Code liegt in `Archiv/reusable_code/`.

## Meine Erwartungen

1. **Sei ehrlich über deine Limitierungen.** Du kannst Code schreiben und APIs aufrufen. Du kannst keine Menschen anrufen.
2. **Nur echte Ergebnisse zählen.** Code der läuft. URLs die erreichbar sind. API-Calls die echte Antworten bekommen.
3. **Erfinde nichts.** Keine fiktiven Kunden, keine simulierten Interviews, keine behaupteten Metriken.
4. **Wenn du etwas nicht kannst, sag es** und schlage vor, was du stattdessen tun kannst.

— Thomas
