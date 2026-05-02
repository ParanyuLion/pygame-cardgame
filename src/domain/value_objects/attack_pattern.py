from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class AttackPattern:
    offsets: tuple[tuple[int, int], ...]

    @classmethod
    def single(cls) -> AttackPattern:
        return cls(offsets=((0, 0),))

    @classmethod
    def line_horizontal(cls) -> AttackPattern:
        return cls(offsets=((0, 0), (1, 0), (2, 0)))

    @classmethod
    def cross(cls) -> AttackPattern:
        return cls(offsets=((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)))

    @classmethod
    def square(cls) -> AttackPattern:
        offsets = tuple(
            (dc, dr) for dc in (-1, 0, 1) for dr in (-1, 0, 1)
        )
        return cls(offsets=offsets)

    @classmethod
    def from_name(cls, name: str) -> AttackPattern:
        table = {
            "single": cls.single,
            "line": cls.line_horizontal,
            "cross": cls.cross,
            "square": cls.square,
        }
        if name not in table:
            raise ValueError(f"Unknown pattern name: '{name}'")
        return table[name]()
