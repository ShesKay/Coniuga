# Schichten: Fachlogik ohne Web-Framework und Datenbank

Date: 2026-11-19

## Status

Accepted

## Context

Die anspruchsvollsten Teile sind fachlich (Konjugationsregeln, Lernlogik). Sie sollen gründlich getestet und in der Präsentation erklärt werden können.

## Options Considered

 * Alles in den Routen von main.py: wenig Dateien, aber Logik nur über HTTP testbar und mit Datenbank verflochten.
 * Schichten: conjugation.py und learning.py sind reines Python; main.py übersetzt zwischen HTTP, Datenbank und Fachlogik.

## Decision

Schichten. learning.py arbeitet mit einfachen Datenobjekten (ItemState) statt mit Datenbankzeilen. Entschieden von Kay.

## Reasons

Die Fachlogik ist mit schnellen Unittests ohne Server und Datenbank prüfbar (die meisten der Tests). Ein Wechsel des Frameworks oder der Datenbank würde die Fachlogik nicht berühren.

## Consequences

main.py muss den Lernstand laden, umwandeln und wieder speichern; das ist etwas mehr Code als ein direkter Zugriff. Diese Regel ist in AGENTS.md festgehalten.
