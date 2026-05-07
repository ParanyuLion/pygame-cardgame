import pytest
from unittest.mock import MagicMock
from src.domain.battle_state import BattleState
from src.domain.entities.grid import Grid
from src.domain.entities.player import Player
from src.domain.entities.card import Card
from src.domain.value_objects.position import Position
from src.domain.value_objects.card_tag import CardTag
from src.domain.value_objects.attack_pattern import AttackPattern
from src.domain.events.battle_events import CardDrawn
from src.use_cases.draw_cards import DrawCardsUseCase

def _card(id: str) -> Card:
    return Card(id=id, name=id, tags=[CardTag("Blade")], ap_cost=1,
                pattern=AttackPattern.single(), damage=0)

def _make_state(*deck_ids: str) -> BattleState:
    grid = Grid()
    player = Player(id="player", position=Position(0, 0), hp=30, max_hp=30, ap=3, max_ap=3)
    state = BattleState(player=player, grid=grid)
    state.deck = [_card(cid) for cid in deck_ids]
    return state

def _make_use_case(state: BattleState) -> tuple[DrawCardsUseCase, MagicMock, MagicMock]:
    repo = MagicMock()
    repo.get.return_value = state
    bus = MagicMock()
    return DrawCardsUseCase(repo, bus), repo, bus

def test_draw_moves_cards_to_hand():
    state = _make_state("a", "b", "c")
    use_case, _, _ = _make_use_case(state)
    use_case.execute(2)
    assert len(state.hand) == 2
    assert len(state.deck) == 1

def test_draw_publishes_card_drawn_per_card():
    state = _make_state("a", "b")
    use_case, _, bus = _make_use_case(state)
    use_case.execute(2)
    assert bus.publish.call_count == 2
    events = [call[0][0] for call in bus.publish.call_args_list]
    assert all(isinstance(e, CardDrawn) for e in events)
    assert {e.card_id for e in events} == {"a", "b"}

def test_draw_stops_at_deck_and_discard_empty():
    state = _make_state("only")
    use_case, _, bus = _make_use_case(state)
    use_case.execute(5)
    assert len(state.hand) == 1
    assert bus.publish.call_count == 1

def test_draw_shuffles_discard_when_deck_empty():
    state = _make_state()
    state.discard = [_card("x"), _card("y")]
    use_case, _, _ = _make_use_case(state)
    use_case.execute(1)
    assert len(state.hand) == 1
    assert len(state.discard) == 0

def test_draw_saves_state_once():
    state = _make_state("a", "b")
    use_case, repo, _ = _make_use_case(state)
    use_case.execute(2)
    repo.save.assert_called_once_with(state)
