# Tests

Diese Seite erklärt, welche automatischen Tests es gibt, wie sie laufen und
**wozu** jeder einzelne da ist. Sie ist bewusst in einfacher Sprache
geschrieben: Jeder Test soll sich in einem Satz erklären lassen.

Kurzfassung: **70 Testfälle**, alle grün, **96 % Abdeckung** des Codes, bei
jedem Pull Request automatisch ausgeführt (Stand 21.11.2026).

## Warum wir testen

Coniuga hat zwei Stellen, die stimmen müssen, ohne dass man Fehler sofort
sieht:

1. **Die Konjugation.** Eine falsche Form sieht in der App aus wie eine
   richtige. Wer lernt, lernt dann etwas Falsches.
2. **Die Lernlogik.** Ein Fehler zeigt sich erst nach Tagen Übung, zum
   Beispiel wenn zu viele Verben auf einmal freigeschaltet werden. Im Browser
   ist das kaum nachzustellen; mit einem Test dauert es eine Sekunde.

## Teststufen

| Stufe | Datei | Was geprüft wird | Braucht |
| --- | --- | --- | --- |
| **Unittests Konjugation** | `tests/test_conjugation.py` (34 Fälle) | Formen, Partizipien, Antwortprüfung, Zeiten-Registry, Suche | nichts: keine Datenbank, kein Netz |
| **Unittests Lernlogik** | `tests/test_learning.py` (19 Fälle) | Karteikasten, Freischaltung, Auswahl der nächsten Aufgabe, Fachfilter | nichts |
| **API-Tests** (Integration) | `tests/test_api.py` (17 Fälle) | Endpunkte zusammen mit der Datenbank | eigene SQLite-Testdatenbank (`tests/conftest.py`) |
| **CI** | `.github/workflows/ci.yml` | ruff, Formatprüfung, alle Tests, `node --check` für `app.js`, Docker-Bau mit Health-Check | GitHub Actions |
| **Manuell** | – | Oberfläche im Browser und am Handy | laufende App |

Warum diese Aufteilung: Die Fachlogik (`conjugation.py`, `learning.py`) kennt
weder Web noch Datenbank (Entscheid 0012). Darum lässt sie sich schnell und
isoliert testen, und dort liegen die meisten Tests. Die API-Tests prüfen, dass
die Teile **zusammen** funktionieren: Anfrage rein, Datenbank schreiben,
richtige Antwort raus.

Nicht automatisiert ist die Oberfläche (Vue im Browser). Sie enthält keine
Fachlogik, nur Darstellung. Seit einer Klammer zu viel die ganze Oberfläche
lahmgelegt hat (Herausforderung 16 in `challenges.md`), prüft die CI aber
wenigstens die Syntax von `app.js`. Browser-Tests (z. B. Playwright) wären der
nächste Schritt.

## Ausführen

```bash
uv run pytest                 # alle Tests mit Abdeckungsbericht
uv run pytest tests/test_learning.py -k cascade   # einen einzelnen Test
```

Die Tests laufen gegen eine eigene, jedes Mal neu angelegte
SQLite-Datenbank. Der externe Dienst Tatoeba wird in den Tests **nicht**
aufgerufen, sondern durch eine feste Antwort ersetzt (`monkeypatch` in
`tests/conftest.py`). So hängen die Tests nicht vom Netz ab.

## Verwendete Techniken (und warum)

* **Parametrisierte Tests** (`@pytest.mark.parametrize`): Dieselbe Prüfung
  für viele Verben, z. B. zehn Verben im Presente. Ein neuer Fall ist eine
  neue Zeile, kein neuer Test.
* **Konstruierte Lernstände:** Die Hilfsfunktion `mastered(...)` in
  `test_learning.py` erzeugt in einer Zeile «diese Verben sitzen». So lässt
  sich ein Zustand nach Wochen Übung sofort herstellen.
* **Feste Zeit:** `NOW` ist ein festes Datum, damit «fällig» und «nicht
  fällig» immer gleich ausgehen.
* **Zufall festlegen:** Wo die App zufällig wählt, bekommt der Test einen
  festen Zufallsgenerator (`random.Random(1)`), damit das Ergebnis
  wiederholbar ist.
* **Ersatz für den externen Dienst** (Mock): siehe oben.
* **Zuerst rot, dann grün:** Für die Kaskade bei der Freischaltung kam zuerst
  der Test allein in Pull Request #5 und wurde rot (`assert 24 == 20`). Erst
  danach kam die Korrektur. So ist belegt, dass die Korrektur genau diesen
  Fehler behebt.

## Testkatalog

### Konjugation (`test_conjugation.py`)

