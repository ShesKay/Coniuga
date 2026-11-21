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
| 13 | Git-Repo in einem OneDrive-Ordner | Entwicklungsumgebung |
| 14 | Git-Ablauf verstehen: add, commit, push | Entwicklungsumgebung |
| 15 | Backend fertig, aber in der App nichts zu sehen | Architektur, Vorgehen |
| 16 | Eine Klammer zu viel legt die ganze Oberfläche lahm | Frontend, Qualitätssicherung |
| 17 | Editor formatierte anders als die Prüfung (Black statt Ruff) | Entwicklungsumgebung, Qualitätssicherung |

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

**Nachtrag (21.11.2026): Die 80 % lösten das Problem nur teilweise.** Die
Formel `START / (START + STEP)` gilt nur für den ersten Schritt. Später wächst
der Anteil der sicheren Verben mit: Ab 16 sicheren Verben sind 16 von 20
bereits 80 %, und die App schaltete sofort auf 24, obwohl die 4 neuen Verben
noch nie geübt waren. Nachgewiesen mit dem Test
`test_no_cascade_when_new_block_is_not_practised` (zuerst rot:
`assert 24 == 20`, Pull Request #5). **Korrektur:** Neue Verben gibt es nur,
wenn auch der zuletzt dazugekommene Block zu 80 % sitzt (`newest` in
`active_verb_count`). **Lerneffekt:** Eine Schwelle, die für den ersten Fall
stimmt, muss nicht für alle Fälle stimmen; Tests für den allgemeinen Fall
schreiben, nicht nur für den Start. Mit Entscheid 0015 werden die Blöcke
später ganz ersetzt.

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

## 13 Git-Repo in einem OneDrive-Ordner

**Ausgangslage (21.11.2026):** Für eigene Commits wurde das Repo mit Git und
VS Code auf den Laptop geklont. Als Ort wurde bewusst ein Ordner gewählt, den
OneDrive synchronisiert (Studienordner der Hochschule), obwohl Git und
Cloud-Synchronisation als heikle Kombination gelten. Ziel: Erfahrung sammeln,
das Risiko ist begrenzt, weil GitHub die eigentliche Sicherung ist.

**Bekannte Risiken (vorher recherchiert):**

* OneDrive lädt beim Klonen Hunderte kleine Dateien im Ordner `.git` hoch und
  sperrt sie dabei kurz. Git kann dann «Permission denied» melden.
* Bei mehreren Geräten legt OneDrive Konfliktkopien an (zum Beispiel
  `FETCH_HEAD-computername`), im schlimmsten Fall wird das Repo unlesbar.
* Mit «Dateien bei Bedarf» lagert OneDrive selten genutzte Dateien in die
  Cloud aus. Git wird dann langsam oder bricht offline ab («Der
  Clouddateianbieter wird nicht ausgeführt»).

**Vorbeugung:** Ordner auf «Immer auf diesem Gerät beibehalten» gestellt,
damit nichts ausgelagert wird. Name und E-Mail nur für dieses Repo gesetzt
(`git config` ohne `--global`), Anmeldung bei GitHub über das Konto im
Klon-Link (`https://ShesKay@github.com/...`), damit das private Konto auf dem
Laptop unberührt bleibt.

**Beobachtung:** Direkt nach dem Klonen (14:13) zeigte der Explorer beim
Ordner `Coniuga` das Symbol «wird synchronisiert». Im Dialog «Ordner öffnen»
von VS Code liess sich der Ordner in diesem Moment nicht wie gewohnt
auswählen. Keine Fehlermeldung von Git.

**Ursache (Einschätzung):** OneDrive hat die frisch angelegten Dateien
hochgeladen. Das Problem ist zeitlich begrenzt und betrifft nur die lokale
Entwicklung, nicht die App online: Render baut aus GitHub, nicht vom Laptop.

**Mögliche Workarounds und wie sie getestet werden:**

| Workaround | Test | Ergebnis |
| --- | --- | --- |
| Warten, bis OneDrive fertig ist | Status im Explorer wechselt auf grünen Haken, danach Ordner öffnen | offen |
| Ordner aus dem Terminal öffnen statt über den Dialog | im Ordner `code . -r` ausführen | offen |
| Synchronisierung während der Arbeit mit Git anhalten | OneDrive pausieren, `git status`, `git commit`, `git push`, danach fortsetzen | offen |
| Repo auf Schäden prüfen | `git fsck` meldet keine Fehler, `git status` zeigt nur die eigenen Änderungen | offen |
| Ausweichen: Repo ausserhalb von OneDrive | neu klonen nach `C:\Users\Kay\Projekte`, Ablauf wiederholen | nur falls nötig |

**Faustregel:** Nach jedem abgeschlossenen Schritt committen und pushen.
Geht lokal etwas kaputt, ist höchstens die letzte Arbeit verloren; das Repo
lässt sich jederzeit neu klonen.

**Lerneffekt:** Die Entwicklungsumgebung ist Teil des Projekts. Werkzeuge, die
dieselben Dateien verwalten wollen (Git und OneDrive), vor dem Einsatz
abwägen und Ausweichwege bereithalten.

## 14 Git-Ablauf verstehen: add, commit, push

**Problem:** In früheren Projekten wurde zuerst im Terminal direkt mit
`git commit` und `git push` gearbeitet, ohne `git add`. Das funktionierte
nicht wie erwartet; später wurde auf den Knopf «Commit» in VS Code
gewechselt. Warum es dort klappte, blieb unklar. Beim ersten eigenen Commit
für Coniuga (21.11.2026) zeigte `git status` die Meldung «no changes added to
commit», obwohl 7 Dateien geändert waren. Das wirkte zuerst wie «keine
Änderungen».

**Ursache:** Ein Commit entsteht bei Git in zwei Schritten. `git add` legt
Änderungen in den Vorbereitungsbereich (Staging Area), `git commit` speichert
nur, was dort liegt. Hochladen ist ein dritter Schritt (`git push`). Viele
Werkzeuge verstecken `git add`: der Knopf «Commit» in VS Code bietet an, alle
Änderungen automatisch vorzumerken («Smart Commit»), `git commit -a` tut
dasselbe, und beim Bearbeiten direkt auf github.com gibt es den Schritt gar
nicht. Die Meldung «no changes added to commit» heisst also: Änderungen sind
da, aber noch nicht vorgemerkt.

**Lösung:** Den Ablauf einmal bewusst von Hand gemacht, mit zwei absichtlich
eingebauten Fehlern (21.11.2026):

1. **Änderungen auf master statt auf einem Branch.** Die 7 geänderten
   Dateien lagen zuerst auf `master`; `git status` zeigte `On branch master`.
   Ein Commit und Push hätte die Änderung ungeprüft live geschaltet, weil
   Render jeden Push auf master sofort ausliefert. Rettung, solange noch
   nichts committet ist: `git switch -c deutsch-nachschlagen` legt den Branch
   an, die offenen Änderungen wandern mit.
2. **Nur einen Teil vorgemerkt.** Mit `git add` nur die 5 Code-Dateien
   ausgewählt, die 2 Testdateien absichtlich nicht. `git status` zeigt das
   deutlich in zwei Gruppen: grün unter «Changes to be committed» (im
   Vorbereitungsbereich), rot unter «Changes not staged for commit» (bleibt
   draussen). Der Commit enthält nur die grünen Dateien; die Tests werden in
   einem zweiten Commit nachgereicht, der als Übung gekennzeichnet ist.

Dazu ein echter Fehler beim Weiterarbeiten: nach `git add .` direkt
`git push`, ohne `git commit`. Git meldete «Everything up-to-date» und lud
nichts hoch. Ein Push schickt nur Commits; was nur im Vorbereitungsbereich
liegt, ist noch kein Commit. Lösung: zuerst `git commit`, dann `git push`.

Zwei weitere echte Stolpersteine am selben Abend:

* **Vim im Terminal:** `git commit` ohne `-m "Nachricht"` öffnet den
  Texteditor Vim im Terminal. Der danach eingefügte Befehl landete als Text in
  der Commit-Nachricht, und das Terminal schien zu hängen. Ausweg: `Esc`,
  dann `:q!` und Enter (beendet ohne Speichern, der Commit wird abgebrochen,
  nichts geht verloren). Für später: `git config core.editor "code --wait"`
  öffnet stattdessen VS Code.
* **Falscher Ordner:** In einem neuen Terminal stand der Pfad eine Ebene über
  dem Repo. Git meldete «fatal: not a git repository». Mit `cd Coniuga` in den
  Repo-Ordner wechseln; vor jedem Git-Befehl auf den Pfad vor `>` schauen.

Und die automatische Prüfung hat ihren Zweck erfüllt: Pull Request #2 war rot
(«1 failing»). Ursache: In beiden Testdateien fehlte am Ende der letzte
Zeilenumbruch; `ruff format --check` verlangt ihn. Inhaltlich waren alle 65
Tests grün. Behoben mit einem weiteren Commit auf demselben Branch; der Pull
Request übernimmt neue Commits automatisch und prüft erneut. Vorbeugung:
In VS Code die Einstellung `"files.insertFinalNewline": true` setzen.

Wiederkehrendes Muster: Mehrmals wurde `git add` ausgeführt, bevor die
Datei im Editor gespeichert war. Git meldete dann «nothing to commit», weil
es nur den gespeicherten Stand kennt. Abhilfe: in VS Code «File → Auto Save»
einschalten.

Zu früh gemergt: Pull Request #4 sollte offen bleiben, bis Test und Korrektur
der Kaskade drin sind, wurde aber direkt gemergt. Folge: nur Entscheid 0015 in
master, kein Schaden. Mit einem Kommentar im Pull Request richtiggestellt;
Test und Korrektur kamen in einen neuen Pull Request. In Teams verhindert das
eine Regel, dass vor dem Merge jemand zustimmen muss (Branch Protection).

Dazu eine Warnung, die zuerst irritiert: «LF will be replaced by CRLF the next
time Git touches it». Windows und Linux beenden Textzeilen unterschiedlich
(CRLF und LF). Git gleicht das auf Windows automatisch an; die Warnung ist
harmlos und ändert nichts am Inhalt.

**Einen Commit rückgängig machen** (ausprobiert am 21.11.2026: Commit
gemacht, mit `git reset HEAD~1` zurückgenommen, die Änderungen blieben in den
Dateien, danach neu committet):

| Situation | Befehl | Änderungen in den Dateien | Verlauf |
| --- | --- | --- | --- |
| noch nicht gepusht, rückgängig | `git reset HEAD~1` | bleiben | Commit verschwindet |
| noch nicht gepusht, kleine Korrektur | `git commit --amend` | bleiben | Commit wird ersetzt |
| schon gepusht | `git revert HEAD` | werden zurückgedreht | Gegen-Commit kommt dazu (wie eine Stornobuchung) |
| alles wegwerfen (Vorsicht) | `git reset --hard HEAD~1` | gelöscht | Commit verschwindet |

Was schon auf GitHub liegt, wird nicht umgeschrieben, sondern mit einem
Gegen-Commit korrigiert; auf `master` gilt das ohne Ausnahme.

**Lerneffekt:** Die Trennung ist kein Umweg, sondern erlaubt saubere Commits:
Was zusammengehört, kommt in denselben Commit. Werkzeuge, die Schritte
automatisch erledigen, sind bequem, verdecken aber, was passiert.

## 15 Backend fertig, aber in der App nichts zu sehen

**Problem:** Die Suche auf Deutsch wurde zuerst nur im Backend gebaut
(`find_verbs` in `conjugation.py`, Adresse `/api/verbs/search` in `main.py`)
und als Pull Request #1 gemergt (21.11.2026). Die automatische Prüfung war
grün, Render hat neu ausgeliefert. Beim Ausprobieren in der App fand das
Suchfeld «gehen» trotzdem nicht. Erwartet war, dass die Funktion nach dem
Merge in der App funktioniert.

**Ursache:** Das Backend stellt eine Funktion nur bereit; die App benutzt sie
erst, wenn das Frontend sie auch aufruft. Das Suchfeld rief weiterhin die alte
Adresse `/api/verbs/{verb}` auf, die nur den italienischen Infinitiv kennt.
Direkt aufgerufen lieferte die neue Adresse das richtige Ergebnis
(`/api/verbs/search?q=gehen` → andare). Bild dazu: ein neues Gericht in der
Küche, das noch nicht auf der Speisekarte steht.

**Lösung:** Die Änderung als zusammenhängenden Ablauf über alle Schichten
planen: Fachlogik, Backend-Adresse, Frontend, Tests, Doku. Ein Zwischen-Merge
nur des Backends ist möglich und schadet nicht, solange klar ist, dass für
Benutzer noch nichts sichtbar ist (im Pull Request so beschrieben).

**Lerneffekt:** Jede neue Funktion im Backend braucht eine passende Anpassung
im Frontend, sonst bleibt sie unsichtbar. Darum vor dem Umsetzen kurz
durchgehen, welche Schichten betroffen sind (Separation of Concerns heisst
getrennte Zuständigkeiten, nicht getrennte Fertigstellung).

## 16 Eine Klammer zu viel legt die ganze Oberfläche lahm

**Problem:** Beim Umbau der Suche in `app.js` (21.11.2026) wurde die alte
Funktion `lookup` markiert und gelöscht. Eine schliessende Klammer `}` blieb
stehen (Zeile 197). Von Auge fiel das nicht auf; VS Code zeigte keine
deutliche Warnung.

**Folge, wenn es so live gegangen wäre:** JavaScript bricht bei einem
Syntaxfehler die ganze Datei ab. Die App hätte nach dem Merge eine leere oder
nicht reagierende Oberfläche gezeigt, nicht nur eine kaputte Suche.

**Wie es gefunden wurde:** Vor dem Commit mit `node --check app.js` geprüft.
Die Meldung «SyntaxError: Unexpected identifier 'practiceVerb'» zeigt auf die
Zeile nach der überzähligen Klammer.

**Lücke in der Absicherung:** Die automatische Prüfung auf GitHub deckt nur
Python ab (ruff, pytest). Für das Frontend gibt es keine Prüfung; dieser
Fehler wäre grün durchgegangen.

**Lösung:** Klammer entfernt. Verbesserungsidee: in der CI einen Schritt
`node --check src/app/static/app.js` ergänzen, damit Syntaxfehler im
Frontend vor dem Merge auffallen.

**Lerneffekt:** Beim Ersetzen von Code genau markieren, wo ein Block beginnt
und endet. Und: Eine grüne Prüfung heisst nur, dass das Geprüfte stimmt; was
nicht geprüft wird, kann trotzdem kaputt sein.

## 17 Editor formatierte anders als die Prüfung (Black statt Ruff)

**Symptom:** Pull Request #2 (21.11.2026) war zweimal rot bei der
Formatprüfung (`ruff format --check`). Beim ersten Mal fehlte am Ende der
Testdateien der Zeilenumbruch. Beim Beheben hat VS Code die neue letzte Zeile
automatisch mit vier Leerzeichen eingerückt; die Datei endete wieder falsch.
Inhaltlich waren alle Tests grün.

**Ursache:** Zwei Probleme in der Entwicklungsumgebung, nicht im Code:

1. **Falsche Konfiguration:** In `.vscode/settings.json` stand als Formatierer
   für Python `ms-python.black-formatter` (Black). Die Prüfung auf GitHub und
   die Empfehlung in `.vscode/extensions.json` verwenden aber Ruff. Editor und
   Prüfung folgten also verschiedenen Regeln. VS Code markierte den Eintrag
   mit einer gelben Wellenlinie, das fiel aber nicht auf.
2. **Fehlende Erweiterung:** Weder Black noch Ruff war in VS Code installiert.
   «Beim Speichern formatieren» war zwar eingeschaltet, hatte aber kein
   Werkzeug und tat darum nichts. Jede Formatierung musste von Hand stimmen.

**Lösung:**

* `settings.json` auf Ruff umgestellt (`charliermarsh.ruff`) und ergänzt:
  Zeilenumbruch am Dateiende einfügen, überzählige leere Zeilen am Ende und
  Leerzeichen am Zeilenende entfernen. Die Datei liegt im Repo und gilt für
  alle, die das Projekt in VS Code öffnen.
* Die Erweiterung «Ruff» (Astral) in VS Code installiert.

**Dritte Ursache, beim dritten roten Lauf gefunden:** Auch nach der Korrektur
griffen die Einstellungen nicht. In VS Code war der übergeordnete Ordner
(«Fürs Github Repo») geöffnet, nicht der Repo-Ordner `Coniuga`. VS Code liest
`.vscode/settings.json` aber nur im geöffneten Hauptordner; die Datei im
Unterordner wurde ignoriert. Lösung: den Repo-Ordner selbst öffnen
(`code . -r` im Ordner `Coniuga`).

**Verlauf und endgültige Lösung:** Insgesamt fünf Anläufe, bis die Prüfung
grün war (Commits 4f27aa8 bis 1107784). Zwei weitere Stolpersteine dabei:
Ein Commit wurde gemacht, bevor die korrigierte Datei gespeichert war (Git
nimmt den Stand zum Zeitpunkt von `git add`), und beim Einfügen ganzer Dateien
aus dem Chat kam der letzte Zeilenumbruch nicht mit. Gelöst wurde es ohne
Editor, mit einem Befehl, der genau einen Zeilenumbruch anhängt:
`Add-Content tests\test_api.py ""`. Danach Pull Request #2 grün und gemergt.

**Lerneffekt:** Ein Symptom (fehlender Zeilenumbruch) kann eine tiefere
Ursache haben (Editor und Prüfung mit verschiedenen Regeln). Statt jedes Mal
von Hand nachzubessern, die Werkzeuge so einstellen, dass sie dieselben
Regeln anwenden wie die automatische Prüfung. Hinweise des Editors
(Wellenlinien, Empfehlungen für Erweiterungen) ernst nehmen.
