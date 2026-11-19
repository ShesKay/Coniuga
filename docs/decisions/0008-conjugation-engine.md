# Konjugation regelbasiert mit Ausnahmeliste

Date: 2026-11-19

## Status

Accepted

## Context

Die App muss Formen erzeugen (Nachschlagen) und Antworten prüfen (Üben).

## Options Considered

 * Alle Formen fest in einer Tabelle speichern: einfach, aber viel Datenpflege und keine Logik.
 * Regeln im Code, Ausnahmen in den Daten: wenig Daten, die Regeln sind sichtbar und testbar.
 * KI oder externe Bibliothek: weniger eigener Code, aber nicht nachvollziehbar bzw. nicht verlässlich.

## Decision

Regeln für -are, -ere, -ire (inkl. -isc-, -care/-gare, -iare) in conjugation.py; unregelmässige Formen, Partizipien und Hilfsverb in verbs.json. Entschieden von Kay.

## Reasons

Die Regeln sind der fachlich interessante Teil und lassen sich mit Unittests absichern. Alle 60 Verben wurden gegen die Verbiste-Daten geprüft.

## Consequences

Neue Verben brauchen nur einen Eintrag in verbs.json, unregelmässige zusätzlich ihre Formen.
