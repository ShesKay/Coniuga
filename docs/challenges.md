# Herausforderungen und Lösungen

Dieses Dokument hält fest, wo es bei der Umsetzung schwierig wurde, wie das
Problem gelöst wurde und womit die Lösung abgesichert ist. Die mit **★**
markierten Punkte eignen sich als «technische Herausforderung» für die
Präsentation.

| Nr | Herausforderung | Bereich |
| --- | --- | --- |
| 1 ★ | Freischaltung schaltete mehrere Stufen auf einmal frei | Lernlogik |
| 2 ★ | Rechtschreibregeln beim Konjugieren | Konjugation |
| 3 ★ | Passato prossimo mit *essere*: mehrere richtige Antworten | Konjugation, Prüfung |
| 4 ★ | Zeiten nachträglich erweiterbar machen | Architektur |
| 5 | Zeitenwahl und Lernpfad sinnvoll kombinieren | Lernlogik, UX |
| 6 | Antworten tolerant, aber nicht nachlässig prüfen | Prüfung |
| 7 | Korrektheit der Verbdaten nachweisen | Daten |
| 8 | Unzuverlässiger externer Dienst | Webdienst |
| 9 | Zwei Datenbanken mit einem Code | Persistenz |
| 10 | Gratis-Datenbank mit Ablaufdatum | Deployment |
| 11 | Linter-Regel gegen FastAPI-Muster | Codequalität |
| 12 | Branch-Name im CI und Deployment | Deployment |

---

## 1 ★ Freischaltung schaltete mehrere Stufen auf einmal frei

**Problem:** Neue Verben kommen dazu, sobald ein bestimmter Anteil der aktiven
Formen sicher ist. Mit einer Schwelle von 60 % sprang die App von 8 direkt auf
16 Verben: Nach der ersten Erweiterung auf 12 Verben waren 8 von 12 Verben
sicher, also 67 %, was wieder über 60 % lag. Die Schleife erweiterte erneut.

**Gefunden:** durch den Unittest `test_start_with_few_verbs_then_unlock_more`,
der genau 12 aktive Verben erwartete und 16 erhielt.

**Lösung:** Schwelle auf 80 % angehoben. Damit gilt: 8 sichere von 12 Verben
ergeben 67 %, also bleibt es bei 12. Allgemein muss die Schwelle über
`START / (START + STEP)` liegen, hier 8 / 12 = 67 %.

**Code:** `learning.py`, `UNLOCK_THRESHOLD` und `active_verb_count`.
**Abgesichert:** `tests/test_learning.py`.

**Lerneffekt:** Ein Test mit konkreten Erwartungswerten hat einen Denkfehler im
Algorithmus aufgedeckt, den eine reine Sichtprüfung im Browser kaum gezeigt
hätte.

## 2 ★ Rechtschreibregeln beim Konjugieren

**Problem:** Regelmässige Verben folgen nicht einfach «Stamm + Endung»:
* *cercare* → *cer**ch**i*, *cer**ch**iamo* (sonst würde sich die Aussprache ändern)
* *mangiare* → *mangi*, *mangiamo* (nicht *mangii*, *mangiiamo*)
* *capire* → *cap**isc**o*, aber *capiamo* (Erweiterung mit *-isc-*)

**Lösung:** Die Regeln sind im Code als kleine, kommentierte Sonderfälle
umgesetzt; echte Ausnahmen (*andare*, *fare* …) stehen als Daten in
`verbs.json`.

**Code:** `conjugation.py`, `_regular_presente`.
**Abgesichert:** parametrisierte Tests mit je einem Verb pro Regel.

## 3 ★ Passato prossimo mit *essere*: mehrere richtige Antworten

**Problem:** Bei Verben mit *essere* richtet sich das Partizip nach dem Subjekt:
*sono andato* (m) und *sono andata* (w) sind beide richtig. Die Tabelle soll
beides zeigen, die Prüfung beides akzeptieren.

**Lösung:** Getrennt in «Anzeigeform» (`sono andato/a`) und «akzeptierte
Varianten» (`["sono andato", "sono andata"]`). Die Registry erlaubt pro Zeit
eine eigene Funktion für akzeptierte Varianten. Dasselbe Prinzip deckt
alternative Partizipien ab (*ho visto* und *ho veduto*).

**Code:** `conjugation.py`, `passato_prossimo`, `passato_prossimo_variants`.
**Abgesichert:** `TestCheckAnswer`.

## 4 ★ Zeiten nachträglich erweiterbar machen

**Problem:** In der ersten Fassung waren die zwei Zeiten an vier Stellen fest
verdrahtet (if-Abfragen, feste Freischaltung, feste Bezeichnungen, feste
Auswahl im Frontend). Eine weitere Zeit hätte überall Änderungen verlangt.

