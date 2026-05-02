from __future__ import annotations
import pygame
from src.domain.entities.grid import Grid
from src.domain.entities.tile import Obstacle
from src.domain.value_objects.position import Position

TILE_SIZE = 96
TILE_GAP = 4
GRID_OFFSET_X = 80
GRID_OFFSET_Y = 60

COLOR_TILE_BASE = (34, 26, 16)
COLOR_TILE_BORDER = (74, 56, 32)
COLOR_TILE_SHADOW = (20, 15, 8)
COLOR_WALL = (50, 42, 34)
COLOR_PIT = (8, 6, 4)
COLOR_BOULDER = (60, 50, 35)

class GridRenderer:
    def render(self, surface: pygame.Surface, grid: Grid) -> None:
        for pos, tile in grid.tiles.items():
            x, y = self.tile_to_screen(pos)
            rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)

            pygame.draw.rect(surface, COLOR_TILE_BASE, rect, border_radius=4)

            shadow_rect = pygame.Rect(x + 2, y + 2, TILE_SIZE - 4, TILE_SIZE - 4)
            pygame.draw.rect(surface, COLOR_TILE_SHADOW, shadow_rect, width=2, border_radius=3)

            pygame.draw.rect(surface, COLOR_TILE_BORDER, rect, width=2, border_radius=4)

            if tile.obstacle:
                self._render_obstacle(surface, tile.obstacle, rect)

    def _render_obstacle(
        self, surface: pygame.Surface, obstacle: Obstacle, rect: pygame.Rect
    ) -> None:
        color_map = {
            "wall": COLOR_WALL,
            "pit": COLOR_PIT,
            "boulder": COLOR_BOULDER,
        }
        color = color_map.get(obstacle.type, COLOR_WALL)
        inner = rect.inflate(-10, -10)
        pygame.draw.rect(surface, color, inner, border_radius=3)

    def tile_to_screen(self, pos: Position) -> tuple[int, int]:
        x = GRID_OFFSET_X + pos.col * (TILE_SIZE + TILE_GAP)
        y = GRID_OFFSET_Y + pos.row * (TILE_SIZE + TILE_GAP)
        return x, y

    def tile_center(self, pos: Position) -> tuple[int, int]:
        x, y = self.tile_to_screen(pos)
        return x + TILE_SIZE // 2, y + TILE_SIZE // 2
