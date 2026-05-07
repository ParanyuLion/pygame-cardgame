import pytest
from unittest.mock import MagicMock
from src.domain.battle_state import BattleState
from src.domain.entities.grid import Grid
from src.domain.entities.player import Player
from src.domain.entities.card import Card
from src.domain.value_objects.position import Position
from src.domain.value_objects.card_tag import CardTag
from src.domain.value_objects.attack_pattern import AttackPattern
from src.domain.events.battle_events import CardsFused
from src.use_cases.fuse_cards import FuseCardsUseCase


def _card(id: str, tags: list[str], ap: int = 1, dmg: int = 0) -> Card:
    return Card(
        id=id, name=id, tags=[CardTag(t) for t in tags],
        ap_cost=ap, pattern=AttackPattern.single(), damage=dmg,
    )


def _make_state(hand_cards: list[Card]) -> BattleState:
    grid = Grid()
    player = Player(id="player", position=Position(0, 0), hp=30, max_hp=30, ap=3, max_ap=3)
    state = BattleState(player=player, grid=grid)
    state.hand = list(hand_cards)
    return state


def _make_use_case(state: BattleState):
    repo = MagicMock()
    repo.get.return_value = state
    bus = MagicMock()
    return FuseCardsUseCase(repo, bus), repo, bus


def test_fuse_removes_both_source_cards():
    a = _card("strike_1", ["Blade"])
    b = _card("slash_1", ["Blade"])
    state = _make_state([a, b])
    use_case, _, _ = _make_use_case(state)
    use_case.execute("strike_1", "slash_1")
    assert a not in state.hand
    assert b not in state.hand


def test_fuse_adds_fused_card_to_hand():
    a = _card("strike_1", ["Blade"])
    b = _card("slash_1", ["Blade"])
    state = _make_state([a, b])
    use_case, _, _ = _make_use_case(state)
    use_case.execute("strike_1", "slash_1")
    assert len(state.hand) == 1
    assert state.hand[0].id == "fused_strike_1_slash_1"


def test_fuse_tracks_consumed_ids():
    a = _card("strike_1", ["Blade"])
    b = _card("slash_1", ["Blade"])
    state = _make_state([a, b])
    use_case, _, _ = _make_use_case(state)
    use_case.execute("strike_1", "slash_1")
    assert "strike_1" in state.fused_card_ids
    assert "slash_1" in state.fused_card_ids


def test_fuse_saves_state():
    a = _card("strike_1", ["Blade"])
    b = _card("slash_1", ["Blade"])
    state = _make_state([a, b])
    use_case, repo, _ = _make_use_case(state)
    use_case.execute("strike_1", "slash_1")
    repo.save.assert_called_once_with(state)


def test_fuse_publishes_cards_fused_event():
    a = _card("strike_1", ["Blade"])
    b = _card("slash_1", ["Blade"])
    state = _make_state([a, b])
    use_case, _, bus = _make_use_case(state)
    use_case.execute("strike_1", "slash_1")
    event = bus.publish.call_args[0][0]
    assert isinstance(event, CardsFused)
    assert event.card_a_id == "strike_1"
    assert event.card_b_id == "slash_1"
    assert event.result_card_id == "fused_strike_1_slash_1"


def test_fuse_card_not_in_hand_raises():
    a = _card("strike_1", ["Blade"])
    state = _make_state([a])
    use_case, _, _ = _make_use_case(state)
    with pytest.raises(ValueError, match="not in hand"):
        use_case.execute("strike_1", "ghost")


def test_fuse_incompatible_cards_raises():
    a = _card("strike_1", ["Blade"])
    b = _card("spark_1", ["Electric"])
    state = _make_state([a, b])
    use_case, _, _ = _make_use_case(state)
    with pytest.raises(ValueError, match="cannot fuse"):
        use_case.execute("strike_1", "spark_1")
