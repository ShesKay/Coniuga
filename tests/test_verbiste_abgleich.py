"""Abgleich aller Formen mit einem unabhängigen Wörterbuch.

Die übrigen Konjugationstests prüfen Stichproben. Dieser Test prüft alle
60 Verben: jede Presente-Form und jedes Partizip muss in der Referenz
vorkommen. Die Referenz stammt aus Verbiste (siehe
``tests/data/verbiste_referenz.json``), nicht aus Coniuga selbst; sonst würde
der Test nur sich selbst bestätigen. Nennt Verbiste mehrere Varianten
(z. B. «devo/debbo»), gilt jede als richtig.
"""

import json
from pathlib import Path

import pytest

from app.conjugation import conjugate, get_verb, load_verbs, participle

REFERENZ = json.loads(
    (Path(__file__).parent / "data" / "verbiste_referenz.json").read_text("utf-8")
)["verben"]


def test_reference_covers_all_verbs():
    assert sorted(REFERENZ) == sorted(load_verbs())


@pytest.mark.parametrize("verb", sorted(REFERENZ))
def test_forms_match_verbiste(verb):
    erwartet = REFERENZ[verb]
    for person, form in enumerate(conjugate(verb, "presente")):
        assert form in erwartet["presente"][person], (verb, person, form)
    assert participle(get_verb(verb)) in erwartet["participio"], verb
