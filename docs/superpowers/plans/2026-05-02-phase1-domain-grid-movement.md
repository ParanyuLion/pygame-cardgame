# Phase 1: Domain Foundation + Grid + Player Movement

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the complete domain foundation and a running Pygame window showing a 4×4 Dark Dungeon grid with a player that moves smoothly between tiles using arrow keys.

**Architecture:** Pure domain layer (zero Pygame dependency) with layered use-case controllers communicating through an event bus. Presentation layer subscribes to domain events and lerps entity positions for smooth movement.

**Tech Stack:** Python 3.11+, Pygame 2.6, pytest 8.x, dataclasses, typing.Protocol

---

## File Map

```
requirements.txt
pytest.ini
src/
  __init__.py
  domain/
    __init__.py
    interfaces.py                        # IEventBus, IBattleRepository protocols
    battle_state.py                      # BattleState dataclass (domain)
    value_objects/
      __init__.py
      position.py                        # Position(col, row) — validated, immutable
      attack_pattern.py                  # AttackPattern — named offset lists
    events/
      __init__.py
      base.py                            # DomainEvent base
      battle_events.py                   # All domain events
    entities/
      __init__.py
      tile.py                            # Tile, Obstacle
      grid.py                            # Grid
      player.py                          # Player, InsufficientAPError
  infrastructure/
    __init__.py
    battle_repository.py                 # InMemoryBattleRepository
    event_bus.py                         # PygameEventBus (direct dispatch)
  use_cases/
    __init__.py
    move_entity.py                       # MoveEntityUseCase
    start_battle.py                      # StartBattleUseCase, Encounter
  presentation/
    __init__.py
    game_state_manager.py                # Scene protocol + GameStateManager
    input_handler.py                     # Keyboard → use case calls
    scenes/
      __init__.py
      battle_scene.py                    # Wires renderers + input handler
    renderers/
      __init__.py
      grid_renderer.py                   # Draws 4×4 dungeon grid
      entity_renderer.py                 # Draws player with lerp animation
tests/
  __init__.py
  domain/
    __init__.py
    value_objects/
      __init__.py
      test_position.py
    entities/
      __init__.py
      test_grid.py
      test_player.py
  infrastructure/
    __init__.py
    test_battle_repository.py
  use_cases/
    __init__.py
    test_move_entity.py
    test_start_battle.py
main.py
```

---

### Task 1: Project Setup

**Files:**
- Create: `requirements.txt`
- Create: `pytest.ini`
- Create: all `__init__.py` files listed in the file map above

- [ ] **Step 1: Create requirements.txt**

```
pygame==2.6.1
pytest==8.3.4
```

- [ ] **Step 2: Create pytest.ini**

```ini
[pytest]
testpaths = tests
pythonpath = .
```

- [ ] **Step 3: Create all __init__.py files**

Run in the project root (`e:/Coding/pygame`):

```powershell
$dirs = @(
  "src", "src/domain", "src/domain/value_objects", "src/domain/events",
  "src/domain/entities", "src/infrastructure", "src/use_cases",
  "src/presentation", "src/presentation/scenes", "src/presentation/renderers",
  "tests", "tests/domain", "tests/domain/value_objects", "tests/domain/entities",
  "tests/infrastructure", "tests/use_cases"
)
foreach ($d in $dirs) {
  New-Item -ItemType Directory -Force -Path $d | Out-Null
  New-Item -ItemType File -Force -Path "$d/__init__.py" | Out-Null
}
```

- [ ] **Step 4: Install dependencies**

```powershell
pip install -r requirements.txt
```

Expected: pygame and pytest install without errors.

- [ ] **Step 5: Verify pytest discovers zero tests**

```powershell
pytest --collect-only
```

Expected: `no tests ran` (or `0 items`)

- [ ] **Step 6: Commit**

```powershell
git add .
git commit -m "chore: project scaffold with requirements and test structure"
```

---

### Task 2: Position Value Object

**Files:**
- Create: `src/domain/value_objects/position.py`
- Create: `tests/domain/value_objects/test_position.py`

- [ ] **Step 1: Write the failing tests**

`tests/domain/value_objects/test_position.py`:
```python
import pytest
from src.domain.value_objects.position import Position

def test_valid_position_stores_col_row():
    pos = Position(2, 3)
    assert pos.col == 2
    assert pos.row == 3

def test_position_col_negative_raises():
    with pytest.raises(ValueError):
        Position(-1, 0)

def test_position_row_negative_raises():
    with pytest.raises(ValueError):
        Position(0, -1)

def test_position_col_at_grid_size_raises():
    with pytest.raises(ValueError):
        Position(4, 0)

def test_position_row_at_grid_size_raises():
    with pytest.raises(ValueError):
        Position(0, 4)

def test_position_corner_valid():
    pos = Position(3, 3)
    assert pos.col == 3 and pos.row == 3

def test_offset_returns_new_position():
    pos = Position(1, 1)
    result = pos.offset(1, 0)
    assert result == Position(2, 1)

def test_offset_out_of_bounds_returns_none():
    pos = Position(0, 0)
    assert pos.offset(-1, 0) is None
    assert pos.offset(0, -1) is None

def test_offset_to_boundary_valid():
    pos = Position(2, 2)
    assert pos.offset(1, 1) == Position(3, 3)

def test_positions_are_equal_by_value():
    assert Position(1, 2) == Position(1, 2)
    assert Position(1, 2) != Position(2, 1)

def test_position_is_hashable():
    s = {Position(0, 0), Position(1, 1), Position(0, 0)}
    assert len(s) == 2
```

