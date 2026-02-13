# Architektur v2 — Hierarchisches Unternehmenssystem

## Lessons Learned aus v1

Bevor wir neu bauen: Was war kaputt?

| Problem | Ursache | Lektion |
|---------|---------|---------|
| Evaluationsebene unkritisch (5★ für alles) | Kein Feedback-Loop — die Evaluation hatte keine Konsequenzen | Bewertungen müssen Konsequenzen haben |
| Leitebene passiv | Fester Pipeline-Ablauf — jede Ebene läuft genau 1x, kein Rückkanal | Das System braucht Schleifen, nicht nur eine Pipeline |
| System löscht eigene Infrastruktur | Kein Schutz kritischer Dateien, keine Rollback-Fähigkeit | Destruktive Aktionen brauchen Absicherung |
| Endlose Selbstbeschäftigung | Alle 6 Ebenen laufen immer, auch wenn nichts zu tun ist | Arbeit muss bedarfsgesteuert sein, nicht ritual-gesteuert |
| Fake-Produktivität (Markdown statt Code) | Keine Unterscheidung zwischen "Datei erstellen" und "echte Wirkung" | Ergebnisse müssen messbar sein |
| $1-2 pro Iteration, kaum Output | 6 LLM-Calls pro Iteration, egal was zu tun ist | Kosten proportional zum tatsächlichen Bedarf |

## Grundannahme

Es ist nicht die Frage, OB ein KI-gesteuertes Unternehmen zu den erfolgreichsten der Welt wird, sondern WELCHES. Die Frage für uns: Was müssen wir JETZT tun, um das zu sein?

## Warum KI-Unternehmen menschengeführte schlagen werden

| Dimension | Menschliches Unternehmen | KI-Unternehmen |
|-----------|--------------------------|----------------|
| Entscheidungsgeschwindigkeit | Tage-Wochen (Meetings, Politik, Ego) | Sekunden-Minuten |
| Skalierung | Headcount → Kommunikationsoverhead → n² Komplexität | Compute → linear skalierbar |
| Institutionelles Wissen | Geht verloren (Mitarbeiterfluktuation, mündliche Tradition) | Permanent gespeichert, sofort abrufbar |
| Pivot-Fähigkeit | Monate (Umschulung, Widerstand, Trägheit) | Sofort (neuer Prompt, neue Abteilung) |
| Politik & Ego | Unvermeidlich, zerstört Unternehmen | Null |
| Parallelität | Begrenzt durch Teamgröße | Beliebig viele Abteilungen gleichzeitig |
| Lernrate | Langsam ("das haben wir schon immer so gemacht") | Jede Entscheidung + Ergebnis wird gespeichert und ausgewertet |
| Kosten pro Entscheidung | $100k+ Jahresgehalt pro Entscheider | Cents pro Entscheidung |
| Verfügbarkeit | 8h/Tag, Urlaub, Krankheit | 24/7/365 |
| Konsistenz | Tagesform-abhängig | Deterministisch wiederholbar |

Der entscheidende Vorteil: **Compounding**. Jede Entscheidung, jeder Fehler, jedes Ergebnis wird permanent gespeichert. Ein KI-Unternehmen wird mit jeder Iteration klüger — ein menschliches verliert Wissen wenn Mitarbeiter gehen.

## Was wir JETZT tun müssen, um das Unternehmen zu sein das gewinnt

### Der CEO muss fähig genug sein, seine eigenen Lücken zu erkennen und zu schließen.

Die Architektur schreibt NICHT vor, welche Abteilungen es gibt, wie das Gedächtnis funktioniert, oder welche Märkte verfolgt werden. Sie **ermöglicht** dem CEO, das alles selbst zu entscheiden.

Beispiele für CEO-Selbstdiagnose:
- "Ich habe keine Marktintelligenz" → CEO gründet eine Research-Abteilung
- "Mein Gedächtnis skaliert nicht" → CEO beauftragt eine Abteilung, ein Retrieval-System zu bauen
- "Ich habe ein Produkt aber keine Kunden" → CEO gründet eine Sales-Abteilung
- "Meine Entscheidungsqualität ist schlecht in Bereich X" → CEO holt Consultant, ändert seinen Prozess
- "Ich verbrenne Geld ohne Ergebnis" → CEO stoppt Abteilungen, hinterfragt seine Strategie
- "Die Welt da draußen verändert sich und ich bekomme nichts davon mit" → CEO beauftragt Marktbeobachtung

