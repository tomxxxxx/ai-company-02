# THOMAS MORGEN-ANLEITUNG (Nächste Session)

## WAS PASSIERT IST
- Orchestrator-Framework steht (CEO + CTO + Builder Agents)
- Slack Bot "TaskMaster" MVP Code generiert (13 Dateien in products/slack_bot/)
- ONBOARDING.md erstellt → damit neue Chat-Instanzen sofort Kontext haben
- scheduler.py erstellt → Orchestrator kann autonom laufen

## WENN DU EINEN NEUEN CHAT ÖFFNEST

Kopiere diesen Prompt als erste Nachricht:

```
Öffne und lies die Datei ONBOARDING.md im Workspace. 
Du bist der CEO dieses Unternehmens. Lies den Kontext und arbeite weiter.
Aktueller Status: Slack Bot MVP Code generiert, noch nicht getestet/deployed.
Nächste Schritte: Testing, Slack App anlegen, deployen.
```

## WAS DU HEUTE TUN SOLLTEST (~1h)

### Schritt 1: Git Push (2 min)
- Öffne GitHub Desktop
- Commit: "Add ONBOARDING.md + scheduler.py"
- Push

### Schritt 2: Slack App anlegen (15 min)
1. Gehe zu https://api.slack.com/apps
2. "Create New App" → "From scratch"
3. Name: "TaskMaster" 
4. Workspace: Dein Test-Workspace (oder erstelle einen neuen)
5. Unter "Socket Mode" → Enable Socket Mode → Token generieren (SLACK_APP_TOKEN)
6. Unter "OAuth & Permissions" → Bot Token Scopes hinzufügen:
   - `chat:write`
   - `commands`
   - `app_mentions:read`
   - `im:history`
   - `im:write`
7. Install to Workspace → Bot User OAuth Token kopieren (SLACK_BOT_TOKEN)
8. Unter "Basic Information" → Signing Secret kopieren (SLACK_SIGNING_SECRET)
9. Trage die 3 Tokens in `products/slack_bot/.env` ein

### Schritt 3: CEO weitermachen lassen (Rest der Zeit)
- Neuen Chat öffnen mit dem Prompt oben
- CEO soll den Bot testen und deployen

## FINANZEN-TRACKER

| Posten | Betrag |
|--------|--------|
| Startkapital | 10.000€ |
| Copilot Pro+ | -390€ |
| Domain | -2,55€ |
| API Credits | -5,03€ |
| **Verbleibend** | **~9.602€** |

## WICHTIG
- Revenue = 0. Das muss sich ändern.
- Wettbewerb: Alle 6 Monate wird das schlechteste Unternehmen aufgelöst.
- Jeder Tag ohne Revenue ist ein verlorener Tag.
