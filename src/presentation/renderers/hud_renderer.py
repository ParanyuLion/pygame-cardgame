from __future__ import annotations
import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.domain.entities.player import Player

_HUD_Y = 14
_COLOR_HP_BAR = (180, 50, 40)
_COLOR_HP_BG = (60, 20, 20)
_COLOR_AP_FULL = (200, 170, 60)
_COLOR_AP_EMPTY = (50, 40, 15)
_COLOR_TEXT = (200, 180, 140)
_BAR_X = 108
_BAR_W = 140
_BAR_H = 14
_PIP_R = 8
_PIP_GAP = 6
_RIGHT_MARGIN = 80
_WINDOW_W = 560

END_TURN_RECT = pygame.Rect(415, 628, 120, 42)
_COLOR_BTN_NORMAL = (55, 40, 22)
_COLOR_BTN_HOVER = (80, 60, 32)
_COLOR_BTN_BORDER = (140, 110, 60)
_COLOR_BTN_BORDER_HOVER = (200, 160, 80)


class HudRenderer:
    def __init__(self) -> None:
        self._font: pygame.font.Font | None = None

    def render(self, surface: pygame.Surface, player: Player) -> None:
        if self._font is None:
            self._font = pygame.font.SysFont("Arial", 14, bold=True)

        self._render_hp(surface, player)
        self._render_ap(surface, player)
        self._render_end_turn_button(surface)

    def _render_end_turn_button(self, surface: pygame.Surface) -> None:
        hovered = END_TURN_RECT.collidepoint(pygame.mouse.get_pos())
        bg = _COLOR_BTN_HOVER if hovered else _COLOR_BTN_NORMAL
        border = _COLOR_BTN_BORDER_HOVER if hovered else _COLOR_BTN_BORDER
        pygame.draw.rect(surface, bg, END_TURN_RECT, border_radius=5)
        pygame.draw.rect(surface, border, END_TURN_RECT, width=2, border_radius=5)
        label = self._font.render("End Turn (E)", True, _COLOR_TEXT)
        lx = END_TURN_RECT.centerx - label.get_width() // 2
        ly = END_TURN_RECT.centery - label.get_height() // 2
        surface.blit(label, (lx, ly))

    def _render_hp(self, surface: pygame.Surface, player: Player) -> None:
        label = self._font.render("HP", True, _COLOR_TEXT)
        surface.blit(label, (80, _HUD_Y))

        bg = pygame.Rect(_BAR_X, _HUD_Y + 1, _BAR_W, _BAR_H)
        pygame.draw.rect(surface, _COLOR_HP_BG, bg, border_radius=3)

        fill_w = int(_BAR_W * max(0, player.hp) / player.max_hp) if player.max_hp else 0
        if fill_w > 0:
            pygame.draw.rect(surface, _COLOR_HP_BAR,
                             pygame.Rect(_BAR_X, _HUD_Y + 1, fill_w, _BAR_H),
                             border_radius=3)

        pygame.draw.rect(surface, _COLOR_TEXT, bg, width=1, border_radius=3)

        nums = self._font.render(f"{player.hp}/{player.max_hp}", True, _COLOR_TEXT)
        surface.blit(nums, (_BAR_X + _BAR_W + 6, _HUD_Y))

    def _render_ap(self, surface: pygame.Surface, player: Player) -> None:
        total_w = player.max_ap * (_PIP_R * 2 + _PIP_GAP) - _PIP_GAP
        start_x = _WINDOW_W - _RIGHT_MARGIN - total_w

        label = self._font.render("AP", True, _COLOR_TEXT)
        surface.blit(label, (start_x - 32, _HUD_Y))

        for i in range(player.max_ap):
            cx = start_x + i * (_PIP_R * 2 + _PIP_GAP) + _PIP_R
            cy = _HUD_Y + _PIP_R
            color = _COLOR_AP_FULL if i < player.ap else _COLOR_AP_EMPTY
            pygame.draw.circle(surface, color, (cx, cy), _PIP_R)
            pygame.draw.circle(surface, _COLOR_TEXT, (cx, cy), _PIP_R, width=1)
