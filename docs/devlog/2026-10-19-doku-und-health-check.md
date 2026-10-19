# 2026-10-19 – Doku-Struktur, Überprüfung des Gerüsts, Health-Check

**Ziel:** Festlegen, wie das Projekt und die KI-assistierte Entwicklung dokumentiert werden, das
Projektgerüst vom 2026-10-11 im laufenden System überprüfen und die dabei gefundenen
Schwachstellen beheben.

**Was die KI gemacht hat:**
- Doku-Struktur vorgeschlagen und angelegt: `docs/ai-workflow.md` (Ablauf, Arbeitsteilung,
  Delegationsstufen, Devlog-Vorlage), `docs/devlog/` und die Entscheidung dazu in `CLAUDE.md`
- Devlog-Eintrag für die Gerüst-Session aus Commit und PRD rekonstruiert
- Stack erklärt (Vite und Alternativen, Node.js und TypeScript, Backend-Aufbau) und die Wahl
  TS-Fullstack gegen Python-Backend mit mir abgewogen
- PRD für das Deployment auf einem Raspberry Pi 3 als Entwurf geschrieben
  (`prd/deployment-raspberry-pi.md`)
- Schritt-für-Schritt-Anleitung zur Überprüfung des Gerüsts geliefert und bei den Problemen
  unterwegs (belegter Port, fehlende Port-Weiterleitung, `502` am Proxy) die Ursache ermittelt
- Health-Endpunkt in `/api/health/live` und `/api/health/ready` getrennt, die Tests auf eine
  ersetzte DB-Session umgestellt und die DB in `docker-compose.yml` an `127.0.0.1` gebunden
- README um einen Abschnitt „Wie dieses Projekt entsteht“ mit Verweis auf `docs/ai-workflow.md`
  und den Devlog ergänzt

Commits: `2543ac2`, `3171d9c`, `d8bafb6`, `1aae1c0`

**Was ich entschieden/korrigiert habe:**
Claude hatte vorgeschlagen, den Health-Endpunkt bei fehlender Datenbank einfach auf `503`
umzustellen. Ich habe nachgefragt, warum das bisherige Verhalten so gebaut war. Ich bin davon
ausgegangen, dass hinter diesem üblichen Verhalten eine Absicht steckt, und wollte es nicht
ändern, ohne diese Absicht zu kennen. Dadurch kam heraus, dass das alte Verhalten ein sinnvoller
Liveness-Check war, der nicht ersetzt, sondern um einen Readiness-Check ergänzt werden sollte.
Umgesetzt wurde deshalb die Trennung in `live` und `ready` statt des ursprünglichen Vorschlags.

**Wo die KI danebenlag:**
- Der erste Befund zum Health-Endpunkt war zu pauschal („`200` bei fehlender DB ist falsch“).
  Durch meine Nachfrage hat sich gezeigt, dass der Vorschlag in eine sinnvolle, übliche
  Funktionsweise eingegriffen hätte: Ein Liveness-Check darf gerade nicht von der Datenbank
  abhängen.
- Claude hatte die Datenbank in `docker-compose.yml` beim Gerüst mit `"5432:5432"`
  freigegeben, also auf `0.0.0.0`. Damit war sie für alle Geräte im selben Netz mit den
  öffentlich im Repo stehenden Zugangsdaten erreichbar. Jetzt ist sie an `127.0.0.1` gebunden.

**Wie ich es überprüft habe:**
- Diff gelesen.
- Container mit `docker compose up -d --force-recreate` neu angelegt; `docker compose ps` zeigt
  jetzt `127.0.0.1:5432->5432/tcp`.
- Mit laufender Datenbank: `live` und `ready` liefern beide `200`.
- Datenbank gestoppt: `ready` liefert `503` mit `"status": "unavailable"`, `live` weiterhin
  `200`.
- `pytest` bei gestoppter Datenbank ausgeführt: alle 3 Tests grün, die Tests hängen also nicht
  mehr vom Zustand meines Rechners ab.

**Learning:**
- **`0.0.0.0` heißt „im ganzen Netz erreichbar“.** Mir war neu, dass eine Freigabe auf
  `0.0.0.0` bedeutet, dass alle Geräte im selben Netz den Dienst aufrufen können, nicht nur mein
  eigener Rechner. Für lokale Entwicklung gehört `127.0.0.1` davor.
- **Docker umgeht die Firewall.** Unter Linux umgehen veröffentlichte Docker-Ports
  Firewall-Regeln wie ufw. Eine Firewall hätte die offene Datenbank also nicht geschützt.
- **Liveness und Readiness sind zwei verschiedene Fragen.** Der Liveness-Check prüft, ob der
  Prozess überhaupt läuft. Er darf nicht von der Datenbank abhängen, weil ein Neustart der App
  einen Datenbankausfall nicht behebt und nur eine Neustart-Schleife auslösen würde. Der
  Readiness-Check prüft dagegen, ob die App gerade arbeiten kann. Er muss die Datenbank
  einbeziehen, damit das Monitoring einen Ausfall erkennt.
- **Fehlerfälle lassen sich über Dependency Injection testen.** Mit `dependency_overrides`
  kann ich die DB-Session im Test durch eine Attrappe ersetzen und so den Ausfall der Datenbank
  gezielt und reproduzierbar prüfen, ohne echte Infrastruktur.
- **Auch die Korrektur der KI hinterfragen.** Claude hat den eigenen Code kritisiert, aber
  selbst diese Kritik war zu pauschal. Erst meine Nachfrage hat zur besseren Lösung geführt.
- **Im laufenden System prüfen, nicht nur Tests.** Grüne Tests allein reichen nicht. Erst der
  Aufruf mit `curl` bei gestoppter Datenbank hat gezeigt, dass `503` und `200` tatsächlich so
  ankommen.

**Offen:**
- Ein Verbindungs-Timeout für die Datenbank ist nicht gesetzt. Bei einer hängenden statt
  abgelehnten Verbindung würde `ready` warten (relevant fürs Deployment).
