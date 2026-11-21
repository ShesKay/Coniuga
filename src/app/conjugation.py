"""Regelbasierte Konjugation italienischer Verben.

Reines Python-Modul ohne Web-Framework: Es kennt die Regeln für regelmässige
Verben und nimmt die Ausnahmen (unregelmässige Formen, Partizipien, Hilfsverb)
aus ``data/verbs.json``. Dadurch lässt es sich direkt mit pytest testen.
"""

from __future__ import annotations

import json
import unicodedata
from collections.abc import Callable
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

DATA_FILE = Path(__file__).parent / "data" / "verbs.json"

PERSONS = ["io", "tu", "lui/lei", "noi", "voi", "loro"]

_ENDINGS = {
    "are": ["o", "i", "a", "iamo", "ate", "ano"],
    "ere": ["o", "i", "e", "iamo", "ete", "ono"],
    "ire": ["o", "i", "e", "iamo", "ite", "ono"],
}
_ISC_ENDINGS = ["isco", "isci", "isce", "iamo", "ite", "iscono"]
_PARTICIPLE = {"are": "ato", "ere": "uto", "ire": "ito"}


@dataclass(frozen=True)
class Verb:
    infinitive: str
    meaning: str
    auxiliary: str = "avere"
    rank: int = 999
    participle: str | None = None
    presente: tuple[str, ...] | None = None
    isc: bool = False
    participle_alt: tuple[str, ...] = ()

    @property
    def group(self) -> str:
        return self.infinitive[-3:]

    @property
    def stem(self) -> str:
        return self.infinitive[:-3]


@dataclass
class CheckResult:
    """Ergebnis einer Antwortprüfung.

    status: "correct" (exakt), "accent" (nur Akzent fehlt), "wrong".
    """

    status: str
    expected: str
    accepted: list[str] = field(default_factory=list)

    @property
    def is_correct(self) -> bool:
        return self.status in ("correct", "accent")


@lru_cache(maxsize=1)
def load_verbs() -> dict[str, Verb]:
    raw = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    verbs = {}
    for item in raw:
        presente = item.get("presente")
        verbs[item["infinitive"]] = Verb(
            infinitive=item["infinitive"],
            meaning=item["meaning"],
            auxiliary=item.get("auxiliary", "avere"),
            rank=item.get("rank", 999),
            participle=item.get("participle"),
            presente=tuple(presente) if presente else None,
            isc=item.get("isc", False),
            participle_alt=tuple(item.get("participle_alt", [])),
        )
    return verbs


def get_verb(infinitive: str) -> Verb:
    verbs = load_verbs()
    key = infinitive.strip().lower()
    if key not in verbs:
        raise KeyError(f"Unbekanntes Verb: {infinitive}")
    return verbs[key]


def _german_words(meaning: str) -> set[str]:
    """«sich befinden, bleiben» -> {"sich befinden", "befinden", "bleiben"}."""
    words = set()
    for part in meaning.lower().split(","):
        part = part.strip()
        if part:
            words.add(part)
            if part.startswith("sich "):
                words.add(part[len("sich ") :])
    return words


def find_verbs(query: str) -> list[Verb]:
    """Nachschlagen auf Italienisch oder Deutsch.

    Zuerst als italienischer Infinitiv, sonst in den deutschen Bedeutungen.
    Ein deutsches Wort kann zu mehreren Verben passen («bleiben»), darum
    eine Liste, sortiert nach der Reihenfolge im Lernpfad.
    """
    key = " ".join(query.strip().lower().split())
    if not key:
        return []
    verbs = load_verbs()
    if key in verbs:
        return [verbs[key]]
    matches = [v for v in verbs.values() if key in _german_words(v.meaning)]
    return sorted(matches, key=lambda v: v.rank)


# --------------------------------------------------------------------- Presente
def _regular_presente(verb: Verb) -> list[str]:
    stem, group = verb.stem, verb.group
    if group == "ire" and verb.isc:
        return [stem + e for e in _ISC_ENDINGS]
    forms = []
    for ending in _ENDINGS[group]:
        s = stem
        if group == "are" and s.endswith(("c", "g")) and ending.startswith("i"):
            # cercare -> cerchi, cerchiamo; pagare -> paghi, paghiamo
            s += "h"
        if s.endswith("i") and ending.startswith("i"):
            # mangiare -> mangi (nicht mangii), mangiamo (nicht mangiiamo)
            ending = ending[1:]
        forms.append(s + ending)
    return forms


def presente(verb: Verb) -> list[str]:
    if verb.presente:
        return list(verb.presente)
    return _regular_presente(verb)


# ------------------------------------------------------------ Passato prossimo
def participle(verb: Verb) -> str:
    return verb.participle or verb.stem + _PARTICIPLE[verb.group]


