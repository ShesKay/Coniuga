# Externer Webdienst: Tatoeba für Beispielsätze

Date: 2026-11-19

## Status

Accepted

## Context

Die Aufgabenstellung verlangt einen externen Webdienst. Er soll zum Lernen beitragen, nicht nur Pflicht sein.

## Options Considered

 * Übersetzungsdienst: liefert Übersetzungen, aber keinen Kontext für die geübte Form.
 * KI-Schnittstelle (z. B. OpenRouter): flexible Übungen, aber Kosten, unzuverlässige Antworten und ein öffentlicher Schlüssel als Risiko.
 * Tatoeba-API: freie Sammlung echter Sätze mit Übersetzungen, ohne Schlüssel.

## Decision

Tatoeba-API (/unstable/sentences), Suche nach der exakten konjugierten Form mit deutscher Übersetzung. Entschieden von Kay.

## Reasons

Echte Sätze zeigen die geübte Form im Kontext. Kein Schlüssel, keine Kosten, offene Lizenz (CC BY 2.0 FR mit Quellenlink).

## Consequences

Die API ist als 'unstable' gekennzeichnet und kann sich ändern. Deshalb: Zeitlimit 4 Sekunden, Zwischenspeicher, und bei Fehlern eine leere Liste statt eines Absturzes. Die Tests rufen den Dienst nicht auf.
