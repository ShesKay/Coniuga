"""Lernlogik: Karteikasten (Leitner) und Freischaltung neuer Verben und Zeiten.

Reines Python ohne Datenbank: Die Funktionen bekommen den aktuellen Lernstand
als Liste von ``ItemState`` und geben Entscheide zurück. So lässt sich die
Logik ohne Web-Framework und ohne Datenbank testen.

Begriffe:
 * Ein *Item* ist eine Kombination aus Verb, Zeit und Person
   (z. B. andare · passato_prossimo · noi).
 * Jedes Item liegt in einem Fach (Box) von 1 bis 5. Richtig -> ein Fach
   weiter, falsch -> zurück in Fach 1. Je höher das Fach, desto später wird
   das Item wieder abgefragt.
 * Ein Item gilt als *sicher*, wenn es mindestens in Fach 3 liegt.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, replace
from datetime import datetime, timedelta

from app.conjugation import PERSONS, TENSES, tense_order

MAX_BOX = 5
MASTERED_BOX = 3
INTERVALS = {
    1: timedelta(minutes=1),
    2: timedelta(minutes=10),
    3: timedelta(days=1),
    4: timedelta(days=3),
    5: timedelta(days=7),
}
START_VERBS = 8  # so viele Verben sind zu Beginn aktiv
STEP_VERBS = 4  # so viele kommen pro Stufe dazu
UNLOCK_THRESHOLD = 0.8  # Anteil sicherer Items, der eine neue Stufe freischaltet
# 0.8 statt tiefer: Sonst würden neue, noch ungeübte Verben die Quote
# kaum senken und mehrere Stufen auf einmal freigeschaltet.

Key = tuple[str, str, int]  # (Verb, Zeit, Person)


@dataclass(frozen=True)
class ItemState:
    verb: str
    tense: str
    person: int
    box: int = 1
    correct: int = 0
    wrong: int = 0
    due_at: datetime | None = None

    @property
    def key(self) -> Key:
        return (self.verb, self.tense, self.person)


def apply_result(state: ItemState, is_correct: bool, now: datetime) -> ItemState:
    """Neuer Zustand eines Items nach einer Antwort."""
    if is_correct:
        box = min(state.box + 1, MAX_BOX)
        return replace(
            state, box=box, correct=state.correct + 1, due_at=now + INTERVALS[box]
        )
    return replace(state, box=1, wrong=state.wrong + 1, due_at=now + INTERVALS[1])


def mastery(
    states: dict[Key, ItemState], verbs: list[str], tenses: str | list[str]
) -> float:
    """Anteil sicherer Items (Fach >= 3) über alle Personen dieser Verben."""
    tenses = [tenses] if isinstance(tenses, str) else tenses
    if not verbs or not tenses:
        return 0.0
    total = len(verbs) * len(tenses) * len(PERSONS)
    safe = sum(
        1
        for v in verbs
        for t in tenses
        for p in range(len(PERSONS))
        if (s := states.get((v, t, p))) and s.box >= MASTERED_BOX
    )
    return safe / total


def unlocked_tenses(
    states: dict[Key, ItemState], ordered_verbs: list[str]
) -> list[str]:
    """Lernpfad: Eine Zeit wird frei, sobald die vorherige bei den ersten
    Verben sitzt. Funktioniert für beliebig viele registrierte Zeiten."""
    order = tense_order()
    first = ordered_verbs[:START_VERBS]
    unlocked = order[:1]
    for previous, following in zip(order, order[1:], strict=False):
        if mastery(states, first, previous) < UNLOCK_THRESHOLD:
            break
        unlocked.append(following)
    return unlocked


def practice_tenses(
    states: dict[Key, ItemState],
    ordered_verbs: list[str],
    selected: list[str] | None = None,
) -> list[str]:
    """Welche Zeiten geübt werden: die eigene Auswahl geht vor, sonst der
    Lernpfad (freigeschaltete Zeiten)."""
    if selected:
        return [t for t in tense_order() if t in selected]
    return unlocked_tenses(states, ordered_verbs)


def active_verb_count(
    states: dict[Key, ItemState],
    ordered_verbs: list[str],
    tenses: list[str] | None = None,
) -> int:
    """Wie viele Verben (nach Häufigkeit) aktuell geübt werden.

    Start mit START_VERBS. Sobald genug davon sitzen, kommen STEP_VERBS
    weitere dazu, und so weiter. Gemessen wird in der grundlegendsten der
    geübten Zeiten (im Lernpfad das Presente), damit eine neu freigeschaltete
    Zeit die Zahl der Verben nicht wieder senkt.
    """
    base = (tenses or tense_order())[0]
    n = min(START_VERBS, len(ordered_verbs))
    while (
        n < len(ordered_verbs)
        and mastery(states, ordered_verbs[:n], base) >= UNLOCK_THRESHOLD
    ):
        n = min(n + STEP_VERBS, len(ordered_verbs))
    return n


def choose_next(
    states: dict[Key, ItemState],
    ordered_verbs: list[str],
    now: datetime,
    last_key: Key | None = None,
    focus_verb: str | None = None,
    tenses: list[str] | None = None,
    rng: random.Random | None = None,
) -> Key:
    """Wählt die nächste Aufgabe.

    Reihenfolge der Prioritäten:
     1. fällige Items, die schwächsten (tiefstes Fach) und ältesten zuerst
     2. neue, noch nie gesehene Items der aktiven Verben
     3. falls alles erledigt ist: das Item, das als nächstes fällig wird
    ``tenses`` ist die eigene Auswahl (sonst Lernpfad), ``focus_verb``
    schränkt auf ein Verb ein.
    """
    rng = rng or random.Random()
    tenses = practice_tenses(states, ordered_verbs, tenses)
    if focus_verb:
        verbs = [focus_verb]
    else:
        verbs = ordered_verbs[: active_verb_count(states, ordered_verbs, tenses)]
    candidates = [(v, t, p) for v in verbs for t in tenses for p in range(len(PERSONS))]
    if len(candidates) > 1 and last_key in candidates:
        candidates.remove(last_key)

    seen = [states[k] for k in candidates if k in states]
    due = [s for s in seen if s.due_at is None or s.due_at <= now]
    if due:
        return min(due, key=lambda s: (s.box, s.due_at or now)).key

    unseen = [k for k in candidates if k not in states]
    if unseen:
        first_verb, first_tense = unseen[0][0], unseen[0][1]
        same = [k for k in unseen if k[0] == first_verb and k[1] == first_tense]
        return rng.choice(same)

    return min(seen, key=lambda s: s.due_at or now).key


def progress_summary(
    states: dict[Key, ItemState],
    ordered_verbs: list[str],
    selected: list[str] | None = None,
) -> dict:
    tenses = practice_tenses(states, ordered_verbs, selected)
    n = active_verb_count(states, ordered_verbs, tenses)
    active = ordered_verbs[:n]
    per_tense = {
        t: {
            "label": TENSES[t].label,
            "mastery": round(mastery(states, active, t), 3),
            "seen": sum(1 for k in states if k[1] == t),
        }
        for t in tense_order()
    }
    boxes = {b: 0 for b in range(1, MAX_BOX + 1)}
    for s in states.values():
        boxes[s.box] += 1
    by_verb: dict[str, list[int]] = {}
    for s in states.values():
        c, w = by_verb.setdefault(s.verb, [0, 0])
        by_verb[s.verb] = [c + s.correct, w + s.wrong]
    weakest = sorted(
        ((v, c, w) for v, (c, w) in by_verb.items() if w > 0),
        key=lambda x: (-x[2] / (x[1] + x[2]), -x[2]),
    )[:5]
    return {
        "active_verbs": active,
        "active_count": n,
        "total_verbs": len(ordered_verbs),
        "unlocked_tenses": unlocked_tenses(states, ordered_verbs),
        "practice_tenses": tenses,
        "selected_tenses": selected,
        "tenses": per_tense,
        "boxes": boxes,
        "weakest": [{"verb": v, "correct": c, "wrong": w} for v, c, w in weakest],
    }
