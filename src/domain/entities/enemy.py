from __future__ import annotations
from dataclasses import dataclass
from src.domain.entities.player import Player
from src.domain.events.battle_events import DamageTaken
from src.domain.value_objects.attack_pattern import AttackPattern
from src.domain.value_objects.grid_snapshot import GridSnapshot
from src.domain.value_objects.intent import Intent
from src.domain.value_objects.position import Position


@dataclass
class Enemy:
    id: str
    position: Position
    hp: int
    max_hp: int
    base_damage: int
    intent: Intent

    def take_damage(self, amount: int) -> DamageTaken:
        self.hp = max(0, self.hp - amount)
        return DamageTaken(entity_id=self.id, amount=amount, source="player")

    def is_alive(self) -> bool:
        return self.hp > 0

    def choose_intent(self, snapshot: GridSnapshot) -> Intent:
        player_pos = snapshot.positions.get("player")
        adjacent = (
            player_pos is not None
            and abs(self.position.col - player_pos.col) + abs(self.position.row - player_pos.row) <= 1
        )
        if adjacent:
            return Intent(type="ATTACK", pattern=AttackPattern.cross(), countdown=1, damage=self.base_damage)
        return Intent(type="MOVE", pattern=AttackPattern.single(), countdown=1, damage=0)

    def tick_intent(self) -> Intent:
        # Pure: returns new Intent; caller assigns enemy.intent = enemy.tick_intent()
        return Intent(
            type=self.intent.type,
            pattern=self.intent.pattern,
            countdown=self.intent.countdown - 1,
            damage=self.intent.damage,
        )

    def resolve_attack(self, player: Player) -> DamageTaken:
        return player.take_damage(self.intent.damage)
