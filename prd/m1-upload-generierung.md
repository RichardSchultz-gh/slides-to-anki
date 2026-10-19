# PRD: Meilenstein 1 – PDF-Upload, Karten-Generierung, Kartenliste

## Problem Statement

Ich lerne für mehrere Vorlesungen, deren Foliensätze als PDF vorliegen. Aus diesen Folien von Hand
Anki-Karten zu schreiben kostet pro Woche viel Zeit, und die Arbeit wiederholt sich: Viele
Foliensätze wachsen im Laufe des Semesters, weil der Dozent jede Woche neue Folien an dieselbe
Datei anhängt oder einzelne Folien korrigiert. Am Semesteranfang kommen dagegen manchmal komplette
Foliensätze mit 100 Seiten auf einmal.

Ein LLM kann Karten aus Folien generieren. Wenn man aber einfach das PDF in einen Chat kopiert,
bleiben drei Probleme:
- Inhalte in Diagrammen und Grafiken gehen verloren oder kosten unnötig viel, wenn jede Seite als
  Bild verarbeitet wird.
- Bei einem gewachsenen Foliensatz entstehen Duplikate zu bereits vorhandenen Karten, oder ich
  muss selbst heraussuchen, welche Seiten neu sind.
- Die Karten landen nicht an einem Ort, an dem ich sie durchsuchen, prüfen und später lernen kann.

Aktuell existiert nur das Projektgerüst (FastAPI mit Health-Endpoint, leeres Datenmodell,
Vite-Starter-Frontend). Es gibt noch keinen Weg, ein PDF in Karten zu verwandeln.

## Solution

Eine Web-App, in die ich ein PDF hochlade, entweder als neues Deck oder als Update zu einem
bestehenden Deck. Die Verarbeitung läuft als Hintergrund-Job:

1. Das PDF wird analysiert: Text pro Seite, ein Hash pro Seite und die Erkennung, ob eine Seite
   wesentliche Grafiken enthält.
2. Bei einem Update werden nur neue und geänderte Seiten verarbeitet. Karten zu geänderten oder
   entfernten Seiten bleiben erhalten und werden markiert.
3. Lange Foliensätze werden an Themengrenzen in Abschnitte geteilt (LLM-Vorschlag, validiert, mit
   festem Fallback). Kurze Wochenpakete gehen in einem Aufruf durch.
4. Pro Abschnitt erzeugt Claude Basic-Karten (Frage/Antwort in Markdown mit LaTeX) in der Sprache
   der Folien. Seiten mit wesentlichen Grafiken werden zusätzlich als Bild mitgeschickt.
5. Die Karten landen mit Quellseite im Status „zu prüfen“ in der Datenbank.

Im Frontend sehe ich die Liste meiner Decks, pro Deck die Karten (mit gerenderten Formeln und
Code) und den Verarbeitungsstatus. Schlagen einzelne Abschnitte fehl, bleibt der Rest erhalten,
und ich kann gezielt nur die fehlgeschlagenen Abschnitte wiederholen.

Das Ergebnis ist der erste demofähige Stand des Projekts. Spätere Meilensteine (Drive-Integration,
Review-UI, Lernmodus, Suche, Export) bauen auf diesem Datenmodell und Verarbeitungs-Job auf.

## User Stories

### Upload
1. Als Student möchte ich ein PDF über die Website hochladen, damit daraus automatisch Karten
   generiert werden.
2. Als Student möchte ich beim Upload wählen, ob das PDF ein neues Deck anlegt oder ein bestehendes
   Deck aktualisiert, damit wöchentlich gewachsene Foliensätze nicht als Duplikat-Deck enden.
3. Als Student möchte ich, dass beim Upload anhand des Dateinamens ein passendes bestehendes Deck
   vorgeschlagen wird, damit ich die Zuordnung nicht jedes Mal von Hand suchen muss.
4. Als Student möchte ich beim Anlegen eines neuen Decks einen Namen vergeben können, der
   standardmäßig aus dem Dateinamen abgeleitet wird, damit ich nicht immer tippen muss.
5. Als Student möchte ich eine sofortige, verständliche Fehlermeldung bekommen, wenn die Datei kein
   PDF ist, damit ich nicht auf einen fehlschlagenden Job warten muss.
6. Als Student möchte ich eine sofortige Fehlermeldung bekommen, wenn das PDF verschlüsselt oder
   beschädigt ist, damit ich weiß, dass ich eine andere Datei brauche.
