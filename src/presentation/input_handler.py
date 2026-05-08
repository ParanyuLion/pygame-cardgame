from __future__ import annotations
import pygame
from src.domain.interfaces import IBattleRepository
from src.domain.entities.player import InsufficientAPError
from src.use_cases.move_entity import MoveEntityUseCase
from src.use_cases.play_card import PlayCardUseCase
from src.use_cases.fuse_cards import FuseCardsUseCase
from src.use_cases.end_turn import EndTurnUseCase
from src.presentation.renderers.hand_renderer import HandRenderer
from src.presentation.renderers.grid_renderer import GridRenderer
from src.presentation.renderers.hud_renderer import END_TURN_RECT

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

_DRAG_THRESHOLD = 8  # Manhattan distance in pixels to confirm drag intent


class InputHandler:
    def __init__(
        self,
        move_use_case: MoveEntityUseCase,
        play_use_case: PlayCardUseCase,
        fuse_use_case: FuseCardsUseCase,
        end_turn_use_case: EndTurnUseCase,
        battle_repo: IBattleRepository,
        hand_renderer: HandRenderer,
        grid_renderer: GridRenderer,
    ) -> None:
        self._move = move_use_case
        self._play = play_use_case
        self._fuse = fuse_use_case
        self._end_turn = end_turn_use_case
        self._repo = battle_repo
        self._hand_renderer = hand_renderer
        self._grid_renderer = grid_renderer
        self._selected_card_id: str | None = None
        self._drag_card_id: str | None = None
        self._drag_start: tuple[int, int] | None = None
        self._dragging: bool = False

    @property
    def selected_card_id(self) -> str | None:
        return self._selected_card_id

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            self._handle_key(event)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._handle_mouse_down(event.pos)
        elif event.type == pygame.MOUSEMOTION:
            self._handle_mouse_motion(event.pos, event.buttons)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._handle_mouse_up(event.pos)

    def _handle_key(self, event: pygame.event.Event) -> None:
        if event.key == pygame.K_e:
            self._end_turn.execute()
            return
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

    def _handle_mouse_down(self, pos: tuple[int, int]) -> None:
        state = self._repo.get()
        clicked_card = self._hand_renderer.card_at_point(pos, state.hand)
        if clicked_card is not None:
            self._drag_card_id = clicked_card.id
            self._drag_start = pos
            self._dragging = False

    def _handle_mouse_motion(
        self, pos: tuple[int, int], buttons: tuple[int, int, int]
    ) -> None:
        if not buttons[0] or self._drag_card_id is None:
            return
        if not self._dragging and self._drag_start is not None:
            dx = abs(pos[0] - self._drag_start[0])
            dy = abs(pos[1] - self._drag_start[1])
            if dx + dy > _DRAG_THRESHOLD:
                self._dragging = True
        if self._dragging:
            state = self._repo.get()
            drag_card = next(
                (c for c in state.hand if c.id == self._drag_card_id), None
            )
            if drag_card is not None:
                self._hand_renderer.set_drag(drag_card, pos)

    def _handle_mouse_up(self, pos: tuple[int, int]) -> None:
        if self._dragging and self._drag_card_id is not None:
            self._hand_renderer.clear_drag()
            state = self._repo.get()
            target_card = self._hand_renderer.card_at_point(pos, state.hand)
            if target_card is not None and target_card.id != self._drag_card_id:
                try:
                    self._fuse.execute(self._drag_card_id, target_card.id)
                    self._selected_card_id = None
                    self._hand_renderer.set_selected(None)
                except ValueError:
                    pass
        else:
            click_pos = self._drag_start if self._drag_start is not None else pos
            self._handle_click(click_pos)
        self._drag_card_id = None
        self._drag_start = None
        self._dragging = False

    def _handle_click(self, pos: tuple[int, int]) -> None:
        if END_TURN_RECT.collidepoint(pos):
            self._end_turn.execute()
            return
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
        target_pos = self._grid_renderer.screen_to_tile(pos[0], pos[1])
        if target_pos is None:
            return
        try:
            self._play.execute(self._selected_card_id, target_pos)
            self._selected_card_id = None
            self._hand_renderer.set_selected(None)
        except (InsufficientAPError, ValueError):
            pass
