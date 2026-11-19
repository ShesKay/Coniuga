# Verbdaten als JSON-Datei statt in der Datenbank

Date: 2026-11-19

## Status

Accepted

## Context

Die 60 Verben mit Bedeutung, Hilfsverb, unregelmässigen Formen und Einführungsreihenfolge sind fachliche Stammdaten. Sie ändern sich nur mit einer neuen Version der App.

## Options Considered

 * In der Datenbank: änderbar ohne Deployment, braucht aber Befüllung (Seed), Migrationen und Verwaltung.
 * Als JSON-Datei im Repository: versioniert mit dem Code, im Review sichtbar, in Tests ohne Datenbank verfügbar.

## Decision

src/app/data/verbs.json. Entschieden von Kay.

## Reasons

Daten und Regeln, die zusammengehören, werden gemeinsam versioniert und getestet. Die Datenbank enthält nur, was pro Benutzer entsteht (Lernstand, Antworten).

## Consequences

Neue Verben brauchen ein Deployment. Für die Grösse der App ist das unproblematisch.
