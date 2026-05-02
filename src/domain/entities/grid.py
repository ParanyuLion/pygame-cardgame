from __future__ import annotations
from dataclasses import dataclass, field
from src.domain.value_objects.position import Position, GRID_SIZE
from src.domain.value_objects.attack_pattern import AttackPattern
from src.domain.entities.tile import Tile, Obstacle

@dataclass
class Grid:
    size: int = GRID_SIZE
    tiles: dict[Position, Tile] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.tiles:
            for col in range(self.size):
                for row in range(self.size):
                    pos = Position(col, row)
                    self.tiles[pos] = Tile(col=col, row=row)

    def in_bounds(self, pos: Position) -> bool:
        return 0 <= pos.col < self.size and 0 <= pos.row < self.size

    def is_occupied(self, pos: Position) -> bool:
        return self.tiles[pos].occupant_id is not None

    def is_passable(self, pos: Position) -> bool:
        return self.tiles[pos].is_passable()

    def place(self, entity_id: str, pos: Position) -> None:
        self.tiles[pos].occupant_id = entity_id

    def remove(self, entity_id: str) -> None:
        for tile in self.tiles.values():
            if tile.occupant_id == entity_id:
                tile.occupant_id = None
                return

    def get_entity_position(self, entity_id: str) -> Position | None:
        for pos, tile in self.tiles.items():
            if tile.occupant_id == entity_id:
                return pos
        return None

    def place_obstacle(self, pos: Position, obstacle: Obstacle) -> None:
        self.tiles[pos].obstacle = obstacle

    def get_targets(self, origin: Position, pattern: AttackPattern) -> list[Position]:
        targets: list[Position] = []
        for dcol, drow in pattern.offsets:
            target = origin.offset(dcol, drow)
            if target is not None and not self.tiles[target].blocks_pattern():
                targets.append(target)
        return targets
