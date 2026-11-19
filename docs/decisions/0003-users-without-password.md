# Benutzer: Name ohne Passwort

Date: 2026-11-19

## Status

Accepted

## Context

Die App ist öffentlich erreichbar. Der Lernstand ist persönlich, enthält aber keine sensiblen Daten.

## Options Considered

 * Kein Benutzer, ein gemeinsamer Lernstand: am einfachsten, aber jede besuchende Person verändert den Lernstand.
 * Name ohne Passwort: jede Person hat ihren eigenen Lernstand; wer den Namen kennt, kann ihn mitbenutzen.
 * Echte Anmeldung mit Passwort: sicher, aber Aufwand für Passwort-Hashing, Sessions und Zurücksetzen.

## Decision

Name ohne Passwort. Entschieden von Kay.

## Reasons

Trennt den Lernstand verschiedener Personen mit minimalem Aufwand. Da keine sensiblen Daten gespeichert werden, ist das Risiko gering. Der Name wird im Browser gespeichert, damit man nicht bei jedem Besuch neu eintippen muss.

## Consequences

Namen werden validiert (2 bis 30 Zeichen, nur Buchstaben, Zahlen, Leerzeichen, _ . -). Eine echte Anmeldung wäre eine mögliche Erweiterung.