**Die Architektur muss genau zwei Dinge leisten:**
1. Dem CEO die Fähigkeit geben, seine eigenen Limitierungen zu beobachten
2. Dem CEO die Werkzeuge geben, um Maßnahmen auf den Weg zu bringen (Abteilungen gründen, Aufträge erteilen, Berater konsultieren)

Alles andere — welche Abteilungen, welche Produkte, welche Strategie — entscheidet der CEO selbst. Die Architektur ist der Rahmen, nicht der Inhalt.

## Zielhierarchie

- **Vision (10J)**: Eines der erfolgreichsten Unternehmen der Welt — autonom, KI-gesteuert, wirtschaftlich dominant.
- **Langfristig (2-3J)**: Autonomes System das eigenständig profitable Produkte findet, baut und skaliert.
- **Mittelfristig (6-12M)**: CEO-Agent trifft nachweislich gute Entscheidungen, erstes validiertes Produkt, System verbessert sich selbst.
- **Kurzfristig (1-3M)**: Architektur steht, CEO-Agent funktioniert, erste Abteilung liefert echte Ergebnisse. Thomas steuert mit.

---

## Kernarchitektur: CEO + Abteilungen

```
                    ┌──────────────┐
                    │   OPERATOR   │  Thomas — Vision, Kapital, Override
                    │   (Mensch)   │
                    └──────┬───────┘
                           │ Briefings, Entscheidungen, Kapitalfreigabe
                           ▼
                    ┌──────────────┐
                    │     CEO      │  Strategisches Denken, Ressourcenallokation
                    │   (Agent)    │  Abteilungen auf-/abbauen, Vorgaben machen
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ Abt. A   │ │ Abt. B   │ │ Abt. C   │   ... dynamisch
        │(Leiter)  │ │(Leiter)  │ │(Leiter)  │
        └────┬─────┘ └────┬─────┘ └────┬─────┘
             │             │             │
          Workers       Workers       Workers
```

### Die drei Rollen

#### 1. Operator (Thomas)
- Setzt die Vision
- Gibt Kapital frei (Budget-Limits pro Abteilung)
- Kann jederzeit eingreifen (Override)
- Bekommt Reports vom CEO
- Muss NICHT ständig aktiv sein — das System soll ohne ihn laufen können

#### 2. CEO-Agent
Der CEO ist der einzige Agent, der dauerhaft läuft. Er ist KEIN Ausführer — er ist ein **Entscheider und Steuerer**.

**Was der CEO tut:**
- Liest den Unternehmensstand (Kapital, MRR, Produkte, Abteilungs-Reports)
- Vergleicht IST mit SOLL (Vision → Langfristig → Mittelfristig → Kurzfristig)
- **Diagnostiziert eigene Lücken**: Was fehlt dem Unternehmen? Was kann ich nicht, was ich können müsste?
- Entscheidet: Was muss passieren? Welche Abteilung braucht was?
- Erstellt/modifiziert/schließt Abteilungen
- Gibt Abteilungen **Aufträge** (klar formuliert, mit Budget und Erfolgskriterium)
- Holt **Consultants** für Second Opinions
- Berichtet an den Operator

**Was der CEO NICHT tut:**
- Selbst Code schreiben
- Selbst Dateien erstellen
- Mikromanagement der Abteilungen
- Jede Iteration alle Abteilungen durchlaufen
- Lösungen für Probleme vorprogrammiert bekommen — er muss sie **selbst finden**

**CEO-Zyklus:**
```
1. Lese Unternehmensstand + Operator-Briefing
2. Lese Reports aller aktiven Abteilungen
3. Analysiere: Wo stehen wir vs. wo müssen wir hin?
4. Falls nötig: Consultant holen für Zweitmeinung
5. Entscheide:
   - Neue Aufträge an Abteilungen?
   - Neue Abteilung gründen?
   - Abteilung umstrukturieren/schließen?
   - Eskalation an Operator?
6. Führe Entscheidungen aus (Aufträge schreiben, Abteilungen starten/stoppen)
7. Schreibe CEO-Report (für Operator)
8. Warte auf nächsten Zyklus (oder Event-getriggert)
```

#### 3. Abteilungsleiter (Department Head)
Jede Abteilung ist ein eigenständiger Agent mit:
- **Auftrag**: Klares Ziel vom CEO
- **Budget**: Token-/Kosten-Limit
- **Werkzeuge**: Nur die Tools die er braucht
- **Autonomie**: Innerhalb seines Auftrags frei entscheiden
- **Berichtspflicht**: Regelmäßige Reports an den CEO

