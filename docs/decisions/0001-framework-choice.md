# Backend-Framework: FastAPI

Date: 2026-11-19

## Status

Accepted

## Context

Das Backend muss in Python mit Flask, Django oder FastAPI umgesetzt werden. Die App ist klein, bietet vor allem eine REST-Schnittstelle für ein separates Frontend und soll in der Präsentation gut erklärbar sein.

## Options Considered

 * Flask: am einfachsten, im Modul-Template dokumentiert; Validierung und API-Dokumentation müssten selbst gebaut werden.
 * FastAPI: auf REST-Schnittstellen ausgerichtet, automatische Validierung mit Pydantic und automatische API-Dokumentation unter /docs; etwas mehr Konzepte (Typannotationen, Dependencies, ASGI).
 * Django: Full-Stack-Framework mit viel Funktionalität, die hier nicht gebraucht wird; deutlich grössere Einstiegshürde.

## Decision

FastAPI, gestartet mit Uvicorn. Entschieden von Kay.

## Reasons

Die App besteht im Kern aus einer JSON-Schnittstelle. FastAPI prüft Eingaben (z. B. Person 0 bis 5, Name) automatisch und erzeugt eine interaktive API-Dokumentation, die sich in der Präsentation direkt zeigen lässt. Die Typannotationen machen den Code selbsterklärend.

## Consequences

Uvicorn statt Gunicorn als Server; das Dockerfile des Templates wurde angepasst. Die Konzepte Dependency Injection (Datenbank-Session) und Pydantic-Modelle müssen verstanden und erklärt werden können.
