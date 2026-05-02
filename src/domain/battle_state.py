from dataclasses import dataclass, field
from src.domain.entities.player import Player
from src.domain.entities.grid import Grid

@dataclass
class BattleState:
    player: Player
    grid: Grid
    enemies: list = field(default_factory=list)   # list[Enemy] — added in Plan 4
    hand: list = field(default_factory=list)       # list[Card] — added in Plan 2
    deck: list = field(default_factory=list)       # list[Card] — added in Plan 2
    discard: list = field(default_factory=list)    # list[Card] — added in Plan 2
    turn_number: int = 1
    fused_card_ids: set = field(default_factory=set)
