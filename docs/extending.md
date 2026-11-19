# Coniuga erweitern

## Eine neue Zeit hinzufügen (Beispiel Imperfetto)

Dank der Zeiten-Registry (`decisions/0010-tense-registry.md`) betrifft eine
neue Zeit nur `conjugation.py`, die Verbdaten und die Tests. Backend,
Lernpfad, Nachschlagen, Fortschritt und die Zeitenwahl im Frontend passen sich
automatisch an.

**1. Formen bilden** in `src/app/conjugation.py`, z. B.:

```python
_IMPERFETTO_ENDINGS = ["vo", "vi", "va", "vamo", "vate", "vano"]


def imperfetto(verb: Verb) -> list[str]:
    if verb.imperfetto:  # unregelmässig, z. B. essere: ero, eri, era …
        return list(verb.imperfetto)
    base = verb.infinitive[:-2]  # parlare -> parla, prendere -> prende
    return [base + e for e in _IMPERFETTO_ENDINGS]
```

**2. Registrieren**, mit der Position im Lernpfad:

```python
register(Tense("imperfetto", "Imperfetto", 3, imperfetto))
```

**3. Ausnahmen in den Daten** ergänzen (`src/app/data/verbs.json`), z. B.
`"imperfetto": ["ero", "eri", "era", "eravamo", "eravate", "erano"]` bei
*essere*, ebenso bei *fare* (*facevo*), *dire* (*dicevo*), *bere* (*bevevo*).
Dazu im Dataclass `Verb` ein Feld `imperfetto` und in `load_verbs()` das
Einlesen ergänzen.

**4. Tests** in `tests/test_conjugation.py` für ein regelmässiges Verb pro
Gruppe und für die Ausnahmen. Den Test `test_registry_order_and_labels` um die
neue Zeit erweitern.

**5. Prüfen**, dass im Frontend unter «Zeiten» die neue Zeit erscheint und im
Nachschlagen eine dritte Tabelle angezeigt wird.

Für Zeiten mit mehreren richtigen Antworten (z. B. zusammengesetzte Zeiten mit
*essere*) wird beim Registrieren zusätzlich eine Funktion für die akzeptierten
Varianten übergeben, wie beim Passato prossimo.

## Ein neues Verb hinzufügen

Eintrag in `src/app/data/verbs.json`:

```json
{"infinitive": "camminare", "meaning": "gehen, wandern", "auxiliary": "avere", "rank": 61}
```

Unregelmässige Verben erhalten zusätzlich `presente` (sechs Formen) und/oder
`participle`; *-isc-*-Verben `"isc": true`. Der `rank` bestimmt, wann das Verb
im Lernpfad eingeführt wird.

## Datenbankschema ändern

Die Tabellen werden beim Start mit `create_all` angelegt. Das legt neue
Tabellen an, ändert aber keine bestehenden. Für spätere Änderungen an
bestehenden Tabellen (neue Spalte) wird ein Migrationswerkzeug wie Alembic
empfohlen.