| Test | Warum |
| --- | --- |
| `test_presente` (10 Verben) | Regelmässige Verben aller drei Gruppen, Rechtschreibregeln (*cerchi*, *paghi*, *mangi*, *studi*), *-isc-* (*capisco*) und unregelmässige (*andare*, *essere*). |
| `test_participle` (5 Verben) | Regelmässige Partizipien je Gruppe und unregelmässige (*fatto*, *aperto*). |
| `test_passato_prossimo_with_avere` | Hilfsverb *avere* plus Partizip, alle sechs Personen. |
| `test_passato_prossimo_with_essere_shows_both_genders` | Bei *essere* zeigt die Tabelle beide Formen (*andato/a*). |
| `test_all_verbs_conjugate_in_all_tenses` | Jedes der 60 Verben ergibt in jeder Zeit sechs nicht leere Formen. Fängt Fehler in `verbs.json` ab. |
| `test_table_contains_meta_data` | Die Nachschlagetabelle enthält Hilfsverb und «unregelmässig». |
| `test_unknown_verb_raises` | Ein unbekanntes Verb führt zu einem klaren Fehler, nicht zu leeren Formen. |
| `TestCheckAnswer` (7 Fälle) | Antwortprüfung: exakt richtig; Gross-/Kleinschreibung, Leerzeichen und Pronomen werden ignoriert; fehlender Akzent zählt als «fast richtig»; falsche Form; weibliche Form bei *essere*; falsches Hilfsverb; alternatives Partizip (*veduto*). |
| `test_registry_order_and_labels` | Die Zeiten kommen in der Reihenfolge des Lernpfads (Entscheid 0010). |
| `test_registering_a_tense_twice_fails` | Eine Zeit lässt sich nicht versehentlich doppelt registrieren. |
| `test_unknown_tense_raises` | Eine unbekannte Zeit führt zu einem klaren Fehler. |
| `test_find_verbs_italian_and_german` | Suche nach Infinitiv und deutscher Bedeutung, unabhängig von Gross-/Kleinschreibung (F12). |
| `test_find_verbs_german_word_with_several_verbs` | «bleiben» ergibt drei Verben, sortiert nach Häufigkeit. |
| `test_find_verbs_parts_and_reflexive` | Teile einer Bedeutung und «sich …» werden gefunden. |
| `test_find_verbs_no_partial_match` | «geh» findet nichts: nur ganze Wörter, damit «gehen» nicht «hinausgehen» trifft. |

### Lernlogik (`test_learning.py`)

| Test | Warum |
| --- | --- |
| `test_correct_moves_up_and_wrong_resets` | Kernregel des Karteikastens: richtig ein Fach höher, falsch zurück in Fach 1, mit passender Wartezeit. |
| `test_box_has_a_maximum` | Über Fach 5 geht es nicht hinaus. |
| `test_mastery_counts_items_in_box_3_or_higher` | «Sitzt» heisst Fach 3 oder höher. |
| `test_start_with_few_verbs_then_unlock_more` | Start mit 8 Verben; sitzen sie, kommen genau 4 dazu (nicht mehr). |
| `test_passato_prossimo_unlocked_after_first_verbs` | Das Passato prossimo wird erst frei, wenn das Presente bei den ersten 8 Verben sitzt. |
| `test_due_weak_items_come_first` | Fällige Formen im tiefsten Fach kommen zuerst. |
| `test_new_items_when_nothing_is_due` | Ist nichts fällig, kommen neue Formen. |
| `test_focus_on_one_verb_and_tense` | Gezielt ein Verb und eine Zeit üben (F9). |
| `test_last_item_is_not_repeated_immediately` | Dieselbe Aufgabe kommt nicht zweimal hintereinander. |
| `test_progress_summary` | Die Fortschrittsübersicht zählt richtig (F8). |
| `test_own_selection_overrides_learning_path` | Die eigene Zeitenwahl geht vor dem Lernpfad (Entscheid 0011). |
| `test_without_selection_the_learning_path_applies` | Ohne Wahl gilt der Lernpfad. |
| `test_selection_follows_registry_order` | Gewählte Zeiten folgen der Reihenfolge der Registry. |
| `test_verb_expansion_is_measured_in_base_tense_of_selection` | Neue Verben werden in der grundlegendsten gewählten Zeit gemessen, damit eine neu gewählte Zeit die Zahl der Verben nicht senkt. |
| `test_new_tense_is_unlocked_generically` | Eine zusätzlich registrierte Zeit wird ohne Codeänderung freigeschaltet (Erweiterbarkeit, `extending.md`). |
| `test_no_cascade_when_new_block_is_not_practised` | **Die Kaskade:** 16 Verben sitzen, die 4 neuen sind ungeübt, also bleiben es 20, nicht 24. War zuerst rot (Herausforderung 1). |
| `test_box_filter_only_picks_chosen_boxes` | Fachfilter: nur Formen aus den gewählten Fächern (F13). |
| `test_box_filter_counts_new_items_as_box_1` | Neue Formen zählen als Fach 1. |
| `test_box_filter_returns_none_when_nothing_matches` | Liegt in der Auswahl nichts, gibt es keine Aufgabe statt einer falschen. |

