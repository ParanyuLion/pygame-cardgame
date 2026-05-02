import pytest
from unittest.mock import MagicMock
from src.domain.battle_state import BattleState
from src.domain.entities.grid import Grid
from src.domain.entities.tile import Obstacle
from src.domain.entities.player import Player, InsufficientAPError
from src.domain.value_objects.position import Position
from src.domain.events.battle_events import EntityMoved
from src.use_cases.move_entity import MoveEntityUseCase

def make_state(player_pos: Position = Position(1, 1), player_ap: int = 3) -> BattleState:
    grid = Grid()
    player = Player(
        id="player", position=player_pos,
        hp=30, max_hp=30, ap=player_ap, max_ap=3,
    )
    grid.place("player", player_pos)
    return BattleState(player=player, grid=grid)

def make_use_case(state: BattleState) -> tuple[MoveEntityUseCase, MagicMock, MagicMock]:
    repo = MagicMock()
    repo.get.return_value = state
    bus = MagicMock()
    return MoveEntityUseCase(repo, bus), repo, bus

def test_move_updates_player_position():
    state = make_state(player_pos=Position(1, 1))
    use_case, _, _ = make_use_case(state)
    use_case.execute("player", Position(1, 2))
    assert state.player.position == Position(1, 2)

def test_move_publishes_entity_moved_event():
    state = make_state(player_pos=Position(1, 1))
    use_case, _, bus = make_use_case(state)
    use_case.execute("player", Position(2, 1))
    bus.publish.assert_called_once()
    event = bus.publish.call_args[0][0]
    assert isinstance(event, EntityMoved)
    assert event.from_pos == Position(1, 1)
    assert event.to_pos == Position(2, 1)

def test_move_deducts_ap():
    state = make_state(player_pos=Position(1, 1), player_ap=3)
    use_case, _, _ = make_use_case(state)
    use_case.execute("player", Position(1, 2))
    assert state.player.ap == 2

def test_move_updates_grid_occupancy():
    state = make_state(player_pos=Position(1, 1))
    use_case, _, _ = make_use_case(state)
    use_case.execute("player", Position(2, 1))
    assert not state.grid.is_occupied(Position(1, 1))
    assert state.grid.is_occupied(Position(2, 1))

def test_move_saves_state():
    state = make_state(player_pos=Position(1, 1))
    use_case, repo, _ = make_use_case(state)
    use_case.execute("player", Position(1, 2))
    repo.save.assert_called_once_with(state)

def test_move_to_occupied_tile_raises():
    state = make_state(player_pos=Position(0, 0))
    state.grid.place("enemy", Position(1, 0))
    use_case, _, _ = make_use_case(state)
    with pytest.raises(ValueError, match="not passable"):
        use_case.execute("player", Position(1, 0))

def test_move_to_wall_raises():
    state = make_state(player_pos=Position(0, 0))
    state.grid.place_obstacle(Position(1, 0), Obstacle(type="wall"))
    use_case, _, _ = make_use_case(state)
    with pytest.raises(ValueError, match="not passable"):
        use_case.execute("player", Position(1, 0))

def test_move_with_zero_ap_raises():
    state = make_state(player_pos=Position(1, 1), player_ap=0)
    use_case, _, _ = make_use_case(state)
    with pytest.raises(InsufficientAPError):
        use_case.execute("player", Position(1, 2))

def test_move_unknown_entity_raises():
    state = make_state()
    use_case, _, _ = make_use_case(state)
    with pytest.raises(ValueError, match="Unknown entity"):
        use_case.execute("ghost", Position(1, 1))
