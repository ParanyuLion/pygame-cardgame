from __future__ import annotations
import pygame
from typing import Callable, TYPE_CHECKING
from src.presentation.renderers.card_reward_renderer import CardRewardRenderer

if TYPE_CHECKING:
    from src.domain.entities.card import Card


class RewardScene:
    def __init__(
        self,
        choices: list[Card],
        on_card_chosen: Callable[[Card], None],
    ) -> None:
        self._choices = choices
        self._on_card_chosen = on_card_chosen
        self._renderer = CardRewardRenderer()

    def on_enter(self) -> None:
        pass

    def on_exit(self) -> None:
        pass

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, card in enumerate(self._choices):
                rect = self._renderer.card_rect(i)
                if rect.collidepoint(event.pos):
                    self._on_card_chosen(card)
                    return

    def update(self, dt: float) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        self._renderer.render(surface, self._choices)
