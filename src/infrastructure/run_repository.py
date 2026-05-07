from __future__ import annotations
from src.domain.run_state import RunState


class InMemoryRunRepository:
    def __init__(self) -> None:
        self._state: RunState | None = None

    def get(self) -> RunState:
        if self._state is None:
            raise RuntimeError("No active run — call save() first")
        return self._state

    def save(self, state: RunState) -> None:
        self._state = state

    def has_active_run(self) -> bool:
        return self._state is not None
