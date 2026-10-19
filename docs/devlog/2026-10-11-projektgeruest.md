# 2026-10-11 – Projektgerüst und PRD für Meilenstein 1

**Ziel:** Ein lauffähiges Grundgerüst für Frontend, Backend und Datenbank aufsetzen, auf dem die
Features aufbauen können, und den ersten Meilenstein planen.

**Was die KI gemacht hat:**
- Tech-Stack-Entscheidung mit Begründung in `CLAUDE.md` festgehalten: React + Vite + TypeScript
  im Frontend, FastAPI + SQLAlchemy 2 + Alembic im Backend, PostgreSQL für DB, Volltextsuche,
  Vektoren und Queue (Procrastinate statt Redis); Entscheidung „nur PDF als Eingabeformat“
- Backend aufgesetzt (`backend/`): FastAPI-Projekt mit uv, async SQLAlchemy, Alembic-Migrationen,
  Health-Endpoint mit Test (`tests/test_health.py`)
- Frontend aufgesetzt (`frontend/`): Vite-React-TS-Starter mit Dev-Proxy `/api` → Backend
- `docker-compose.yml` mit Postgres 17 + pgvector
- README mit Start-Anleitung
- PRD für Meilenstein 1 (`prd/m1-upload-generierung.md`): PDF-Upload, Karten-Generierung als
  Hintergrund-Job, inkrementelle Updates über Seiten-Hashes, Kartenliste

Commit: `21c6957`

**Was ich entschieden/korrigiert habe:**
Ich stand vor der Wahl zwischen TypeScript als Fullstack und einem Python-Backend. Am 2026-10-19
habe ich diese Entscheidung nochmals abgewogen und das Python-Backend bewusst bestätigt. In Python
ist die PDF-Verarbeitung sehr ausgereift, und es gibt schon sehr viele Erfahrungswerte. Zusätzlich
sind die Bibliotheken für die Generierung von Anki-Karten in TypeScript veraltet. Dagegen gibt es
in Python die Bibliothek genanki, die aktuell und gut dokumentiert ist. Im Backend werde ich
hauptsächlich mit Delegationsstufe 2 oder 3 arbeiten, da dort die wichtigen Features liegen.
Deswegen wollte ich dort nicht zusätzlich eine neue Sprache lernen, sondern mit Python arbeiten,
das ich in der Uni schon oft verwendet habe.

Außerdem habe ich festgelegt, dass weitere Bausteine (z. B. SSE, pgvector, Drive-Webhook) erst
eingeführt werden, wenn ein konkretes Problem sie erfordert, damit der Stack nicht unnötig wächst.

**Wo die KI danebenlag:**
Bei der Überprüfung des Gerüsts sind mir drei Schwachstellen im generierten Code aufgefallen:
- Der Health-Endpunkt antwortet auch bei gestoppter Datenbank mit `200`, nur mit
  `"database": false` im JSON. Docker-Healthchecks und Monitoring prüfen meist nur den
  Statuscode und würden den Ausfall nicht erkennen. Üblich wäre `503`.
  *Präzisiert im Eintrag vom 2026-10-19: Das alte Verhalten war ein sinnvoller
  Liveness-Check und wurde um einen Readiness-Check ergänzt, statt durch `503` ersetzt
  ([2026-10-19-doku-und-health-check.md](2026-10-19-doku-und-health-check.md)).*
- Der Test `test_health_responds_even_without_database` verspricht im Namen, das Verhalten ohne
  Datenbank zu prüfen. Tatsächlich läuft er gegen die echte Datenbank, falls sie gestartet ist,
  und prüft das Feld `database` gar nicht.
- In `docker-compose.yml` ist die Datenbank auf `0.0.0.0` freigegeben, also im ganzen Netzwerk
  mit dem Passwort `anki` erreichbar. Für die lokale Entwicklung reicht `127.0.0.1`.

**Wie ich es überprüft habe:**
Die Überprüfung habe ich nachträglich am 2026-10-19 gemacht, Schicht für Schicht von der
Datenbank bis zum Frontend. So ist bei einem Fehler sofort klar, in welcher Schicht er liegt.

Ich habe als Erstes Postgres per Docker gestartet. Der erste Start schlug fehl, weil Port 5432
auf meinem PC durch einen alten System-Postgres aus einem früheren Projekt belegt war. Ich habe
den Dienst gestoppt, deinstalliert und die Daten gelöscht.
Danach war der Container zwar `healthy`, aber ohne Port-Weiterleitung, weil er beim
fehlgeschlagenen Versuch angelegt worden war. Mit `docker compose up -d --force-recreate` habe
ich ihn neu angelegt, danach war der Port korrekt freigegeben.

Danach:
- **Verbindung Backend → Datenbank:** `alembic upgrade head` hat sich erfolgreich mit Postgres
  verbunden. Migrationen wurden keine ausgeführt, weil es noch keine gibt.
- **API:** `GET /api/health` direkt auf Port 8000 lieferte `200` mit `"database": true`.
  Zusätzlich habe ich die Datenbank gestoppt und den Endpunkt erneut aufgerufen: Die Antwort
  kam weiterhin mit `200`, nur mit `"database": false`.
- **Tests und Linter:** `pytest` (1 Test) und `ruff check` liefen ohne Fehler durch.
- **Frontend und Proxy:** Den Vite-Dev-Server gestartet und `/api/health` über Port 5173
  aufgerufen. Die Antwort kam von uvicorn (`server: uvicorn` im Header) mit `200` und
  `"database": true`. Damit funktioniert die Weiterleitung von `/api` an das Backend. Beim
  ersten Versuch kam ein `502 Bad Gateway`, weil ich das Backend zwischenzeitlich beendet hatte.
  Nach dem Neustart des Backends lief es.

**Learning:**
- **„Läuft“ heißt nicht „funktioniert richtig“.** Der generierte Code lief auf Anhieb, und Test
  und Linter waren grün. Die Schwachstellen im Health-Endpunkt habe ich erst gefunden, als ich
  gezielt den Fehlerfall ausprobiert habe (Datenbank gestoppt). KI-Code prüfe ich deshalb nicht
  nur auf den Normalfall, sondern auch darauf, was bei Fehlern passiert.
- **Ein grüner Test sagt nur etwas über das, was er tatsächlich prüft.** Der Name des
  Health-Tests klang nach mehr, als er abdeckt. Bei KI-generierten Tests lese ich ab jetzt, was
  wirklich geprüft wird, statt mich auf Namen und grüne Haken zu verlassen.
- **Schicht für Schicht prüfen lohnt sich.** Der Container meldete `healthy`, war aber von außen
  gar nicht erreichbar. Weil ich jede Schicht einzeln geprüft habe (Container, Port, Datenbank-
  Verbindung, API, Proxy), war jeder Fehler sofort eingegrenzt.
- **Die eigene Entwicklungsumgebung ist Teil des Systems.** Ein vergessener Postgres aus einem
  alten Projekt hat den Port blockiert. Bei „Port belegt“-Fehlern schaue ich jetzt zuerst nach,
  welcher Prozess den Port nutzt (`ss -ltnp`).

**Offen:** Das Frontend ist noch der unveränderte Vite-Starter (Beispielseite, Logos). Das
Datenmodell ist leer. Beides wird in Meilenstein 1 ersetzt.
