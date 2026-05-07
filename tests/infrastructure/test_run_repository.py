import pytest
from src.domain.run_state import RunState, MapNode
from src.infrastructure.run_repository import InMemoryRunRepository


def _run() -> RunState:
    return RunState(deck=[], player_hp=30, player_max_hp=30, floor=1, floors=[[], [], []])


def test_get_raises_when_no_run():
    repo = InMemoryRunRepository()
    with pytest.raises(RuntimeError):
        repo.get()


def test_has_active_run_false_initially():
    repo = InMemoryRunRepository()
    assert repo.has_active_run() is False


def test_save_and_get_round_trips():
    repo = InMemoryRunRepository()
    run = _run()
    repo.save(run)
    assert repo.get() is run


def test_has_active_run_true_after_save():
    repo = InMemoryRunRepository()
    repo.save(_run())
    assert repo.has_active_run() is True
