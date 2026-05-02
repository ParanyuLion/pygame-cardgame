from __future__ import annotations
from dataclasses import dataclass
from typing import Literal

ObstacleType = Literal["wall", "pit", "boulder"]

@dataclass
class Obstacle:
    type: ObstacleType

    def blocks_movement(self) -> bool:
        return True

    def blocks_attack_pattern(self) -> bool:
        return self.type == "wall"

    def is_destructible(self) -> bool:
        return self.type == "boulder"

@dataclass
class Tile:
    col: int
    row: int
    obstacle: Obstacle | None = None
    occupant_id: str | None = None

    def is_passable(self) -> bool:
        return self.obstacle is None and self.occupant_id is None

    def blocks_pattern(self) -> bool:
        return self.obstacle is not None and self.obstacle.blocks_attack_pattern()
