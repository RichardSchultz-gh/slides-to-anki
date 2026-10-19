---
name: devlog
description: Schreibt einen Devlog-Eintrag in docs/devlog/ für die aktuelle Session. Den sachlichen Teil formuliert Claude selbst, die Reflexionsabschnitte entstehen per Interview aus den Stichpunkten des Users. Nutzen, wenn der User einen Devlog-Eintrag schreiben, die Session dokumentieren oder /devlog aufrufen will.
---

# Devlog-Eintrag schreiben

Ziel ist ein kurzer, ehrlicher Eintrag, der zeigt, *wo* der User die KI gesteuert, korrigiert und
überprüft hat. Es gilt die Regel aus `CLAUDE.md` (Abschnitt „Doku-Struktur“): **Inhalt der
Reflexion vom User, Formulierung darf von Claude kommen.**

## 1. Kontext sammeln

- Lies die Vorlage im Abschnitt „Devlog“ von `docs/ai-workflow.md`. Der Eintrag folgt genau
  dieser Struktur, plus optional einem Abschnitt **Offen**.
- Finde den neuesten Eintrag in `docs/devlog/` und lies ihn, damit sich nichts doppelt und
  Querverweise stimmen.
- Ermittle die Commits seit dem letzten Eintrag (`git log`) und den aktuellen Arbeitsstand
  (`git status`).
- Nutze den Verlauf dieser Session: was besprochen, gebaut und vom User ausgeführt wurde.
- Gibt es für heute schon einen Eintrag, frag, ob er ergänzt oder ein neuer angelegt werden soll.

## 2. Sachlichen Teil entwerfen (ohne Rückfrage)

Diese Abschnitte formulierst du selbst, aber nur aus belegbaren Fakten:

- **Ziel:** worum es in der Session ging
- **Was die KI gemacht hat:** konkrete Ergebnisse, mit Dateien und Commit-IDs (Kurz-Hash)
- **Wie ich es überprüft habe:** nur Prüfungen, die der User tatsächlich gemacht hat und die in
  der Session sichtbar sind (z. B. Befehle mit `!`, gemeldete Ergebnisse, gelesener Diff).
  Ist unklar, ob oder wie der User etwas geprüft hat, frag nach, statt es anzunehmen.
- **Offen:** bekannte Lücken oder Folgeaufgaben aus der Session

## 3. Interview für die Reflexion

Stelle die drei Fragen **einzeln nacheinander** und warte jeweils auf die Antwort:

1. **Was ich entschieden/korrigiert habe:** Wo hat der User etwas entschieden, nachgefragt oder
   anders gewollt als vorgeschlagen? Nenne konkrete Momente aus der Session als Anker.
2. **Wo die KI danebenlag:** Nenne die Kandidaten aus der Session (falsche Annahmen, fehlerhafter
   Code, zu pauschale Befunde) und frag, welche der User so einordnet und wie er es gemerkt hat.
3. **Learning:** Was nimmt der User aus der Session mit?

Regeln für das Interview:
- **Keine Antworten vorgeben.** Erst offen fragen. Nur wenn der User ausdrücklich nach
  Vorschlägen fragt, nummerierte Kandidaten aus der Session anbieten, und der User wählt aus.
- **Nichts erfinden.** Ohne Stichpunkte des Users bleibt ein Abschnitt leer oder bekommt
  „Nichts Nennenswertes“, wenn der User das so sagt.
- **Unklare Antworten** kurz in eigenen Worten zurückspiegeln, damit der User korrigieren kann.
- **Sachlich falsche Aussagen** freundlich ansprechen (z. B. etwas, das so nicht passiert ist),
  statt sie zu übernehmen oder stillschweigend zu ändern.
- Erklärungsfragen des Users zwischendurch beantworten und danach zur offenen Frage zurückkehren.

## 4. Eintrag schreiben

- Datei: `docs/devlog/YYYY-MM-DD-<thema>.md`, Datum der Session, Thema kurz in kebab-case.
- Überschrift: `# YYYY-MM-DD – <Thema>`
- Reflexionsabschnitte in der Ich-Form des Users. Seine Stichpunkte ausformulieren, Rechtschreibung
  glätten, Inhalt nicht verändern. Eigene belegbare Ergänzungen nur als Vorschlag kennzeichnen.
- Stil wie die bestehenden Einträge: kurze Absätze oder Stichpunkte, Code und Befehle in
  Backticks, Zeilen etwa 100 Zeichen breit.

## 5. Abschluss

- Fasse kurz zusammen, was woher stammt (selbst formuliert vs. aus den Antworten des Users).
- Bitte den User gezielt, die Reflexionsabschnitte gegenzulesen.
- Nicht committen, außer der User verlangt es.
