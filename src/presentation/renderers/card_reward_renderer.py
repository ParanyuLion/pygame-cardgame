from __future__ import annotations
import pygame

_CARD_W = 120
_CARD_H = 180
_CARD_GAP = 20
_CARD_TOP = 200
_W = 560

_COLOR_BG = (60, 45, 30)
_COLOR_BORDER = (180, 140, 80)
_COLOR_TEXT = (220, 200, 160)
_COLOR_HEADING = (220, 180, 100)


class CardRewardRenderer:
    def __init__(self) -> None:
        self._font = pygame.font.SysFont("serif", 14)
        self._font_heading = pygame.font.SysFont("serif", 24)

    def card_rect(self, idx: int) -> pygame.Rect:
        total_w = 3 * _CARD_W + 2 * _CARD_GAP
        start_x = (_W - total_w) // 2
        x = start_x + idx * (_CARD_W + _CARD_GAP)
        return pygame.Rect(x, _CARD_TOP, _CARD_W, _CARD_H)

    def render(self, surface: pygame.Surface, cards: list) -> None:
        heading = self._font_heading.render("Choose a reward:", True, _COLOR_HEADING)
        surface.blit(heading, (_W // 2 - heading.get_width() // 2, 140))
        for i, card in enumerate(cards):
            rect = self.card_rect(i)
            pygame.draw.rect(surface, _COLOR_BG, rect)
            pygame.draw.rect(surface, _COLOR_BORDER, rect, 2)
            name_surf = self._font.render(card.name, True, _COLOR_TEXT)
            surface.blit(name_surf, (rect.x + 8, rect.y + 10))
            cost_surf = self._font.render(f"AP: {card.ap_cost}", True, _COLOR_TEXT)
            surface.blit(cost_surf, (rect.x + 8, rect.y + 30))
