from __future__ import annotations
import pygame
from src.domain.interfaces import IBattleRepository
from src.domain.entities.player import InsufficientAPError
from src.use_cases.move_entity import MoveEntityUseCase

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
        battle_repo: IBattleRepository,
    ) -> None:
        self._move = move_use_case
        self._repo = battle_repo

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
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
