from __future__ import annotations
import os
import pygame
from src.domain.entities.player import Player
from src.presentation.renderers.grid_renderer import GridRenderer, TILE_SIZE

LERP_SPEED = 10.0
_SPRITE_SIZE = TILE_SIZE - 16  # 80px — leaves 8px padding each side
_SPRITE_PATH = os.path.join("assets", "sprites", "player.png")

COLOR_PLAYER_GLOW = (220, 190, 80, 50)


class EntityRenderer:
    def __init__(self, grid_renderer: GridRenderer) -> None:
        self._grid = grid_renderer
        self._display_x: float | None = None
        self._display_y: float | None = None
        self._sprite: pygame.Surface | None = None

    def _load_sprite(self) -> None:
        if os.path.exists(_SPRITE_PATH):
            try:
                raw = pygame.image.load(_SPRITE_PATH).convert_alpha()
            except pygame.error:
                raw = pygame.image.load(_SPRITE_PATH)
            self._sprite = pygame.transform.scale(raw, (_SPRITE_SIZE, _SPRITE_SIZE))

    def update(self, dt: float, player: Player) -> None:
        tx, ty = self._grid.tile_center(player.position)
        if self._display_x is None:
            self._display_x, self._display_y = float(tx), float(ty)
        else:
            self._display_x += (tx - self._display_x) * LERP_SPEED * dt
            self._display_y += (ty - self._display_y) * LERP_SPEED * dt

    def render(self, surface: pygame.Surface, player: Player) -> None:
        if self._display_x is None:
            return
        if self._sprite is None:
            self._load_sprite()

        cx, cy = int(self._display_x), int(self._display_y)

        if self._sprite is not None:
            half = _SPRITE_SIZE // 2
            surface.blit(self._sprite, (cx - half, cy - half))
        else:
            # Fallback: colored circle
            radius = TILE_SIZE // 3
            glow = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
            pygame.draw.circle(glow, COLOR_PLAYER_GLOW, (radius * 2, radius * 2), radius + 10)
            surface.blit(glow, (cx - radius * 2, cy - radius * 2))
            pygame.draw.circle(surface, (190, 150, 60), (cx, cy), radius)
            pygame.draw.circle(surface, (240, 200, 80), (cx, cy), radius, 2)
