# PRD: Deployment auf Raspberry Pi 3 mit öffentlicher Demo

> **Status:** Entwurf. Die Issues werden erst nach Abschluss von Meilenstein 1
> (`prd/m1-upload-generierung.md`) erzeugt, weil Details wie der tatsächliche Speicherbedarf des
> Workers und die PDF-Ablage erst dann feststehen. Offene Punkte stehen unter
> „Offene Entscheidungen“.

## Problem Statement

Das Projekt soll in Bewerbungen als laufende Anwendung verlinkt werden. Ein GitHub-Repo allein
wird von Recruitern selten genauer angeschaut, eine App, die man anklicken kann, dagegen schon.
Aktuell läuft die App nur lokal auf meinem Rechner.

Ich habe einen Raspberry Pi 3 (1 GB RAM), auf dem die App laufen soll. Dabei gibt es mehrere
Hürden:
- Mein Internetanschluss hat eventuell keine eigene öffentliche IPv4-Adresse (DS-Lite/CGNAT), und
  eine Portfreigabe würde mein Heimnetz öffnen.
- Ohne Schutz könnte jeder Besucher PDFs hochladen und damit LLM-Kosten auf meine Rechnung
  auslösen. Meilenstein 1 hat bewusst keinen Login.
- 1 GB RAM ist knapp für Postgres, API, Worker, Reverse Proxy und Tunnel. Die PDF-Verarbeitung
  kann den Speicher kurzfristig stark belasten.
- SD-Karten gehen unter Datenbank-Schreiblast schnell kaputt, und ohne Backups wären alle Decks
  verloren.
- Der Pi 3 ist zu langsam, um Frontend und Docker-Images selbst zu bauen.

## Solution

Die App läuft auf dem Pi 3 als Docker-Compose-Setup und ist über einen Cloudflare Tunnel unter
einer eigenen Domain per HTTPS erreichbar, ohne dass am Router ein Port geöffnet wird.

- **Besucher** sehen eine **öffentliche, rein lesende Demo** mit vorbereiteten Beispiel-Decks
  (nur selbst erstellte oder CC-lizenzierte Folien). Upload und Retry sind für sie nicht sichtbar
  und serverseitig gesperrt.
- **Ich als Betreiber** melde mich mit einem Admin-Passwort an und kann dann hochladen und
  verarbeiten wie lokal.
- Die Images werden **nicht auf dem Pi gebaut**, sondern für ARM64 vorab gebaut und auf dem Pi nur
  heruntergeladen und gestartet.
- Speicherbedarf wird durch kleine Postgres-Konfiguration, einen Worker mit nur einem Job
  gleichzeitig, niedrigere Grenzwerte und zram-Swap begrenzt.
- Die Datenbank und die hochgeladenen PDFs werden regelmäßig außerhalb des Pi gesichert.

Reicht der Pi 3 nicht aus, zieht dasselbe Compose-Setup ohne Umbau auf einen kleinen VPS oder
einen Pi 5 um.

## User Stories

### Besucher / Recruiter
1. Als Besucher möchte ich die App über einen Link mit HTTPS öffnen, damit ich ohne
   Sicherheitswarnung direkt einen Eindruck bekomme.
2. Als Besucher möchte ich ohne Registrierung Beispiel-Decks und deren Karten ansehen, damit ich
   die App sofort ausprobieren kann.
3. Als Besucher möchte ich direkt auf einen Unterseiten-Link (z. B. ein Deck) gehen oder die Seite
   neu laden können, ohne eine Fehlerseite zu bekommen, damit geteilte Links funktionieren.
4. Als Besucher möchte ich erkennen, dass es sich um eine Demo mit eingeschränkten Funktionen
   handelt, damit ich fehlende Upload-Funktionen nicht für einen Fehler halte.
5. Als Besucher möchte ich, dass die Seiten auch auf dem schwachen Server zügig laden, damit der
   erste Eindruck nicht unter Wartezeiten leidet.

### Betreiber (ich)
6. Als Betreiber möchte ich mich mit einem Admin-Passwort anmelden, damit nur ich Uploads und
   damit LLM-Kosten auslösen kann.
7. Als Betreiber möchte ich, dass schreibende Endpunkte (Upload, Retry) ohne Anmeldung serverseitig
   abgelehnt werden, damit der Schutz nicht nur im Frontend besteht.
