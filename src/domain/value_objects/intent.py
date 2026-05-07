from __future__ import annotations
from dataclasses import dataclass
from src.domain.value_objects.attack_pattern import AttackPattern


@dataclass(frozen=True)
class Intent:
    type: str          # "ATTACK", "MOVE", "BUFF"
    pattern: AttackPattern
    countdown: int
    damage: int
