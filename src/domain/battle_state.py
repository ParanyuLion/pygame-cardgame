from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from src.domain.entities.player import Player
from src.domain.entities.grid import Grid

if TYPE_CHECKING:
    from src.domain.entities.enemy import Enemy
    from src.domain.entities.card import Card

@dataclass
class BattleState:
    player: Player
    grid: Grid
    enemies: list[Enemy] = field(default_factory=list)
    hand: list[Card] = field(default_factory=list)
    deck: list[Card] = field(default_factory=list)
    discard: list[Card] = field(default_factory=list)
    turn_number: int = 1
    fused_card_ids: set[str] = field(default_factory=set)