- [ ] **Step 2: Run tests to verify they fail**

```powershell
pytest tests/domain/value_objects/test_position.py -v
```

Expected: `ImportError` — `position` module not found.

- [ ] **Step 3: Implement Position**

`src/domain/value_objects/position.py`:
```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

```powershell
pytest tests/domain/value_objects/test_position.py -v
```

Expected: all 11 tests PASS.

- [ ] **Step 5: Commit**

```powershell
git add src/domain/value_objects/position.py tests/domain/value_objects/test_position.py
git commit -m "feat: add Position value object with bounds validation"
```

---

### Task 3: AttackPattern Value Object

**Files:**
- Create: `src/domain/value_objects/attack_pattern.py`

No separate test file — AttackPattern is pure data with no logic to test independently. It will be tested through `Grid.get_targets` in Task 6.

- [ ] **Step 1: Implement AttackPattern**

`src/domain/value_objects/attack_pattern.py`:
```python
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
```

- [ ] **Step 2: Commit**

```powershell
git add src/domain/value_objects/attack_pattern.py
git commit -m "feat: add AttackPattern value object with named constructors"
```

---

### Task 4: Domain Events

**Files:**
- Create: `src/domain/events/base.py`
- Create: `src/domain/events/battle_events.py`

No tests — events are frozen dataclasses with no logic.

- [ ] **Step 1: Create base event**

`src/domain/events/base.py`:
```python
from dataclasses import dataclass

@dataclass(frozen=True)
class DomainEvent:
    pass
```

- [ ] **Step 2: Create all battle events**

`src/domain/events/battle_events.py`:
```python
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
class EnemyOrderAssigned(DomainEvent):
    enemy_id: str
    order: int

@dataclass(frozen=True)
class ObstaclePlaced(DomainEvent):
    pos: Position
    obstacle_type: str
```

- [ ] **Step 3: Commit**

```powershell
git add src/domain/events/
git commit -m "feat: add domain events as frozen dataclasses"
```

---

### Task 5: Tile & Obstacle Entities

**Files:**
- Create: `src/domain/entities/tile.py`

- [ ] **Step 1: Implement Tile and Obstacle**

`src/domain/entities/tile.py`:
```python
from __future__ import annotations
from dataclasses import dataclass
from typing import Literal

ObstacleType = Literal["wall", "pit", "boulder"]

@dataclass
class Obstacle:
    type: ObstacleType

    def blocks_movement(self) -> bool:
        return True

    def blocks_attack_pattern(self) -> bool:
        return self.type == "wall"

    def is_destructible(self) -> bool:
        return self.type == "boulder"

@dataclass
class Tile:
    col: int
    row: int
    obstacle: Obstacle | None = None
    occupant_id: str | None = None

    def is_passable(self) -> bool:
        return self.obstacle is None and self.occupant_id is None

    def blocks_pattern(self) -> bool:
        return self.obstacle is not None and self.obstacle.blocks_attack_pattern()
```

- [ ] **Step 2: Commit**

```powershell
git add src/domain/entities/tile.py
git commit -m "feat: add Tile and Obstacle entities"
```

---

### Task 6: Grid Entity

**Files:**
- Create: `src/domain/entities/grid.py`
- Create: `tests/domain/entities/test_grid.py`

- [ ] **Step 1: Write the failing tests**

`tests/domain/entities/test_grid.py`:
```python
import pytest
from src.domain.entities.grid import Grid
from src.domain.entities.tile import Obstacle
from src.domain.value_objects.position import Position
from src.domain.value_objects.attack_pattern import AttackPattern

def test_grid_has_16_tiles():
    grid = Grid()
    assert len(grid.tiles) == 16

def test_all_tiles_passable_on_init():
    grid = Grid()
    for pos in grid.tiles:
        assert grid.is_passable(pos)

def test_place_makes_tile_occupied():
    grid = Grid()
    pos = Position(0, 0)
    grid.place("player", pos)
    assert grid.is_occupied(pos)
    assert not grid.is_passable(pos)

def test_remove_clears_occupant():
    grid = Grid()
    pos = Position(2, 2)
    grid.place("player", pos)
    grid.remove("player")
    assert not grid.is_occupied(pos)
    assert grid.is_passable(pos)

def test_get_entity_position_returns_current_pos():
    grid = Grid()
    pos = Position(1, 3)
    grid.place("player", pos)
    assert grid.get_entity_position("player") == pos

def test_get_entity_position_returns_none_when_absent():
    grid = Grid()
    assert grid.get_entity_position("ghost") is None

def test_wall_obstacle_blocks_movement():
    grid = Grid()
    pos = Position(1, 0)
    grid.place_obstacle(pos, Obstacle(type="wall"))
    assert not grid.is_passable(pos)

def test_pit_obstacle_blocks_movement():
    grid = Grid()
    pos = Position(2, 1)
    grid.place_obstacle(pos, Obstacle(type="pit"))
    assert not grid.is_passable(pos)

def test_get_targets_single_hits_origin():
    grid = Grid()
    origin = Position(1, 1)
    targets = grid.get_targets(origin, AttackPattern.single())
    assert Position(1, 1) in targets

