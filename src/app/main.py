"""FastAPI-Backend von Coniuga.

Das Backend verbindet die drei Teile der App:
 * die Konjugations-Engine (app.conjugation),
 * die Lernlogik (app.learning) mit dem Lernstand in der Datenbank (app.db),
 * den externen Dienst für Beispielsätze (app.examples).
Ausserdem liefert es das Frontend (src/app/static) aus.
"""

from __future__ import annotations

import re
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import conjugation, examples, learning
from app.db import Attempt, Progress, SessionLocal, User, init_db, now_utc

STATIC_DIR = Path(__file__).parent / "static"
NAME_PATTERN = re.compile(r"^[A-Za-zÀ-ÿ0-9 _.-]{2,30}$")


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Coniuga",
    description="Adaptiver Konjugationstrainer für Italienisch",
    lifespan=lifespan,
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def get_session():
    with SessionLocal() as session:
        yield session


# Abkürzung für FastAPI: Jede Route bekommt automatisch eine eigene DB-Session
SessionDep = Annotated[Session, Depends(get_session)]


def ordered_verbs() -> list[str]:
    return [
        v.infinitive
        for v in sorted(conjugation.load_verbs().values(), key=lambda v: v.rank)
    ]


# ------------------------------------------------------------------ Schemas
class UserIn(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def valid_name(cls, value: str) -> str:
        value = value.strip()
        if not NAME_PATTERN.match(value):
            raise ValueError(
                "Name: 2 bis 30 Zeichen, nur Buchstaben, Zahlen, Leerzeichen, _ . -"
            )
        return value


class SettingsIn(BaseModel):
    """Gewählte Zeiten; null oder leere Liste = automatisch (Lernpfad)."""

    tenses: list[str] | None = None

    @field_validator("tenses")
    @classmethod
    def known_tenses(cls, value: list[str] | None) -> list[str] | None:
        if not value:
            return None
        unknown = [t for t in value if t not in conjugation.TENSES]
        if unknown:
            raise ValueError(f"Unbekannte Zeit: {', '.join(unknown)}")
        return [t for t in conjugation.tense_order() if t in value]


class AnswerIn(BaseModel):
    verb: str
    tense: str
    person: int = Field(ge=0, le=5)
    answer: str = Field(max_length=80)


# ------------------------------------------------------------------ Hilfen
def find_user(session: Session, name: str) -> User:
    user = session.scalar(select(User).where(User.name == name.strip()))
    if not user:
        raise HTTPException(404, "Benutzer nicht gefunden")
    return user


def load_states(session: Session, user: User) -> dict[learning.Key, learning.ItemState]:
    rows = session.scalars(select(Progress).where(Progress.user_id == user.id))
    return {
        (r.verb, r.tense, r.person): learning.ItemState(
            r.verb, r.tense, r.person, r.box, r.correct, r.wrong, r.due_at
        )
        for r in rows
    }


def selected_tenses(user: User) -> list[str] | None:
    if not user.tenses:
        return None
    return [t for t in user.tenses.split(",") if t in conjugation.TENSES] or None


def user_info(user: User, created: bool = False) -> dict:
    return {"name": user.name, "created": created, "tenses": selected_tenses(user)}


def check_verb_and_tense(verb: str, tense: str | None) -> None:
    if verb not in conjugation.load_verbs():
        raise HTTPException(404, f"Unbekanntes Verb: {verb}")
    if tense is not None and tense not in conjugation.TENSES:
        raise HTTPException(400, f"Unbekannte Zeit: {tense}")


# ------------------------------------------------------------------ Routen
@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/tenses")
def list_tenses():
    """Alle registrierten Zeiten in der Reihenfolge des Lernpfads."""
    return [
        {"key": t, "label": conjugation.TENSES[t].label, "order": i + 1}
        for i, t in enumerate(conjugation.tense_order())
    ]


@app.get("/api/verbs")
def list_verbs():
    """Alle Verben, sortiert nach der Reihenfolge, in der sie eingeführt werden."""
    return [
        {
            "infinitive": v.infinitive,
            "meaning": v.meaning,
            "auxiliary": v.auxiliary,
            "rank": v.rank,
            "irregular": bool(v.presente or v.participle),
        }
        for v in sorted(conjugation.load_verbs().values(), key=lambda v: v.rank)
    ]


@app.get("/api/verbs/{infinitive}")
def verb_table(infinitive: str):
    """Kernoperation Nachschlagen: vollständige Konjugationstabelle."""
    try:
        return conjugation.conjugation_table(infinitive)
    except KeyError as err:
        raise HTTPException(404, str(err)) from err


@app.get("/api/verbs/{infinitive}/examples")
def verb_examples(
    infinitive: str, tense: str = "presente", person: int = Query(0, ge=0, le=5)
):
    """Echte Beispielsätze von Tatoeba für eine konjugierte Form."""
    check_verb_and_tense(infinitive, tense)
    form = conjugation.conjugate(infinitive, tense)[person]
    return examples.fetch_examples(form)


@app.post("/api/users", status_code=201)
def create_or_login(data: UserIn, session: SessionDep):
    """Name ohne Passwort: existiert er, wird weitergemacht, sonst neu angelegt."""
    user = session.scalar(select(User).where(User.name == data.name))
    created = False
    if not user:
        user = User(name=data.name)
        session.add(user)
        session.commit()
        created = True
    return user_info(user, created)


@app.put("/api/users/{name}/settings")
def update_settings(name: str, data: SettingsIn, session: SessionDep):
    """Zeiten wählen. Die eigene Wahl geht vor der Freischaltung im Lernpfad."""
    user = find_user(session, name)
    user.tenses = ",".join(data.tenses) if data.tenses else None
    session.commit()
    return user_info(user)


@app.get("/api/users/{name}/exercise")
def next_exercise(
    name: str,
    session: SessionDep,
    verb: str | None = None,
    tense: str | None = None,
    last_verb: str | None = None,
    last_tense: str | None = None,
    last_person: int | None = None,
):
    """Nächste Aufgabe gemäss Lernlogik, optional mit Fokus auf Verb oder Zeit."""
    user = find_user(session, name)
    if verb:
        check_verb_and_tense(verb, tense)
    elif tense:
        check_verb_and_tense(ordered_verbs()[0], tense)
    states = load_states(session, user)
    last = (
        (last_verb, last_tense, last_person)
        if last_verb and last_tense and last_person is not None
        else None
    )
    tenses = [tense] if tense else selected_tenses(user)
    v, t, p = learning.choose_next(
        states, ordered_verbs(), now_utc(), last, verb, tenses
    )
    info = conjugation.get_verb(v)
    state = states.get((v, t, p))
    return {
        "verb": v,
        "meaning": info.meaning,
        "tense": t,
        "tense_label": conjugation.TENSES[t].label,
        "person": p,
        "pronoun": conjugation.PERSONS[p],
        "box": state.box if state else 0,
        "new": state is None,
        "auxiliary_hint": info.auxiliary if t == "passato_prossimo" else None,
    }


@app.post("/api/users/{name}/answers")
def submit_answer(name: str, data: AnswerIn, session: SessionDep):
    """Kernoperation Üben: Antwort prüfen, Lernstand speichern, Feedback geben."""
    user = find_user(session, name)
    check_verb_and_tense(data.verb, data.tense)
    result = conjugation.check_answer(data.verb, data.tense, data.person, data.answer)
    now = now_utc()

    row = session.scalar(
        select(Progress).where(
            Progress.user_id == user.id,
            Progress.verb == data.verb,
            Progress.tense == data.tense,
            Progress.person == data.person,
        )
    )
    before_states = load_states(session, user)
    key = (data.verb, data.tense, data.person)
    is_new = key not in before_states
    start = before_states.get(key) or learning.ItemState(
        *key
    )  # neues Item beginnt in Fach 1
    after = learning.apply_result(start, result.is_correct, now)
    if row is None:
        row = Progress(
            user_id=user.id, verb=data.verb, tense=data.tense, person=data.person
        )
        session.add(row)
    row.box, row.correct, row.wrong, row.due_at = (
        after.box,
        after.correct,
        after.wrong,
        after.due_at,
    )
    session.add(
        Attempt(
            user_id=user.id,
            verb=data.verb,
            tense=data.tense,
            person=data.person,
            answer=data.answer.strip()[:80],
            status=result.status,
        )
    )
    session.commit()

    verbs = ordered_verbs()
    after_states = load_states(session, user)
    unlocked_before = learning.unlocked_tenses(before_states, verbs)
    unlocked_after = learning.unlocked_tenses(after_states, verbs)
    chosen = selected_tenses(user)
    active_before = learning.active_verb_count(
        before_states, verbs, learning.practice_tenses(before_states, verbs, chosen)
    )
    active_after = learning.active_verb_count(
        after_states, verbs, learning.practice_tenses(after_states, verbs, chosen)
    )
    return {
        "status": result.status,
        "expected": result.expected,
        "accepted": result.accepted,
        "row": dict(
            zip(
                conjugation.PERSONS,
                conjugation.conjugate(data.verb, data.tense),
                strict=True,
            )
        ),
        "box_before": 0 if is_new else start.box,
        "box_after": after.box,
        "new_tenses": [
            conjugation.TENSES[t].label
            for t in unlocked_after
            if t not in unlocked_before
        ],
        "new_verbs": verbs[active_before:active_after],
    }


@app.get("/api/users/{name}/progress")
def progress(name: str, session: SessionDep):
    """Lernfortschritt: Freischaltungen, Sicherheit pro Zeit, schwächste Verben."""
    user = find_user(session, name)
    summary = learning.progress_summary(
        load_states(session, user), ordered_verbs(), selected_tenses(user)
    )
    attempts = list(
        session.scalars(
            select(Attempt)
            .where(Attempt.user_id == user.id)
            .order_by(Attempt.created_at.desc())
        )
    )
    correct = sum(1 for a in attempts if a.status in ("correct", "accent"))
    summary["attempts"] = len(attempts)
    summary["accuracy"] = round(correct / len(attempts), 3) if attempts else None
    summary["practice_days"] = len({a.created_at.date() for a in attempts})
    summary["recent"] = [
        {
            "verb": a.verb,
            "tense": conjugation.TENSES[a.tense].label
            if a.tense in conjugation.TENSES
            else a.tense,
            "pronoun": conjugation.PERSONS[a.person],
            "answer": a.answer,
            "status": a.status,
        }
        for a in attempts[:10]
    ]
    return summary
