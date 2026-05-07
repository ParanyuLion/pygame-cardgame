from __future__ import annotations
import pygame

_TITLE_COLOR = (220, 180, 100)
_SUB_COLOR = (160, 140, 110)
_W = 560
_H = 700


class MenuRenderer:
    def __init__(self) -> None:
        self._font_title = pygame.font.SysFont("serif", 36)
        self._font_sub = pygame.font.SysFont("serif", 20)

    def render(self, surface: pygame.Surface) -> None:
        title = self._font_title.render("Dungeon Card Roguelike", True, _TITLE_COLOR)
        sub = self._font_sub.render("Press SPACE to start", True, _SUB_COLOR)
        surface.blit(title, (_W // 2 - title.get_width() // 2, 200))
        surface.blit(sub, (_W // 2 - sub.get_width() // 2, 350))
