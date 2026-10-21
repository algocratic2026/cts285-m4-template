# M4 bonus: Three Layers in Python (beta), notes

Written 2026-10-21. Companion to `claude/m4-intro-deck-notes.md`.

## What it is
A bonus assignment worked in class. Students use a small DataMan CLI (`app.py` interface, `dataman/logic.py` rules, `dataman/store.py` data) in a Codespace. They change the screen text, add a rule, and switch storage from memory to a file. It is a beta test this semester.

## Time plan
45 minutes was judged not enough: first Codespace, setup, and a push all fit badly. So it is two 45-minute segments.

| Segment | Steps (min) | Ends with |
|---|---|---|
| 1 | Start 5, predict and find 10, run it 10, change the interface 10, push and check 5 | `python check.py 1` |
| 2 | Restart 3, add a rule 12, break it 10, swap the data 8, reflect, push, check 7 | `python check.py 2` |

Each segment is 40 minutes of steps plus 5 minutes of buffer. Times are planned, not measured.

## Plan and execution gate
Page has "One rule about order". Gate 1 is Segment 1 step 2: four file predictions in `NOTES.md` Part 1 before any code is opened or edited. Gate 2 is Segment 2 step 3: a written guess in Part 5 of which test will fail, before the rule is removed.

## Checkpoint
`check.py` reads machine facts only: tests pass, tests unchanged (hash), library has no `input()` or `print()`, `app.py` changed, `NOTES.md` has no TODO for that segment, work is committed and pushed. Segment 2 adds: library restored, exercise tests pass, `default="json"` set, Reflection has 25+ words. It does not grade the answers. The instructor reads those.

## Page decisions
- CTS-285 compositor: banner header (assignment), black and gold, `<h2>` title, `<h3>` sections, inline styles only.
- No SHODANN or other fiction on the page. DataMan only.
- Student artifact device names `NOTES.md`. Instructor-out-of-character gutter carries the beta note.
- ASCII three-layer figure is 24 columns wide, with prose after it.
- One `<details>` hint. It survives in this Canvas instance per the compositor skill.
- Points, due date, and availability are not on the page. Canvas shows them.

## Open
- One link is pending: the GitHub template repository (`bonus-template-repo`).
- Where students submit the repository URL is not set.
- AI-use rule is not stated.
- Where the bonus sits in the course is not assumed. Banner reads "Module 4 · Bonus (beta)".
- Grader access to student repositories depends on the sharing setting.
- Gold `#E3B23C` is still estimated.
- Not tested in a live Codespace or in Canvas itself. The student flow ran in a local simulation with a bare git remote.

## Bug found and fixed in testing
Plain `pytest -q` failed with `No module named 'dataman'`. Earlier runs went through `python -m pytest`, which hid it. `pytest.ini` now has `pythonpath = .`. This also fixes the deck's Demo 2 command in the instructor kit.
