from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from src.domain.value_objects.card_tag import CardTag
from src.domain.value_objects.attack_pattern import AttackPattern

if TYPE_CHECKING:
    from src.domain.value_objects.position import Position


@dataclass
class CardContext:
    player: object          # Player — typed loosely; Phase 4 adds Enemy imports
    targets: list           # list[Position]
    enemies: list           # list[Enemy] in Phase 4, empty for now


@dataclass
class Card:
    id: str
    name: str
    tags: list[CardTag]
    ap_cost: int
    pattern: AttackPattern
    damage: int
    grants_ap: int = 0
    draw_after_play: int = 0
    status_effect: str | None = None
    description: str = ""

    def is_move_card(self) -> bool:
        return CardTag(value="Move") in self.tags

    def can_fuse_with(self, other: Card) -> bool:
        return bool(set(self.tags) & set(other.tags))

    def apply(self, context: CardContext) -> list:
        """Returns DamageTaken events for enemies on targeted tiles. Empty in Phase 2 (no enemies)."""
        events: list = []
        if self.damage > 0:
            for enemy in context.enemies:
                if enemy.position in context.targets:
                    events.append(enemy.take_damage(self.damage))
        return events
