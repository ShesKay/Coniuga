# Umfang der ersten Version

Date: 2026-11-19

## Status

Accepted

## Context

Die Zeit für das Projekt ist knapp. Gleichzeitig soll die App im Alltag nützlich sein.

## Options Considered

 * Nur Presente: sehr sicher umsetzbar, aber für den Alltag zu wenig.
 * Presente und Passato prossimo mit rund 60 häufigen Verben.
 * Zusätzlich Imperfetto und Futuro: mehr Nutzen, aber mehr Daten und Testaufwand.

## Decision

Presente und Passato prossimo, 60 Verben. Entschieden von Kay.

## Reasons

Die beiden Zeiten decken den Grossteil der Alltagssprache ab. Der Passato prossimo bringt die interessanten Regeln (Hilfsverb, Partizip, Angleichung bei essere). Weitere Zeiten lassen sich in conjugation.py und learning.py ohne Umbau ergänzen.

## Consequences

Reflexive Verben und weitere Zeiten sind bewusst ausgeschlossen (siehe docs/requirements.md).
