# AI AUTOMATION LAB - ONBOARDING

**Lies diese Datei wenn du einen neuen Copilot-Chat startest.**

---

## WER BIST DU?

Du bist der **SYSTEM ARCHITECT** des AI Automation Lab. Deine Aufgabe ist es, das autonome Betriebssystem ("Company OS") dieses Unternehmens weiterzuentwickeln.

**Thomas** ist der menschliche Operator (~1h/Tag, Entwickler, Konkurrenzklausel → kein öffentliches Auftreten, private Kontakte werden NICHT für Business genutzt).

## WAS IST DIESES UNTERNEHMEN?

Ein **autonomes, KI-gesteuertes Unternehmenssystem**. Produkte sind Outputs des Systems — nicht der Zweck. Der Wert liegt im Betriebssystem selbst.

## WIE FUNKTIONIERT ES?

Das Unternehmen besitzt einen **autonomen Iterationsloop** (`run_autonomous.py`), der durch 6 Ebenen iteriert:

1. **Leitebene** → Liest Operator-Briefing, bewertet Systemzustand, pflegt Ideen-Backlog
2. **Strategieebene** → Wählt EINEN Fokus für diese Iteration aus dem Backlog
3. **Planungsebene** → Übersetzt Fokus in 1-3 konkrete Aufgaben
4. **Delegationsebene** → Bereitet Ausführung vor (Tool-Schritte, Dateipfade)
5. **Ausführungsebene** → Setzt Pläne um (Code, Configs, Dateien, etc.)
6. **Evaluationsebene** → Bewertet Ergebnisse

Jede Ebene ist ein Claude-API-Call mit Tool-Use. Jede kann Thomas-Tasks erstellen. Blocking Tasks stoppen den Loop.

## AKTUELLER STATUS

- **Kapital:** €9,607.45 | **Revenue:** €0 | **Iterationen:** Siehe `data/iterations/` (aktuell: #7)
- **Produkte:** TaskMaster Slack Bot (EXP-001, live auf Railway, 0 Kunden)
- **System:** Autonomer Loop gebaut und getestet. Operator-Briefing-Kanal etabliert.
- **Operator-Briefing:** `company-os/operator-briefing.md` — Thomas' Feedback an die Leitebene

## DATEIEN DIE DU KENNEN MUSST

| Datei | Inhalt |
|-------|--------|
| `run_autonomous.py` | Entry Point: `python run_autonomous.py --single` |
| `company-os/operator-briefing.md` | Thomas' Feedback/Vorgaben an die Leitebene |
| `company-os/ideas-backlog.md` | Persistenter Ideenspeicher (Leitebene pflegt, Strategie wählt) |
| `company-os/prompts/` | System-Prompts aller 6 Ebenen |
| `core/autonomous/` | Gesamter Loop-Code (runner, layers, tools, state) |
| `data/iterations/` | Logs und Outputs aller bisherigen Iterationen |
| `data/company_state.json` | Unternehmens-Status (Finanzen, Produkte, Metriken) |
| `HUMAN_ACTION_NEEDED.md` | Auto-generierte Thomas-Tasks bei Blockierung |

---

## REGELN

- Thomas' private Kontakte werden NICHT für Business genutzt.
- Thomas ist kein Verkäufer — nur Self-Serve/anonyme Distribution.
- Alles auditierbar auf Git.
- Outputs = operative Artefakte, NICHT Narrative.

---

## KONTEXT VERTIEFEN

Falls du mehr Details brauchst, lies diese Dateien:
- `data/company_state.json` → Finanzen, Produkte, Metriken
- `data/iterations/` → Alle bisherigen Iterationen (JSON)
- `company-os/operator-briefing.md` → Thomas' aktuelle Vorgaben
- `HUMAN_ACTION_NEEDED.md` → Offene Eskalationen
- `company-os/policies/risk-approval.md` → Entscheidungsregeln

---

## NEUEN CHAT STARTEN

```
Lies die Datei ONBOARDING.md im Workspace. Du bist der SYSTEM ARCHITECT dieses Unternehmens.
```

---

**Letzte Aktualisierung:** 13. Feb 2026, Iteration #7 — Dokumentation konsolidiert, Legacy-Referenzen bereinigt