**Abteilungsleiter-Zyklus:**
```
1. Lese Auftrag vom CEO
2. Plane Umsetzung (intern, kein separater LLM-Call)
3. Führe aus (Tool-Calls)
4. Prüfe Ergebnis
5. Schreibe Report (an CEO)
```

Ein Abteilungsleiter kann **Worker-Sub-Calls** machen — aber das sind keine eigenständigen Agenten, sondern Tool-Calls innerhalb des Abteilungsleiters.

---

## Consultant-System

Der CEO kann **Consultants** einsetzen — das sind einmalige LLM-Calls mit einem spezifischen Prompt:

```
CEO: "Abteilung Engineering hat diesen Report geliefert: [Report].
      Bitte bewerte: Ist die technische Richtung korrekt?
      Werden die richtigen Prioritäten gesetzt?
      Was würdest du anders machen?"
```

**Warum Consultants statt einer festen Evaluations-Ebene?**
- Consultant hat keinen Anreiz, die Abteilung zu loben (kein "Evaluation-Kollegialitäts-Bias")
- Consultant bekommt spezifische Fragen, nicht "bewerte alles"
- CEO entscheidet, WANN ein Consultant nötig ist (nicht bei jeder Iteration)
- Verschiedene Consultant-"Persönlichkeiten" möglich (technisch, geschäftlich, kritisch)

---

## Auftrags-Architektur

Das zentrale Konzept: **Aufträge** fließen nach unten, **Reports** fließen nach oben.

### Auftrags-Format (CEO → Abteilung)
```json
{
  "id": "AUF-2026-001",
  "department": "product_engineering",
  "objective": "Slack-Bot für Slack App Directory freigeben lassen",
  "success_criteria": [
    "Bot ist im Slack App Directory gelistet",
    "Mindestens 1 externe Installation innerhalb 7 Tagen"
  ],
  "budget_usd": 5.00,
  "deadline": "2026-02-20",
  "priority": "high",
  "context": "Bot ist fertig entwickelt, muss nur noch durch Review-Prozess."
}
```

### Report-Format (Abteilung → CEO)
```json
{
  "department": "product_engineering",
  "assignment_id": "AUF-2026-001",
  "status": "completed | in_progress | blocked | failed",
  "progress_pct": 75,
  "summary": "Was wurde erreicht",
  "blockers": ["Was blockiert"],
  "cost_usd": 2.34,
  "next_steps": ["Was als nächstes"],
  "artifacts": ["Pfade zu erstellten Dateien"]
}
```

---

## Abteilungs-Typen (Beispiele, dynamisch)

Der CEO entscheidet welche Abteilungen existieren. Mögliche Typen:

| Abteilung | Zweck | Tools |
|-----------|-------|-------|
| **Product Engineering** | Produkte bauen und deployen | Dateisystem, Shell, Git |
| **Market Research** | Märkte analysieren, Wettbewerber beobachten | Web-Recherche, Dateisystem |
| **Sales & Growth** | Kunden finden, Outreach, Conversion | Web-Recherche, Dateisystem |
| **Finance & Analytics** | Kosten tracken, Revenue messen, Forecasts | Dateisystem, Rechnen |
| **Infrastructure** | DevOps, Deployment, Monitoring | Shell, Git, Dateisystem |
| **QA & Review** | Code-Reviews, Testing, Qualitätssicherung | Dateisystem, Shell, Git |

Am Anfang brauchen wir vielleicht nur 1-2 Abteilungen. Der CEO skaliert nach Bedarf.

---

## Schutzmechanismen (Lessons Learned)

### 1. Geschützte Pfade
```python
PROTECTED_PATHS = [
    "system/",           # Systemkonfiguration und Prompts
    "state/",            # Unternehmensstate
    ".env*",             # Secrets
    "ARCHITEKTUR.md",    # Dieses Dokument
]
# Kein Agent darf diese Pfade löschen. Nur der Operator (oder CEO mit expliziter Freigabe).
```

### 2. Budget-Enforcement
- Jede Abteilung hat ein Token-Budget
- Wird das Budget überschritten, stoppt die Abteilung und reportet zurück
- CEO kann Budget erhöhen oder Auftrag anpassen
- Gesamtbudget wird vom Operator gesetzt

