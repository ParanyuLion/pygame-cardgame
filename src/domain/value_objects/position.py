from __future__ import annotations
from dataclasses import dataclass

GRID_SIZE = 4

@dataclass(frozen=True)
class Position:
    col: int
    row: int

    def __post_init__(self) -> None:
        if not (0 <= self.col < GRID_SIZE and 0 <= self.row < GRID_SIZE):
            raise ValueError(
                f"Position ({self.col}, {self.row}) is out of bounds "
                f"for grid size {GRID_SIZE}"
            )

    def offset(self, dcol: int, drow: int) -> Position | None:
        try:
            return Position(self.col + dcol, self.row + drow)
        except ValueError:
            return None