def test_get_targets_cross_from_corner_excludes_oob():
    grid = Grid()
    origin = Position(0, 0)
    targets = grid.get_targets(origin, AttackPattern.cross())
    assert all(grid.in_bounds(t) for t in targets)
    assert Position(0, 0) in targets
    assert Position(1, 0) in targets
    assert Position(0, 1) in targets

def test_get_targets_wall_excluded_from_pattern():
    grid = Grid()
    grid.place_obstacle(Position(2, 1), Obstacle(type="wall"))
    origin = Position(1, 1)
    targets = grid.get_targets(origin, AttackPattern.cross())
    assert Position(2, 1) not in targets

def test_get_targets_pit_not_excluded_from_pattern():
    grid = Grid()
    grid.place_obstacle(Position(2, 1), Obstacle(type="pit"))
    origin = Position(1, 1)
    targets = grid.get_targets(origin, AttackPattern.cross())
    assert Position(2, 1) in targets
```

- [ ] **Step 2: Run tests to verify they fail**

```powershell
pytest tests/domain/entities/test_grid.py -v
```

Expected: `ImportError` — grid module not found.

- [ ] **Step 3: Implement Grid**

`src/domain/entities/grid.py`:
```python
from __future__ import annotations
from dataclasses import dataclass, field
from src.domain.value_objects.position import Position, GRID_SIZE
from src.domain.value_objects.attack_pattern import AttackPattern
from src.domain.entities.tile import Tile, Obstacle

@dataclass
class Grid:
    size: int = GRID_SIZE
    tiles: dict[Position, Tile] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.tiles:
            for col in range(self.size):
                for row in range(self.size):
                    pos = Position(col, row)
                    self.tiles[pos] = Tile(col=col, row=row)

    def in_bounds(self, pos: Position) -> bool:
        return 0 <= pos.col < self.size and 0 <= pos.row < self.size

    def is_occupied(self, pos: Position) -> bool:
        return self.tiles[pos].occupant_id is not None

    def is_passable(self, pos: Position) -> bool:
        return self.tiles[pos].is_passable()

    def place(self, entity_id: str, pos: Position) -> None:
        self.tiles[pos].occupant_id = entity_id

    def remove(self, entity_id: str) -> None:
        for tile in self.tiles.values():
            if tile.occupant_id == entity_id:
                tile.occupant_id = None
                return

    def get_entity_position(self, entity_id: str) -> Position | None:
        for pos, tile in self.tiles.items():
            if tile.occupant_id == entity_id:
                return pos
        return None

    def place_obstacle(self, pos: Position, obstacle: Obstacle) -> None:
        self.tiles[pos].obstacle = obstacle

    def get_targets(self, origin: Position, pattern: AttackPattern) -> list[Position]:
        targets: list[Position] = []
        for dcol, drow in pattern.offsets:
            target = origin.offset(dcol, drow)
            if target is not None and not self.tiles[target].blocks_pattern():
                targets.append(target)
        return targets
```

- [ ] **Step 4: Run tests to verify they pass**

```powershell
pytest tests/domain/entities/test_grid.py -v
```

Expected: all 12 tests PASS.

- [ ] **Step 5: Commit**

```powershell
git add src/domain/entities/grid.py tests/domain/entities/test_grid.py
git commit -m "feat: add Grid entity with obstacle support and pattern targeting"
```

---

### Task 7: Player Entity

**Files:**
- Create: `src/domain/entities/player.py`
- Create: `tests/domain/entities/test_player.py`

- [ ] **Step 1: Write the failing tests**

`tests/domain/entities/test_player.py`:
```python
import pytest
from src.domain.entities.player import Player, InsufficientAPError
from src.domain.value_objects.position import Position
from src.domain.events.battle_events import EntityMoved, DamageTaken

def make_player(pos: Position = Position(0, 0), hp: int = 30, ap: int = 3) -> Player:
    return Player(id="player", position=pos, hp=hp, max_hp=30, ap=ap, max_ap=3)

def test_take_damage_reduces_hp():
    player = make_player(hp=30)
    event = player.take_damage(10)
    assert player.hp == 20
    assert isinstance(event, DamageTaken)
    assert event.amount == 10
    assert event.entity_id == "player"

def test_take_damage_does_not_go_below_zero():
    player = make_player(hp=10)
    player.take_damage(100)
    assert player.hp == 0

def test_move_to_updates_position_and_returns_event():
    player = make_player(pos=Position(0, 0))
    event = player.move_to(Position(1, 0))
    assert player.position == Position(1, 0)
    assert isinstance(event, EntityMoved)
    assert event.from_pos == Position(0, 0)
    assert event.to_pos == Position(1, 0)
    assert event.entity_id == "player"

def test_spend_ap_deducts_amount():
    player = make_player(ap=3)
    player.spend_ap(2)
    assert player.ap == 1

def test_spend_ap_raises_when_insufficient():
    player = make_player(ap=1)
    with pytest.raises(InsufficientAPError) as exc_info:
        player.spend_ap(2)
    assert exc_info.value.available == 1
    assert exc_info.value.required == 2

def test_spend_ap_exact_amount_succeeds():
    player = make_player(ap=2)
    player.spend_ap(2)
    assert player.ap == 0

def test_refresh_ap_restores_to_max():
    player = make_player(ap=0)
    refreshed = player.refresh_ap()
    assert player.ap == player.max_ap
    assert refreshed == player.max_ap