**Lösung:** Zeiten-Registry. Jede Zeit wird einmal angemeldet; Backend,
Lernpfad und Frontend lesen die Liste dynamisch. Der Lernpfad leitet die
Freischaltung aus der Reihenfolge ab.

**Code:** `conjugation.py` (Registry), `learning.py` (`unlocked_tenses`),
`main.py` (`/api/tenses`), `static/app.js`.
**Abgesichert:** `test_new_tense_is_unlocked_generically` registriert eine
dritte Test-Zeit und prüft, dass sie automatisch im Lernpfad erscheint.
Anleitung: `docs/extending.md`. Entscheid: `decisions/0010`.

## 5 Zeitenwahl und Lernpfad sinnvoll kombinieren

**Problem:** Wählt jemand nur den Passato prossimo, würde die bisherige Logik
neue Verben erst freigeben, wenn das (gar nicht geübte) Presente sitzt. Und
beim automatischen Freischalten einer neuen Zeit wäre die Zahl der Verben
kurzzeitig wieder gesunken.

**Lösung:** Die eigene Auswahl geht vor (`practice_tenses`). Neue Verben werden
an der grundlegendsten der *geübten* Zeiten gemessen.

**Code:** `learning.py`. **Abgesichert:**
`test_verb_expansion_is_measured_in_base_tense_of_selection`,
`test_tense_selection_is_saved_and_used`. Entscheid: `decisions/0011`.

## 6 Antworten tolerant, aber nicht nachlässig prüfen

**Problem:** Auf dem Handy fehlen Akzente, manche tippen das Pronomen mit,
Gross/Klein variiert. Echte Fehler müssen trotzdem erkannt werden.

**Lösung:** Gezielte Toleranzen statt unscharfem Vergleich, drittes Ergebnis
«fast richtig» für fehlende Akzente, Akzent-Tasten im Frontend.
Entscheid: `decisions/0013`.

## 7 Korrektheit der Verbdaten nachweisen

**Problem:** Eine Lern-App mit falschen Formen schadet mehr, als sie nützt.

**Lösung:** Alle 60 Verben wurden mit einem Skript gegen die Verbiste-Daten
(Teil der Bibliothek mlconjug3) verglichen. Die 11 Abweichungen betrafen
ausschliesslich veraltete Nebenformen (*debbo*, *veggo*, *fo*) oder Fehler in
der Referenz selbst (*bere*). Echte Alternativen (*veduto*, *perduto*) werden
seither ebenfalls akzeptiert.

## 8 Unzuverlässiger externer Dienst

**Problem:** Die Tatoeba-Schnittstelle ist als «unstable» gekennzeichnet und
kann langsam oder nicht erreichbar sein.

**Lösung:** Zeitlimit von 4 Sekunden, Zwischenspeicher pro Suchbegriff, bei
Fehlern eine leere Liste mit Hinweis im Frontend statt eines Absturzes. In den
Tests wird der Dienst ersetzt (Mock), damit die Tests nicht vom Internet
abhängen; die Auswertung der Antwort ist separat getestet.

## 9 Zwei Datenbanken mit einem Code

**Problem:** Lokal und in Tests SQLite, produktiv PostgreSQL. Neon liefert
URLs mit `postgres://` oder `postgresql://`, SQLAlchemy braucht
`postgresql+psycopg://`.

**Lösung:** SQLAlchemy als gemeinsame Schicht, Umwandlung der URL in
`database_url()`. Zusätzlich lokal gegen einen echten PostgreSQL-Server
getestet. **Abgesichert:** `test_database_url_is_converted_for_psycopg`.

## 10 Gratis-Datenbank mit Ablaufdatum

**Problem:** Die App muss bis Ende der Prüfungssession laufen; die
Gratis-Datenbank von Render wird nach 30 Tagen gelöscht.

**Lösung:** App auf Render, Datenbank bei Neon (ohne Ablaufdatum).
Entscheid: `decisions/0006`.

## 11 Linter-Regel gegen FastAPI-Muster

**Problem:** Ruff meldete `B008` («kein Funktionsaufruf in Standardwerten»)
für das übliche FastAPI-Muster `session: Session = Depends(get_session)`.

**Lösung:** Statt die Regel abzuschalten, die von FastAPI empfohlene
Schreibweise mit `Annotated` verwendet (`SessionDep`). Der Code ist dadurch
auch kürzer.

## 12 Branch-Name im CI und Deployment

**Problem:** Das Template-Repository verwendet `master`, die CI und
`render.yaml` waren zuerst auf `main` eingestellt. Der erste Push schlug fehl.

**Lösung:** Beide auf `master` umgestellt. Lerneffekt: Konfigurationen, die
sich auf Namen beziehen, beim Aufsetzen gegen das echte Repository prüfen.
