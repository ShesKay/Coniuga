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

## Ausblick: Schriftliche Unterhaltung mit einer KI

Idee: Nach dem Training kurze Gespräche auf Italienisch führen, in denen die
geübten Verben vorkommen. Das ist nicht umgesetzt; so würde es eingebaut:

* **Backend:** neuer Endpunkt in `main.py` (zum Beispiel `POST /api/chat`), der
  die Nachricht an ein Sprachmodell weiterreicht. Die Logik dazu (welche Verben
  und Zeiten die Person gerade lernt, Anweisung an das Modell) gehört in ein
  eigenes Modul, wie `examples.py` für Tatoeba (Entscheid 0012).
* **Schlüssel:** Der API-Schlüssel des Anbieters wird wie `DATABASE_URL` als
  Umgebungsvariable bei Render hinterlegt. Der Browser ruft das Modell nie
  direkt auf, sonst wäre der Schlüssel öffentlich sichtbar.
* **Anbieter:** Möglich sind die Schnittstelle eines Anbieters direkt, ein
  Vermittler wie OpenRouter oder das AI Gateway von Neon. Alle drei bieten eine
  Schnittstelle, die mit der von OpenAI kompatibel ist; der Wechsel ist also
  vor allem eine andere Adresse und ein anderer Schlüssel. Das AI Gateway lässt
  sich im Neon-Projekt auch später noch einschalten.
* **Wie bei Tatoeba:** Timeout und Rückfallebene, damit die App weiterläuft,
  wenn der Dienst nicht antwortet; in den Tests wird der Dienst ersetzt (Mock).
* **Neu zu klären:** Kosten pro Nachricht, Begrenzung der Anfragen pro Person
  (heute gibt es kein Rate Limiting) und Datenschutz, weil Texte an einen
  externen Anbieter gehen.