7. Als Student möchte ich eine Fehlermeldung bekommen, wenn das PDF die maximale Dateigröße oder
   Seitenzahl überschreitet, damit ein versehentlich hochgeladenes Riesen-Skript keine hohen
   API-Kosten verursacht.
8. Als Student möchte ich, dass die Prüfung auf „echtes PDF“ am Dateiinhalt erfolgt und nicht an der
   Dateiendung, damit umbenannte Dateien zuverlässig abgelehnt werden.
9. Als Student möchte ich nach dem Upload sofort eine Rückmeldung bekommen, dass die Verarbeitung
   gestartet wurde, damit ich nicht auf die gesamte Generierung warten muss.
10. Als Student möchte ich, dass ein Upload ohne neue oder geänderte Seiten keinen LLM-Aufruf
    auslöst und mir das mitgeteilt wird, damit versehentlich doppelte Uploads nichts kosten.

### Inkrementelle Verarbeitung
11. Als Student möchte ich, dass bei einem Update nur neue Seiten verarbeitet werden, damit keine
    Duplikate zu bereits vorhandenen Karten entstehen.
12. Als Student möchte ich, dass neue Seiten auch dann erkannt werden, wenn der Dozent Folien in der
    Mitte eingefügt hat, damit die Erkennung nicht nur „alles ab Seite N“ abdeckt.
13. Als Student möchte ich, dass inhaltlich geänderte Seiten neu verarbeitet werden, damit
    Korrekturen des Dozenten in meinen Karten ankommen.
14. Als Student möchte ich, dass Karten zu geänderten Seiten erhalten bleiben und als „Quelle
    geändert“ markiert werden, damit ich bereits bearbeitete oder angenommene Karten nicht verliere.
15. Als Student möchte ich, dass Karten zu entfernten Seiten erhalten bleiben und als „Quelle
    entfernt“ markiert werden, damit ich selbst entscheide, ob sie noch relevant sind.
16. Als Student möchte ich, dass verschobene, aber unveränderte Seiten nicht neu verarbeitet werden,
    damit Umsortierungen keine Duplikate und Kosten erzeugen.
17. Als Student möchte ich, dass Seiten ohne lernrelevanten Inhalt (Titelfolie, Gliederung) als
    verarbeitet gelten, auch wenn daraus keine Karten entstanden sind, damit sie nicht bei jedem
    Update erneut ans LLM gehen.

### Analyse & Abschnittsbildung
18. Als Student möchte ich, dass Seiten mit wesentlichen Diagrammen oder Grafiken zusätzlich als
    Bild ans LLM gehen, damit Inhalte aus Grafiken in die Karten einfließen.
19. Als Student möchte ich, dass reine Textseiten nur als Text verarbeitet werden, damit die
    API-Kosten niedrig bleiben.
20. Als Student möchte ich, dass Vektorgrafiken (Pfeile, Kästen, Plots) genauso erkannt werden wie
    eingebettete Bilder, damit typische Folien-Diagramme nicht übersehen werden.
21. Als Student möchte ich, dass wiederkehrende Elemente der Folienvorlage (Logo, Fußzeile) nicht
    als Grafik zählen, damit nicht jede Seite unnötig als Bild verarbeitet wird.
22. Als Student möchte ich, dass ein kurzes Wochenpaket (bis ~30 Seiten) in einem einzigen
    LLM-Aufruf verarbeitet wird, damit der volle Kontext erhalten bleibt.
23. Als Student möchte ich, dass ein langer Foliensatz an Themengrenzen statt mitten in einem
    Thema geteilt wird, damit Definitionen und zugehörige Beispiele im selben Abschnitt landen.
24. Als Student möchte ich, dass bei einem fehlerhaften oder ungültigen Themengrenzen-Vorschlag
    automatisch nach fester Seitenzahl geteilt wird, damit die Verarbeitung nie an diesem Schritt
    scheitert.

### Generierung
25. Als Student möchte ich Karten im Frage/Antwort-Format, damit ich sie direkt lernen und später
    nach Anki exportieren kann.
26. Als Student möchte ich, dass Karten in der Sprache der Folien generiert werden, damit
    Fachbegriffe so vorkommen wie in Vorlesung und Klausur.
27. Als Student möchte ich, dass Formeln als LaTeX und Code als Code-Block in den Karten stehen,
    damit sie korrekt dargestellt werden.
