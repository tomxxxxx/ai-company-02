# Archiv

Altes System (v1), archiviert am 2026-02-13 beim Neustart auf v2.

## reusable_code/ — PORTIERBAR

Code der direkt in v2 wiederverwendet werden kann:

| Datei | Beschreibung | Status |
|-------|-------------|--------|
| `llm_client.py` | Anthropic Claude Tool-Use Client mit Rate-Limit-Retry | Getestet, funktioniert |
| `tools/base.py` | Tool-Abstraktion + Registry | Sauber, direkt nutzbar |
| `tools/filesystem.py` | Read/Write/Edit/List Dateien | Dateischutz muss ergänzt werden |
| `tools/git.py` | Git Status/Commit mit Auto-Push | Funktioniert |
| `tools/shell.py` | Shell-Command-Ausführung | Funktioniert |
| `tools/token_utils.py` | Token-Schätzung | Einfach aber nützlich |
| `iteration_state.py` | State-Tracking pro Iteration | Muss für CEO-Zyklen angepasst werden |
| `run_autonomous.py` | Alter Entrypoint | Nur als Referenz |
| `requirements.txt` | Python-Dependencies | Basis für v2 |

## products/slack_bot/ — BESTEHENDES PRODUKT

Funktionsfähiger Slack-Bot (TaskMaster). Deployed auf Railway.
0 Nutzer, aber vollständiger Code. Kann vom v2-System als Produkt erkannt und weiterentwickelt werden.