8. Als Betreiber möchte ich, dass wiederholte falsche Login-Versuche gebremst werden, damit das
   Passwort nicht durchprobiert werden kann.
9. Als Betreiber möchte ich beim LLM-Anbieter ein Ausgabenlimit gesetzt haben, damit selbst bei
   einem Fehler keine unbegrenzten Kosten entstehen.
10. Als Betreiber möchte ich, dass am Router kein Port geöffnet werden muss, damit mein Heimnetz
    nicht von außen erreichbar ist.
11. Als Betreiber möchte ich ein Update mit wenigen Befehlen einspielen (neue Images holen,
    Migrationen ausführen, neu starten), damit Deployments nicht zur Hürde werden.
12. Als Betreiber möchte ich, dass die Container nach einem Absturz oder Stromausfall automatisch
    wieder starten, damit die Demo ohne mein Zutun erreichbar bleibt.
13. Als Betreiber möchte ich, dass Datenbank-Migrationen beim Deployment automatisch laufen, bevor
    die API startet, damit Code und Schema nicht auseinanderlaufen.
14. Als Betreiber möchte ich eine nächtliche Sicherung von Datenbank und hochgeladenen PDFs
    außerhalb des Pi, damit ein Defekt nicht alle Decks vernichtet.
15. Als Betreiber möchte ich die Wiederherstellung aus einem Backup einmal getestet haben, damit
    ich weiß, dass die Backups im Ernstfall funktionieren.
16. Als Betreiber möchte ich die Beispiel-Decks der Demo reproduzierbar erzeugen können, damit ich
    sie nach einem Neuaufsetzen wiederherstellen kann.
17. Als Betreiber möchte ich eine kurze Anleitung zum Aufsetzen des Pi und zum Deployen im Repo,
    damit ich (oder jemand anderes) das Setup nachvollziehen kann.
18. Als Betreiber möchte ich benachrichtigt werden, wenn die Demo nicht erreichbar ist, damit ich
    es nicht erst durch einen Recruiter erfahre.

### Ressourcen (Pi 3)
19. Als Betreiber möchte ich, dass der Worker nur einen Job gleichzeitig verarbeitet, damit der
    Speicher bei großen PDFs nicht ausgeht.
20. Als Betreiber möchte ich für die Produktion niedrigere Grenzwerte (max. Dateigröße, max. Seiten)
    setzen können als lokal, damit ein großes PDF den Pi nicht überlastet.
21. Als Betreiber möchte ich den tatsächlichen Speicherbedarf aller Dienste im Ruhezustand und
    während der Verarbeitung eines großen PDFs gemessen haben, damit ich fundiert entscheiden kann,
    ob der Pi 3 reicht.
22. Als Betreiber möchte ich, dass Speicherspitzen über zram-Swap abgefangen werden, statt dass
    Linux einen Dienst beendet.

### Entwickler
23. Als Entwickler möchte ich, dass die Images für ARM64 außerhalb des Pi gebaut und in einer
    Registry abgelegt werden, damit der Pi nur fertige Images startet.
24. Als Entwickler möchte ich, dass API und Worker aus demselben Image mit unterschiedlichem
    Startbefehl laufen, damit es nur ein Backend-Image zu pflegen gibt.
25. Als Entwickler möchte ich eine von der lokalen Entwicklung getrennte Compose-Konfiguration für
    die Produktion, damit lokale Einstellungen nicht versehentlich live gehen.
26. Als Entwickler möchte ich getrennte Health-Endpunkte für Liveness (Prozess lebt, ohne DB) und
    Readiness (DB erreichbar, sonst `503`), damit Monitoring den DB-Ausfall erkennt, ohne dass ein
    Neustart-Mechanismus die App sinnlos neu startet. (Bereits umgesetzt am 2026-10-19.)
27. Als Entwickler möchte ich, dass Secrets (API-Key, Admin-Passwort, DB-Passwort) nur in einer
    Umgebungsdatei auf dem Pi liegen und nie im Repo, damit sie nicht öffentlich werden.
28. Als Entwickler möchte ich, dass gehashte Frontend-Dateien lange gecacht werden und die
    `index.html` nicht, damit Besucher nach einem Update sofort die neue Version bekommen.

