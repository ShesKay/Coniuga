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
    key = choose_next(
        {}, VERBS, NOW, focus_verb="verb15", focus_tense="passato_prossimo"
    )
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
