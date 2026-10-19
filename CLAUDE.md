# Anki-KI-Projekt

## Zweck
Portfolio-Projekt für Praktikumsbewerbung (Informatik, 8. Semester), Zielrolle
"Webentwicklung mit KI-Unterstützung". Zeigt Web-Entwicklung als Hauptschwerpunkt, mit
LLM-Integration und Datenmodellierung als unterstützende Teile in einem zusammenhängenden
Projekt.

## Architektur (grob)
- **Extraktion/Generierung**: Hochgeladene Foliensätze werden per LLM (über API) analysiert und
  daraus automatisch Anki-Karten (Frage/Antwort) generiert.
- **Datenhaltung**: Generierte Karten werden in einer Datenbank gespeichert (nicht nur als
  Anki-Export-Datei), damit sie über die Website durchsuchbar/anzeigbar sind.
- **Website** (Hauptschwerpunkt): Backend erkennt neue Foliensätze aus Google Drive (eigene
  Integration, siehe Entscheidung unten) und verarbeitet sie asynchron; Frontend zum
  Anzeigen/Verwalten/Bearbeiten der generierten Karten-Datenbank, Such-/Filterfunktion über
  große Karten-Mengen, Review-UI für generierte Karten, Lern-Modus (Spaced Repetition), Anzeige
  der Eval-Metriken (siehe unten) pro Foliensatz.
- **Eval-Pipeline** (unterstützend, bewusst klein gehalten): Vergleich generierter Karten gegen
  ein handgepflegtes Gold-Set, um Qualität messbar zu machen (Details siehe Abschnitt
  "Eval-Pipeline"). Dient als Nachweis für verantwortungsvollen KI-Einsatz, nicht als
  Hauptdarsteller des Projekts.

## Entscheidungen

### Kern-Pipeline vor RAG
Reihenfolge: (1) Upload → Karten-Extraktion, (2) DB + Anzeige-Website, (3) RAG-Fragebeantwortung
erst danach, als optionales Stretch-Feature.
**Warum**: Upload→Extraktion→DB→Web-UI ist für sich schon ein vollständiges, erklärbares Projekt.
RAG zusätzlich on top erhöht den Scope erheblich (Vector-Store, Retrieval-Tuning, Evaluation).
Lieber den Kern robust und gut demonstrierbar machen, als drei halb fertige Teile zu haben.

