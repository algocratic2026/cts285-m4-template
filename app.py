"""Text interface layer. This is the only file that uses input() and print().

Run:  python app.py              (data lives in RAM)
      python app.py --store json (data survives a restart)
"""
import argparse

from dataman.logic import (MemoryBank, PracticeSession, Problem, SetFull,
                           curator_report)
from dataman.store import JsonFileStore, MemoryStore

PROBLEM = Problem("P1", "7 x 8", 56)
SESSION = "maya-1"


def practice(store):
    session = PracticeSession(store, SESSION, PROBLEM)
    if session.is_finished():
        print("This session is finished. Choose 'report'.")
        return
    while not session.is_finished():
        raw = input(f"Try {session.next_try()}: {PROBLEM.prompt} = ")
        if not raw.strip().lstrip("-").isdigit():
            print("Enter a whole number.")
            continue
        out = session.submit(int(raw))
        if out.status == "correct":
            print("Correct.")
        elif out.status == "retry":
            print("Not yet. Try again.")
        else:
            print(f"The answer is {out.revealed_answer}.")


def report(store):
    rep = curator_report(store, SESSION, PROBLEM.id)
    print(f"Curator report for {SESSION}: {rep['label']}")
    for r in rep["attempts"]:
        print(f"  try {r['try']}: answered {r['answer']} -> "
              f"{'correct' if r['correct'] else 'wrong'}")


def bank(store):
    memory_bank = MemoryBank(store, "set-1")
    pid = input("Problem id to add (for example P11): ").strip()
    try:
        memory_bank.add_problem(pid)
        print(f"Added. Set holds {len(memory_bank.members())}.")
    except SetFull as err:
        print(f"Refused: {err}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--store", choices=["memory", "json"], default="memory")
    args = parser.parse_args()
    store = JsonFileStore() if args.store == "json" else MemoryStore()
    actions = {"practice": practice, "report": report, "bank": bank}
    while True:
        choice = input("practice / report / bank / quit > ").strip().lower()
        if choice == "quit":
            break
        if choice in actions:
            actions[choice](store)


if __name__ == "__main__":
    main()
