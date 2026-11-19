# Datenbank: SQLAlchemy mit SQLite lokal und PostgreSQL produktiv

Date: 2026-11-19

## Status

Accepted

## Context

Gespeichert werden Benutzer, Lernstand pro Item und alle Antworten. Lokal und in den Tests soll keine Datenbank installiert werden müssen; produktiv müssen die Daten Neustarts und Deployments überleben.

## Options Considered

 * Nur SQLite: einfach, aber auf Render (Gratisplan) gehen Dateien bei jedem Deployment verloren.
 * PostgreSQL mit SQL von Hand: volle Kontrolle, aber eigener Code für zwei Datenbanken.
 * SQLAlchemy (ORM) mit SQLite lokal und PostgreSQL produktiv: gleicher Code für beide.

## Decision

SQLAlchemy 2.0 mit Treiber psycopg; gesteuert über die Umgebungsvariable DATABASE_URL. Entschieden von Kay.

## Reasons

Ein Code für beide Datenbanken, Tests laufen schnell gegen SQLite. Die Verben selbst sind fachliche Stammdaten und liegen versioniert in verbs.json statt in der Datenbank.

## Consequences

Die Tabellen werden beim Start angelegt (create_all); für spätere Änderungen am Schema wäre ein Migrationswerkzeug (Alembic) nötig. Die App wurde zusätzlich gegen eine echte PostgreSQL-Datenbank getestet.
