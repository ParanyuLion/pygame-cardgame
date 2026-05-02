import pytest
from src.infrastructure.battle_repository import InMemoryBattleRepository
from src.domain.battle_state import BattleState
from src.domain.entities.player import Player
from src.domain.entities.grid import Grid
from src.domain.value_objects.position import Position


def make_state() -> BattleState:
    grid = Grid()
    player = Player(id="player", position=Position(0, 0), hp=30, max_hp=30, ap=3, max_ap=3)
    grid.place("player", Position(0, 0))
    return BattleState(player=player, grid=grid)


def test_get_raises_before_save():
    repo = InMemoryBattleRepository()
    with pytest.raises(RuntimeError):
        repo.get()


def test_save_and_get_returns_same_state():
    repo = InMemoryBattleRepository()
    state = make_state()
    repo.save(state)
    assert repo.get() is state


def test_save_overwrites_previous_state():
    repo = InMemoryBattleRepository()
    state1 = make_state()
    state2 = make_state()
    repo.save(state1)
    repo.save(state2)
    assert repo.get() is state2
