# Erweiterbarkeit: Zeiten als Registry

Date: 2026-11-19

## Status

Accepted

## Context

Die erste Version kennt zwei Zeiten. Später sollen weitere dazukommen (Imperfetto, Futuro, Condizionale, Congiuntivo), ohne Backend, Lernlogik und Frontend umbauen zu müssen. In der ersten Fassung waren die Zeiten an mehreren Stellen fest verdrahtet (if-Abfragen in conjugation.py, feste Freischaltung 'Presente, dann Passato prossimo' in learning.py, feste Auswahl im Frontend).

## Options Considered

 * Fest verdrahtet lassen: am einfachsten heute, aber jede neue Zeit ändert mindestens vier Dateien und die Tests.
 * Registry: Jede Zeit ist ein Objekt (Schlüssel, Bezeichnung, Reihenfolge, Funktion für die Formen, optional Funktion für akzeptierte Varianten) und wird an einer Stelle angemeldet. Alle anderen Teile lesen nur die Registry.
 * Klassenhierarchie mit einer Unterklasse pro Zeit: ebenfalls erweiterbar, aber mehr Struktur als nötig.

## Decision

Registry in conjugation.py (Tense, register, TENSES, tense_order). Entschieden von Kay.

## Reasons

Die Erweiterung wird auf genau eine Stelle reduziert: eine Funktion schreiben und registrieren. Der Lernpfad (learning.unlocked_tenses) leitet die Freischaltung aus der Reihenfolge ab, die Schnittstelle /api/tenses liefert die Liste ans Frontend, Nachschlagen und Fortschritt durchlaufen alle registrierten Zeiten. Einfache Funktionen statt Klassen bleiben leicht verständlich.

## Consequences

Neue Zeit: siehe docs/extending.md. Ein Test registriert eine dritte Test-Zeit und prüft, dass der Lernpfad sie automatisch freischaltet. Zeiten mit eigener Prüflogik (z. B. Angleichung) liefern eine zusätzliche Funktion für die akzeptierten Varianten.
