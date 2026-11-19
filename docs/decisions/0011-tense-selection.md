# Zeitenwahl: eigene Auswahl geht vor dem Lernpfad

Date: 2026-11-19

## Status

Accepted

## Context

Lernende sind unterschiedlich weit. Wer das Presente schon kann, will nicht zuerst 80 % davon nachweisen müssen, um den Passato prossimo zu üben. Gleichzeitig soll es für Anfängerinnen einen geführten Weg geben.

## Options Considered

 * Nur Lernpfad: Zeiten werden ausschliesslich freigeschaltet; streng, aber bevormundend.
 * Auswahl nur innerhalb der freigeschalteten Zeiten: geführt, aber Fortgeschrittene müssen sich durcharbeiten.
 * Eigene Auswahl geht vor, ohne Auswahl gilt der Lernpfad ('Automatisch').

## Decision

Mehrfachauswahl der Zeiten, gespeichert pro Benutzer in der Datenbank (users.tenses). Leer bedeutet 'Automatisch' (Lernpfad). Die Auswahl darf auch gesperrte Zeiten enthalten. Entschieden von Kay.

## Reasons

Lernende kennen ihr Niveau selbst am besten; der Lernpfad bleibt als Standard und Empfehlung erhalten. Die Speicherung in der Datenbank statt im Browser sorgt dafür, dass die Wahl auf Handy und Laptop gleich ist. Die gewählten Zeiten werden immer in der Reihenfolge des Lernpfads sortiert, damit das Verhalten unabhängig von der Klickreihenfolge ist.

## Consequences

Neue Verben kommen dazu, wenn die grundlegendste der geübten Zeiten sitzt (bei Auswahl nur 'Passato prossimo' also der Passato prossimo). So wächst der Wortschatz auch ohne Presente-Übung, und eine neu freigeschaltete Zeit senkt die Zahl der Verben nicht wieder. Die Anzeige erklärt, welcher Modus aktiv ist.
