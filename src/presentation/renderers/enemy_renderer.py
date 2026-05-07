from __future__ import annotations
import pygame
from src.domain.entities.enemy import Enemy
from src.presentation.renderers.grid_renderer import GridRenderer, TILE_SIZE

COLOR_ENEMY = (160, 40, 40)
COLOR_ENEMY_BORDER = (200, 60, 60)
COLOR_HP_BG = (60, 20, 20)
COLOR_HP_FG = (200, 60, 60)
COLOR_ORDER = (240, 200, 80)


class EnemyRenderer:
    def __init__(self, grid_renderer: GridRenderer) -> None:
        self._grid = grid_renderer
        self._font: pygame.font.Font | None = None

    def render(self, surface: pygame.Surface, enemies: list[Enemy]) -> None:
        if self._font is None:
            self._font = pygame.font.SysFont("Arial", 14, bold=True)
        alive = sorted([e for e in enemies if e.is_alive()], key=lambda e: e.hp)
        for order, enemy in enumerate(alive, start=1):
            self._render_enemy(surface, enemy, order)

    def _render_enemy(
        self, surface: pygame.Surface, enemy: Enemy, order: int
    ) -> None:
        cx, cy = self._grid.tile_center(enemy.position)
        radius = TILE_SIZE // 3

        pygame.draw.circle(surface, COLOR_ENEMY, (cx, cy), radius)
        pygame.draw.circle(surface, COLOR_ENEMY_BORDER, (cx, cy), radius, 2)

        bar_w = TILE_SIZE - 10
        bar_h = 6
        bar_x = cx - bar_w // 2
        bar_y = cy - radius - 14
        pygame.draw.rect(surface, COLOR_HP_BG, (bar_x, bar_y, bar_w, bar_h))
        fill_w = int(bar_w * enemy.hp / enemy.max_hp)
        if fill_w > 0:
            pygame.draw.rect(surface, COLOR_HP_FG, (bar_x, bar_y, fill_w, bar_h))

        order_surf = self._font.render(str(order), True, COLOR_ORDER)
        surface.blit(order_surf, (cx - order_surf.get_width() // 2, bar_y - 16))
