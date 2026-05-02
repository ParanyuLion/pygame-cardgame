from __future__ import annotations
from dataclasses import dataclass
from src.domain.value_objects.position import Position
from src.domain.events.battle_events import EntityMoved, DamageTaken

class InsufficientAPError(Exception):
    def __init__(self, available: int, required: int) -> None:
        self.available = available
        self.required = required
        super().__init__(f"Requires {required} AP, only {available} available")

@dataclass
class Player:
    id: str
    position: Position
    hp: int
    max_hp: int
    ap: int
    max_ap: int

    def take_damage(self, amount: int) -> DamageTaken:
        self.hp = max(0, self.hp - amount)
        return DamageTaken(entity_id=self.id, amount=amount, source="enemy")

    def move_to(self, new_pos: Position) -> EntityMoved:
        old_pos = self.position
        self.position = new_pos
        return EntityMoved(entity_id=self.id, from_pos=old_pos, to_pos=new_pos)

    def spend_ap(self, amount: int) -> None:
        if self.ap < amount:
            raise InsufficientAPError(available=self.ap, required=amount)
        self.ap -= amount

    def refresh_ap(self) -> int:
        self.ap = self.max_ap
        return self.max_ap

    def is_alive(self) -> bool:
        return self.hp > 0