28. Als Student möchte ich, dass jede Karte die Quellseite kennt, damit ich nachvollziehen kann,
    woher eine Karte stammt.
29. Als Student möchte ich, dass ungültige LLM-Antworten (fehlende Felder, leere Frage, Quellseite
    außerhalb des Abschnitts) erkannt und nicht als Karten gespeichert werden, damit die Datenbank
    keine kaputten Karten enthält.
30. Als Student möchte ich, dass vorübergehende API-Fehler (Rate-Limit, Timeout, Serverfehler)
    automatisch mit Backoff wiederholt werden, damit kurze Störungen keinen manuellen Eingriff
    erfordern.
31. Als Student möchte ich, dass neu generierte Karten im Status „zu prüfen“ landen, damit ich sie
    später in der Review-UI annehmen oder verwerfen kann.

### Fehlerbehandlung & Wiederholung
32. Als Student möchte ich, dass bei einem langen Foliensatz die Karten erfolgreicher Abschnitte
    gespeichert werden, auch wenn ein Abschnitt fehlschlägt, damit ich nicht alles neu bezahlen muss.
33. Als Student möchte ich sehen, welcher Abschnitt (welche Seiten) mit welchem Fehler
    fehlgeschlagen ist, damit ich verstehe, was passiert ist.
34. Als Student möchte ich nur die fehlgeschlagenen Abschnitte erneut anstoßen können, damit
    erfolgreiche Abschnitte nicht doppelt generiert werden.
35. Als Student möchte ich, dass ein Job nach einem Absturz des Workers nicht in „läuft“ hängen
    bleibt, sondern als fehlgeschlagen erkennbar und wiederholbar ist.

### Anzeige
36. Als Student möchte ich eine Liste aller Decks mit Name, Anzahl Karten und letztem
    Verarbeitungsstatus sehen, damit ich einen Überblick habe.
37. Als Student möchte ich in einem Deck alle Karten mit Frage, Antwort und Quellseite sehen, damit
    ich das Ergebnis der Generierung beurteilen kann.
38. Als Student möchte ich, dass Markdown, LaTeX-Formeln und Code-Blöcke in der Kartenliste
    gerendert werden, damit die Karten so aussehen, wie ich sie später lerne.
39. Als Student möchte ich, dass gerenderter Karteninhalt kein ausführbares HTML/JavaScript enthalten
    kann, damit LLM-Ausgaben keine Sicherheitslücke öffnen.
40. Als Student möchte ich in der Kartenliste sehen, welche Karten als „Quelle geändert“ oder
    „Quelle entfernt“ markiert sind, damit ich sie gezielt prüfen kann.
41. Als Student möchte ich auf der Deck-Seite den Status der letzten Verarbeitung sehen (wartend,
    läuft, fertig, teilweise fehlgeschlagen, fehlgeschlagen), damit ich weiß, ob die Karten
    vollständig sind.
42. Als Student möchte ich auf der Deck-Seite bei fehlgeschlagenen Abschnitten einen
    „Wiederholen“-Button haben, damit ich den Retry ohne API-Werkzeug auslösen kann.
43. Als Student möchte ich (optional) dass sich der Status während der Verarbeitung automatisch
    aktualisiert, damit ich die Seite nicht neu laden muss.
44. Als Student möchte ich bei großen Decks eine paginierte Kartenliste, damit die Seite auch bei
    vielen Karten schnell bleibt.

### Entwickler / Betrieb
45. Als Entwickler möchte ich, dass die Frontend-Typen aus dem OpenAPI-Schema generiert werden,
    damit Frontend und Backend nicht auseinanderlaufen.
46. Als Entwickler möchte ich, dass alle API-Fehler ein einheitliches Format haben, damit das
    Frontend sie einheitlich anzeigen kann.
47. Als Entwickler möchte ich, dass der LLM-Zugriff hinter einem eigenen Interface liegt, damit
    Tests ohne echte API-Aufrufe und Kosten laufen.
48. Als Entwickler möchte ich, dass die Ablage der PDFs hinter einem Storage-Interface liegt, damit
    ein späterer Wechsel zu S3 nur eine Konfigurationsfrage ist und Tests in-memory laufen.
49. Als Entwickler möchte ich, dass Grenzwerte (max. Dateigröße, max. Seiten, Abschnittsgrenze,
    Abschnittsgröße, Grafik-Schwellwerte, Modell) konfigurierbar sind, damit ich sie ohne
    Code-Änderung anpassen kann.
