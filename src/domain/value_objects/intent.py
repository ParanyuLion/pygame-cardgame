from __future__ import annotations
from dataclasses import dataclass
from typing import Literal
from src.domain.value_objects.attack_pattern import AttackPattern


@dataclass(frozen=True)
class Intent:
    type: Literal["ATTACK", "MOVE", "BUFF"]
    pattern: AttackPattern
    countdown: int
    damage: int
