from __future__ import annotations
from src.domain.battle_state import BattleState


class InMemoryBattleRepository:
    def __init__(self) -> None:
        self._state: BattleState | None = None

    def get(self) -> BattleState:
        if self._state is None:
            raise RuntimeError("No battle in progress — call save() first")
        return self._state

    def save(self, state: BattleState) -> None:
        self._state = state
