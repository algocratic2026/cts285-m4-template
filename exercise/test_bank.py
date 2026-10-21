import pytest
from bank import MemoryBank, SetFull


def test_ten_fit():
    b = MemoryBank()
    for i in range(10):
        b.add_problem(f"P{i}")
    assert len(b.members) == 10


def test_eleventh_is_refused():
    b = MemoryBank()
    for i in range(10):
        b.add_problem(f"P{i}")
    with pytest.raises(SetFull):
        b.add_problem("P10")
    assert len(b.members) == 10
