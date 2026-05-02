import pytest
from unittest.mock import MagicMock
from src.infrastructure.battle_repository import InMemoryBattleRepository
from src.use_cases.start_battle import StartBattleUseCase, Encounter
from src.domain.value_objects.position import Position
from src.domain.events.battle_events import BattleTurnStarted

def make_use_case():
    repo = InMemoryBattleRepository()
    bus = MagicMock()
    return StartBattleUseCase(repo, bus), repo, bus

def test_start_battle_player_placed_at_encounter_start():
    use_case, repo, _ = make_use_case()
    use_case.execute(Encounter(player_start=Position(0, 0)))
    state = repo.get()
    assert state.player.position == Position(0, 0)
    assert state.grid.is_occupied(Position(0, 0))

def test_start_battle_player_has_full_hp():
    use_case, repo, _ = make_use_case()
    use_case.execute(Encounter(player_start=Position(1, 1)))
    state = repo.get()
    assert state.player.hp == state.player.max_hp

def test_start_battle_player_has_full_ap():
    use_case, repo, _ = make_use_case()
    use_case.execute(Encounter(player_start=Position(0, 0)))
    state = repo.get()
    assert state.player.ap == state.player.max_ap

def test_start_battle_publishes_turn_started():
    use_case, _, bus = make_use_case()
    use_case.execute(Encounter(player_start=Position(0, 0)))
    bus.publish.assert_called_once()
    event = bus.publish.call_args[0][0]
    assert isinstance(event, BattleTurnStarted)
    assert event.turn_number == 1

def test_start_battle_grid_is_4x4():
    use_case, repo, _ = make_use_case()
    use_case.execute(Encounter(player_start=Position(0, 0)))
    state = repo.get()
    assert len(state.grid.tiles) == 16
