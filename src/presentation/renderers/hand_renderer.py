from __future__ import annotations
import os
import re
import pygame
from src.domain.entities.card import Card

CARD_W = 80
CARD_H = 110
CARD_GAP = 10
HAND_Y = 490

_ICON_SIZE = 52
_ICON_Y_OFFSET = 20  # from card top to icon top

COLOR_CARD_BG = (220, 200, 160)
COLOR_CARD_SELECTED = (255, 240, 180)
COLOR_TEXT = (30, 20, 10)

_TAG_BORDER: dict[str, tuple[int, int, int]] = {
    "Move":     (60, 160, 80),
    "Blade":    (80, 120, 180),
    "Fire":     (200, 80, 40),
    "Electric": (200, 180, 40),
    "Area":     (140, 60, 180),
}
_DEFAULT_BORDER = (120, 110, 90)

_ICON_CACHE: dict[str, pygame.Surface | None] = {}
_ICONS_DIR = os.path.join("assets", "sprites", "cards")


def _def_id(card_id: str) -> str:
    cid = re.sub(r"^reward_", "", card_id)
    cid = re.sub(r"_\d+$", "", cid)
    return cid


def _load_icon(def_id: str) -> pygame.Surface | None:
    if def_id in _ICON_CACHE:
        return _ICON_CACHE[def_id]
    path = os.path.join(_ICONS_DIR, f"{def_id}.png")
    if not os.path.exists(path):
        _ICON_CACHE[def_id] = None
        return None
    try:
        raw = pygame.image.load(path).convert_alpha()
    except pygame.error:
        try:
            raw = pygame.image.load(path)
        except Exception:
            _ICON_CACHE[def_id] = None
            return None
    surf = pygame.transform.smoothscale(raw, (_ICON_SIZE, _ICON_SIZE))
    _ICON_CACHE[def_id] = surf
    return surf


class HandRenderer:
    def __init__(self, window_width: int = 560) -> None:
        self._window_width = window_width
        self._selected_id: str | None = None
        self._font_name: pygame.font.Font | None = None
        self._font_cost: pygame.font.Font | None = None
        self._drag_card: Card | None = None
        self._drag_pos: tuple[int, int] | None = None

    def set_selected(self, card_id: str | None) -> None:
        self._selected_id = card_id

    def set_drag(self, card: Card, pos: tuple[int, int]) -> None:
        self._drag_card = card
        self._drag_pos = pos

    def clear_drag(self) -> None:
        self._drag_card = None
        self._drag_pos = None

    def card_rect(self, index: int, hand_size: int) -> pygame.Rect:
        total_w = hand_size * CARD_W + max(0, hand_size - 1) * CARD_GAP
        start_x = (self._window_width - total_w) // 2
        x = start_x + index * (CARD_W + CARD_GAP)
        return pygame.Rect(x, HAND_Y, CARD_W, CARD_H)

    def card_at_point(self, point: tuple[int, int], hand: list[Card]) -> Card | None:
        px, py = point
        half_gap = CARD_GAP // 2
        for i, card in enumerate(hand):
            r = self.card_rect(i, len(hand))
            if (r.left - half_gap <= px <= r.right + half_gap
                    and r.top <= py <= r.bottom):
                return card
        return None

    def render(self, surface: pygame.Surface, hand: list[Card]) -> None:
        if not hand:
            return
        if self._font_name is None:
            self._font_name = pygame.font.SysFont("Arial", 10, bold=True)
            self._font_cost = pygame.font.SysFont("Arial", 14, bold=True)

        for i, card in enumerate(hand):
            rect = self.card_rect(i, len(hand))
            is_selected = card.id == self._selected_id
            self._render_card(surface, card, rect, is_selected)

        self._render_drag_ghost(surface)

    def _render_card(
        self, surface: pygame.Surface, card: Card, rect: pygame.Rect, is_selected: bool
    ) -> None:
        bg = COLOR_CARD_SELECTED if is_selected else COLOR_CARD_BG
        pygame.draw.rect(surface, bg, rect, border_radius=4)

        first_tag = card.tags[0].value if card.tags else ""
        border_color = _TAG_BORDER.get(first_tag, _DEFAULT_BORDER)
        border_w = 3 if is_selected else 2
        pygame.draw.rect(surface, border_color, rect, width=border_w, border_radius=4)

        # Card name (top)
        name_surf = self._font_name.render(card.name, True, COLOR_TEXT)
        surface.blit(name_surf, (rect.x + 4, rect.y + 4))

        # Icon centred in the card body
        icon = _load_icon(_def_id(card.id))
        if icon is not None:
            ix = rect.x + (CARD_W - _ICON_SIZE) // 2
            iy = rect.y + _ICON_Y_OFFSET
            surface.blit(icon, (ix, iy))

        # AP cost (bottom-left)
        cost_label = f"{card.ap_cost}AP"
        cost_surf = self._font_cost.render(cost_label, True, border_color)
        surface.blit(cost_surf, (rect.x + 4, rect.bottom - 20))

    def _render_drag_ghost(self, surface: pygame.Surface) -> None:
        if self._drag_card is None or self._drag_pos is None:
            return
        ghost = pygame.Surface((CARD_W, CARD_H), pygame.SRCALPHA)
        first_tag = self._drag_card.tags[0].value if self._drag_card.tags else ""
        border_color = _TAG_BORDER.get(first_tag, _DEFAULT_BORDER)
        ghost.fill((*COLOR_CARD_BG, 180))
        pygame.draw.rect(ghost, (*border_color, 220), ghost.get_rect(), width=3, border_radius=4)
        x = self._drag_pos[0] - CARD_W // 2
        y = self._drag_pos[1] - CARD_H // 2
        surface.blit(ghost, (x, y))
