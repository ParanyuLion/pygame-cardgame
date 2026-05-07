from __future__ import annotations
import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.domain.run_state import MapNode

_NODE_R = 25        # circle radius
_NODE_Y = 350       # vertical center
_NODE_SPACING = 120 # horizontal distance between node centers
_FIRST_X = 80       # x center of node 0

_COLOR_COMPLETE = (70, 70, 70)
_COLOR_CURRENT = (220, 180, 80)
_COLOR_FUTURE = (50, 40, 30)
_COLOR_BOSS_CURRENT = (200, 70, 60)
_COLOR_BORDER = (120, 100, 80)
_COLOR_LINE = (80, 70, 60)
_COLOR_LABEL = (200, 180, 140)
_COLOR_FLOOR = (160, 140, 100)


class MapRenderer:
    def __init__(self) -> None:
        self._font = pygame.font.SysFont("serif", 13)
        self._font_floor = pygame.font.SysFont("serif", 22)

    def node_rect(self, idx: int) -> pygame.Rect:
        cx = _FIRST_X + idx * _NODE_SPACING
        return pygame.Rect(cx - _NODE_R, _NODE_Y - _NODE_R, _NODE_R * 2, _NODE_R * 2)

    def node_center(self, idx: int) -> tuple[int, int]:
        return (_FIRST_X + idx * _NODE_SPACING, _NODE_Y)

    def render(self, surface: pygame.Surface, nodes: list[MapNode], node_idx: int, floor: int) -> None:
        floor_surf = self._font_floor.render(f"Floor {floor}", True, _COLOR_FLOOR)
        surface.blit(floor_surf, (20, 30))

        for i in range(len(nodes) - 1):
            cx1, cy1 = self.node_center(i)
            cx2, cy2 = self.node_center(i + 1)
            pygame.draw.line(surface, _COLOR_LINE, (cx1, cy1), (cx2, cy2), 2)

        for i, node in enumerate(nodes):
            cx, cy = self.node_center(i)
            if node.is_complete:
                color = _COLOR_COMPLETE
            elif i == node_idx:
                color = _COLOR_BOSS_CURRENT if node.node_type == "boss" else _COLOR_CURRENT
            else:
                color = _COLOR_FUTURE
            pygame.draw.circle(surface, color, (cx, cy), _NODE_R)
            pygame.draw.circle(surface, _COLOR_BORDER, (cx, cy), _NODE_R, 2)
            label = "Boss" if node.node_type == "boss" else f"C{i + 1}"
            lbl = self._font.render(label, True, _COLOR_LABEL)
            surface.blit(lbl, (cx - lbl.get_width() // 2, cy - lbl.get_height() // 2))
