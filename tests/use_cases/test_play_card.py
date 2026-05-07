import pytest
from unittest.mock import MagicMock
from src.domain.battle_state import BattleState
from src.domain.entities.grid import Grid
from src.domain.entities.player import Player, InsufficientAPError
from src.domain.entities.card import Card, CardContext
from src.domain.value_objects.position import Position
from src.domain.value_objects.card_tag import CardTag
from src.domain.value_objects.attack_pattern import AttackPattern
from src.domain.events.battle_events import CardPlayed
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
