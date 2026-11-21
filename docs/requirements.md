# Anforderungen

## Ausgangslage und Ziel

Beim Italienischlernen fehlt oft das **aktive** Konjugieren: Apps wie Duolingo
lassen Formen eher wiedererkennen als selbst bilden, und Konjugationstabellen
muss man sich aus verschiedenen Quellen zusammensuchen.

Coniuga soll
1. Verben gezielt und aktiv konjugieren lassen (Form eintippen),
2. sich an den Lernstand anpassen (Schwaches öfter, Neues erst, wenn Altes sitzt),
3. den Fortschritt sichtbar machen,
4. jedes Verb mit vollständiger Tabelle nachschlagbar machen.

## Benutzer

Lernende auf Niveau A1 bis B1, die unterwegs auf dem Handy üben.

## Funktionale Anforderungen

| ID | Anforderung | Priorität |
| --- | --- | --- |
| F1 | Anmelden nur mit Namen; der Lernstand wird pro Name gespeichert. | Muss |
| F2 | **Üben:** Die App stellt eine Aufgabe (Verb, Person, Zeit), die Antwort wird eingetippt und geprüft. | Muss (Kernoperation) |
| F3 | Feedback: richtig / fast richtig (nur Akzent) / falsch, mit richtiger Form und ganzer Zeile. | Muss |
| F4 | Bei Verben mit *essere* werden männliche und weibliche Formen akzeptiert. | Muss |
| F5 | **Nachschlagen:** Tabelle für Presente und Passato prossimo mit Hilfsverb und Partizip. | Muss (Kernoperation) |
| F6 | Lernlogik: falsch beantwortete Formen kommen bald wieder, sichere seltener (Karteikasten). | Muss |
| F7 | Neue Verben und Zeiten werden schrittweise freigeschaltet. | Muss |
| F8 | Fortschrittsübersicht: Sicherheit pro Zeit, Fächer, Trefferquote, schwächste Verben. | Muss |
| F9 | Gezielt ein Verb oder eine Zeit üben. | Soll |
| F10 | Echte Beispielsätze zur geübten Form (externer Webdienst). | Soll |
| F11 | Weitere Zeiten (Imperfetto, Futuro, Condizionale, Congiuntivo). | Kann (spätere Version) |
| F12 | **Nachschlagen auf Deutsch:** Verben auch über die deutsche Bedeutung finden («gehen» → andare), Auswahl bei mehreren Treffern, Vorschlagsliste beim Tippen, am Handy bedienbar. | Soll |

## Nichtfunktionale Anforderungen

* Bedienbar auf dem Handy (Layout ab 360 px Breite, Akzent-Tasten).
* Öffentlich erreichbar bis Ende der Prüfungssession; automatisches Deployment.
* Fällt der externe Dienst aus, funktioniert der Rest der App weiter.
* Konjugationen fachlich korrekt (geprüft gegen eine Referenz).
* Kern-Logik ohne Web-Framework testbar; Tests laufen automatisch in der CI.

## Abgrenzung (nicht Teil dieser Version)

* Kein Passwort, keine Rollen: Die App enthält keine sensiblen Daten.
* Keine reflexiven Verben (*alzarsi*) und keine weiteren Zeiten.
* Keine KI: Alle Prüfungen sind regelbasiert und damit nachvollziehbar.
