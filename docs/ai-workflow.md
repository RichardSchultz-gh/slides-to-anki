# AI-assisted Entwicklung

Dieses Projekt entsteht mit [Claude Code](https://claude.com/claude-code) als Programmier-Assistent.
Dieses Dokument beschreibt, **wie** dabei gearbeitet wird: welche Entscheidungen bei mir liegen,
welche Aufgaben die KI übernimmt und wie die Ergebnisse überprüft werden.

## Werkzeuge

- **Claude Code** (CLI) als Coding-Assistent
- **[`CLAUDE.md`](../CLAUDE.md)**: Projektkontext für die KI mit Architektur, Konventionen und
  Entscheidungen samt Begründung. Claude liest die Datei in jeder Session, dadurch bleiben die
  Vorgaben über Sessions hinweg konsistent.
- **Skills** (wiederverwendbare Anleitungen für Claude Code):
  - `write-a-prd`: aus einer Feature-Idee ein PRD erstellen (`prd/`)
  - `prd-to-issues`: ein PRD in einzeln umsetzbare Issues zerlegen (`issues/`)
  - `tdd`: Umsetzung nach Red-Green-Refactor
  - `grill-me`: einen Plan kritisch hinterfragen lassen, bevor er umgesetzt wird

## Ablauf

1. **Idee → PRD**: Größere Features werden zuerst als PRD in `prd/` beschrieben. Ziel, Umfang
   und Abgrenzung lege ich fest.
2. **PRD → Issues**: Das PRD wird in kleine, unabhängig umsetzbare Issues in `issues/` zerlegt.
3. **Plan, dann Umsetzung**: Pro Session wird ein Issue bearbeitet. Zuerst legt Claude einen Plan
   vor, den ich freigebe oder korrigiere. Danach folgt die Umsetzung je nach Delegationsstufe
   (siehe unten), wo sinnvoll test-first.
4. **Review durch mich**: Ich lese den Diff, lasse die Tests laufen und prüfe das Feature
   manuell. Wenn nötig, korrigiere ich selbst oder gebe der KI konkretes Feedback.
5. **Commit**: Kleine Commits, deren Message das „Warum“ erklärt. KI-Beteiligung wird über den
   `Co-Authored-By`-Trailer offen gekennzeichnet.
6. **Devlog**: Nach der Session schreibe ich einen kurzen Eintrag in `docs/devlog/` (siehe unten).

## Meine Regeln

<!-- TODO: selbst ausfüllen. Beispiele zur Orientierung:
- Architektur- und Technologieentscheidungen treffe ich; die KI darf Vorschläge machen.
- Kein Commit von Code, den ich nicht gelesen und verstanden habe.
- Kein Merge ohne grüne Tests.
- Was ich bewusst nicht an die KI abgebe, und warum: …
-->

## Arbeitsteilung

| Bereich | Ich | KI |
|---|---|---|
| Ziele, Scope, Priorisierung | entscheide | stellt Rückfragen, hinterfragt |
| Architektur & Stack | entscheide | schlägt Optionen vor, bewertet Trade-offs |
| Implementierung | je nach Stufe (siehe unten) | je nach Stufe (siehe unten) |
| Tests | formuliere Testfälle, prüfe Aussagekraft | schreibt Tests aus |
| Dokumentation | Inhalt von Reflexion und Entscheidungen, Gegenlesen | Gerüste, sachliche Zusammenfassungen, Formulierung aus meinen Stichpunkten |

## Delegationsstufen

Leitprinzip: Ich muss jede Zeile im Projekt erklären können. Wie viel ich an die KI abgebe,
entscheide ich deshalb pro Bereich.

**Stufe 1: komplett an die KI.** Das sind Teile ohne eigenen Lern- oder Gesprächswert.
- Konfiguration, Docker, Projekt-Setup
- Alembic-Migrationen nach vorgegebenem Modell
- Grundgerüste für Styling und Layout
- Test-Fixtures, Seed-Daten
- Prompt-Pipeline für die Karten-Generierung (bewusst simpel gehalten, siehe `CLAUDE.md`)

**Stufe 2: ich entwerfe, die KI setzt um, ich reviewe gründlich.** Das betrifft den Großteil der
Web-Arbeit.
- REST-Endpunkte, DB-Modell, Fehlerbehandlung
- React-Komponenten, Review-UI, Bulk-Actions
- Suche, Filter, Pagination

Endpunkte, Datenmodell und Komponentenstruktur lege ich vorher fest; die KI füllt sie aus.

**Stufe 3: ich schreibe selbst, die KI erklärt und reviewt.** Das sind die Kernstücke, die ich im
Projekt zeigen will.
- Google-Drive-Webhook, OAuth-Flow und Fehlerbehandlung
- Queue-Job und SSE-Live-Status
- Spaced-Repetition-Algorithmus
- Eval-Matching und Coverage-Berechnung

Hier lasse ich mir zuerst das Konzept erklären, implementiere selbst und lasse die KI danach
reviewen. Die KI dient hier als Tutor, nicht als Autor.

## Devlog

Pro Session oder Meilenstein gibt es einen kurzen Eintrag unter
`docs/devlog/YYYY-MM-DD-<thema>.md`. Er wird direkt nach der Session geschrieben und kostet etwa
10–15 Minuten. Den sachlichen Teil darf Claude vorformulieren.

Für die Abschnitte zu Entscheidungen, Fehlern der KI und Learnings gilt: **Der Inhalt kommt von
mir, die Formulierung darf von Claude kommen.**
1. Ich schreibe Stichpunkte, schnell und unformuliert.
2. Claude formuliert daraus den Text. Eigene Ergänzungen schlägt Claude nur vor, wenn sie belegbar
   sind (z. B. Testergebnisse), und kennzeichnet sie als Vorschlag.
3. Ich lese gegen und streiche, was nicht stimmt oder nicht meins ist.

Claude erfindet keine Reflexionen ohne meine Stichpunkte. Nur ich weiß, was ich tatsächlich
entschieden und gelernt habe, und muss es im Gespräch aus eigener Erinnerung erzählen können.
Die KI als Schreibhilfe zu nutzen, passt dagegen zum Projekt, solange es offen dokumentiert ist.

Vorlage:

```markdown
# YYYY-MM-DD – <Thema/Meilenstein>

**Ziel:** …
**Was die KI gemacht hat:** …
**Was ich entschieden/korrigiert habe:** …
**Wo die KI danebenlag:** …
**Wie ich es überprüft habe:** Tests, manueller Check, …
**Learning:** …
```

## Was bewusst nicht dokumentiert wird

- **Vollständige Chat-Transkripte**: zu lang, und der eigene Anteil ginge darin unter.
- **Rückblickende Gesamtdarstellungen**: Laufende Einträge sind genauer und glaubwürdiger.