50. Als Entwickler möchte ich, dass Datenbank, API und Worker per docker-compose bzw. einfachen
    Befehlen lokal starten, damit die Demo reproduzierbar ist.
51. Als Entwickler möchte ich, dass verbrauchte Tokens pro LLM-Aufruf gespeichert werden, damit ich
    die Kosten nachvollziehen und später eine Kostenschätzung bauen kann.

## Implementation Decisions

### Module (Backend)

- **PDF-Analyse** (tiefes Modul): Nimmt PDF-Bytes, liefert eine Liste von Seiten mit Text,
  Text-Hash (über normalisierten Text), Titelzeile, Grafik-Flächenanteil und `needs_vision`-Flag;
  kann eine Seite zusätzlich als Bild rendern. Prüft Magic Bytes, Verschlüsselung und Lesbarkeit.
  Grafik-Erkennung umfasst eingebettete Bilder und Vektorgrafiken. Elemente, die auf einem Großteil
  der Seiten an derselben Position wiederkehren, werden nicht zur Grafikfläche gezählt.
  `needs_vision` ist wahr, wenn die (bereinigte) Grafikfläche einen Schwellwert (Startwert ~30 %)
  überschreitet oder die Seite kaum Text, aber eine Grafik enthält. Keine Abhängigkeit zu DB oder LLM.
- **Deck-Diff** (tiefes Modul, reine Funktion): Nimmt die gespeicherten Seiten-Hashes des Decks und
  die neu analysierten Seiten, liefert die Einteilung neu / geändert / entfernt / unverändert.
  Abgleich über Hashes, nicht über Seitenpositionen; „geändert“ wird über eine Ähnlichkeit zu einer
  entfallenen alten Seite an benachbarter Position erkannt, sonst gilt eine Seite als neu.
- **Abschnittsbildung** (tiefes Modul): Nimmt die zu verarbeitenden Seiten, liefert Abschnitte
  (Seitenbereiche). Bis zur Abschnittsgrenze (Startwert 30 Seiten) ein einziger Abschnitt. Darüber
  wird ein injizierter Grenzen-Vorschlager (LLM-Aufruf, Eingabe nur Titelzeilen pro Seite) befragt;
  das Ergebnis wird validiert (lückenlos, aufsteigend, kein Abschnitt über Maximalgröße). Bei Fehler
  oder ungültigem Vorschlag Fallback auf feste Abschnitte (~20–25 Seiten).
- **Kartengenerator** (tiefes Modul): Nimmt einen Abschnitt (Text je Seite, Bilder für
  `needs_vision`-Seiten), liefert validierte Karten (Frage, Antwort, Quellseite) und Token-Verbrauch.
  Nutzt Claude über ein eigenes LLM-Client-Interface; strukturierte Ausgabe per Tool Use mit
  JSON-Schema, Abbildung auf Pydantic-Modelle. Prompt fordert: Sprache der Folien, Markdown mit
  LaTeX (`$…$`/`$$…$$`), Code-Blöcke, atomare Karten, keine Karten für Titel-/Gliederungsfolien.
  Validierung verwirft Karten mit leeren Feldern oder Quellseite außerhalb des Abschnitts.
  Vorübergehende Fehler (429, 5xx, Timeout) werden mit exponentiellem Backoff wiederholt;
  dauerhaft ungültige Antworten führen zum Fehlschlag des Abschnitts.
- **Storage**: Interface speichern/lesen/löschen; Implementierung auf lokalem Dateisystem
  (Docker-Volume), In-Memory-Implementierung für Tests.
- **Verarbeitungs-Job**: Procrastinate-Task pro Upload. Orchestriert PDF-Analyse → Deck-Diff →
  Markierung betroffener Karten → Abschnittsbildung → Generierung pro Abschnitt → Speichern.
  Jeder Abschnitt wird in einer eigenen Transaktion gespeichert (Teilerfolg). Status pro Seite und
  pro Abschnitt wird explizit gespeichert, nicht aus der Kartenanzahl abgeleitet. Ein Retry-Task
  verarbeitet nur Abschnitte im Status „fehlgeschlagen“. Hängengebliebene Jobs werden über
  Procrastinates Mechanismen für abgebrochene/stalled Jobs erkannt.
