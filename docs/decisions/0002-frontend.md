# Frontend: Vue 3 über CDN

Date: 2026-11-19

## Status

Accepted

## Context

Das Frontend ist frei wählbar. Die Dozierenden empfehlen Vue 3 über CDN. Die App braucht mehrere Ansichten (Üben, Nachschlagen, Fortschritt) mit Zustand und soll auf dem Handy gut bedienbar sein.

## Options Considered

 * Eigenes JavaScript: keine Abhängigkeit, aber viel Code für Zustand und Darstellung.
 * Alpine.js oder HTMX: sehr schlank, aber für drei Ansichten mit gemeinsamem Zustand weniger übersichtlich.
 * Vue 3 über CDN: deklarative Verbindung von Daten und Darstellung, kein Build-Schritt.
 * Vue mit Vite, React, Angular: Build-Tools nötig, für den Umfang zu komplex.

## Decision

Vue 3 über CDN, ohne Build-Tools; eigenes CSS ohne Framework. Entschieden von Kay.

## Reasons

Empfehlung der Dozierenden, kein Build-Schritt, Zustand und Darstellung sauber getrennt. Eigenes CSS hält die Abhängigkeiten klein und erlaubt ein gezielt handytaugliches Layout.

## Consequences

Die App braucht beim Laden Zugriff auf das CDN (unpkg). Der Code liegt in drei Dateien (index.html, app.js, style.css) in src/app/static und wird vom Backend ausgeliefert.
