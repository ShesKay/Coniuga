import random
from datetime import datetime, timedelta

from app import learning
from app.learning import ItemState, apply_result, choose_next, mastery

NOW = datetime(2026, 11, 20, 12, 0)
VERBS = [f"verb{i}" for i in range(20)]


def mastered(verbs, tense="presente", box=3):
    return {
        (v, tense, p): ItemState(v, tense, p, box=box, due_at=NOW + timedelta(days=1))
        for v in verbs
        for p in range(6)
    }


def test_correct_moves_up_and_wrong_resets():
    s = ItemState("andare", "presente", 0, box=3)
    up = apply_result(s, True, NOW)
    assert up.box == 4 and up.correct == 1 and up.due_at == NOW + learning.INTERVALS[4]
    down = apply_result(up, False, NOW)
    assert down.box == 1 and down.wrong == 1


def test_box_has_a_maximum():
    s = ItemState("andare", "presente", 0, box=learning.MAX_BOX)
    assert apply_result(s, True, NOW).box == learning.MAX_BOX


def test_mastery_counts_items_in_box_3_or_higher():
    states = mastered(VERBS[:1], box=3)
    assert mastery(states, VERBS[:2], "presente") == 0.5


def test_start_with_few_verbs_then_unlock_more():
    assert learning.active_verb_count({}, VERBS) == learning.START_VERBS
    states = mastered(VERBS[:8])
    assert learning.active_verb_count(states, VERBS) == 12


def test_passato_prossimo_unlocked_after_first_verbs():
    assert learning.unlocked_tenses({}, VERBS) == ["presente"]
    assert "passato_prossimo" in learning.unlocked_tenses(mastered(VERBS[:8]), VERBS)


def test_due_weak_items_come_first():
    states = {
        ("verb0", "presente", 0): ItemState(
            "verb0", "presente", 0, box=4, due_at=NOW - timedelta(hours=1)
        ),
        ("verb1", "presente", 2): ItemState(
            "verb1", "presente", 2, box=1, due_at=NOW - timedelta(minutes=1)
        ),
    }
    assert choose_next(states, VERBS, NOW) == ("verb1", "presente", 2)


def test_new_items_when_nothing_is_due():
    states = {
        ("verb0", "presente", 0): ItemState(
            "verb0", "presente", 0, box=2, due_at=NOW + timedelta(hours=1)
        )
    }
    key = choose_next(states, VERBS, NOW, rng=random.Random(1))
    assert key[0] == "verb0" and key not in states


def test_focus_on_one_verb_and_tense():
    key = choose_next({}, VERBS, NOW, focus_verb="verb15", tenses=["passato_prossimo"])
    assert key[:2] == ("verb15", "passato_prossimo")


def test_last_item_is_not_repeated_immediately():
    states = {
        ("verb0", "presente", p): ItemState("verb0", "presente", p, box=1, due_at=NOW)
        for p in range(2)
    }
    assert choose_next(states, VERBS, NOW, last_key=("verb0", "presente", 0)) == (
        "verb0",
        "presente",
        1,
    )


def test_progress_summary():
    summary = learning.progress_summary(mastered(VERBS[:8]), VERBS)
    assert summary["active_count"] == 12
    assert summary["tenses"]["presente"]["mastery"] > 0
    assert summary["boxes"][3] == 48


def test_own_selection_overrides_learning_path():
    # Nichts gelernt, Passato prossimo also noch gesperrt, aber gewählt
    key = choose_next({}, VERBS, NOW, tenses=["passato_prossimo"])
    assert key[1] == "passato_prossimo"
    assert learning.practice_tenses({}, VERBS, ["passato_prossimo"]) == [
        "passato_prossimo"
    ]


def test_without_selection_the_learning_path_applies():
    assert learning.practice_tenses({}, VERBS, None) == ["presente"]


def test_selection_follows_registry_order():
    order = learning.practice_tenses({}, VERBS, ["passato_prossimo", "presente"])
    assert order == ["presente", "passato_prossimo"]


def test_verb_expansion_is_measured_in_base_tense_of_selection():
    states = mastered(VERBS[:8], tense="passato_prossimo")
    assert learning.active_verb_count(states, VERBS, ["passato_prossimo"]) == 12
    assert learning.active_verb_count(states, VERBS, ["presente"]) == 8


def test_new_tense_is_unlocked_generically(monkeypatch):
    from app import conjugation

    extra = conjugation.Tense("demo", "Demo", 3, conjugation.presente)
    monkeypatch.setitem(conjugation.TENSES, "demo", extra)
    states = {**mastered(VERBS[:8]), **mastered(VERBS[:8], "passato_prossimo")}
    assert learning.unlocked_tenses(states, VERBS) == [
        "presente",
        "passato_prossimo",
        "demo",
    ]
    assert learning.unlocked_tenses(mastered(VERBS[:8]), VERBS) == [
        "presente",
        "passato_prossimo",
    ]


def test_no_cascade_when_new_block_is_not_practised():
    # 16 Verben sitzen, 4 neue kommen dazu und sind noch ungeübt.
    # 16 von 20 sind genau 80 %; trotzdem dürfen nicht gleich 24 aktiv werden.
    verbs = [f"verb{i}" for i in range(30)]
    states = mastered(verbs[:16])
    assert learning.active_verb_count(states, verbs) == 20


def test_box_filter_only_picks_chosen_boxes():
    states = mastered(VERBS[:8], box=4)
    states[("verb2", "presente", 3)] = ItemState("verb2", "presente", 3, box=2)
    assert choose_next(states, VERBS, NOW, boxes=[2]) == ("verb2", "presente", 3)


def test_box_filter_counts_new_items_as_box_1():
    key = choose_next({}, VERBS, NOW, boxes=[1])
    assert key is not None and key[0] in VERBS[: learning.START_VERBS]


def test_box_filter_returns_none_when_nothing_matches():
    assert choose_next(mastered(VERBS[:8], box=4), VERBS, NOW, boxes=[5]) is None