- **REST-API**: Endpoints für Upload (multipart; Ziel „neues Deck“ mit Name oder „Update zu Deck
  X“), Deck-Liste, Deck-Detail inkl. letztem Job-Status, paginierte Kartenliste pro Deck,
  Job-Status inkl. Abschnitte, Retry fehlgeschlagener Abschnitte, Deck-Vorschlag zu einem
  Dateinamen. Upload-Validierung (Größe, Magic Bytes, Seitenzahl, Verschlüsselung) passiert
  synchron vor dem Einreihen des Jobs. Einheitliches Fehlerformat (Code, Nachricht, optionale
  Details) für alle Fehler.

### Datenmodell (erste Alembic-Migration)

- **Deck**: Name, Quell-Dateiname, Zeitstempel.
- **Upload**: gehört zu Deck; Original-Dateiname, Storage-Schlüssel, Seitenzahl, Zeitstempel.
  Jeder Upload ist eine Version des Decks.
- **Seite**: gehört zu Deck; aktuelle Position, Text-Hash, Titelzeile, `needs_vision`,
  Verarbeitungsstatus (ausstehend / verarbeitet / fehlgeschlagen), Flag „entfernt“; Verweis auf
  den Upload, in dem sie zuletzt gesehen wurde.
- **Karte**: gehört zu Deck und Quellseite; Typ (vorerst nur `basic`), Frage, Antwort (Markdown),
  Status (`pending_review` / `accepted` / `rejected` — in M1 nur `pending_review` genutzt),
  Quell-Markierung (keine / Quelle geändert / Quelle entfernt), Verweis auf den erzeugenden
  Abschnitt, Zeitstempel.
- **Verarbeitungs-Job**: gehört zu Upload; Status (wartend / läuft / fertig / teilweise
  fehlgeschlagen / fehlgeschlagen / nichts zu tun), Fehlermeldung, Zeitstempel.
- **Abschnitt**: gehört zu Job; Seitenbereich, Status, Fehlermeldung, Anzahl Versuche,
  Token-Verbrauch (Eingabe/Ausgabe), ob Seiten als Bild mitgeschickt wurden.
- Kein `user_id` in M1 (Single-User).

### Konfiguration
Anthropic-API-Key, Modellname, max. Dateigröße (Start 50 MB), max. Seiten (Start 150),
Abschnittsgrenze (30), feste Abschnittsgröße für Fallback, Grafik-Schwellwerte, Storage-Pfad —
alles über die bestehenden Settings (Umgebungsvariablen).

### Frontend
- React Router für die Seiten: Deck-Liste, Deck-Detail, Upload.
- TanStack Query für Datenabruf, Lade- und Fehlerzustände.
- API-Typen per `openapi-typescript` aus dem FastAPI-Schema generiert, Aufrufe über `openapi-fetch`.
- Tailwind CSS + shadcn/ui für die Oberfläche.
- Kartenanzeige mit einer Markdown-Bibliothek plus KaTeX; rohes HTML in Karteninhalten wird nicht
  gerendert.
- Upload-Seite: Dateiauswahl, Wahl „neues Deck“ (Name vorbelegt aus Dateiname) oder „Update zu
  Deck X“ (vorausgewählt per Dateinamen-Vorschlag), Anzeige von Validierungsfehlern.
- Deck-Detail: Job-Status beim Laden (kein Live-Update), Liste der Abschnitte mit Fehlern,
  Retry-Button, paginierte Kartenliste mit Quellseite und Quell-Markierung.
- Optional als letzter Schritt: Polling des Job-Status, solange der Job läuft.

## Testing Decisions

**Was ein guter Test ist**: Tests prüfen nur das von außen sichtbare Verhalten über die
öffentliche Schnittstelle eines Moduls (Eingabe → Ergebnis), nicht interne Hilfsfunktionen oder
Aufrufreihenfolgen. Ein Refactoring ohne Verhaltensänderung darf keinen Test brechen. Keine Tests
gegen die echte Anthropic-API in der Testsuite; Test-PDFs werden zur Laufzeit per PyMuPDF erzeugt
(keine echten Uni-Folien im Repo, siehe Urheberrechts-Entscheidung in CLAUDE.md).

**Unit-Tests**:
- **PDF-Analyse**: Text- und Hash-Extraktion; gleicher Inhalt ergibt gleichen Hash; Erkennung von
  Bild- und Vektorgrafik-Seiten; wiederkehrendes Logo löst kein `needs_vision` aus; Ablehnung von
  Nicht-PDF, verschlüsseltem und beschädigtem PDF.