## Implementation Decisions

### Infrastruktur
- **Hosting**: Raspberry Pi 3, Raspberry Pi OS Lite 64-Bit (ohne Desktop). Wenn möglich Boot von
  einer USB-SSD statt SD-Karte. SSH nur mit Schlüssel, automatische Sicherheitsupdates.
- **Erreichbarkeit**: Cloudflare Tunnel (`cloudflared` als Container). Der Tunnel baut die
  Verbindung vom Pi nach außen auf; HTTPS endet bei Cloudflare. Am Router wird nichts geöffnet.
  Benötigt eine eigene Domain bei Cloudflare.
- **Dienste** (eine Compose-Datei für die Produktion):
  - **Reverse Proxy (Caddy)**: liefert das gebaute Frontend aus, leitet `/api` an FastAPI weiter,
    SPA-Fallback (unbekannte Pfade außerhalb von `/api` liefern die `index.html`), Kompression,
    Cache-Header (gehashte Assets lange, `index.html` nie).
  - **API**: FastAPI/uvicorn, ein Prozess.
  - **Worker**: Procrastinate, gleiches Image wie die API, Nebenläufigkeit 1.
  - **Migration**: einmaliger Container, der `alembic upgrade head` ausführt; API und Worker starten
    erst nach dessen Erfolg.
  - **Postgres** mit pgvector, klein konfiguriert (z. B. `shared_buffers` 64–128 MB, wenige
    Verbindungen).
  - Alle Dienste mit Neustart-Richtlinie und Speicherlimits; Healthchecks für Postgres und API.
- **Images**: Backend-Image und Proxy-Image (mit eingebautem Frontend-Build) werden für ARM64
  außerhalb des Pi gebaut und in eine Container-Registry gepusht. Der Pi zieht nur fertige Images.
- **Speicher**: zram-Swap auf dem Pi. Grenzwerte für Dateigröße und Seitenzahl in der Produktion
  niedriger als lokal (über die bestehenden Settings, siehe User Story 49 in M1).

### Zugriffsschutz (Demo-Modus + Admin-Login)
- **Single-User**: Es gibt genau einen Admin. Keine Registrierung, keine Benutzertabelle, passend
  zu M1 (kein `user_id`).
- Das Admin-Passwort liegt als Hash in der Umgebungskonfiguration.
- Login-Endpunkt prüft das Passwort und setzt ein signiertes Session-Cookie (`HttpOnly`, `Secure`,
  `SameSite=Strict`). Logout löscht es.
- Login-Versuche werden pro IP gebremst.
- Alle schreibenden Endpunkte verlangen eine gültige Session (FastAPI-Dependency) und antworten
  sonst mit `401` im einheitlichen Fehlerformat aus M1. Lesende Endpunkte bleiben öffentlich.
- Ein Endpunkt liefert dem Frontend, ob der Nutzer angemeldet ist. Das Frontend blendet Upload und
  Retry für Besucher aus und zeigt einen Hinweis „Demo – nur lesend“.

### Betrieb
- **Backups**: nächtlicher `pg_dump` plus Kopie der hochgeladenen PDFs, Aufbewahrung von N Tagen,
  Ablage außerhalb des Pi. Wiederherstellung wird einmal vollständig getestet.
- **Demo-Daten**: Beispiel-Decks werden einmal über die echte Pipeline aus eigenen oder
  CC-lizenzierten Folien erzeugt. Ein Dump davon dient zur Wiederherstellung.
- **Monitoring**: externer, kostenloser Uptime-Check gegen den Readiness-Endpunkt mit
  Benachrichtigung per E-Mail.
- **Deployment**: manuell (neue Images ziehen, Compose neu starten). Ablauf ist in einer
  Deployment-Anleitung im Repo dokumentiert.

### Health-Endpunkte (bereits umgesetzt)
- `/api/health/live`: immer `200`, ohne DB-Abfrage. Für Docker-Healthcheck/Neustart-Mechanismen.
- `/api/health/ready`: `200`, wenn die DB erreichbar ist, sonst `503`. Für den Uptime-Check.

## Testing Decisions

**Was ein guter Test ist**: wie in M1. Tests prüfen von außen sichtbares Verhalten über die
öffentliche Schnittstelle, nicht Implementierungsdetails.

