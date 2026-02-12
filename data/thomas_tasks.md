# Tasks for Thomas (Operator)
# Updated: Cycle #8 — Autonomer Cycle Runner gebaut, TICKET-001 autonom ausgeführt

## STATUS: Company OS steht + HTTP Migration Code generiert + Warten auf Thomas

---

## ⭐ JETZT (Reihenfolge beachten)

### 1. LLM-generierten Code reviewen
Der Cycle Runner hat TICKET-001 autonom ausgeführt und 5 Files in `products/slack_bot/` geschrieben/überschrieben.
**Bitte reviewen vor Deploy:**
- `products/slack_bot/app.py` — komplett neu (HTTP Mode + OAuth)
- `products/slack_bot/oauth_store.py` — NEU (SQLite OAuth Store)
- `products/slack_bot/config.py` — updated (OAuth env vars)
- `products/slack_bot/database.py` — updated
- `products/slack_bot/requirements.txt` — updated (neue Dependencies)

### 2. TICKET-003: Slack Dashboard URLs konfigurieren (~5 Min)
Schritt-für-Schritt Anleitung in `company-os/tickets/003-slack-dashboard-config.md`.
- Slack API Dashboard → Redirect URL + Request URL setzen
- Railway env var `SOCKET_MODE=False` setzen

### 3. TICKET-002: App Directory Submission (~20 Min)
Content vorbereitet in `SLACK_DIRECTORY_SUBMISSION.md`.
- App Icon (512x512 PNG) erstellen (Canva, lila Checkmark)
- Submission Form ausfüllen + absenden

---

## BALD (nach App Directory)

- [ ] Stripe Account anlegen (erst wenn >0 User)
- [ ] EXP-001 Scorecard Week 1 Review (nach 2026-02-19)

---

## ERLEDIGT ✅

- [x] Slack App erstellt + Tokens konfiguriert
- [x] Bot lokal getestet — funktioniert  
- [x] Railway Deployment — läuft 24/7
- [x] Builder Agent Code repariert (8 Files)
- [x] Landing Page gebaut → GitHub Pages
- [x] Privacy Policy + Terms of Service erstellt
- [x] Slack Directory Submission Guide erstellt

---

## ⚠️ HINWEISE
- Bot-Code in `products/slack_bot/` wurde vom LLM überschrieben — reviewen!
- Alte Agents (`agents/`) + `core/orchestrator.py` = LEGACY, nicht mehr benutzen
- Neue Engine: `core/cycle_runner.py` + `scheduler.py`
- Offene Eskalationen stehen immer in `HUMAN_ACTION_NEEDED.md`
```