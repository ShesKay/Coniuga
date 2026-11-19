# Hosting: Render (App) und Neon (Datenbank)

Date: 2026-11-19

## Status

Accepted

## Context

Die App muss bis Ende der Prüfungssession öffentlich erreichbar und automatisch deploybar sein. Erfahrung aus einem anderen Projekt: Die Gratis-Datenbank von Render läuft nach 30 Tagen ab.

## Options Considered

 * Render für App und Datenbank: alles an einem Ort, aber die Datenbank läuft nach 30 Tagen ab.
 * Azure App Service: im Template dokumentiert, aber Konto und Konfiguration aufwändiger.
 * Render für die App (Docker) und Neon für PostgreSQL: beide gratis, Neon ohne Ablaufdatum.

## Decision

Render (Docker-Webdienst, render.yaml) und Neon (PostgreSQL). Entschieden von Kay.

## Reasons

Gratis, automatisches Deployment bei jedem Push auf main, Datenbank ohne Ablaufdatum. Das Docker-Image ist dasselbe, das in der CI gebaut und getestet wird.

## Consequences

Der Gratisplan von Render legt die App nach Inaktivität schlafen; der erste Aufruf dauert dann rund eine Minute. Die Verbindungs-URL von Neon muss bei Render als DATABASE_URL hinterlegt werden.
