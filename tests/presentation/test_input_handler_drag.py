import pygame
from unittest.mock import MagicMock
from src.domain.battle_state import BattleState
from src.domain.entities.grid import Grid
from src.domain.entities.player import Player
from src.domain.entities.card import Card
from src.domain.value_objects.position import Position
from src.domain.value_objects.card_tag import CardTag
from src.domain.value_objects.attack_pattern import AttackPattern
from src.presentation.input_handler import InputHandler
from src.presentation.renderers.hand_renderer import HandRenderer
from src.presentation.renderers.grid_renderer import GridRenderer


def _card(id: str, tags: list[str] | None = None) -> Card:
    return Card(
        id=id, name=id,
        tags=[CardTag(t) for t in (tags or ["Blade"])],
        ap_cost=1, pattern=AttackPattern.single(), damage=0,
    )


def _make_state(hand_cards: list[Card]) -> BattleState:
    grid = Grid()
    player = Player(id="player", position=Position(0, 0), hp=30, max_hp=30, ap=3, max_ap=3)
    state = BattleState(player=player, grid=grid)
    state.hand = list(hand_cards)
    return state


def _make_handler(state: BattleState) -> tuple[InputHandler, MagicMock, HandRenderer]:
    repo = MagicMock()
    repo.get.return_value = state
    move = MagicMock()
    play = MagicMock()
    fuse = MagicMock()
    end_turn = MagicMock()
    hand_renderer = HandRenderer()
    grid_renderer = GridRenderer()
    handler = InputHandler(move, play, fuse, end_turn, repo, hand_renderer, grid_renderer)
    return handler, fuse, hand_renderer


def test_drag_onto_different_card_calls_fuse():
    card_a = _card("a_1")
    card_b = _card("b_1")
    state = _make_state([card_a, card_b])
    handler, fuse, hand_renderer = _make_handler(state)

    rect_a = hand_renderer.card_rect(0, 2)
    rect_b = hand_renderer.card_rect(1, 2)
    center_a = rect_a.center
    center_b = rect_b.center

    # Press on card_a
    handler.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=center_a))
    # Move far enough to trigger drag (cards are 90px apart)
    handler.handle_event(pygame.event.Event(
        pygame.MOUSEMOTION, pos=center_b, buttons=(1, 0, 0), rel=(0, 0),
    ))
    # Release on card_b
    handler.handle_event(pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=center_b))

    fuse.execute.assert_called_once_with("a_1", "b_1")


def test_drag_onto_same_card_does_not_fuse():
    card_a = _card("a_1")
    card_b = _card("b_1")
    state = _make_state([card_a, card_b])
    handler, fuse, hand_renderer = _make_handler(state)

    rect_a = hand_renderer.card_rect(0, 2)
    center_a = rect_a.center

    handler.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=center_a))
    handler.handle_event(pygame.event.Event(
        pygame.MOUSEMOTION,
        pos=(center_a[0] + 20, center_a[1]),
        buttons=(1, 0, 0),
        rel=(0, 0),
    ))
    handler.handle_event(pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=center_a))

    fuse.execute.assert_not_called()


def test_click_card_without_drag_selects_it():
    card_a = _card("a_1")
    state = _make_state([card_a])
    handler, fuse, hand_renderer = _make_handler(state)

    rect = hand_renderer.card_rect(0, 1)
    center = rect.center
    # Quick click (no MOUSEMOTION → _dragging stays False)
    handler.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=center))
    handler.handle_event(pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=center))

    assert handler._selected_card_id == "a_1"
    fuse.execute.assert_not_called()
