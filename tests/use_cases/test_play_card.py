import pytest
from unittest.mock import MagicMock
from src.domain.battle_state import BattleState
from src.domain.entities.grid import Grid
from src.domain.entities.player import Player, InsufficientAPError
from src.domain.entities.card import Card, CardContext
from src.domain.value_objects.position import Position
from src.domain.value_objects.card_tag import CardTag
from src.domain.value_objects.attack_pattern import AttackPattern
from src.domain.events.battle_events import CardPlayed, CardDrawn, BattleEnded
from src.domain.entities.enemy import Enemy
from src.domain.value_objects.intent import Intent
from src.use_cases.play_card import PlayCardUseCase

def _card(id: str, ap_cost: int = 1, damage: int = 0, draw_after: int = 0) -> Card:
    return Card(id=id, name=id, tags=[CardTag("Blade")], ap_cost=ap_cost,
                pattern=AttackPattern.single(), damage=damage, draw_after_play=draw_after)

def _extra_deck_card(id: str) -> Card:
    return Card(id=id, name=id, tags=[CardTag("Blade")], ap_cost=1,
                pattern=AttackPattern.single(), damage=0)

def _make_state(hand_cards: list[Card], ap: int = 3) -> BattleState:
    grid = Grid()
    player = Player(id="player", position=Position(1, 1), hp=30, max_hp=30, ap=ap, max_ap=3)
    grid.place("player", Position(1, 1))
    state = BattleState(player=player, grid=grid)
    state.hand = list(hand_cards)
    return state

def _make_use_case(state: BattleState) -> tuple[PlayCardUseCase, MagicMock, MagicMock]:
    repo = MagicMock()
    repo.get.return_value = state
    bus = MagicMock()
    return PlayCardUseCase(repo, bus), repo, bus

def test_play_card_moves_card_to_discard():
    card = _card("slash_1", ap_cost=1)
    state = _make_state([card])
    use_case, _, _ = _make_use_case(state)
    use_case.execute("slash_1")
    assert card not in state.hand
    assert card in state.discard

def test_play_card_deducts_ap():
    card = _card("slash_1", ap_cost=2)
    state = _make_state([card], ap=3)
    use_case, _, _ = _make_use_case(state)
    use_case.execute("slash_1")
    assert state.player.ap == 1

def test_play_card_publishes_card_played_event():
    card = _card("slash_1", ap_cost=1)
    state = _make_state([card])
    use_case, _, bus = _make_use_case(state)
    use_case.execute("slash_1")
    event = bus.publish.call_args_list[0][0][0]
    assert isinstance(event, CardPlayed)
    assert event.card_id == "slash_1"
    assert event.player_id == "player"

def test_play_card_saves_state():
    card = _card("slash_1", ap_cost=1)
    state = _make_state([card])
    use_case, repo, _ = _make_use_case(state)
    use_case.execute("slash_1")
    repo.save.assert_called_once_with(state)

def test_play_card_not_in_hand_raises():
    state = _make_state([])
    use_case, _, _ = _make_use_case(state)
    with pytest.raises(ValueError, match="not in hand"):
        use_case.execute("ghost")

def test_play_card_insufficient_ap_raises():
    card = _card("slash_1", ap_cost=3)
    state = _make_state([card], ap=0)
    use_case, _, _ = _make_use_case(state)
    with pytest.raises(InsufficientAPError):
        use_case.execute("slash_1")

def test_play_card_draw_after_play_draws_from_deck():
    card = _card("charge_1", ap_cost=0, draw_after=1)
    extra = _extra_deck_card("extra_1")
    state = _make_state([card])
    state.deck = [extra]
    use_case, _, _ = _make_use_case(state)
    use_case.execute("charge_1")
    assert extra in state.hand

def test_play_card_zero_ap_cost_allowed():
    card = _card("charge_1", ap_cost=0)
    state = _make_state([card], ap=0)
    use_case, _, _ = _make_use_case(state)
    use_case.execute("charge_1")   # must not raise
    assert card in state.discard

def test_play_charge_grants_ap():
    card = Card(id="charge_1", name="charge_1", tags=[CardTag("Charge")], ap_cost=0,
                pattern=AttackPattern.single(), damage=0, grants_ap=1)
    state = _make_state([card], ap=2)
    use_case, _, _ = _make_use_case(state)
    use_case.execute("charge_1")
    assert state.player.ap == 3  # 2 - 0 + 1 = 3

def test_play_draw_after_play_publishes_card_drawn():
    card = _card("charge_1", ap_cost=0, draw_after=1)
    extra = _extra_deck_card("extra_1")
    state = _make_state([card])
    state.deck = [extra]
    use_case, _, bus = _make_use_case(state)
    use_case.execute("charge_1")
    events = [call[0][0] for call in bus.publish.call_args_list]
    assert any(isinstance(e, CardDrawn) and e.card_id == "extra_1" for e in events)


_ENEMY_POS = Position(2, 1)  # adjacent to player at (1,1)


def _enemy(id: str = "e1", hp: int = 5) -> Enemy:
    return Enemy(
        id=id,
        position=_ENEMY_POS,
        hp=hp,
        max_hp=hp,
        base_damage=2,
        intent=Intent(type="ATTACK", pattern=AttackPattern.cross(), countdown=2, damage=2),
    )


