from __future__ import annotations
import pygame
from src.domain.interfaces import IBattleRepository
from src.domain.entities.player import InsufficientAPError
from src.use_cases.move_entity import MoveEntityUseCase
from src.use_cases.play_card import PlayCardUseCase
from src.presentation.renderers.hand_renderer import HandRenderer
from src.presentation.renderers.grid_renderer import GridRenderer

_ARROW_TO_OFFSET: dict[int, tuple[int, int]] = {
    pygame.K_UP:    (0, -1),
    pygame.K_DOWN:  (0,  1),
    pygame.K_LEFT:  (-1, 0),
    pygame.K_RIGHT: (1,  0),
    pygame.K_w:     (0, -1),
    pygame.K_s:     (0,  1),
    pygame.K_a:     (-1, 0),
    pygame.K_d:     (1,  0),
}

class InputHandler:
    def __init__(
        self,
        move_use_case: MoveEntityUseCase,
        play_use_case: PlayCardUseCase,
        battle_repo: IBattleRepository,
        hand_renderer: HandRenderer,
        grid_renderer: GridRenderer,
    ) -> None:
        self._move = move_use_case
        self._play = play_use_case
        self._repo = battle_repo
        self._hand_renderer = hand_renderer
        self._grid_renderer = grid_renderer
        self._selected_card_id: str | None = None

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            self._handle_key(event)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._handle_click(event.pos)

    def _handle_key(self, event: pygame.event.Event) -> None:
        if event.key not in _ARROW_TO_OFFSET:
            return
        state = self._repo.get()
        dcol, drow = _ARROW_TO_OFFSET[event.key]
        target = state.player.position.offset(dcol, drow)
        if target is None:
            return
        try:
            self._move.execute(state.player.id, target)
        except (InsufficientAPError, ValueError):
            pass

    def _handle_click(self, pos: tuple[int, int]) -> None:
        state = self._repo.get()

        clicked_card = self._hand_renderer.card_at_point(pos, state.hand)
        if clicked_card is not None:
            if self._selected_card_id == clicked_card.id:
                self._selected_card_id = None
            else:
                self._selected_card_id = clicked_card.id
            self._hand_renderer.set_selected(self._selected_card_id)
            return

        if self._selected_card_id is None:
            return

        try:
            self._play.execute(self._selected_card_id)
            self._selected_card_id = None
            self._hand_renderer.set_selected(None)
        except (InsufficientAPError, ValueError):
            pass
