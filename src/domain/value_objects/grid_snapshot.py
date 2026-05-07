from __future__ import annotations
from dataclasses import dataclass
from src.domain.value_objects.position import Position


@dataclass
class GridSnapshot:
    positions: dict[str, Position]  # entity_id -> position
    hp: dict[str, int]              # entity_id -> current hp
