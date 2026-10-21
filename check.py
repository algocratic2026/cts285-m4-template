"""Checkpoint check for the Module 4 bonus.

Run after you push:  python check.py 1     (end of Segment 1)
                     python check.py 2     (end of Segment 2)

The check reads facts a machine can see. Your instructor reads the rest.
"""
import ast
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ORIG = json.loads((ROOT / "checks" / "originals.json").read_text())


def sh(*args):
    return subprocess.run(args, cwd=ROOT, capture_output=True, text=True)


def digest(rel):
    data = (ROOT / rel).read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def pytest_ok(*paths):
    r = sh(sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", *paths)
    return r.returncode == 0, (r.stdout.strip().splitlines() or [""])[-1]


def notes_sections():
    text = (ROOT / "NOTES.md").read_text()
    out = {}
    for block in re.split(r"(?m)^## ", text)[1:]:
        title, _, body = block.partition("\n")
        out[title.strip()] = body
    return out


def todo_left(segment):
    tag = f"[S{segment}]"
    return [t for t, body in notes_sections().items() if tag in t and "TODO" in body]


# ---- individual checks. Each returns (ok, message). ----

def tests_pass():
    ok, last = pytest_ok("tests")
    return ok, last if not ok else "tests pass"


def tests_unchanged():
    same = digest("tests/test_logic.py") == ORIG["tests/test_logic.py"]
    return same, "tests/test_logic.py was changed. Restore it: git restore tests/test_logic.py"


def library_pure():
    bad = []
    for f in sorted((ROOT / "dataman").glob("*.py")):
        for node in ast.walk(ast.parse(f.read_text())):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                    and node.func.id in ("input", "print")):
                bad.append(f"{f.name}:{node.lineno}")
    return not bad, "the library calls input() or print() at " + ", ".join(bad)


def interface_changed():
    return digest("app.py") != ORIG["app.py"], "app.py is the same as the starter. Change the retry message."


def library_restored():
    for rel in ("dataman/logic.py", "dataman/store.py"):
        if digest(rel) != ORIG[rel]:
            return False, f"{rel} was changed. Restore it: git restore {rel}"
    return True, ""


def exercise_pass():
    ok, last = pytest_ok("exercise")
    return ok, "exercise tests fail: " + last


def exercise_test_unchanged():
    same = digest("exercise/test_bank.py") == ORIG["exercise/test_bank.py"]
    return same, "exercise/test_bank.py was changed. Restore it: git restore exercise/test_bank.py"


def default_store_json():
    ok = re.search(r'default\s*=\s*"json"', (ROOT / "app.py").read_text()) is not None
    return ok, 'in app.py, change default="memory" to default="json"'


def notes_done(segment):
    def run():
        left = todo_left(segment)
        return not left, "NOTES.md still has TODO in: " + "; ".join(left)
    return run


def reflection_length():
    for title, body in notes_sections().items():
        if title.startswith("Reflection"):
            words = len(body.replace("TODO", "").split())
            return words >= 25, f"Reflection has {words} words. Write at least 25."
    return False, "NOTES.md has no Reflection section"


def pushed(min_commits):
    def run():
        if sh("git", "status", "--porcelain").stdout.strip():
            return False, "you have changes that are not committed. Run: git add -A && git commit"
        up = sh("git", "rev-parse", "--abbrev-ref", "@{u}")
        if up.returncode != 0:
            return False, "this branch has no upstream. Run: git push -u origin main"
        ahead = sh("git", "rev-list", "--count", "@{u}..HEAD").stdout.strip()
        if ahead != "0":
            return False, f"{ahead} commit(s) are not pushed. Run: git push"
        n = int(sh("git", "rev-list", "--count", "HEAD").stdout.strip() or 0)
        if n < min_commits:
            return False, f"expected at least {min_commits} commits, found {n}"
        return True, ""
    return run


SEGMENT_1 = [
    ("tests pass", tests_pass),
    ("tests were not edited", tests_unchanged),
    ("library has no input() or print()", library_pure),
    ("app.py was changed", interface_changed),
    ("NOTES.md Part 1 to 3 are filled", notes_done(1)),
    ("work is committed and pushed", pushed(2)),
]
SEGMENT_2 = SEGMENT_1[:4] + [
    ("library files are restored", library_restored),
    ("exercise tests pass", exercise_pass),
    ("exercise test was not edited", exercise_test_unchanged),
    ("default store is json", default_store_json),
    ("NOTES.md Part 1 to 6 are filled", lambda: (not (todo_left(1) + todo_left(2)),
        "NOTES.md still has TODO in: " + "; ".join(todo_left(1) + todo_left(2)))),
    ("reflection is long enough", reflection_length),
    ("work is committed and pushed", pushed(3)),
]


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ("1", "2"):
        print("Use: python check.py 1   or   python check.py 2")
        return 2
    seg = sys.argv[1]
    first_fail = None
    for name, fn in (SEGMENT_1 if seg == "1" else SEGMENT_2):
        ok, msg = fn()
        print(("PASS  " if ok else "FAIL  ") + name + ("" if ok else "\n      " + msg))
        if not ok and first_fail is None:
            first_fail = name
    if first_fail:
        print(f"\nFailed on: {first_fail}. Fix it, push, and run the check again.")
        return 1
    print(f"\nAll checks pass. Segment {seg} is ready for your instructor to read.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