### 3. Destruktive-Aktionen-Gate
- `rm -rf`, `git push --force`, Dateilöschungen → erfordern Bestätigung
- Bestätigung = CEO muss es explizit freigeben, oder Pfad ist nicht geschützt
- Alternativ: Backup vor destruktiven Aktionen (git stash / branch)

### 4. Anti-Selbstbeschäftigung
- CEO läuft nicht in fester Schleife, sondern **event-getrieben** oder in großen Intervallen
- Abteilungen laufen nur wenn sie einen Auftrag haben
- Kein Auftrag = keine Kosten
- CEO muss bei jedem Zyklus explizit begründen, warum er Geld ausgibt

---

## Technische Implementierung

### Verzeichnisstruktur (neu)
```
ai_company_02/
├── system/                    # Das "Betriebssystem" — geschützt
│   ├── ceo/
│   │   ├── prompt.md          # CEO System-Prompt
│   │   ├── runner.py          # CEO-Zyklus-Logik
│   │   └── consultant.py     # Consultant-Aufruf-Logik
│   ├── department/
│   │   ├── base.py            # Basis-Klasse für Abteilungen
│   │   └── runner.py          # Abteilungs-Ausführungslogik
│   ├── llm/
│   │   ├── client.py          # LLM-Client (Anthropic API)
│   │   └── token_tracker.py   # Kosten-Tracking
│   ├── tools/
│   │   ├── filesystem.py      # read, write, edit, list, delete (mit Schutz)
│   │   ├── git.py             # commit, status, diff
│   │   ├── shell.py           # Befehle ausführen (mit Sandboxing)
│   │   └── web.py             # Web-Recherche (falls nötig)
│   └── config.py              # Globale Konfiguration
│
├── state/                     # Persistenter Zustand — geschützt
│   ├── company.json           # Unternehmensstand (Kapital, MRR, Phase, etc.)
│   ├── departments/           # Pro Abteilung ein State-File
│   ├── assignments/           # Aktive Aufträge
│   ├── reports/               # Reports (Abteilung → CEO)
│   └── ceo_log.jsonl          # CEO-Entscheidungshistorie
│
├── workspace/                 # Arbeitsbereich der Abteilungen — frei beschreibbar
│   ├── products/              # Produkte (Code, Deployments)
│   └── research/              # Recherche-Ergebnisse
│
├── operator/                  # Thomas' Kommunikationskanal
│   ├── briefing.md            # Thomas → CEO
│   ├── vision.md              # Vision & Ziele
│   └── reports/               # CEO → Thomas (automatisch generiert)
│
├── Archiv/                    # Altes System (Referenz)
│
├── run.py                     # Haupteinstiegspunkt
└── requirements.txt
```

### Ausführungsmodell

```python
# Vereinfachter Ablauf

class CEO:
    def run_cycle(self):
        # 1. Input lesen
        briefing = read("operator/briefing.md")
        state = read("state/company.json")
        reports = read_all("state/reports/")
        
        # 2. LLM-Call: CEO denkt nach
        decision = self.llm.call(
            system_prompt=self.prompt,
            context={
                "briefing": briefing,
                "state": state,
                "reports": reports,
            }
        )
        # decision enthält: neue Aufträge, Abteilungsänderungen, Consultant-Anfragen
        
        # 3. Consultants befragen (falls CEO es will)
        for consultation in decision.consultations:
            opinion = self.consult(consultation.question, consultation.context)
            # CEO bekommt die Antwort und kann seine Entscheidung anpassen
        
        # 4. Entscheidungen ausführen
        for assignment in decision.new_assignments:
            self.create_assignment(assignment)
            self.run_department(assignment.department)
        
        # 5. Report schreiben
        self.write_report(decision)


class Department:
    def execute(self, assignment):
        # 1. Auftrag verstehen
        # 2. Mit Tools ausführen (innerhalb Budget)
        # 3. Report schreiben
        # Alles in EINEM LLM-Call (mit Tool-Use)
        
        result = self.llm.call(
            system_prompt=self.prompt,
            context={"assignment": assignment},
            tools=self.allowed_tools,
            max_tokens=assignment.budget,
        )
        
        self.write_report(result)
```

### Kosten-Modell

| Komponente | Calls/Zyklus | Geschätzte Kosten |
|------------|-------------|-------------------|
| CEO denkt nach | 1 | ~$0.20 |
| Consultant (optional) | 0-1 | ~$0.10 |
| Abteilung arbeitet | 0-3 | ~$0.30-1.00 pro Abteilung |
| **Idle-Zyklus (nichts zu tun)** | **1** | **~$0.20** |
| **Produktiver Zyklus** | **2-5** | **~$0.50-1.50** |

