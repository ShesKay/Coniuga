# Lernlogik: Karteikasten mit schrittweiser Freischaltung

Date: 2026-11-19

## Status

Accepted

## Context

Die App soll sich an den Lernstand anpassen und den Fortschritt fördern, ohne zu überfordern.

## Options Considered

 * Zufällige Aufgaben: einfach, aber nicht adaptiv.
 * Karteikasten (Leitner) mit fünf Fächern und Wartezeiten.
 * Algorithmen wie SM-2 (Anki): genauer, aber schwerer zu erklären.

## Decision

Karteikasten mit 5 Fächern (Wartezeit 1 Minute bis 7 Tage). Start mit 8 Verben; sind 80 % der aktiven Formen sicher (Fach 3 oder höher), kommen 4 Verben dazu, und der Passato prossimo wird frei. Entschieden von Kay.

## Reasons

Leicht verständlich, gut testbar und für die Lernenden transparent (Fach wird angezeigt). Die Schwelle 80 % verhindert, dass mehrere Stufen auf einmal freigeschaltet werden.

## Consequences

Die Parameter (Startmenge, Schwelle, Wartezeiten) sind Konstanten in learning.py und können nach eigenen Erfahrungen angepasst werden.