def test_is_alive_true_when_hp_positive():
    player = make_player(hp=1)
    assert player.is_alive() is True

def test_is_alive_false_when_hp_zero():
    player = make_player(hp=0)
    assert player.is_alive() is False
```

- [ ] **Step 2: Run tests to verify they fail**

```powershell
pytest tests/domain/entities/test_player.py -v
```

Expected: `ImportError` — player module not found.

- [ ] **Step 3: Implement Player**

`src/domain/entities/player.py`:
```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

```powershell
pytest tests/domain/entities/test_player.py -v
```

Expected: all 9 tests PASS.

- [ ] **Step 5: Commit**

```powershell
git add src/domain/entities/player.py tests/domain/entities/test_player.py
git commit -m "feat: add Player entity with AP and movement"
```

---

### Task 8: Domain Interfaces & BattleState

**Files:**
- Create: `src/domain/interfaces.py`
- Create: `src/domain/battle_state.py`

No separate tests — BattleState is a data container; IBattleRepository is a Protocol. Both are tested through use cases.

- [ ] **Step 1: Implement domain interfaces**

`src/domain/interfaces.py`:
```python
from __future__ import annotations
from typing import Protocol, Callable, TYPE_CHECKING
from src.domain.events.base import DomainEvent

if TYPE_CHECKING:
    from src.domain.battle_state import BattleState

class IEventBus(Protocol):
    def publish(self, event: DomainEvent) -> None: ...
    def subscribe(self, event_type: type, handler: Callable) -> None: ...
    def unsubscribe(self, event_type: type, handler: Callable) -> None: ...

class IBattleRepository(Protocol):
    def get(self) -> BattleState: ...
    def save(self, state: BattleState) -> None: ...
```

- [ ] **Step 2: Implement BattleState**

`src/domain/battle_state.py`:
```python
from dataclasses import dataclass, field
from src.domain.entities.player import Player
from src.domain.entities.grid import Grid

@dataclass
class BattleState:
    player: Player
    grid: Grid
    enemies: list = field(default_factory=list)   # list[Enemy] — added in Plan 4
    hand: list = field(default_factory=list)       # list[Card] — added in Plan 2
    deck: list = field(default_factory=list)       # list[Card] — added in Plan 2
    discard: list = field(default_factory=list)    # list[Card] — added in Plan 2
    turn_number: int = 1
    fused_card_ids: set = field(default_factory=set)
```

- [ ] **Step 3: Commit**

```powershell
git add src/domain/interfaces.py src/domain/battle_state.py
git commit -m "feat: add domain interfaces and BattleState container"
```

---

### Task 9: InMemoryBattleRepository

**Files:**
- Create: `src/infrastructure/battle_repository.py`
- Create: `tests/infrastructure/test_battle_repository.py`

- [ ] **Step 1: Write the failing tests**

`tests/infrastructure/test_battle_repository.py`:
```python
import pytest
from src.infrastructure.battle_repository import InMemoryBattleRepository
from src.domain.battle_state import BattleState
from src.domain.entities.player import Player
from src.domain.entities.grid import Grid
from src.domain.value_objects.position import Position

def make_state() -> BattleState:
    grid = Grid()
    player = Player(id="player", position=Position(0, 0), hp=30, max_hp=30, ap=3, max_ap=3)
    grid.place("player", Position(0, 0))
    return BattleState(player=player, grid=grid)

def test_get_raises_before_save():
    repo = InMemoryBattleRepository()
    with pytest.raises(RuntimeError):
        repo.get()

def test_save_and_get_returns_same_state():
    repo = InMemoryBattleRepository()
    state = make_state()
    repo.save(state)
    assert repo.get() is state

def test_save_overwrites_previous_state():
    repo = InMemoryBattleRepository()
    state1 = make_state()
    state2 = make_state()
    repo.save(state1)
    repo.save(state2)
    assert repo.get() is state2
```

- [ ] **Step 2: Run tests to verify they fail**

```powershell
pytest tests/infrastructure/test_battle_repository.py -v
```

Expected: `ImportError`.

- [ ] **Step 3: Implement InMemoryBattleRepository**

`src/infrastructure/battle_repository.py`:
```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

```powershell
pytest tests/infrastructure/test_battle_repository.py -v
```

Expected: all 3 tests PASS.

- [ ] **Step 5: Commit**

```powershell
git add src/infrastructure/battle_repository.py tests/infrastructure/test_battle_repository.py
git commit -m "feat: add InMemoryBattleRepository"
```

---

### Task 10: PygameEventBus

**Files:**
- Create: `src/infrastructure/event_bus.py`

The event bus uses direct dispatch (not `pygame.event.post`) so it's synchronous and testable without a running Pygame display. Presentation-layer rendering is driven by the update loop, not event posts.

- [ ] **Step 1: Implement PygameEventBus**

`src/infrastructure/event_bus.py`:
```python
from __future__ import annotations
from collections import defaultdict
from typing import Callable
from src.domain.events.base import DomainEvent

class PygameEventBus:
    def __init__(self) -> None:
        self._handlers: dict[type, list[Callable]] = defaultdict(list)

    def publish(self, event: DomainEvent) -> None:
        for handler in list(self._handlers[type(event)]):
            handler(event)

    def subscribe(self, event_type: type, handler: Callable) -> None:
        self._handlers[event_type].append(handler)

    def unsubscribe(self, event_type: type, handler: Callable) -> None:
        try:
            self._handlers[event_type].remove(handler)
        except ValueError:
            pass
