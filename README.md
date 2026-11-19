# Coniuga

Coniuga ist ein adaptiver Konjugationstrainer für Italienisch. Statt Kärtchen
umzudrehen, tippt man die konjugierte Form selbst ein (aktiver Wortschatz).
Die App merkt sich pro Verb, Zeit und Person, wie sicher man ist, fragt
Schwaches häufiger ab und schaltet neue Verben und Zeiten erst frei, wenn die
bisherigen sitzen. Zusätzlich lässt sich jedes Verb nachschlagen, und echte
Beispielsätze zeigen die geübte Form im Kontext.

Projekt im Modul SWEN (HSLU, HS2026).

## Funktionen

| Funktion | Beschreibung |
| --- | --- |
| **Üben** (Kernoperation 1) | Aufgabe wie «noi · andare · Passato prossimo», Antwort eintippen, sofortiges Feedback mit ganzer Konjugationszeile. Fehlende Akzente gelten als «fast richtig». |
| **Nachschlagen** (Kernoperation 2) | Vollständige Tabelle für Presente und Passato prossimo inkl. Hilfsverb und Partizip, mit Knopf «Dieses Verb üben». |
| **Zeitenwahl** | Automatisch (Lernpfad schaltet die nächste Zeit frei) oder eigene Auswahl, z. B. nur Passato prossimo. Die Wahl wird pro Benutzer gespeichert. |
| **Fortschritt** | Sicherheit pro Zeit, Karteikasten-Fächer, Trefferquote, Übungstage, schwächste Verben, letzte Antworten. |
| **Beispielsätze** | Echte italienische Sätze mit deutscher Übersetzung von [Tatoeba](https://tatoeba.org) (externer Webdienst). |

Umfang der ersten Version: 60 häufige Verben (regelmässige, *-isc-*-Verben und
die wichtigsten unregelmässigen), Zeiten Presente und Passato prossimo. Weitere
Zeiten lassen sich über die Zeiten-Registry ergänzen, ohne Backend, Lernlogik
oder Frontend umzubauen (siehe `docs/extending.md`).

## Get started

Voraussetzung: [uv](https://docs.astral.sh/uv/) ist installiert.

```bash
uv sync
uv run uvicorn app.main:app --app-dir src --reload
```

Danach im Browser http://localhost:8000 öffnen. Ohne weitere Einstellung
speichert die App lokal in der SQLite-Datei `coniuga.db`. Die interaktive
API-Dokumentation von FastAPI liegt unter http://localhost:8000/docs.

Für eine andere Datenbank die Umgebungsvariable `DATABASE_URL` setzen, zum
Beispiel in einer Datei `.env` oder direkt:

```bash
DATABASE_URL="postgresql://user:passwort@host/db" uv run uvicorn app.main:app --app-dir src
```

## Tests und Codequalität

```bash
uv run pytest            # Tests inkl. Abdeckung
uv run ruff check src tests
uv run ruff format src tests
```

Die Tests laufen gegen eine eigene SQLite-Datenbank und rufen den externen
Dienst nicht auf. GitHub Actions führt Linter, Formatprüfung, Tests und einen
Docker-Build mit Health-Check bei jedem Push aus (`.github/workflows/ci.yml`).

## Local deployment

```bash
docker build . -t coniuga
docker run -p 8000:8000 coniuga
```

Danach ist die App unter http://localhost:8000 erreichbar.

## Deployment

* **App:** [Render](https://render.com), Docker-Webdienst, beschrieben in
  `render.yaml`. Jeder Push auf `master` löst automatisch ein neues Deployment aus.
* **Datenbank:** PostgreSQL bei [Neon](https://neon.tech). Die Verbindungs-URL
  wird bei Render als Umgebungsvariable `DATABASE_URL` hinterlegt.
* Öffentliche URL: *wird nach dem ersten Deployment eingetragen*

Begründungen siehe `docs/decisions/0006-hosting.md`.

## Understanding the sources

```mermaid
flowchart LR
    FE["Frontend: Vue 3 (CDN)"] -- "HTTP / JSON" --> BE["Backend: FastAPI (main.py)"]
    BE --> ENG["Konjugation (conjugation.py)"]
    BE --> LRN["Lernlogik (learning.py)"]
    BE -- "SQLAlchemy" --> DB[("SQLite lokal / PostgreSQL")]
    BE -- "HTTP" --> TT["Tatoeba API (extern)"]
```

Die App ist in Schichten aufgebaut, damit die eigentliche Logik ohne Web-Framework
und ohne Datenbank testbar ist:

| Datei | Aufgabe |
| --- | --- |
| `src/app/conjugation.py` | Zeiten-Registry und regelbasierte Konjugation: Endungen für *-are/-ere/-ire*, Sonderregeln (*cercare → cerchi*, *mangiare → mangi*, *capire → capisco*), Ausnahmen aus `data/verbs.json`, Antwortprüfung (Akzente, Pronomen, männlich/weiblich bei *essere*). |
| `src/app/learning.py` | Karteikasten (Leitner, 5 Fächer) und Freischaltung: Start mit 8 Verben; sobald 80 % der aktiven Formen sicher sind (Fach ≥ 3), kommen 4 neue Verben bzw. der Passato prossimo dazu. |
| `src/app/db.py` | Datenmodell (Benutzer, Lernstand pro Item, alle Antworten) mit SQLAlchemy. |
| `src/app/examples.py` | Abfrage der Tatoeba-API mit Zeitlimit, Cache und Rückfallebene, falls der Dienst nicht erreichbar ist. |
| `src/app/main.py` | REST-Schnittstelle (FastAPI) und Auslieferung des Frontends. |
| `src/app/static/` | Frontend: `index.html`, `app.js`, `style.css`, für Handys optimiert. |
| `src/app/data/verbs.json` | 60 Verben mit Bedeutung, Hilfsverb, unregelmässigen Formen und Einführungsreihenfolge. |

Weitere Dokumentation:

* `docs/requirements.md`: Anforderungen und Abgrenzung
* `docs/architecture.md`: Architektur, Datenmodell, Schnittstelle
* `docs/decisions/`: 14 Entscheide (Decision Records), Übersicht in `docs/architecture.md`
* `docs/challenges.md`: Herausforderungen und wie sie gelöst wurden
* `docs/extending.md`: neue Zeit oder neues Verb hinzufügen

## Quellen und Lizenzen

* Beispielsätze: [Tatoeba](https://tatoeba.org), Lizenz CC BY 2.0 FR. Jeder
  angezeigte Satz verlinkt auf seine Quelle.
* Die Konjugationen wurden gegen die Verbiste-Daten (via mlconjug3) geprüft;
  Abweichungen betreffen nur veraltete Nebenformen (z. B. *debbo*, *veggo*).
* Code: MIT-Lizenz (siehe `LICENSE`).
* Umgesetzt mit Unterstützung eines KI-Assistenten (Claude, Anthropic).
