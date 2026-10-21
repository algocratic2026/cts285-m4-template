"""Business-logic layer.

Rules live here. This file never calls input() or print().
It reaches data only through a store object (see store.py).
"""
from dataclasses import dataclass

MAX_ATTEMPTS = 2      # Rule from the requirement: exactly two tries.
MAX_SET_SIZE = 10     # Rule from the requirement: up to 10 problems in a set.


@dataclass(frozen=True)
class Problem:
    id: str
    prompt: str
    answer: int


@dataclass(frozen=True)
class Outcome:
    """What the interface needs in order to draw a screen. Nothing more."""
    status: str                 # "correct" | "retry" | "reveal"
    try_number: int             # the try that was just used
    revealed_answer: int | None  # set only when status == "reveal"


class SetFull(Exception):
    """Raised when a Memory Bank set already holds MAX_SET_SIZE problems."""


class AttemptsExhausted(Exception):
    """Raised when a session is already finished and gets another answer."""


class PracticeSession:
    """One learner, one problem. State comes from the store, not from memory."""

    def __init__(self, store, session_id: str, problem: Problem):
        self.store = store
        self.session_id = session_id
        self.problem = problem

    def attempts(self) -> list[dict]:
        return self.store.attempts_for(self.session_id, self.problem.id)

    def is_finished(self) -> bool:
        rows = self.attempts()
        return bool(rows) and (rows[-1]["correct"] or len(rows) >= MAX_ATTEMPTS)

    def next_try(self) -> int:
        return len(self.attempts()) + 1

    def submit(self, answer: int) -> Outcome:
        if self.is_finished():
            raise AttemptsExhausted(self.problem.id)
        try_number = self.next_try()
        correct = answer == self.problem.answer
        self.store.save_attempt(
            self.session_id, self.problem.id, try_number, answer, correct
        )
        if correct:
            return Outcome("correct", try_number, None)
        if try_number >= MAX_ATTEMPTS:
            return Outcome("reveal", try_number, self.problem.answer)
        return Outcome("retry", try_number, None)


def result_label(attempts: list[dict]) -> str:
    """Curator view: tell the three outcomes apart."""
    if not attempts:
        return "not attempted"
    if attempts[0]["correct"]:
        return "first-try success"
    if len(attempts) >= 2 and attempts[1]["correct"]:
        return "second-try success"
    if len(attempts) >= MAX_ATTEMPTS:
        return "two misses"
    return "in progress"


def curator_report(store, session_id: str, problem_id: str) -> dict:
    """Curator view for one session and one problem: the outcome label and every attempt."""
    rows = store.attempts_for(session_id, problem_id)
    return {"label": result_label(rows), "attempts": rows}


class MemoryBank:
    """A practice set. The size limit is a business rule, not a screen rule."""

    def __init__(self, store, set_id: str):
        self.store = store
        self.set_id = set_id

    def members(self) -> list[str]:
        return self.store.members(self.set_id)

    def add_problem(self, problem_id: str) -> None:
        current = self.members()
        if problem_id in current:
            return
        if len(current) >= MAX_SET_SIZE:
            raise SetFull(f"{self.set_id} already holds {MAX_SET_SIZE} problems")
        self.store.add_member(self.set_id, problem_id)