```

- [ ] **Step 2: Commit**

```powershell
git add src/infrastructure/event_bus.py
git commit -m "feat: add PygameEventBus with direct dispatch"
```

---

### Task 11: MoveEntityUseCase

**Files:**
- Create: `src/use_cases/move_entity.py`
- Create: `tests/use_cases/test_move_entity.py`

- [ ] **Step 1: Write the failing tests**

`tests/use_cases/test_move_entity.py`:
```python
import pytest
from unittest.mock import MagicMock
from src.domain.battle_state import BattleState
from src.domain.entities.grid import Grid
from src.domain.entities.tile import Obstacle
from src.domain.entities.player import Player, InsufficientAPError
from src.domain.value_objects.position import Position
from src.domain.events.battle_events import EntityMoved
from src.use_cases.move_entity import MoveEntityUseCase

def make_state(player_pos: Position = Position(1, 1), player_ap: int = 3) -> BattleState:
    grid = Grid()
    player = Player(
        id="player", position=player_pos,
        hp=30, max_hp=30, ap=player_ap, max_ap=3,
    )
    grid.place("player", player_pos)
    return BattleState(player=player, grid=grid)

def make_use_case(state: BattleState) -> tuple[MoveEntityUseCase, MagicMock, MagicMock]:
    repo = MagicMock()
    repo.get.return_value = state
    bus = MagicMock()
    return MoveEntityUseCase(repo, bus), repo, bus

def test_move_updates_player_position():
    state = make_state(player_pos=Position(1, 1))
    use_case, _, _ = make_use_case(state)
    use_case.execute("player", Position(1, 2))
    assert state.player.position == Position(1, 2)

def test_move_publishes_entity_moved_event():
    state = make_state(player_pos=Position(1, 1))
    use_case, _, bus = make_use_case(state)
    use_case.execute("player", Position(2, 1))
    bus.publish.assert_called_once()
    event = bus.publish.call_args[0][0]
    assert isinstance(event, EntityMoved)
    assert event.from_pos == Position(1, 1)
    assert event.to_pos == Position(2, 1)

def test_move_deducts_ap():
    state = make_state(player_pos=Position(1, 1), player_ap=3)
    use_case, _, _ = make_use_case(state)
    use_case.execute("player", Position(1, 2))
    assert state.player.ap == 2

def test_move_updates_grid_occupancy():
    state = make_state(player_pos=Position(1, 1))
    use_case, _, _ = make_use_case(state)
    use_case.execute("player", Position(2, 1))
    assert not state.grid.is_occupied(Position(1, 1))
    assert state.grid.is_occupied(Position(2, 1))

def test_move_saves_state():
    state = make_state(player_pos=Position(1, 1))
    use_case, repo, _ = make_use_case(state)
    use_case.execute("player", Position(1, 2))
    repo.save.assert_called_once_with(state)

def test_move_to_occupied_tile_raises():
    state = make_state(player_pos=Position(0, 0))
    state.grid.place("enemy", Position(1, 0))
    use_case, _, _ = make_use_case(state)
    with pytest.raises(ValueError, match="not passable"):
        use_case.execute("player", Position(1, 0))

def test_move_to_wall_raises():
    state = make_state(player_pos=Position(0, 0))
    state.grid.place_obstacle(Position(1, 0), Obstacle(type="wall"))
    use_case, _, _ = make_use_case(state)
    with pytest.raises(ValueError, match="not passable"):
        use_case.execute("player", Position(1, 0))

def test_move_with_zero_ap_raises():
    state = make_state(player_pos=Position(1, 1), player_ap=0)
    use_case, _, _ = make_use_case(state)
    with pytest.raises(InsufficientAPError):
        use_case.execute("player", Position(1, 2))

def test_move_unknown_entity_raises():
    state = make_state()
    use_case, _, _ = make_use_case(state)
    with pytest.raises(ValueError, match="Unknown entity"):
        use_case.execute("ghost", Position(1, 1))
```

- [ ] **Step 2: Run tests to verify they fail**

```powershell
pytest tests/use_cases/test_move_entity.py -v
```

Expected: `ImportError`.

- [ ] **Step 3: Implement MoveEntityUseCase**

`src/use_cases/move_entity.py`:
```python
from src.domain.interfaces import IBattleRepository, IEventBus
from src.domain.value_objects.position import Position

MOVE_AP_COST = 1

class MoveEntityUseCase:
    def __init__(self, battle_repo: IBattleRepository, event_bus: IEventBus) -> None:
        self._repo = battle_repo
        self._bus = event_bus

    def execute(self, entity_id: str, target_pos: Position) -> None:
        state = self._repo.get()

        if state.player.id != entity_id:
            raise ValueError(f"Unknown entity: '{entity_id}'")

        if not state.grid.is_passable(target_pos):
            raise ValueError(
                f"Position {target_pos} is not passable"
            )

        state.player.spend_ap(MOVE_AP_COST)

        state.grid.remove(entity_id)
        event = state.player.move_to(target_pos)
        state.grid.place(entity_id, target_pos)

        self._repo.save(state)
        self._bus.publish(event)