### Eigener Dreh: Eval statt reines Prompting
Statt nur "Folien rein, Karten raus" per API zu zeigen, ist die Qualitätsmessung (Gold-Set-
Vergleich) Teil des Projekts — aber bewusst klein dimensioniert, nicht der Hauptfokus.
**Warum**: Eine reine Generierungs-Pipeline über eine API wirkt im Portfolio dünn ("nur ein
Wrapper"). Die Fähigkeit zu zeigen, *ob* die generierten Karten gut sind, erfordert eigene
algorithmische Arbeit (Matching, Metriken) und hebt das Projekt von einem reinen API-Call ab.

### Web-Teil als Hauptschwerpunkt (Zielrolle-Anpassung)
Da die Zielrolle "Webentwicklung mit KI-Unterstützung" ist, bekommt der Web-Teil die meiste
Implementierungstiefe (UX für Karten-Review/-Bearbeitung, Such-/Filterfunktion, saubere
API-Architektur, Performance bei vielen Decks); die Eval-Pipeline bleibt schlank.
**Warum**: Bei dieser Rolle ist Web-Dev der Kern, KI nur Unterstützung. Gleich viel Tiefe in
beide Teile zu stecken, würde bei begrenzter Zeit dazu führen, dass keiner der Teile wirklich
überzeugt. Der Web-Teil soll im Gespräch der Hauptdarsteller sein, die Eval-Pipeline der Beleg
für verantwortungsvollen KI-Einsatz.

### Karten-Generierung (API-Wrapper) bewusst simpel/stabil halten
Die Karten-Generierung (Prompt + API-Call) wird einmal solide gebaut und danach **nicht** weiter
ausgebaut. Die Eval-Pipeline wird auf eine minimale Version reduziert: nur ein Coverage-Check
gegen ein kleines Gold-Set, **ohne** LLM-Judge-Kalibrierung oder Duplikat-Erkennung. Die Website
ist der Bereich für laufende Erweiterung — hier fließt die restliche Projektzeit hinein.
**Warum**: Konsequenz aus der Zielrollen-Anpassung. Eine komplett fehlende Qualitätsmessung wäre
im Gespräch angreifbar ("nur ein Wrapper"), eine voll ausgebaute Eval-Pipeline würde aber wieder
Zeit vom eigentlichen Schwerpunkt (Web) abziehen. Die minimale Version reicht, um die Frage "wie
weißt du, dass die Karten gut sind?" glaubwürdig zu beantworten, ohne selbst zum Hauptprojekt zu
werden.

### Google Drive Integration direkt, nicht über MCP
Foliensätze werden automatisch nach Google Drive gebackupt. Statt diese per MCP (Model Context
Protocol) an die API durchzureichen, baut das eigene Backend eine direkte Google Drive API
Integration (OAuth2/Service-Account), die neue Dateien erkennt und den Verarbeitungs-Job auslöst.
Reihenfolge: zuerst manueller Upload (Meilenstein 1), dann Erkennung per **Polling** der Drive-API,
Push-Notification-Webhook nur optional, falls am Ende noch Zeit bleibt.
**Warum**: MCP ist ein Protokoll, um KI-Assistenten mit Tools zu verbinden — nicht der übliche
Baustein für den Backend-Service einer Web-App. Es per MCP zu lösen, würde eine fertige
Integration nutzen statt selbst eine zu bauen, und würde damit den gewollten Web-Dev-Tiefe-Punkt
(eigene Auth-/Webhook-/Fehlerbehandlung) wieder verwässern — genau der Effekt, den der
Rollen-Fokus auf Web vermeiden soll.
**Warum Polling vor Webhook**: Ein Drive-Webhook braucht eine öffentlich erreichbare HTTPS-URL
(Deployment oder Tunnel), und die Watch-Channels laufen ab und müssen erneuert werden. Polling ist
robuster, funktioniert auch lokal und ist trotzdem eine eigene API-Integration mit OAuth.

### Umgang mit echten Uni-Folien (Datenschutz/Urheberrecht)
Echte eigene Uni-Foliensätze dürfen privat zum Testen über die LLM-API verarbeitet werden
(geringes praktisches Risiko, vergleichbar mit Nutzung von DeepL/ChatGPT für Lerninhalte).
Für die **öffentliche** Demo (Portfolio, GitHub, Bewerbungsgespräch, Screenshots) werden
stattdessen nur selbst erstellte Beispiel-Folien oder CC-lizenzierte Open-Courseware-Materialien
verwendet — niemals echte, urheberrechtlich geschützte Uni-Folien.
**Warum**: Rechtlich ist das Verarbeiten geschützter Inhalte über eine externe API ein
Graubereich, praktisch aber Alltagsnutzung (keine bekannten Fälle von Konsequenzen bei rein
privater, nicht veröffentlichter Nutzung). Das eigentliche Risiko entsteht erst durch
**Veröffentlichung** fremden geschützten Materials — das lässt sich durch die Wahl der
Demo-Inhalte vollständig vermeiden, ohne die private Testnutzung einzuschränken.

### Nur PDF als Eingabeformat
Foliensätze werden ausschließlich als PDF verarbeitet, kein PPTX-Parser.
**Warum**: Uni-Folien liegen praktisch immer als PDF vor; ein zweiter Parser wäre Aufwand ohne
Mehrwert für den Web-Schwerpunkt.

### Tech-Stack: TypeScript-Frontend + Python-Backend
- **Frontend**: React + Vite + TypeScript
- **Backend**: FastAPI (Python), SQLAlchemy 2 + Alembic
- **DB**: PostgreSQL (Volltextsuche via `tsvector`, später `pgvector` für Eval-Embeddings)
- **Queue**: Procrastinate (Postgres-basiert, kein Redis)
- **PDF**: PyMuPDF
- **Live-Status**: Server-Sent Events
- **API-Vertrag**: TS-Typen werden per `openapi-typescript` aus dem FastAPI-OpenAPI-Schema generiert

**Warum**: Python dort, wo es Vorteile hat, TypeScript dort, wo es Standard ist (Browser-UI). Die
Sprachgrenze erzwingt eine saubere REST-Schnittstelle; generierte Typen verhindern, dass Frontend
und Backend auseinanderlaufen. Postgres deckt DB, Volltextsuche, Vektoren und Queue ab — eine
Infrastruktur-Komponente statt vier.

**Warum nicht TS-Fullstack** (am 2026-10-19 nochmals abgewogen und bestätigt): TS-Fullstack hätte
echte Vorteile (eine Sprache, geteilte Typen ohne Codegenerierung, z. B. per tRPC). Ausschlaggebend
für Python waren:
- **PyMuPDF** ist für Text pro Seite, Grafikerkennung und Rendering ausgereifter als die
  JS-Alternativen, mit deutlich mehr Erfahrungswerten.
- **`genanki`** für den `.apkg`-Export ist in Python etabliert und gepflegt; die JS-Alternativen
  sind veraltet.
- Die Teile, die der User selbst schreiben will (Delegationsstufe 3, siehe `docs/ai-workflow.md`),
  liegen fast alle im Backend. Der User kennt Python aus dem Studium und lernt TypeScript im
  Frontend; zwei neue Ökosysteme gleichzeitig würden mehr Delegation an die KI erzwingen.
- Für ein "Web mit KI"-Profil zeigen zwei Sprachen mit sauberer Schnittstelle eher mehr Breite.

Kein Grund ist dagegen die Eval: Embeddings kommen per API, der Vergleich läuft über pgvector,
numpy wird dafür nicht gebraucht.

### Bausteine erst bei Bedarf einführen
Neue Bibliotheken, Dienste oder Infrastruktur (z. B. SSE, pgvector-Nutzung, Drive-Webhook) kommen
erst ins Projekt, wenn ein konkretes Problem sie erfordert. Was ein PRD für einen Meilenstein
bereits festlegt, gilt als begründet.
Claude schlägt keine Extras "für später" vor und fügt keine neuen Dependencies ohne Rückfrage hinzu.
Bewusst nicht vorgesehen: Redis, Microservices, Kubernetes, GraphQL, separate Vector-DB, Redux.
**Warum**: Jeder Baustein muss im Gespräch mit einem echten Problem begründbar sein ("die
Generierung dauerte zu lange, deshalb Hintergrund-Job"). Vorsorglich eingebaute Bausteine sind
schwer zu begründen, kosten Zeit und machen das Projekt schwerer erklärbar. KI-Assistenten neigen
dazu, zu viel einzubauen — die Regel ist die Leitplanke dagegen.

### Doku-Struktur: AI-assisted Entwicklung sichtbar machen
- `README.md` — Kurzüberblick für Recruiter (Was, Stack, Starten), verlinkt auf `docs/`
- `CLAUDE.md` — Architektur, Konventionen, Entscheidungen mit "Warum"
- `docs/ai-workflow.md` — wie das Projekt mit KI-Unterstützung entwickelt wird (Ablauf, Regeln)
- `docs/devlog/YYYY-MM-DD-<thema>.md` — kurzer Eintrag pro Session/Meilenstein (Vorlage in
  `docs/ai-workflow.md`)

Am Ende einer Session darf Claude den sachlichen Teil eines Devlog-Eintrags vorformulieren.
Für die Abschnitte "Was ich entschieden/korrigiert habe", "Wo die KI danebenlag" und "Learning"
gilt: **Inhalt vom User, Formulierung darf von Claude kommen.**
1. Der User liefert Stichpunkte (unformuliert reicht).
2. Claude formuliert daraus den Text. Eigene Ergänzungen nur, wenn sie belegbar sind (z. B.
   Testergebnisse, Befunde aus der Session), und als Vorschlag gekennzeichnet.
3. Der User liest gegen und streicht, was nicht stimmt oder nicht seins ist.
Claude erfindet keine Reflexionen ohne Stichpunkte des Users. Fehlen sie, fragt Claude danach.
**Warum**: Im Portfolio soll nachvollziehbar sein, *wo* der User die KI gesteuert, korrigiert
und überprüft hat — nicht nur, dass KI benutzt wurde. Laufende kurze Einträge sind glaubwürdiger
und detailreicher als eine rückblickende Zusammenfassung. Nur der User weiß, was er tatsächlich
entschieden und gelernt hat, und muss es im Gespräch aus eigener Erinnerung erzählen können; die
Formulierung abzugeben spart dagegen Zeit für den Web-Schwerpunkt, ohne die Echtheit zu gefährden.

## Website-Features (priorisiert)

1. **Google Drive Integration + Async Processing mit Live-Status**: Eigene Erkennung neuer
   Dateien in Drive (OAuth2/Service-Account, Polling; Webhook optional, siehe Entscheidung
   oben), Verarbeitung als Hintergrund-Job (Queue),
   Live-Fortschritt in der UI (SSE/WebSockets). Zeigt Umgang mit asynchronen Prozessen,
   Echtzeit-Updates und eigener Drittanbieter-API-Integration.
2. **Human-in-the-loop Review-UI**: Generierte Karten landen zunächst in einem Review-Status;
   UI zum Durchgehen, Bearbeiten, Annehmen/Verwerfen (inkl. Bulk-Actions).
3. **Spaced-Repetition-Lernmodus**: Echter Lern-Modus mit Wiederholungsalgorithmus (z. B.
   SM-2 oder vereinfachte Variante), der Performance pro Karte trackt.
4. **Suche/Organisation bei Skalierung**: Volltextsuche, Tagging, Filter, Deck-Verwaltung;
   performant auch bei großen Karten-Mengen (Pagination/Indexierung).
5. **Export (.apkg)**: Generierung des Anki-Binärformats zum Download.
6. **Saubere API-Architektur**: Klare REST-Schnittstelle Frontend/Backend, Error-Handling
   (fehlgeschlagene LLM-Calls, nicht parsbare Foliensätze), Rate-Limiting.

## Eval-Pipeline (Goldset-Vergleich)

**Ziel**: Automatisiert messen, wie gut generierte Karten gegenüber einem handgepflegten
Gold-Standard sind — nicht nur "läuft durch", sondern mit Zahlen belegbar.

**MVP-Umfang (das, was tatsächlich gebaut wird — siehe "Karten-Generierung bewusst
simpel/stabil halten")**:
1. **Gold-Set**: Für 1–2 Foliensätze von Hand erstellte Referenz-Karten, jede mit einer
   `concept_id` (welches inhaltliche Konzept wird abgefragt).
2. **Matching**: Generierte Karten und Gold-Karten werden per Embedding (Cosinus-Ähnlichkeit)
   verglichen, oberhalb eines Ähnlichkeits-Schwellwerts gematcht.
3. **Metrik**: Nur *Coverage* — Anteil der Gold-Konzepte, die von mind. einer generierten Karte
   abgedeckt wurden. Wird pro Foliensatz auf der Website angezeigt.

**Mögliche Erweiterung (nicht Teil des aktuellen Plans, nur falls am Ende noch Zeit bleibt)**:
- Precision (Anteil generierter Karten, die ein Gold-Konzept matchen)
- LLM-as-Judge-Check für fachliche Korrektheit pro Match (Embedding-Ähnlichkeit zeigt nur
  thematische Nähe, nicht Richtigkeit) + Kalibrierung gegen eigene Bewertung
- Duplikat-Rate innerhalb der generierten Karten
- Gold-Set auf mehrere Foliensätze ausweiten

## Zeitaufwand & Vorgehen
Grobe Schätzung des Gesamtumfangs (siehe Website-Features + Eval-MVP oben): ca. 160 Std.
Bei Teilzeit entspricht das ca. 16 Wochen (10 Std./Woche), 11 Wochen (15 Std./Woche) oder
8 Wochen (20 Std./Woche). Setzt Grundkenntnisse in Webhooks/OAuth, Queues und Embeddings
voraus — bei Einarbeitung in diese Themen zusätzlich +20–30% einplanen.

**Reihenfolge**: Jeder Meilenstein soll ein demofähiges Zwischenergebnis liefern (zuerst
Drive → Generierung → einfache Kartenliste, dann Review-UI, dann Spaced-Repetition, dann Eval),
damit zu jedem Zeitpunkt etwas Vollständiges zeigbar ist.
**Warum**: Bewerbungs-Timing ist nicht fix planbar; falls der Zeitrahmen enger wird als gedacht,
soll trotzdem ein vollständiges (wenn auch kleineres) Produkt vorzeigbar sein, statt mehrerer
halb fertiger Features gleichzeitig.

**Bewerbungsstrategie**: Nicht auf Projekt-Fertigstellung warten, sondern parallel bewerben und
während laufender Bewerbungsprozesse weiterbauen (Prozesse dauern ohnehin oft Wochen/Monate).
Projekt kann im Anschreiben/Gespräch als "aktuell in Arbeit" mit wachsendem GitHub-Repo
dargestellt werden.
