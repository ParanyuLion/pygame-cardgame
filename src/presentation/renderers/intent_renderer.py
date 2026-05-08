from __future__ import annotations
import pygame
from src.domain.entities.enemy import Enemy
from src.domain.entities.grid import Grid
from src.domain.value_objects.position import Position
from src.presentation.renderers.grid_renderer import GridRenderer, TILE_SIZE

COLOR_TARGET_TINT = (200, 40, 40, 80)
COLOR_COUNTDOWN_ATTACK = (240, 100, 100)
COLOR_COUNTDOWN_MOVE = (80, 180, 255)
COLOR_MOVE_ARROW = (80, 180, 255)


class IntentRenderer:
    def __init__(self, grid_renderer: GridRenderer) -> None:
        self._grid = grid_renderer
        self._font: pygame.font.Font | None = None

    def render(
        self, surface: pygame.Surface, enemies: list[Enemy], grid: Grid
    ) -> None:
        if self._font is None:
            self._font = pygame.font.SysFont("Arial", 24, bold=True)
        for enemy in enemies:
            if not enemy.is_alive():
                continue
            if enemy.intent.type == "ATTACK":
                self._render_attack_intent(surface, enemy, grid)
            elif enemy.intent.type == "MOVE":
                self._render_move_intent(surface, enemy)

    def _render_attack_intent(self, surface: pygame.Surface, enemy: Enemy, grid: Grid) -> None:
        targets = grid.get_targets(enemy.position, enemy.intent.pattern)
        for pos in targets:
            self._tint_tile(surface, pos)
        cx, cy = self._grid.tile_center(enemy.position)
        cd_surf = self._font.render(str(enemy.intent.countdown), True, COLOR_COUNTDOWN_ATTACK)
        surface.blit(cd_surf, (cx - cd_surf.get_width() // 2, cy - cd_surf.get_height() // 2))

    def _render_move_intent(self, surface: pygame.Surface, enemy: Enemy) -> None:
        cx, cy = self._grid.tile_center(enemy.position)
        # Draw small boot/footstep arrows (two small triangles pointing down-right)
        r = 6
        for ox, oy in [(-6, -4), (4, 2)]:
            pts = [
                (cx + ox, cy + oy - r),
                (cx + ox + r, cy + oy + r),
                (cx + ox - r, cy + oy + r),
            ]
            pygame.draw.polygon(surface, COLOR_MOVE_ARROW, pts)
        cd_surf = self._font.render(str(enemy.intent.countdown), True, COLOR_COUNTDOWN_MOVE)
        surface.blit(cd_surf, (cx - cd_surf.get_width() // 2, cy - cd_surf.get_height() // 2))

    def _tint_tile(self, surface: pygame.Surface, pos: Position) -> None:
        x, y = self._grid.tile_to_screen(pos)
        tint = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        tint.fill(COLOR_TARGET_TINT)
        surface.blit(tint, (x, y))