### API (`test_api.py`)

| Test | Warum |
| --- | --- |
| `test_health` | Der Health-Check antwortet; Render und die CI verlassen sich darauf. |
| `test_frontend_is_served` | Die Startseite wird ausgeliefert. |
| `test_verbs_and_table` | Verbliste und Nachschlagen (F5), unbekanntes Verb gibt 404. |
| `test_user_login_is_idempotent` | Erster Login legt an, zweiter macht weiter (F1). |
| `test_invalid_name` | Ein Name wie `<script>` wird abgelehnt (Eingabeprüfung). |
| `test_practice_cycle_updates_progress` | **Kernoperation Üben** von Anfang bis Ende: Aufgabe holen, richtig und falsch antworten, Fach und Fortschritt stimmen (F2, F3, F6, F8). |
| `test_focus_exercise` | Gezieltes Üben über die API (F9). |
| `test_unknown_user_and_tense` | Unbekannte Person gibt 404, unbekannte Zeit 400. |
| `test_examples_endpoint_uses_service` | Der Endpunkt für Beispielsätze nutzt den Dienst (F10). |
| `test_parse_tatoeba_response` | Die Antwort von Tatoeba wird richtig gelesen, ohne Netz. |
| `test_database_url_is_converted_for_psycopg` | Die Verbindungsadresse von Neon wird für den Datenbanktreiber umgeschrieben (Entscheid 0006). |
| `test_tenses_endpoint` | Die Zeiten kommen in der richtigen Reihenfolge. |
| `test_tense_selection_is_saved_and_used` | Die Zeitenwahl wird gespeichert und beim Üben verwendet. |
| `test_reset_selection_to_learning_path` | Zurück zu «Automatisch» funktioniert. |
| `test_invalid_tense_selection` | Eine unbekannte Zeit in der Auswahl wird abgelehnt. |
| `test_search_verbs_endpoint` | Suche über die API, inkl. mehrerer Treffer und leerer Eingabe (F12). |
| `test_exercise_box_filter` | Fachfilter über die API, leere Auswahl und ungültiges Fach (F13). |

## Anforderungen und ihre Tests

| Anforderung | Abgedeckt durch |
| --- | --- |
| F1 Anmelden | `test_user_login_is_idempotent`, `test_invalid_name` |
| F2, F3 Üben und Feedback | `test_practice_cycle_updates_progress`, `TestCheckAnswer` |
| F4 *essere* männlich/weiblich | `test_passato_prossimo_with_essere_shows_both_genders`, `TestCheckAnswer` |
| F5 Nachschlagen | `test_verbs_and_table`, `test_table_contains_meta_data` |
| F6 Karteikasten | `test_correct_moves_up_and_wrong_resets`, `test_due_weak_items_come_first` |
| F7 Freischaltung | `test_start_with_few_verbs_then_unlock_more`, `test_passato_prossimo_unlocked_after_first_verbs`, `test_no_cascade_when_new_block_is_not_practised` |
| F8 Fortschritt | `test_progress_summary`, `test_practice_cycle_updates_progress` |
| F9 Gezielt üben | `test_focus_on_one_verb_and_tense`, `test_focus_exercise`, Tests zur Zeitenwahl |
| F10 Beispielsätze | `test_examples_endpoint_uses_service`, `test_parse_tatoeba_response` |
| F12 Nachschlagen auf Deutsch | `test_find_verbs_*`, `test_search_verbs_endpoint` |
| F13 Üben nach Fach | `test_box_filter_*`, `test_exercise_box_filter` |

F11 (weitere Zeiten) ist nicht umgesetzt; dass eine neue Zeit ohne
Codeänderung freigeschaltet würde, prüft `test_new_tense_is_unlocked_generically`.

## Abdeckung

| Modul | Abdeckung | Bemerkung |
| --- | --- | --- |
| `conjugation.py` | 99 % | |
| `learning.py` | 97 % | |
| `main.py` | 98 % | |
| `db.py` | 100 % | |
| `examples.py` | 67 % | Der echte Netzaufruf zu Tatoeba wird in den Tests bewusst ersetzt (siehe oben). |
| **Gesamt** | **96 %** | |

## Grenzen

* Die Tests laufen gegen **SQLite**, die App online gegen **PostgreSQL**.
  SQLAlchemy gleicht die Unterschiede aus (Herausforderung 9), geprüft wird
  das aber nur online. Nächster Schritt: in der CI zusätzlich gegen einen
  PostgreSQL-Container testen.
* Die Oberfläche wird nur von Hand geprüft (siehe Teststufen).
