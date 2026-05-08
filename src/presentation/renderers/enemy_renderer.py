from __future__ import annotations
import os
import pygame
from src.domain.entities.enemy import Enemy
from src.presentation.renderers.grid_renderer import GridRenderer, TILE_SIZE

_SPRITE_SIZE = TILE_SIZE - 16  # 80px
_SPRITE_PATH = os.path.join("assets", "sprites", "enemy.png")

COLOR_ENEMY = (160, 40, 40)
COLOR_ENEMY_BORDER = (200, 60, 60)
COLOR_HP_BG = (60, 20, 20)
COLOR_HP_FG = (200, 60, 60)
COLOR_ORDER = (240, 200, 80)


class EnemyRenderer:
    def __init__(self, grid_renderer: GridRenderer) -> None:
        self._grid = grid_renderer
        self._font: pygame.font.Font | None = None
        self._sprite: pygame.Surface | None = None

    def _load_sprite(self) -> None:
        if os.path.exists(_SPRITE_PATH):
            try:
                raw = pygame.image.load(_SPRITE_PATH).convert_alpha()
            except pygame.error:
                raw = pygame.image.load(_SPRITE_PATH)
            self._sprite = pygame.transform.scale(raw, (_SPRITE_SIZE, _SPRITE_SIZE))

    def render(self, surface: pygame.Surface, enemies: list[Enemy]) -> None:
        if self._font is None:
            self._font = pygame.font.SysFont("Arial", 14, bold=True)
        if self._sprite is None:
            self._load_sprite()
        alive = sorted([e for e in enemies if e.is_alive()], key=lambda e: e.hp)
        for order, enemy in enumerate(alive, start=1):
            self._render_enemy(surface, enemy, order)

    def _render_enemy(
        self, surface: pygame.Surface, enemy: Enemy, order: int
    ) -> None:
        cx, cy = self._grid.tile_center(enemy.position)

        if self._sprite is not None:
            half = _SPRITE_SIZE // 2
            surface.blit(self._sprite, (cx - half, cy - half))
            hp_offset = half + 6
        else:
            radius = TILE_SIZE // 3
            pygame.draw.circle(surface, COLOR_ENEMY, (cx, cy), radius)
            pygame.draw.circle(surface, COLOR_ENEMY_BORDER, (cx, cy), radius, 2)
            hp_offset = radius + 14

        bar_w = TILE_SIZE - 10
        bar_h = 6
        bar_x = cx - bar_w // 2
        bar_y = cy - hp_offset
        pygame.draw.rect(surface, COLOR_HP_BG, (bar_x, bar_y, bar_w, bar_h))
        fill_w = int(bar_w * enemy.hp / enemy.max_hp) if enemy.max_hp > 0 else 0
        if fill_w > 0:
            pygame.draw.rect(surface, COLOR_HP_FG, (bar_x, bar_y, fill_w, bar_h))

        order_surf = self._font.render(str(order), True, COLOR_ORDER)
        surface.blit(order_surf, (cx - order_surf.get_width() // 2, bar_y - 16))
