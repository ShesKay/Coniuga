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

Karteikasten mit 5 Fächern (Wartezeit 1 Minute bis 7 Tage). Start mit 8 Verben; sind 80 % der aktiven Formen sicher (Fach 3 oder höher), kommen 4 Verben dazu. Jede weitere Zeit wird frei, sobald die vorherige bei den ersten 8 Verben zu 80 % sitzt (Reihenfolge aus der Registry, siehe 0010). Entschieden von Kay.

## Reasons

Leicht verständlich, gut testbar und für die Lernenden transparent (Fach wird angezeigt). Die Schwelle lag zuerst bei 60 %. Ein Test zeigte, dass dann mehrere Stufen auf einmal freigeschaltet werden: 8 sichere von 12 Verben ergeben bereits 67 %. Mit 80 % ist das ausgeschlossen (siehe docs/challenges.md).

## Consequences

Die Parameter (Startmenge, Schwelle, Wartezeiten) sind Konstanten in learning.py und können nach eigenen Erfahrungen angepasst werden.