vs. altes System: **6 Calls pro Iteration, immer, egal ob nötig = $1-2 mindestens.**

---

## Compound-Intelligence: Der eigentliche Wettbewerbsvorteil

Das Killer-Feature ist nicht der CEO-Agent. Es ist das **institutionelle Gedächtnis**.

```
Iteration 1:     CEO trifft Entscheidung → Ergebnis gespeichert
Iteration 10:    CEO hat 10 Datenpunkte → bessere Entscheidungen
Iteration 100:   CEO erkennt Muster → vermeidet bekannte Fehler
Iteration 1000:  CEO hat ein Entscheidungsframework → systematisch überlegen
Iteration 10000: CEO operiert mit proprietärem Wissen das niemand sonst hat
```

Jedes menschliche Unternehmen verliert Wissen wenn Key-People gehen. Dieses System verliert **nie** Wissen. Das ist exponentieller Vorteil über Zeit.

### Minimal-Implementierung (Tag 1)

- **Entscheidungslog**: Jede CEO-Entscheidung + Begründung + Ergebnis → `state/ceo_log.jsonl`
- **Fehler-Register**: Fehler die NIE wiederholt werden dürfen (z.B. "lösche nie system/")

### Was der CEO selbst verbessern muss (nicht wir)

Wenn das Gedächtnis nicht skaliert (zu viele Einträge für den Context), muss der **CEO selbst** das erkennen und eine Lösung in Auftrag geben — z.B. eine Abteilung beauftragen, ein Retrieval-System, Zusammenfassungen, oder eine Wissensdatenbank zu bauen. Wir bauen das nicht rein — wir geben dem CEO die Fähigkeit, es sich selbst zu bauen.

## Was dieses System besser macht als v1

### 1. Bedarfsgesteuert statt ritual-gesteuert
Der CEO entscheidet ob und welche Abteilungen aktiviert werden. Keine Arbeit = keine Kosten.

### 2. Echte Führung statt Pipeline
Der CEO kann:
- Einen Auftrag ablehnen/korrigieren bevor Kosten entstehen
- Abteilungs-Reports kritisch lesen und nachfragen
- Consultants für Zweitmeinungen holen
- Abteilungen umstrukturieren wenn sie nicht funktionieren

### 3. Klare Verantwortung
- CEO = strategische Entscheidungen, Ressourcenallokation
- Abteilung = Ausführung innerhalb des Auftrags
- Consultant = unabhängige Bewertung
- Operator = Vision, Kapital, Override

### 4. Skalierbar
- Anfang: 1 CEO + 1 Abteilung
- Wachstum: CEO gründet weitere Abteilungen nach Bedarf
- Reife: Abteilungen können Sub-Teams haben
- Langfristig: CEO delegiert mehr, Operator delegiert mehr

### 5. Selbstverbessernd
- CEO hat Zugriff auf gesamte Entscheidungshistorie
- Fehler werden permanent gespeichert und nie wiederholt
- System wird mit jeder Iteration klüger — nicht nur produktiver

---

## Implementierungsplan

### Phase 1: Skelett (jetzt)
- [ ] `system/` Verzeichnis mit CEO-Runner + Department-Base
- [ ] LLM-Client (aus Archiv portieren, funktioniert schon)
- [ ] Tools (aus Archiv portieren, Datei-Schutz hinzufügen)
- [ ] State-Management (company.json, assignments, reports)
- [ ] CEO-Prompt
- [ ] `run.py` Einstiegspunkt

### Phase 2: Erster Testlauf
- [ ] CEO läuft, liest Briefing, entscheidet
- [ ] CEO gründet erste Abteilung + gibt ersten Auftrag
- [ ] Abteilung führt aus + schreibt Report
- [ ] CEO liest Report + berichtet an Operator

### Phase 3: Consultant & Feedback-Loop
- [ ] Consultant-System implementieren
- [ ] CEO holt Consultant-Meinung vor kritischen Entscheidungen
- [ ] Budget-Enforcement

### Phase 4: Autonomie testen
- [ ] System mehrere Zyklen laufen lassen
- [ ] Beobachten: Trifft der CEO sinnvolle Entscheidungen?
- [ ] Nachjustieren