**Automatisierte Tests**:
- **Zugriffsschutz**: schreibende Endpunkte ohne Session ergeben `401` im einheitlichen
  Fehlerformat; mit gültiger Session funktionieren sie; lesende Endpunkte sind ohne Session
  erreichbar; falsches Passwort ergibt keinen Login; manipuliertes Cookie wird abgelehnt; Bremse
  greift nach wiederholten Fehlversuchen.
- **Health-Endpunkte**: bereits umgesetzt und getestet (Liveness ohne DB; Readiness `200`/`503`
  mit ersetzter DB-Session).

**Manueller Smoke-Test nach jedem Deployment** (als Checkliste in der Deployment-Anleitung):
- Readiness-Endpunkt über die öffentliche Domain liefert `200`.
- Direktaufruf einer Unterseite liefert die App (SPA-Fallback).
- Upload ohne Login wird abgelehnt.
- Nach Login funktioniert ein Upload eines kleinen Test-PDFs.

**Messung statt Test**: Speicherbedarf aller Dienste im Ruhezustand und während der Verarbeitung
eines PDFs an der Produktionsgrenze, festgehalten im Devlog.

**Nicht getestet**: Infrastruktur-Konfiguration (Caddy, Tunnel, Compose) außer über den
Smoke-Test.

## Out of Scope

- Mehrere Benutzer, Registrierung, Rollen
- Automatisches Deployment (CD) bei jedem Push
- Google-Drive-Webhook (eigener Meilenstein; der Tunnel liefert aber die dafür nötige öffentliche
  HTTPS-URL)
- Monitoring-Stack mit Metriken (Prometheus, Grafana o. Ä.)
- Hochverfügbarkeit, mehrere Instanzen
- Der Umzug auf VPS oder Pi 5 selbst (nur als Fallback vorgesehen, siehe Further Notes)
- Lasttests

## Offene Entscheidungen

- **Domain**: welche, bei welchem Anbieter (ca. 10 €/Jahr). Muss über Cloudflare verwaltet werden.
- **Image-Build**: GitHub Actions mit Push in die GitHub Container Registry (empfohlen, setzt den
  ersten Push nach GitHub und die Umbenennung von `master` in `main` voraus) oder lokal per
  `docker buildx` auf dem PC.
- **Backup-Ziel**: eigener PC, externer Speicher oder Cloud-Speicher.
- **Pi-Modell**: Pi 3B oder 3B+? Der 3B+ kann direkt von USB booten, beim 3B muss das erst
  aktiviert werden.
- **Admin-Login**: Variante oben ist ein Vorschlag (ein Passwort, Session-Cookie). Alternative wäre
  Cloudflare Access vor den Admin-Funktionen, dann ohne eigenen Login-Code, aber auch ohne
  eigenen Web-Dev-Anteil.

## Further Notes

- **Abhängigkeit**: Setzt den Abschluss von Meilenstein 1 voraus (Upload, Worker, Kartenliste,
  React Router).
- **Speicher-Schätzung** (vor der Messung): OS ca. 150 MB, Docker 50–100 MB, Postgres
  100–200 MB, API 80–120 MB, Worker ca. 100 MB im Ruhezustand, Caddy + cloudflared 60–80 MB.
  Zusammen etwa 550–750 MB von 1 GB. Kritisch ist die PDF-Verarbeitung im Worker.
- **Ausstiegskriterium Pi 3**: Wenn ein PDF an der Produktionsgrenze trotz der Maßnahmen zu
  Speicherfehlern führt oder die öffentlichen Seiten spürbar langsam laden, wird dasselbe Setup
  auf einen kleinen VPS (ca. 4 €/Monat) oder einen Pi 5 umgezogen.
- **Plan B für Bewerbungen**: Screenshots oder ein GIF in der README, falls die Demo gerade nicht
  erreichbar ist.
- **Demo-Inhalte**: nur selbst erstellte oder CC-lizenzierte Folien (siehe CLAUDE.md).
- **Gesprächswert**: Betrieb auf 1 GB RAM mit gemessenem Speicherbedarf, Tunnel statt
  Portfreigabe, serverseitiger Zugriffsschutz gegen Kostenmissbrauch.
- **Aufwand**: grob 12–20 Stunden, aufgeteilt in etwa 5–7 Issues.
