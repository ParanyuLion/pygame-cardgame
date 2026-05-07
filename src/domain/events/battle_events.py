from __future__ import annotations
from dataclasses import dataclass
from typing import Literal
from .base import DomainEvent
from ..value_objects.position import Position

@dataclass(frozen=True)
class EntityMoved(DomainEvent):
    entity_id: str
    from_pos: Position
    to_pos: Position

@dataclass(frozen=True)
class DamageTaken(DomainEvent):
    entity_id: str
    amount: int
    source: str

@dataclass(frozen=True)
class BattleTurnStarted(DomainEvent):
    turn_number: int
    ap_refreshed: int

@dataclass(frozen=True)
class BattleEnded(DomainEvent):
    outcome: Literal["victory", "defeat"]

@dataclass(frozen=True)
class CardPlayed(DomainEvent):
    card_id: str
    player_id: str
    targets: tuple[Position, ...]

@dataclass(frozen=True)
class CardsFused(DomainEvent):
    card_a_id: str
    card_b_id: str
    result_card_id: str

@dataclass(frozen=True)
class CardDrawn(DomainEvent):
    card_id: str

@dataclass(frozen=True)
class IntentBroadcast(DomainEvent):
    enemy_id: str
    intent_type: str
    countdown: int

@dataclass(frozen=True)
class ObstaclePlaced(DomainEvent):
    pos: Position
    obstacle_type: str
