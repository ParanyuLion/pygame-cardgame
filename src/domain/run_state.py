from __future__ import annotations
from dataclasses import dataclass, field
from typing import Literal, TYPE_CHECKING
from src.domain.value_objects.position import Position

if TYPE_CHECKING:
    from src.domain.entities.card import Card

NodeType = Literal["combat", "boss"]


@dataclass(frozen=True)
class EnemySpec:
    id: str
    position: Position
    hp: int
    base_damage: int


@dataclass
class MapNode:
    id: str
    node_type: NodeType
    enemies: list[EnemySpec]
    is_complete: bool = False


@dataclass
class RunState:
    deck: list[Card]
    player_hp: int
    player_max_hp: int
    floor: int          # 1–3
    floors: list[list[MapNode]]
    node_idx: int = 0
    run_complete: bool = False

    @property
    def nodes(self) -> list[MapNode]:
        return self.floors[self.floor - 1]

    def current_node(self) -> MapNode:
        return self.nodes[self.node_idx]

    def is_floor_complete(self) -> bool:
        return self.node_idx >= len(self.nodes)

    def advance_node(self) -> None:
        self.nodes[self.node_idx].is_complete = True
        self.node_idx += 1

    def advance_floor(self) -> None:
        self.floor += 1
        self.node_idx = 0
