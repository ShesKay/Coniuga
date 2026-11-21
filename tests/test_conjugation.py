import pytest

from app.conjugation import (
    check_answer,
    conjugate,
    conjugation_table,
    find_verbs,
    get_verb,
    load_verbs,
    participle,
)


@pytest.mark.parametrize(
    ("verb", "forms"),
    [
        ("parlare", ["parlo", "parli", "parla", "parliamo", "parlate", "parlano"]),
        (
            "prendere",
            ["prendo", "prendi", "prende", "prendiamo", "prendete", "prendono"],
        ),
        ("dormire", ["dormo", "dormi", "dorme", "dormiamo", "dormite", "dormono"]),
        ("capire", ["capisco", "capisci", "capisce", "capiamo", "capite", "capiscono"]),
        ("cercare", ["cerco", "cerchi", "cerca", "cerchiamo", "cercate", "cercano"]),
        ("pagare", ["pago", "paghi", "paga", "paghiamo", "pagate", "pagano"]),
        ("mangiare", ["mangio", "mangi", "mangia", "mangiamo", "mangiate", "mangiano"]),
        ("studiare", ["studio", "studi", "studia", "studiamo", "studiate", "studiano"]),
        ("andare", ["vado", "vai", "va", "andiamo", "andate", "vanno"]),
        ("essere", ["sono", "sei", "è", "siamo", "siete", "sono"]),
    ],
)
def test_presente(verb, forms):
    assert conjugate(verb, "presente") == forms


@pytest.mark.parametrize(
    ("verb", "expected"),
    [
        ("parlare", "parlato"),
        ("vendere", "venduto"),
        ("dormire", "dormito"),
        ("fare", "fatto"),
        ("aprire", "aperto"),
    ],
)
def test_participle(verb, expected):
    assert participle(get_verb(verb)) == expected


def test_passato_prossimo_with_avere():
    assert conjugate("mangiare", "passato_prossimo") == [
        "ho mangiato",
        "hai mangiato",
        "ha mangiato",
        "abbiamo mangiato",
        "avete mangiato",
        "hanno mangiato",
    ]


def test_passato_prossimo_with_essere_shows_both_genders():
    forms = conjugate("andare", "passato_prossimo")
    assert forms[0] == "sono andato/a"
    assert forms[3] == "siamo andati/e"


def test_all_verbs_conjugate_in_all_tenses():
    for verb in load_verbs():
        for tense in ("presente", "passato_prossimo"):
            forms = conjugate(verb, tense)
            assert len(forms) == 6 and all(forms)


def test_table_contains_meta_data():
    table = conjugation_table("venire")
    assert table["auxiliary"] == "essere"
    assert table["irregular"] is True
    assert table["tenses"]["presente"]["forms"]["io"] == "vengo"


def test_unknown_verb_raises():
    with pytest.raises(KeyError):
        get_verb("xyzare")


class TestCheckAnswer:
    def test_exact(self):
        assert check_answer("andare", "presente", 0, "vado").status == "correct"

    def test_case_spaces_and_pronoun_are_ignored(self):
        assert (
            check_answer("andare", "presente", 3, "  Noi  Andiamo ").status == "correct"
        )

    def test_missing_accent_is_almost_correct(self):
        result = check_answer("essere", "presente", 2, "e")
        assert result.status == "accent" and result.is_correct

    def test_wrong(self):
        result = check_answer("fare", "presente", 0, "faco")
        assert result.status == "wrong" and result.expected == "faccio"

    def test_essere_accepts_feminine(self):
        assert (
            check_answer("andare", "passato_prossimo", 0, "sono andata").status
            == "correct"
        )
        assert (
            check_answer("andare", "passato_prossimo", 5, "sono andate").status
            == "correct"
        )

    def test_wrong_auxiliary(self):
        assert (
            check_answer("andare", "passato_prossimo", 0, "ho andato").status == "wrong"
        )

    def test_alternative_participle(self):
        assert (
            check_answer("vedere", "passato_prossimo", 0, "ho veduto").status
            == "correct"
        )


def test_registry_order_and_labels():
    from app.conjugation import TENSES, tense_order

    assert tense_order() == ["presente", "passato_prossimo"]
    assert TENSES["passato_prossimo"].label == "Passato prossimo"


def test_registering_a_tense_twice_fails():
    from app.conjugation import TENSES, register

    with pytest.raises(ValueError):
        register(TENSES["presente"])


def test_unknown_tense_raises():
    with pytest.raises(ValueError):
        conjugate("parlare", "futuro")


def names(query):
    return [v.infinitive for v in find_verbs(query)]


def test_find_verbs_italian_and_german():
    assert names("andare") == ["andare"]
    assert names("  Andare ") == ["andare"]
    assert names("gehen") == ["andare"]
    assert names("GEHEN") == ["andare"]


def test_find_verbs_german_word_with_several_verbs():
    # «bleiben» passt zu drei Verben, sortiert nach Lernpfad
    assert names("bleiben") == ["stare", "rimanere", "restare"]
    assert names("lernen") == ["studiare", "imparare"]


def test_find_verbs_parts_and_reflexive():
    assert names("anrufen") == ["chiamare"]
    assert names("befinden") == ["stare"]
    assert names("sich befinden") == ["stare"]


def test_find_verbs_no_partial_match():
    # «gehen» darf nicht «hinausgehen» finden, «geh» nichts
    assert names("geh") == []
    assert names("kochen") == []
    assert names("") == []