```

- [ ] **Step 4: Run tests to verify they pass**

```powershell
pytest tests/use_cases/test_move_entity.py -v
```

Expected: all 9 tests PASS.

- [ ] **Step 5: Commit**

```powershell
git add src/use_cases/move_entity.py tests/use_cases/test_move_entity.py
git commit -m "feat: add MoveEntityUseCase with AP and passability guards"
```

---

### Task 12: StartBattleUseCase

**Files:**
- Create: `src/use_cases/start_battle.py`
- Create: `tests/use_cases/test_start_battle.py`

- [ ] **Step 1: Write the failing tests**

`tests/use_cases/test_start_battle.py`:
```python
import pytest
from unittest.mock import MagicMock
from src.infrastructure.battle_repository import InMemoryBattleRepository
from src.use_cases.start_battle import StartBattleUseCase, Encounter
from src.domain.value_objects.position import Position
from src.domain.events.battle_events import BattleTurnStarted

def make_use_case():
    repo = InMemoryBattleRepository()
    bus = MagicMock()
    return StartBattleUseCase(repo, bus), repo, bus

def test_start_battle_player_placed_at_encounter_start():
    use_case, repo, _ = make_use_case()
    use_case.execute(Encounter(player_start=Position(0, 0)))
    state = repo.get()
    assert state.player.position == Position(0, 0)
    assert state.grid.is_occupied(Position(0, 0))

def test_start_battle_player_has_full_hp():
    use_case, repo, _ = make_use_case()
    use_case.execute(Encounter(player_start=Position(1, 1)))
    state = repo.get()
    assert state.player.hp == state.player.max_hp

def test_start_battle_player_has_full_ap():
    use_case, repo, _ = make_use_case()
    use_case.execute(Encounter(player_start=Position(0, 0)))
    state = repo.get()
    assert state.player.ap == state.player.max_ap

def test_start_battle_publishes_turn_started():
    use_case, _, bus = make_use_case()
    use_case.execute(Encounter(player_start=Position(0, 0)))
    bus.publish.assert_called_once()
    event = bus.publish.call_args[0][0]
    assert isinstance(event, BattleTurnStarted)
    assert event.turn_number == 1

def test_start_battle_grid_is_4x4():
    use_case, repo, _ = make_use_case()
    use_case.execute(Encounter(player_start=Position(0, 0)))
    state = repo.get()
    assert len(state.grid.tiles) == 16
```

- [ ] **Step 2: Run tests to verify they fail**

```powershell
pytest tests/use_cases/test_start_battle.py -v
```

Expected: `ImportError`.

- [ ] **Step 3: Implement StartBattleUseCase**

`src/use_cases/start_battle.py`:
```python
from dataclasses import dataclass
from src.domain.interfaces import IBattleRepository, IEventBus
from src.domain.battle_state import BattleState
from src.domain.entities.player import Player
from src.domain.entities.grid import Grid
from src.domain.value_objects.position import Position
from src.domain.events.battle_events import BattleTurnStarted

PLAYER_MAX_HP = 30
PLAYER_MAX_AP = 3

@dataclass
class Encounter:
    player_start: Position

class StartBattleUseCase:
    def __init__(self, battle_repo: IBattleRepository, event_bus: IEventBus) -> None:
        self._repo = battle_repo
        self._bus = event_bus

    def execute(self, encounter: Encounter) -> None:
        grid = Grid()
        player = Player(
            id="player",
            position=encounter.player_start,
            hp=PLAYER_MAX_HP,
            max_hp=PLAYER_MAX_HP,
            ap=PLAYER_MAX_AP,
            max_ap=PLAYER_MAX_AP,
        )
        grid.place("player", encounter.player_start)

        state = BattleState(player=player, grid=grid)
        self._repo.save(state)
        self._bus.publish(BattleTurnStarted(turn_number=1, ap_refreshed=PLAYER_MAX_AP))
```

- [ ] **Step 4: Run tests to verify they pass**

```powershell
pytest tests/use_cases/test_start_battle.py -v
```

Expected: all 5 tests PASS.

- [ ] **Step 5: Run the full test suite to confirm nothing is broken**

```powershell
pytest -v
```

Expected: all 39 tests PASS.

- [ ] **Step 6: Commit**

```powershell
git add src/use_cases/start_battle.py tests/use_cases/test_start_battle.py
git commit -m "feat: add StartBattleUseCase and Encounter"
```

---

### Task 13: GameStateManager

**Files:**
- Create: `src/presentation/game_state_manager.py`

No unit tests — pure Pygame wiring with no testable logic.

- [ ] **Step 1: Implement Scene protocol and GameStateManager**

`src/presentation/game_state_manager.py`:
```python
from __future__ import annotations
import pygame
from typing import Protocol

class Scene(Protocol):
    def on_enter(self) -> None: ...
    def on_exit(self) -> None: ...
    def handle_event(self, event: pygame.event.Event) -> None: ...
    def update(self, dt: float) -> None: ...
    def render(self, surface: pygame.Surface) -> None: ...

class GameStateManager:
    def __init__(self, initial_scene: Scene) -> None:
        self._scene = initial_scene
        self._scene.on_enter()

    def transition_to(self, scene: Scene) -> None:
        self._scene.on_exit()
        self._scene = scene
        self._scene.on_enter()

    def handle_event(self, event: pygame.event.Event) -> None:
        self._scene.handle_event(event)

    def update(self, dt: float) -> None:
        self._scene.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        self._scene.render(surface)