- **Deck-Diff**: erster Upload (alles neu); angehängte Seiten; eingefügte Seite in der Mitte;
  geänderte Seite; entfernte Seite; umsortierte unveränderte Seiten; identischer Upload (nichts
  zu tun).
- **Abschnittsbildung**: kurze Eingabe ergibt einen Abschnitt; gültiger LLM-Vorschlag wird
  übernommen; Lücken, Überlappungen, zu große Abschnitte und Fehler des Vorschlagers führen zum
  festen Fallback.
- **Kartengenerator** (mit Fake-LLM-Client): gültige Antwort wird zu Karten; Karten mit leeren
  Feldern oder Quellseite außerhalb des Abschnitts werden verworfen; vorübergehende Fehler werden
  wiederholt; dauerhafte Fehler führen zum Fehlschlag; Bilder werden nur für `needs_vision`-Seiten
  mitgeschickt.

**Integrationstests** (echtes Postgres aus docker-compose, Fake-LLM, In-Memory-Storage):
- **Verarbeitungs-Job**: erster Upload erzeugt Seiten und Karten; Update verarbeitet nur neue und
  geänderte Seiten und markiert betroffene Karten; ein fehlschlagender Abschnitt ergibt
  „teilweise fehlgeschlagen“ mit gespeicherten Karten der übrigen Abschnitte; Retry verarbeitet
  nur den fehlgeschlagenen Abschnitt.
- **REST-API**: Upload-Validierung (Nicht-PDF, zu groß, zu viele Seiten, verschlüsselt) mit
  einheitlichem Fehlerformat; Upload reiht Job ein; Deck-Liste, Deck-Detail, paginierte
  Kartenliste, Retry-Endpoint, Deck-Vorschlag per Dateiname.

**Prior Art**: Der vorhandene Health-Test nutzt FastAPIs `TestClient` gegen die App; die
API-Integrationstests folgen diesem Stil. Für DB-Tests wird zusätzlich eine Test-Datenbank-Fixture
benötigt (existiert noch nicht).

**Nicht getestet in M1**: Frontend (Typsicherheit über generierte Typen genügt vorerst).

## Out of Scope

- Google-Drive-Integration (eigener Meilenstein; nutzt später denselben Verarbeitungs-Job, die
  Drive-Datei-ID ersetzt dann die manuelle Deck-Zuordnung)
- Live-Status per SSE (Polling nur als optionaler letzter Schritt)
- Review-UI: Karten bearbeiten, annehmen, verwerfen, Bulk-Actions (Status-Feld existiert bereits)
- Spaced-Repetition-Lernmodus
- Volltextsuche, Tags, Filter
- .apkg-Export
- Eval-Pipeline / Gold-Set-Vergleich
- Login, Multi-User, Rate-Limiting pro Nutzer
- Kostenschätzung mit Bestätigung vor dem Start (Token-Verbrauch wird aber bereits gespeichert)
- Weitere Kartentypen (Cloze, umgekehrte Karten); das Typ-Feld ist vorbereitet
- Thematische Gruppierung/Tags der Karten (Themengrenzen dienen nur der Abschnittsbildung)
- Sprachwahl pro Deck
- Löschen/Umbenennen von Decks
- Anzeige der Quellfolie neben der Karte
- Dateiformate außer PDF, OCR für eingescannte Folien
- Deployment / öffentliche Demo

## Further Notes

- **Kosten**: Die Bildverarbeitung ist der größte Kostentreiber. Die Grafik-Schwellwerte sollten
  nach den ersten echten Foliensätzen anhand des gespeicherten Token-Verbrauchs nachjustiert werden.
- **Öffentliche Demo**: Ohne Login könnte jeder Uploads und damit API-Kosten auslösen. Vor einer
  öffentlichen Demo braucht es Auth oder einen reinen Lesemodus.
- **Demo-Inhalte**: Für Screenshots und die öffentliche Demo nur selbst erstellte oder
  CC-lizenzierte Folien verwenden.
- **Generierung stabil halten**: Laut Projektentscheidung wird die Generierung (Prompt + Aufruf)
  einmal solide gebaut und danach nicht weiter ausgebaut. Die Abschnittsbildung und die
  Vision-Heuristik sind Teil dieses einmaligen Aufbaus.
- **Branch**: Lokal existiert nur `master`, als Haupt-Branch ist aber `main` vorgesehen. Vor dem
  ersten Push angleichen.
- **Aufwand**: grob 25–35 Stunden, aufgeteilt in etwa 6–8 Issues.
