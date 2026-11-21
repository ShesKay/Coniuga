# Lernlogik überarbeitet: Langzeit statt Kurzzeit, dosiert statt in Blöcken

Date: 2026-11-21

## Status

Accepted (Umsetzung nach der Abgabe; ersetzt Teile von 0009)

Nachtrag 21.11.2026: Aus Punkt 9 ist das Üben nach Fach vorgezogen (Anforderung F13): Fächer 1 bis 5 einzeln wählbar, neue Formen zählen als Fach 1, Hinweis statt Aufgabe, wenn die Auswahl leer ist. Es gelten noch die Fächer und Regeln aus 0009; Fach-Namen, Anzahl pro Fach und der Satz «Du übst: …» folgen mit der übrigen Umsetzung.

## Context

Beim Üben am Handy (21.11.2026) sind drei Schwächen der Lernlogik aus 0009 aufgefallen:

1. **Kurzzeitgedächtnis statt Lernen.** Eine Form gilt ab Fach 3 als «sicher». Dorthin kommt man mit zwei richtigen Antworten im Abstand von 10 Minuten. Zudem steigt eine Karte bei jeder richtigen Antwort, auch wenn sie noch gar nicht fällig war. Wer ein Verb auswählt, bringt so alle Formen in wenigen Minuten bis Fach 5.
2. **Kaskade.** Neue Verben kommen in Blöcken (Start 8, dann je 4), sobald 80 % der aktiven Formen sitzen. Ab 16 sicheren Verben sind 16 von 20 bereits 80 %, und der nächste Block wird frei, bevor die 4 neuen Verben geübt sind. Die Behauptung in 0009, 80 % schliesse das aus, war falsch.
3. **Fächer ohne Bedeutung für Benutzer.** «Fach 3» sagt einem Laien nichts, und man kann nicht gezielt nach Fächern üben.

## Options Considered

 * **Blöcke behalten, nur die Kaskade beheben:** kleinste Änderung, löst aber das Kurzzeitproblem nicht.
 * **Alle 60 Verben von Anfang an gemischt:** keine Blöcke, also keine Kaskade; aber 360 neue Karten auf einmal überfordern Anfänger, jede Karte kommt selten dran, man liegt meistens falsch.
 * **Alle Verben im Spiel, neue Karten dosiert:** keine Blöcke, häufige Verben zuerst, höchstens etwa jede dritte Aufgabe neu (Lernprogramme wie Anki begrenzen neue Karten ähnlich).

## Decision

Entschieden von Kay, nach Abwägung mit Claude:

1. **Dosiert statt in Blöcken.** Alle Verben sind im Spiel; neue Karten werden dosiert eingemischt (häufige zuerst). Damit entfällt die Freischaltung in Blöcken und mit ihr die Kaskade.
2. **«Gelernt» heisst ab Fach 4.** Dafür muss eine Karte auch am nächsten Tag noch richtig sein (Langzeitgedächtnis).
3. **Aufstieg nur, wenn fällig.** Eine richtige Antwort vor Ablauf der Wartezeit zählt in der Statistik, ändert das Fach aber nicht.
4. **Fach 1 nach 2 braucht zwei richtige Antworten**, danach je eine.
5. **Abstand:** dieselbe Aufgabe frühestens nach 10 anderen; sind weniger Formen ausgewählt, wird der Abstand automatisch kleiner.
6. **Zurückfallen abgestuft:** ein Fehler kostet ein Fach; jeder weitere Fehler hintereinander (ohne richtige Antwort dazwischen) ein Fach mehr, bis Fach 1. Die falsche Karte kommt bald wieder.
7. **Sechstes Fach** und **Namen für Benutzer:**

| Fach | Name | Bedeutung | kommt wieder nach |
| --- | --- | --- | --- |
| (keins) | Neu | noch nie geübt | |
| 1 | Unsicher | gerade falsch oder erst gesehen | 1 Minute |
| 2 | Im Aufbau | zweimal richtig | 10 Minuten |
| 3 | Frisch gelernt | heute richtig, morgen kommt die Probe | 1 Tag |
| 4 | Sitzt | auch am nächsten Tag richtig | 3 Tage |
| 5 | Gefestigt | auch nach 3 Tagen richtig | 7 Tage |
| 6 | Gemeistert | auch nach einer Woche richtig; Kontrolle | 30 Tage |

8. **Passato prossimo pro Verb:** Sitzt ein Verb im Presente (alle 6 Formen ab Fach 4), mischt «Automatisch» das Passato prossimo dieses Verbs dazu, statt eine Zeit global freizuschalten.
9. **Üben nach Wahl:** «Automatisch» oder gezielt nach Verb, Zeit und Fach (kombinierbar, mit Anzahl pro Fach und einem Satz «Du übst: …»). Ist in der Auswahl nichts mehr fällig, erscheint ein Hinweis mit Vorschlägen statt einer Endlosschleife.

## Reasons

Die Fächer messen damit, was jemand wirklich behalten hat, nicht was er vor zwei Minuten gesehen hat. Ohne Blöcke gibt es keine Schwellen-Kaskaden mehr; das Problem verschwindet, statt geflickt zu werden. Die Namen machen den Lernstand für Benutzer verständlich und zeigen die Stufe des Gedächtnisses: heute, morgen, nach Tagen, nach Wochen. Die Werte (Dosierung, Abstand 10, Fach 4) sind Annahmen aus der eigenen Nutzung und nicht mit weiteren Lernenden geprüft.

## Consequences

* Bis zur Umsetzung gilt 0009; die Kaskade wird dort als Sofortmassnahme behoben (nur erweitern, wenn auch der zuletzt dazugekommene Block zu 80 % sitzt).
* Das Passato prossimo erscheint im Lernpfad frühestens nach etwa 4 Tagen. Wer früher will, wählt die Zeit selbst (0011).
* Für die Eskalation beim Zurückfallen braucht es die letzten Antworten pro Karte; sie stehen bereits in der Tabelle `attempts`, eine Änderung der Datenbank ist nicht nötig. Das sechste Fach ist nur ein weiterer Zahlenwert in `progress.box`.
* Anforderungen F6, F7 und F9 werden bei der Umsetzung angepasst.
