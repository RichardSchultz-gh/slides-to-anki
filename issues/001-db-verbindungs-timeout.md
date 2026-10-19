# DB-Verbindungs-Timeout setzen

## Kontext

Technische Schuld, gefunden bei der Überprüfung am 2026-10-19
(`docs/devlog/2026-10-19-doku-und-health-check.md`, Abschnitt „Offen“). Kein Parent-PRD; relevant
vor allem für `prd/deployment-raspberry-pi.md`.

## Problem

Für die Datenbankverbindung ist kein Verbindungs-Timeout gesetzt. Wird eine Verbindung sofort
abgelehnt (DB-Container gestoppt), antwortet `/api/health/ready` in Millisekunden mit `503`. Ist
die Datenbank dagegen *hängend* nicht erreichbar (Netzwerkproblem, überlastete DB, später auf dem
Pi), wartet jeder Request, bis ein Timeout des Betriebssystems greift. Das kann sehr lange dauern:
Readiness-Checks und Monitoring hängen, und API-Requests blockieren Verbindungen.

## Was zu tun ist

Ein konfigurierbares Verbindungs-Timeout für die DB-Engine setzen (über die bestehenden Settings,
mit einem kurzen Standardwert von einigen Sekunden), sodass `/api/health/ready` und alle anderen
DB-Zugriffe bei nicht erreichbarer Datenbank zügig mit einem Fehler zurückkehren.

## Acceptance criteria

- [ ] Verbindungs-Timeout ist über die Settings (Umgebungsvariable) konfigurierbar, mit einem
      sinnvollen Standardwert
- [ ] Bei einer hängenden, nicht erreichbaren Datenbank liefert `/api/health/ready` innerhalb
      des Timeouts `503`
- [ ] Manuell geprüft, z. B. mit einer `DATABASE_URL`, die auf eine nicht antwortende Adresse
      zeigt
- [ ] `.env.example` dokumentiert die neue Einstellung

## Blocked by

None - can start immediately