def _participle_variants(verb: Verb, person_index: int) -> list[str]:
    """Bei 'essere' richtet sich das Partizip nach dem Subjekt."""
    p = participle(verb)
    if verb.auxiliary != "essere":
        return [p, *verb.participle_alt]
    base = p[:-1]
    if person_index < 3:
        return [base + "o", base + "a"]
    return [base + "i", base + "e"]


def passato_prossimo_variants(verb: Verb, person_index: int) -> list[str]:
    aux = presente(get_verb(verb.auxiliary))[person_index]
    return [f"{aux} {p}" for p in _participle_variants(verb, person_index)]


def passato_prossimo(verb: Verb) -> list[str]:
    """Anzeigeform, z. B. 'sono andato/a' oder 'siamo andati/e'."""
    forms = []
    for i in range(6):
        variants = passato_prossimo_variants(verb, i)
        if verb.auxiliary == "essere":
            forms.append(f"{variants[0]}/{variants[1][-1]}")
        else:
            forms.append(variants[0])
    return forms


# ----------------------------------------------------------- Zeiten-Registry
@dataclass(frozen=True)
class Tense:
    """Eine Zeit, die geübt und nachgeschlagen werden kann.

    forms:    die sechs Anzeigeformen (io bis loro)
    accepted: alle als richtig akzeptierten Antworten für eine Person
    order:    Reihenfolge im Lernpfad (bestimmt die Freischaltung)
    """

    key: str
    label: str
    order: int
    forms: Callable[[Verb], list[str]]
    accepted: Callable[[Verb, int], list[str]] | None = None

    def accepted_for(self, verb: Verb, person_index: int) -> list[str]:
        if self.accepted:
            return self.accepted(verb, person_index)
        return [self.forms(verb)[person_index]]


TENSES: dict[str, Tense] = {}


def register(tense: Tense) -> Tense:
    """Eine neue Zeit anmelden. Alle anderen Teile der App lesen nur TENSES."""
    if tense.key in TENSES:
        raise ValueError(f"Zeit doppelt registriert: {tense.key}")
    TENSES[tense.key] = tense
    return tense


register(Tense("presente", "Presente", 1, presente))
register(
    Tense(
        "passato_prossimo",
        "Passato prossimo",
        2,
        passato_prossimo,
        passato_prossimo_variants,
    )
)
# Eine neue Zeit, z. B. das Imperfetto, braucht nur:
#   1. eine Funktion, die aus einem Verb die sechs Formen bildet,
#   2. register(Tense("imperfetto", "Imperfetto", 3, imperfetto)),
#   3. Tests. Backend, Lernlogik und Frontend passen sich automatisch an.


def tense_order() -> list[str]:
    return [t.key for t in sorted(TENSES.values(), key=lambda t: t.order)]


def get_tense(key: str) -> Tense:
    if key not in TENSES:
        raise ValueError(f"Unbekannte Zeit: {key}")
    return TENSES[key]


# ----------------------------------------------------------------- Öffentlich
def conjugate(infinitive: str, tense: str) -> list[str]:
    return get_tense(tense).forms(get_verb(infinitive))


def accepted_answers(infinitive: str, tense: str, person_index: int) -> list[str]:
    return get_tense(tense).accepted_for(get_verb(infinitive), person_index)


def conjugation_table(infinitive: str) -> dict:
    verb = get_verb(infinitive)
    return {
        "infinitive": verb.infinitive,
        "meaning": verb.meaning,
        "auxiliary": verb.auxiliary,
        "participle": participle(verb),
        "irregular": bool(verb.presente or verb.participle),
        "tenses": {
            key: {
                "label": TENSES[key].label,
                "forms": dict(
                    zip(PERSONS, conjugate(verb.infinitive, key), strict=True)
                ),
            }
            for key in tense_order()
        },
    }


# --------------------------------------------------------------- Antwortprüfung
def _normalize(text: str) -> str:
    return " ".join(text.lower().replace("’", "'").split())


def _strip_accents(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text)
    return "".join(c for c in decomposed if unicodedata.category(c) != "Mn")


def _strip_pronoun(answer: str, person_index: int) -> str:
    pronouns = {
        0: ["io"],
        1: ["tu"],
        2: ["lui", "lei"],
        3: ["noi"],
        4: ["voi"],
        5: ["loro"],
    }
    words = answer.split(" ", 1)
    if len(words) == 2 and words[0] in pronouns[person_index]:
        return words[1]
    return answer


def check_answer(
    infinitive: str, tense: str, person_index: int, answer: str
) -> CheckResult:
    accepted = accepted_answers(infinitive, tense, person_index)
    given = _strip_pronoun(_normalize(answer), person_index)
    expected = conjugate(infinitive, tense)[person_index]
    if given in [_normalize(a) for a in accepted]:
        return CheckResult("correct", expected, accepted)
    if _strip_accents(given) in [_strip_accents(_normalize(a)) for a in accepted]:
        return CheckResult("accent", expected, accepted)
    return CheckResult("wrong", expected, accepted)