def test_killing_last_enemy_publishes_battle_ended_victory():
    card = _card("slash_1", ap_cost=1, damage=10)
    state = _make_state([card])
    state.enemies = [_enemy("e1", hp=5)]
    use_case, _, bus = _make_use_case(state)
    use_case.execute("slash_1", _ENEMY_POS)
    events = [call[0][0] for call in bus.publish.call_args_list]
    assert any(isinstance(e, BattleEnded) and e.outcome == "victory" for e in events)


def test_wounding_enemy_does_not_publish_battle_ended():
    card = _card("slash_1", ap_cost=1, damage=2)
    state = _make_state([card])
    state.enemies = [_enemy("e1", hp=10)]
    use_case, _, bus = _make_use_case(state)
    use_case.execute("slash_1", _ENEMY_POS)
    events = [call[0][0] for call in bus.publish.call_args_list]
    assert not any(isinstance(e, BattleEnded) for e in events)


def test_no_enemies_does_not_publish_battle_ended():
    card = _card("slash_1", ap_cost=1)
    state = _make_state([card])
    use_case, _, bus = _make_use_case(state)
    use_case.execute("slash_1", Position(1, 1))
    events = [call[0][0] for call in bus.publish.call_args_list]
    assert not any(isinstance(e, BattleEnded) for e in events)


def test_targeting_wrong_tile_misses_enemy():
    card = _card("slash_1", ap_cost=1, damage=10)
    state = _make_state([card])
    state.enemies = [_enemy("e1", hp=5)]
    use_case, _, bus = _make_use_case(state)
    use_case.execute("slash_1", Position(1, 0))  # adjacent but not enemy tile — enemy survives
    assert state.enemies[0].is_alive()
    events = [call[0][0] for call in bus.publish.call_args_list]
    assert not any(isinstance(e, BattleEnded) for e in events)


def test_targeting_out_of_range_raises_and_does_not_spend_ap():
    card = _card("slash_1", ap_cost=1, damage=10)
    state = _make_state([card])
    state.enemies = [_enemy("e1", hp=5)]
    use_case, _, _ = _make_use_case(state)
    with pytest.raises(ValueError, match="out of range"):
        use_case.execute("slash_1", Position(3, 3))  # distance 4 from player at (1,1)
    assert state.player.ap == 3  # AP not spent


def _step_card(id: str) -> Card:
    return Card(id=id, name="Step", tags=[CardTag("Move")], ap_cost=1,
                pattern=AttackPattern.single(), damage=0)


def test_step_card_moves_player_to_clicked_tile():
    card = _step_card("step_1")
    state = _make_state([card])
    dest = Position(1, 2)  # adjacent to player at (1,1)
    use_case, _, _ = _make_use_case(state)
    use_case.execute("step_1", dest)
    assert state.player.position == dest
    assert state.grid.get_entity_position("player") == dest


def test_step_card_discards_and_spends_ap():
    card = _step_card("step_1")
    state = _make_state([card], ap=3)
    use_case, _, _ = _make_use_case(state)
    use_case.execute("step_1", Position(2, 1))
    assert card not in state.hand
    assert card in state.discard
    assert state.player.ap == 2


def test_step_card_onto_occupied_tile_raises():
    card = _step_card("step_1")
    state = _make_state([card])
    state.enemies = [_enemy("e1", hp=5)]
    state.grid.place("e1", _ENEMY_POS)  # production always places enemies on the grid
    use_case, _, _ = _make_use_case(state)
    with pytest.raises(ValueError, match="not passable"):
        use_case.execute("step_1", _ENEMY_POS)
    assert state.player.ap == 3  # AP not spent


def test_step_card_without_target_raises():
    card = _step_card("step_1")
    state = _make_state([card])
    use_case, _, _ = _make_use_case(state)
    with pytest.raises(ValueError):
        use_case.execute("step_1")


def _double_step_card(id: str) -> Card:
    return Card(id=id, name="Step+Step", tags=[CardTag("Move")], ap_cost=1,
                pattern=AttackPattern.single(), damage=0, move_distance=2)


def test_double_step_card_can_reach_distance_2():
    card = _double_step_card("step_step_1")
    state = _make_state([card])
    dest = Position(1, 3)  # 2 tiles away from player at (1,1)
    use_case, _, _ = _make_use_case(state)
    use_case.execute("step_step_1", dest)
    assert state.player.position == dest
    assert state.grid.get_entity_position("player") == dest


def test_double_step_card_can_also_reach_distance_1():
    card = _double_step_card("step_step_1")
    state = _make_state([card])
    dest = Position(1, 2)  # 1 tile away — still valid
    use_case, _, _ = _make_use_case(state)
    use_case.execute("step_step_1", dest)
    assert state.player.position == dest


def test_single_step_card_cannot_reach_distance_2():
    card = _step_card("step_1")
    state = _make_state([card])
    use_case, _, _ = _make_use_case(state)
    with pytest.raises(ValueError, match="out of range"):
        use_case.execute("step_1", Position(1, 3))  # 2 tiles away
    assert state.player.ap == 3  # AP not spent
