"""These tests import the library only. No interface runs. That is the point."""
import pytest

from dataman.logic import (AttemptsExhausted, MemoryBank, PracticeSession,
                           Problem, SetFull, curator_report, result_label)
from dataman.store import JsonFileStore, MemoryStore

P = Problem("P1", "7 x 8", 56)


def session(store=None):
    return PracticeSession(store or MemoryStore(), "s1", P)


def test_first_miss_hides_answer():
    out = session().submit(55)
    assert out.status == "retry" and out.revealed_answer is None


def test_second_miss_reveals():
    s = session()
    s.submit(55)
    out = s.submit(54)
    assert out.status == "reveal" and out.revealed_answer == 56


def test_third_answer_is_refused():
    s = session()
    s.submit(55)
    s.submit(54)
    with pytest.raises(AttemptsExhausted):
        s.submit(56)


@pytest.mark.parametrize("answers,label", [
    ([56], "first-try success"),
    ([55, 56], "second-try success"),
    ([55, 54], "two misses"),
])
def test_curator_can_tell_three_outcomes_apart(answers, label):
    store = MemoryStore()
    s = session(store)
    for a in answers:
        s.submit(a)
    assert result_label(store.attempts_for("s1", "P1")) == label


def test_state_survives_restart(tmp_path):
    path = tmp_path / "store.json"
    session(JsonFileStore(path)).submit(55)
    resumed = session(JsonFileStore(path))     # new objects, same file
    assert resumed.next_try() == 2


def test_eleventh_problem_is_refused():
    bank = MemoryBank(MemoryStore(), "set-1")
    for i in range(1, 11):
        bank.add_problem(f"P{i}")
    with pytest.raises(SetFull):
        bank.add_problem("P11")
    assert len(bank.members()) == 10


def test_curator_report_gives_label_and_attempts():
    store = MemoryStore()
    s = session(store)
    s.submit(55)
    s.submit(56)
    rep = curator_report(store, "s1", "P1")
    assert rep["label"] == "second-try success"
    assert [a["answer"] for a in rep["attempts"]] == [55, 56]