```

- [ ] **Step 2: Commit**

```powershell
git add src/presentation/game_state_manager.py
git commit -m "feat: add Scene protocol and GameStateManager"
```

---

### Task 14: GridRenderer

**Files:**
- Create: `src/presentation/renderers/grid_renderer.py`

- [ ] **Step 1: Implement GridRenderer**

`src/presentation/renderers/grid_renderer.py`:
```python
from __future__ import annotations
import pygame
from src.domain.entities.grid import Grid
from src.domain.entities.tile import Obstacle
from src.domain.value_objects.position import Position

TILE_SIZE = 96
TILE_GAP = 4
GRID_OFFSET_X = 80
GRID_OFFSET_Y = 60

COLOR_TILE_BASE = (34, 26, 16)
COLOR_TILE_BORDER = (74, 56, 32)
COLOR_TILE_SHADOW = (20, 15, 8)
COLOR_WALL = (50, 42, 34)
COLOR_PIT = (8, 6, 4)
COLOR_BOULDER = (60, 50, 35)

class GridRenderer:
    def render(self, surface: pygame.Surface, grid: Grid) -> None:
        for pos, tile in grid.tiles.items():
            x, y = self.tile_to_screen(pos)
            rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)

            pygame.draw.rect(surface, COLOR_TILE_BASE, rect, border_radius=4)

            shadow_rect = pygame.Rect(x + 2, y + 2, TILE_SIZE - 4, TILE_SIZE - 4)
            pygame.draw.rect(surface, COLOR_TILE_SHADOW, shadow_rect, width=2, border_radius=3)

            pygame.draw.rect(surface, COLOR_TILE_BORDER, rect, width=2, border_radius=4)

            if tile.obstacle:
                self._render_obstacle(surface, tile.obstacle, rect)

    def _render_obstacle(
        self, surface: pygame.Surface, obstacle: Obstacle, rect: pygame.Rect
    ) -> None:
        color_map = {
            "wall": COLOR_WALL,
            "pit": COLOR_PIT,
            "boulder": COLOR_BOULDER,
        }
        color = color_map.get(obstacle.type, COLOR_WALL)
        inner = rect.inflate(-10, -10)
        pygame.draw.rect(surface, color, inner, border_radius=3)

    def tile_to_screen(self, pos: Position) -> tuple[int, int]:
        x = GRID_OFFSET_X + pos.col * (TILE_SIZE + TILE_GAP)
        y = GRID_OFFSET_Y + pos.row * (TILE_SIZE + TILE_GAP)
        return x, y

    def tile_center(self, pos: Position) -> tuple[int, int]:
        x, y = self.tile_to_screen(pos)
        return x + TILE_SIZE // 2, y + TILE_SIZE // 2
```

- [ ] **Step 2: Commit**

```powershell
git add src/presentation/renderers/grid_renderer.py
git commit -m "feat: add GridRenderer with dark dungeon tile style"
```

---

### Task 15: EntityRenderer with Lerp

**Files:**
- Create: `src/presentation/renderers/entity_renderer.py`

- [ ] **Step 1: Implement EntityRenderer with lerp animation**

`src/presentation/renderers/entity_renderer.py`:
```python
from __future__ import annotations
import pygame
from src.domain.entities.player import Player
from src.presentation.renderers.grid_renderer import GridRenderer, TILE_SIZE

LERP_SPEED = 10.0

COLOR_PLAYER = (190, 150, 60)
COLOR_PLAYER_BORDER = (240, 200, 80)
COLOR_PLAYER_GLOW = (220, 190, 80, 50)

class EntityRenderer:
    def __init__(self, grid_renderer: GridRenderer) -> None:
        self._grid = grid_renderer
        self._display_x: float | None = None
        self._display_y: float | None = None

    def update(self, dt: float, player: Player) -> None:
        tx, ty = self._grid.tile_center(player.position)
        if self._display_x is None:
            self._display_x, self._display_y = float(tx), float(ty)
        else:
            self._display_x += (tx - self._display_x) * LERP_SPEED * dt
            self._display_y += (ty - self._display_y) * LERP_SPEED * dt

    def render(self, surface: pygame.Surface, player: Player) -> None:
        if self._display_x is None:
            return
        cx, cy = int(self._display_x), int(self._display_y)
        radius = TILE_SIZE // 3

        glow = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow, COLOR_PLAYER_GLOW, (radius * 2, radius * 2), radius + 10)
        surface.blit(glow, (cx - radius * 2, cy - radius * 2))

        pygame.draw.circle(surface, COLOR_PLAYER, (cx, cy), radius)
        pygame.draw.circle(surface, COLOR_PLAYER_BORDER, (cx, cy), radius, 2)
```

- [ ] **Step 2: Commit**

```powershell
git add src/presentation/renderers/entity_renderer.py
git commit -m "feat: add EntityRenderer with lerp animation and gold glow"
```

---

### Task 16: InputHandler

**Files:**
- Create: `src/presentation/input_handler.py`

- [ ] **Step 1: Implement InputHandler**

`src/presentation/input_handler.py`:
```python
from __future__ import annotations
import pygame
from src.domain.interfaces import IBattleRepository
from src.domain.entities.player import InsufficientAPError
from src.use_cases.move_entity import MoveEntityUseCase

