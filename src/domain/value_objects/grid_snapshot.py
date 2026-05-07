from __future__ import annotations
from dataclasses import dataclass
from src.domain.value_objects.position import Position


@dataclass
class GridSnapshot:
    """Read-only snapshot of entity positions and HP, passed to enemy AI.

    Intentionally mutable (not frozen) because dict fields cannot be hashed.
    Treat as immutable — do not modify after construction.
    """

    positions: dict[str, Position]  # entity_id -> position
    hp: dict[str, int]              # entity_id -> current hp
