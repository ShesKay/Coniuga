# Antwortprüfung: streng in der Grammatik, tolerant bei Tippdetails

Date: 2026-11-19

## Status

Accepted

## Context

Auf dem Handy fehlen Akzente oft, Lernende schreiben manchmal das Pronomen mit, und bei Verben mit essere gibt es männliche und weibliche Formen. Gleichzeitig sollen echte Fehler (falsches Hilfsverb, falsche Endung) als falsch zählen.

## Options Considered

 * Exakter Textvergleich: einfach, aber 'e' statt 'è' oder 'Io vado' wären falsch.
 * Unscharfer Vergleich (z. B. Ähnlichkeit in Prozent): tolerant, würde aber auch echte Fehler durchlassen.
 * Gezielte Toleranzen: Gross/Klein und Leerzeichen ignorieren, passendes Pronomen entfernen, alle korrekten Varianten akzeptieren, fehlende Akzente als eigener Status 'fast richtig'.

## Decision

Gezielte Toleranzen mit drei Ergebnissen: richtig, fast richtig (Akzent), falsch. 'Fast richtig' zählt im Karteikasten als richtig, wird aber angezeigt. Entschieden von Kay.

## Reasons

Jede Toleranz ist bewusst und einzeln getestet. Akzente sind im Italienischen bedeutungsrelevant (e/è), deshalb wird der Fehler gezeigt; ihn als falsch zu werten, würde auf dem Handy aber frustrieren. Akzent-Tasten im Frontend helfen zusätzlich.

## Consequences

Falsches Pronomen (z. B. 'tu vado') wird nicht entfernt und zählt als falsch. Alternative Partizipien (veduto, perduto) sind in den Verbdaten hinterlegt.