_ARROW_TO_OFFSET: dict[int, tuple[int, int]] = {
    pygame.K_UP:    (0, -1),
    pygame.K_DOWN:  (0,  1),
    pygame.K_LEFT:  (-1, 0),
    pygame.K_RIGHT: (1,  0),
    pygame.K_w:     (0, -1),
    pygame.K_s:     (0,  1),
    pygame.K_a:     (-1, 0),
    pygame.K_d:     (1,  0),
}

class InputHandler:
    def __init__(
        self,
        move_use_case: MoveEntityUseCase,
        battle_repo: IBattleRepository,
    ) -> None:
        self._move = move_use_case
        self._repo = battle_repo

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if event.key not in _ARROW_TO_OFFSET:
            return

        state = self._repo.get()
        dcol, drow = _ARROW_TO_OFFSET[event.key]
        target = state.player.position.offset(dcol, drow)

        if target is None:
            return

        try:
            self._move.execute(state.player.id, target)
        except (InsufficientAPError, ValueError):
            pass
```

- [ ] **Step 2: Commit**

```powershell
git add src/presentation/input_handler.py
git commit -m "feat: add InputHandler mapping arrow keys and WASD to MoveEntityUseCase"
```

---

### Task 17: BattleScene + main.py

**Files:**
- Create: `src/presentation/scenes/battle_scene.py`
- Create: `main.py`

- [ ] **Step 1: Implement BattleScene**

`src/presentation/scenes/battle_scene.py`:
```python
from __future__ import annotations
import pygame
from src.domain.interfaces import IBattleRepository, IEventBus
from src.use_cases.move_entity import MoveEntityUseCase
from src.presentation.renderers.grid_renderer import GridRenderer
from src.presentation.renderers.entity_renderer import EntityRenderer
from src.presentation.input_handler import InputHandler

COLOR_BG = (10, 8, 6)

class BattleScene:
    def __init__(
        self,
        battle_repo: IBattleRepository,
        event_bus: IEventBus,
    ) -> None:
        self._repo = battle_repo
        move_use_case = MoveEntityUseCase(battle_repo, event_bus)
        self._grid_renderer = GridRenderer()
        self._entity_renderer = EntityRenderer(self._grid_renderer)
        self._input_handler = InputHandler(move_use_case, battle_repo)

    def on_enter(self) -> None:
        pass

    def on_exit(self) -> None:
        pass

    def handle_event(self, event: pygame.event.Event) -> None:
        self._input_handler.handle_event(event)

    def update(self, dt: float) -> None:
        state = self._repo.get()
        self._entity_renderer.update(dt, state.player)

    def render(self, surface: pygame.Surface) -> None:
        state = self._repo.get()
        self._grid_renderer.render(surface, state.grid)
        self._entity_renderer.render(surface, state.player)
```

- [ ] **Step 2: Implement main.py**

`main.py`:
```python
import pygame
from src.infrastructure.battle_repository import InMemoryBattleRepository
from src.infrastructure.event_bus import PygameEventBus
from src.use_cases.start_battle import StartBattleUseCase, Encounter
from src.domain.value_objects.position import Position
from src.presentation.game_state_manager import GameStateManager
from src.presentation.scenes.battle_scene import BattleScene

WINDOW_WIDTH = 560
WINDOW_HEIGHT = 520
FPS = 60
WINDOW_TITLE = "Dungeon Card Roguelike"

def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)
    clock = pygame.time.Clock()

    event_bus = PygameEventBus()
    battle_repo = InMemoryBattleRepository()

    StartBattleUseCase(battle_repo, event_bus).execute(
        Encounter(player_start=Position(0, 0))
    )

    battle_scene = BattleScene(battle_repo, event_bus)
    gsm = GameStateManager(initial_scene=battle_scene)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                gsm.handle_event(event)
        gsm.update(dt)
        screen.fill((10, 8, 6))
        gsm.render(screen)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Run the full test suite**

```powershell
pytest -v
```

Expected: all 49 tests PASS, no failures.

- [ ] **Step 4: Launch the game and verify visually**

```powershell
python main.py
```

Verify:
- A 560×520 window opens with a dark background
- A 4×4 grid of stone-coloured tiles with brown borders is visible
- A gold circle (player) sits on tile (0, 0) top-left
- Arrow keys / WASD move the player; movement is blocked at grid edges
- Player slides smoothly to adjacent tiles (lerp animation)
- Player cannot move when AP is 0 (3 moves exhaust AP; restart to reset)

- [ ] **Step 5: Commit**

```powershell
git add src/presentation/scenes/battle_scene.py main.py
git commit -m "feat: wire BattleScene and main loop — Phase 1 complete"
```

---

## Phase 1 Complete

The foundation is in place: pure domain layer, tested use cases, event bus, and a running dungeon grid with smooth player movement.

**Plans 2–5 build on this:**
- **Plan 2:** Card system — CardTag, Card entity, DeckManager, Hand UI, card data from cards.json
- **Plan 3:** Fusion Engine — FusionEngine domain service, FuseCardsUseCase, drag-to-fuse UI
- **Plan 4:** Enemy AI — Enemy entity, EnemyTakeTurnUseCase, IntentRenderer with red tile telegraphing and order-of-action numbers
- **Plan 5:** Roguelike Meta-Loop — GameStateManager scenes (Map, Reward, Shop), node generation, floor progression
