# Phase 2: Card System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a fully functional card system — CardTag, Card entity, DeckManager, CardRepository loading from cards.json, DrawCardsUseCase, PlayCardUseCase, Move-card enforcement in MoveEntityUseCase, opening hand draw in StartBattleUseCase, and a HandRenderer with click-to-select/click-to-play UI.

**Architecture:** Pure domain layer (CardTag, Card, CardContext, DeckManager) has zero Pygame imports. Use cases (DrawCardsUseCase, PlayCardUseCase) depend on IBattleRepository and IEventBus via Protocol interfaces defined in `src/domain/interfaces.py`. CardRepository (infrastructure) loads `data/cards.json` and returns typed Card instances. HandRenderer (presentation) renders cards at the bottom of the screen; InputHandler extended with mouse-click handling.

**Tech Stack:** Python 3.11, Pygame 2, pytest, dataclasses, typing.Protocol, pathlib.Path, json, random.

---

## Existing codebase — key facts for this plan

- `GRID_SIZE = 4` in `src/domain/value_objects/position.py`
- `TILE_SIZE=96`, `TILE_GAP=4`, `GRID_OFFSET_X=80`, `GRID_OFFSET_Y=60` in `src/presentation/renderers/grid_renderer.py`
- `WINDOW_WIDTH=560`, `WINDOW_HEIGHT=520` in `main.py` — **will be increased to 700**
- `BattleState` in `src/domain/battle_state.py` already has `hand: list`, `deck: list`, `discard: list`, `fused_card_ids: set` fields (typed as bare `list` pending this plan)
- `InsufficientAPError` lives in `src/domain/entities/player.py`
- `AttackPattern.from_name(name)` accepts `"single"`, `"line"`, `"cross"`, `"square"`
- `Grid.get_targets(origin, pattern)` returns `list[Position]`
- All existing tests pass: `pytest -q` → 49 passed

---

## File map

| Action | Path | Responsibility |
|--------|------|----------------|
| Create | `src/domain/value_objects/card_tag.py` | `CardTag` frozen dataclass |
| Create | `src/domain/entities/card.py` | `Card` dataclass + `CardContext` dataclass |
| Create | `src/domain/services/__init__.py` | package marker |
| Create | `src/domain/services/deck_manager.py` | `DeckManager.draw()` static method |
| Create | `data/cards.json` | card definitions + starting deck |
| Modify | `src/domain/interfaces.py` | add `ICardRepository` Protocol |
| Create | `src/infrastructure/card_repository.py` | `CardRepository` loads cards.json |
| Create | `src/use_cases/draw_cards.py` | `DrawCardsUseCase` |
| Create | `src/use_cases/play_card.py` | `PlayCardUseCase` |
| Modify | `src/use_cases/move_entity.py` | require Move card in hand, discard after move |
| Modify | `src/use_cases/start_battle.py` | accept `ICardRepository`, build deck, draw 5 cards |
| Create | `src/presentation/renderers/hand_renderer.py` | render hand cards, hit-test clicks |
| Modify | `src/presentation/renderers/grid_renderer.py` | add `screen_to_tile()` |
| Modify | `src/presentation/scenes/battle_scene.py` | wire `HandRenderer` + `PlayCardUseCase` |
| Modify | `src/presentation/input_handler.py` | add mouse click: select card, play card on tile click |
| Modify | `main.py` | wire `CardRepository`, increase `WINDOW_HEIGHT` to 700 |
| Create | `tests/domain/value_objects/test_card_tag.py` | |
| Create | `tests/domain/entities/test_card.py` | |
| Create | `tests/domain/services/__init__.py` | package marker |
| Create | `tests/domain/services/test_deck_manager.py` | |
| Create | `tests/infrastructure/test_card_repository.py` | |
| Create | `tests/use_cases/test_draw_cards.py` | |
| Create | `tests/use_cases/test_play_card.py` | |
| Modify | `tests/use_cases/test_move_entity.py` | update `make_state` to include Move card; add 2 new tests |
| Modify | `tests/use_cases/test_start_battle.py` | update `make_use_case` to pass card_repo mock; add 2 new tests |

---

## Task 1: CardTag value object

**Files:**
- Create: `src/domain/value_objects/card_tag.py`
- Create: `tests/domain/value_objects/test_card_tag.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/domain/value_objects/test_card_tag.py
from src.domain.value_objects.card_tag import CardTag

def test_card_tag_equality():
    assert CardTag("Blade") == CardTag("Blade")

def test_card_tag_different_values_not_equal():
    assert CardTag("Blade") != CardTag("Fire")

def test_card_tag_hashable_in_set():
    s = {CardTag("Blade"), CardTag("Fire"), CardTag("Blade")}
    assert len(s) == 2

def test_card_tag_value_attribute():
    tag = CardTag("Electric")
    assert tag.value == "Electric"
```

- [ ] **Step 2: Run test to verify it fails**

```
pytest tests/domain/value_objects/test_card_tag.py -v
```
Expected: 4 errors — `ModuleNotFoundError: No module named 'src.domain.value_objects.card_tag'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/domain/value_objects/card_tag.py
from dataclasses import dataclass

@dataclass(frozen=True)
class CardTag:
    value: str
```

- [ ] **Step 4: Run test to verify it passes**

```
pytest tests/domain/value_objects/test_card_tag.py -v
```
Expected: 4 passed

- [ ] **Step 5: Commit**

```
git add src/domain/value_objects/card_tag.py tests/domain/value_objects/test_card_tag.py
git commit -m "feat: add CardTag value object"
```

---

## Task 2: Card entity + CardContext

**Files:**
- Create: `src/domain/entities/card.py`
- Create: `tests/domain/entities/test_card.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/domain/entities/test_card.py
from src.domain.entities.card import Card, CardContext
from src.domain.value_objects.card_tag import CardTag
from src.domain.value_objects.attack_pattern import AttackPattern
from src.domain.value_objects.position import Position

def _make_card(id: str, tags: list[CardTag], ap_cost: int = 1, damage: int = 0) -> Card:
    return Card(
        id=id, name=id, tags=tags, ap_cost=ap_cost,
        pattern=AttackPattern.single(), damage=damage,
    )

def test_is_move_card_true():
    card = _make_card("step_1", [CardTag("Move")])
    assert card.is_move_card() is True

def test_is_move_card_false():
    card = _make_card("slash_1", [CardTag("Blade")])
    assert card.is_move_card() is False

def test_can_fuse_with_shared_tag():
    a = _make_card("a", [CardTag("Fire"), CardTag("Blade")])
    b = _make_card("b", [CardTag("Blade")])
    assert a.can_fuse_with(b) is True

def test_can_fuse_with_no_shared_tag():
    a = _make_card("a", [CardTag("Fire")])
    b = _make_card("b", [CardTag("Electric")])
    assert a.can_fuse_with(b) is False

def test_apply_returns_empty_with_no_enemies():
    card = _make_card("slash_1", [CardTag("Blade")], damage=4)
    ctx = CardContext(player=None, targets=[Position(1, 0)], enemies=[])
    assert card.apply(ctx) == []

def test_card_defaults():
    card = _make_card("x", [CardTag("Blade")])
    assert card.grants_ap == 0
    assert card.draw_after_play == 0
    assert card.status_effect is None
    assert card.description == ""
```

- [ ] **Step 2: Run test to verify it fails**

```
pytest tests/domain/entities/test_card.py -v
```
Expected: errors — `ModuleNotFoundError: No module named 'src.domain.entities.card'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/domain/entities/card.py
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
```

- [ ] **Step 4: Run test to verify it passes**

```
pytest tests/domain/entities/test_card.py -v
```
Expected: 6 passed

- [ ] **Step 5: Commit**

```
git add src/domain/entities/card.py tests/domain/entities/test_card.py
git commit -m "feat: add Card entity and CardContext"
```

---

## Task 3: DeckManager domain service

**Files:**
- Create: `src/domain/services/__init__.py`
- Create: `src/domain/services/deck_manager.py`
- Create: `tests/domain/services/__init__.py`
- Create: `tests/domain/services/test_deck_manager.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/domain/services/test_deck_manager.py
from src.domain.services.deck_manager import DeckManager
from src.domain.entities.card import Card
from src.domain.value_objects.card_tag import CardTag
from src.domain.value_objects.attack_pattern import AttackPattern
from src.domain.events.battle_events import CardDrawn

def _card(id: str) -> Card:
    return Card(id=id, name=id, tags=[CardTag("Blade")], ap_cost=1,
                pattern=AttackPattern.single(), damage=0)

def test_draw_moves_top_card_to_hand():
    deck = [_card("a"), _card("b")]
    hand: list[Card] = []
    discard: list[Card] = []
    event = DeckManager.draw(deck, hand, discard)
    assert isinstance(event, CardDrawn)
    assert event.card_id == "a"
    assert hand[0].id == "a"
    assert len(deck) == 1

def test_draw_shuffles_discard_into_deck_when_deck_empty():
    deck: list[Card] = []
    hand: list[Card] = []
    discard = [_card("x"), _card("y")]
    event = DeckManager.draw(deck, hand, discard)
    assert event is not None
    assert len(hand) == 1
    assert len(discard) == 0
    assert len(deck) == 1   # one card remains in deck after drawing one

def test_draw_returns_none_when_both_empty():
    event = DeckManager.draw([], [], [])
    assert event is None

def test_draw_does_not_add_to_hand_when_empty():
    hand: list[Card] = []
    DeckManager.draw([], hand, [])
    assert hand == []

def test_draw_depletes_deck_in_order():
    deck = [_card("first"), _card("second")]
    hand: list[Card] = []
    DeckManager.draw(deck, hand, [])
    DeckManager.draw(deck, hand, [])
    assert hand[0].id == "first"
    assert hand[1].id == "second"
```

- [ ] **Step 2: Run test to verify it fails**

```
pytest tests/domain/services/test_deck_manager.py -v
```
Expected: errors — `ModuleNotFoundError: No module named 'src.domain.services'`

- [ ] **Step 3: Write implementation**

Create the package markers first:

```python
# src/domain/services/__init__.py
# (empty)
```

```python
# tests/domain/services/__init__.py
# (empty)
```

Then the service:

```python
# src/domain/services/deck_manager.py
from __future__ import annotations
import random
from src.domain.entities.card import Card
from src.domain.events.battle_events import CardDrawn

class DeckManager:
    @staticmethod
    def draw(
        deck: list[Card],
        hand: list[Card],
        discard: list[Card],
    ) -> CardDrawn | None:
        if not deck and not discard:
            return None
        if not deck:
            shuffled = list(discard)
            random.shuffle(shuffled)
            deck[:] = shuffled
            discard.clear()
        card = deck.pop(0)
        hand.append(card)
        return CardDrawn(card_id=card.id)
```

- [ ] **Step 4: Run test to verify it passes**

```
pytest tests/domain/services/test_deck_manager.py -v
```
Expected: 5 passed

- [ ] **Step 5: Commit**

```
git add src/domain/services/__init__.py src/domain/services/deck_manager.py tests/domain/services/__init__.py tests/domain/services/test_deck_manager.py
git commit -m "feat: add DeckManager domain service"
```

---

## Task 4: cards.json + ICardRepository + CardRepository

**Files:**
- Create: `data/cards.json`
- Modify: `src/domain/interfaces.py` (add `ICardRepository`)
- Create: `src/infrastructure/card_repository.py`
- Create: `tests/infrastructure/test_card_repository.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/infrastructure/test_card_repository.py
import json
import pytest
from pathlib import Path
from src.infrastructure.card_repository import CardRepository
from src.domain.value_objects.card_tag import CardTag

def _minimal_json(cards: list[dict], starting_deck: list[str]) -> str:
    return json.dumps({"cards": cards, "starting_deck": starting_deck})

def _step_def() -> dict:
    return {"id": "step", "name": "Step", "tags": ["Move"], "ap_cost": 1,
            "pattern": "single", "damage": 0, "grants_ap": 0,
            "draw_after_play": 0, "status_effect": None, "description": "Move."}

def _slash_def() -> dict:
    return {"id": "slash", "name": "Iron Slash", "tags": ["Blade"], "ap_cost": 2,
            "pattern": "line", "damage": 4, "grants_ap": 0,
            "draw_after_play": 0, "status_effect": None, "description": "Line attack."}

def test_get_starting_deck_correct_length(tmp_path: Path):
    f = tmp_path / "cards.json"
    f.write_text(_minimal_json([_step_def()], ["step", "step", "step"]))
    repo = CardRepository(path=f)
    deck = repo.get_starting_deck()
    assert len(deck) == 3

def test_get_starting_deck_unique_instance_ids(tmp_path: Path):
    f = tmp_path / "cards.json"
    f.write_text(_minimal_json([_step_def()], ["step", "step"]))
    repo = CardRepository(path=f)
    deck = repo.get_starting_deck()
    assert deck[0].id == "step_1"
    assert deck[1].id == "step_2"

def test_get_starting_deck_correct_tags(tmp_path: Path):
    f = tmp_path / "cards.json"
    f.write_text(_minimal_json([_slash_def()], ["slash"]))
    repo = CardRepository(path=f)
    deck = repo.get_starting_deck()
    assert CardTag("Blade") in deck[0].tags

def test_get_starting_deck_move_card_recognised(tmp_path: Path):
    f = tmp_path / "cards.json"
    f.write_text(_minimal_json([_step_def()], ["step"]))
    repo = CardRepository(path=f)
    deck = repo.get_starting_deck()
    assert deck[0].is_move_card() is True

def test_get_starting_deck_mixed_cards(tmp_path: Path):
    f = tmp_path / "cards.json"
    f.write_text(_minimal_json([_step_def(), _slash_def()], ["step", "slash", "step"]))
    repo = CardRepository(path=f)
    deck = repo.get_starting_deck()
    assert len(deck) == 3
    assert deck[0].id == "step_1"
    assert deck[1].id == "slash_1"
    assert deck[2].id == "step_2"
```

- [ ] **Step 2: Run test to verify it fails**

```
pytest tests/infrastructure/test_card_repository.py -v
```
Expected: errors — `ModuleNotFoundError: No module named 'src.infrastructure.card_repository'`

- [ ] **Step 3: Create cards.json, update interfaces.py, write CardRepository**

**3a — Create `data/cards.json`** (create the `data/` directory first — it's not a Python package, no `__init__.py` needed):

```json
{
  "cards": [
    {
      "id": "step",
      "name": "Step",
      "tags": ["Move"],
      "ap_cost": 1,
      "pattern": "single",
      "damage": 0,
      "grants_ap": 0,
      "draw_after_play": 0,
      "status_effect": null,
      "description": "Move to an adjacent tile."
    },
    {
      "id": "slash",
      "name": "Iron Slash",
      "tags": ["Blade"],
      "ap_cost": 2,
      "pattern": "line",
      "damage": 4,
      "grants_ap": 0,
      "draw_after_play": 0,
      "status_effect": null,
      "description": "Strike in a line of 3 tiles."
    },
    {
      "id": "strike",
      "name": "Quick Strike",
      "tags": ["Blade"],
      "ap_cost": 1,
      "pattern": "single",
      "damage": 2,
      "grants_ap": 0,
      "draw_after_play": 0,
      "status_effect": null,
      "description": "A fast strike on one tile."
    },
    {
      "id": "spark",
      "name": "Spark",
      "tags": ["Electric"],
      "ap_cost": 1,
      "pattern": "cross",
      "damage": 2,
      "grants_ap": 0,
      "draw_after_play": 0,
      "status_effect": null,
      "description": "Electric burst in a cross pattern."
    },
    {
      "id": "fireball",
      "name": "Fireball",
      "tags": ["Fire"],
      "ap_cost": 2,
      "pattern": "cross",
      "damage": 3,
      "grants_ap": 0,
      "draw_after_play": 0,
      "status_effect": null,
      "description": "Fiery explosion in a cross pattern."
    },
    {
      "id": "charge",
      "name": "Charge",
      "tags": ["Blade"],
      "ap_cost": 0,
      "pattern": "single",
      "damage": 1,
      "grants_ap": 1,
      "draw_after_play": 1,
      "status_effect": null,
      "description": "Quick attack, grants 1 AP, draw 1 card."
    }
  ],
  "starting_deck": [
    "step", "step", "step",
    "slash", "slash",
    "strike", "strike",
    "spark",
    "fireball",
    "charge"
  ]
}
```

**3b — Update `src/domain/interfaces.py`** — add `ICardRepository`:

```python
# src/domain/interfaces.py
from __future__ import annotations
from typing import Protocol, Callable, TYPE_CHECKING
from src.domain.events.base import DomainEvent

if TYPE_CHECKING:
    from src.domain.battle_state import BattleState
    from src.domain.entities.card import Card

class IEventBus(Protocol):
    def publish(self, event: DomainEvent) -> None: ...
    def subscribe(self, event_type: type, handler: Callable) -> None: ...
    def unsubscribe(self, event_type: type, handler: Callable) -> None: ...

class IBattleRepository(Protocol):
    def get(self) -> BattleState: ...
    def save(self, state: BattleState) -> None: ...

class ICardRepository(Protocol):
    def get_starting_deck(self) -> list[Card]: ...
```

**3c — Create `src/infrastructure/card_repository.py`**:

```python
# src/infrastructure/card_repository.py
from __future__ import annotations
import json
from pathlib import Path
from src.domain.entities.card import Card
from src.domain.value_objects.card_tag import CardTag
from src.domain.value_objects.attack_pattern import AttackPattern

_DEFAULT_PATH = Path(__file__).parent.parent.parent / "data" / "cards.json"

class CardRepository:
    def __init__(self, path: Path = _DEFAULT_PATH) -> None:
        raw = json.loads(path.read_text())
        self._definitions: dict[str, dict] = {c["id"]: c for c in raw["cards"]}
        self._starting_deck_ids: list[str] = raw["starting_deck"]

    def get_starting_deck(self) -> list[Card]:
        counts: dict[str, int] = {}
        result: list[Card] = []
        for def_id in self._starting_deck_ids:
            counts[def_id] = counts.get(def_id, 0) + 1
            defn = self._definitions[def_id]
            card = Card(
                id=f"{def_id}_{counts[def_id]}",
                name=defn["name"],
                tags=[CardTag(t) for t in defn["tags"]],
                ap_cost=defn["ap_cost"],
                pattern=AttackPattern.from_name(defn["pattern"]),
                damage=defn["damage"],
                grants_ap=defn.get("grants_ap", 0),
                draw_after_play=defn.get("draw_after_play", 0),
                status_effect=defn.get("status_effect"),
                description=defn.get("description", ""),
            )
            result.append(card)
        return result
```

- [ ] **Step 4: Run all tests to verify**

```
pytest tests/infrastructure/test_card_repository.py tests/domain/ -v
```
Expected: 5 new card_repository tests pass + all existing domain tests still pass

- [ ] **Step 5: Commit**

```
git add data/cards.json src/domain/interfaces.py src/infrastructure/card_repository.py tests/infrastructure/test_card_repository.py
git commit -m "feat: add cards.json, ICardRepository interface, and CardRepository"
```

---

## Task 5: DrawCardsUseCase

**Files:**
- Create: `src/use_cases/draw_cards.py`
- Create: `tests/use_cases/test_draw_cards.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/use_cases/test_draw_cards.py
import pytest
from unittest.mock import MagicMock
from src.domain.battle_state import BattleState
from src.domain.entities.grid import Grid
from src.domain.entities.player import Player
from src.domain.entities.card import Card
from src.domain.value_objects.position import Position
from src.domain.value_objects.card_tag import CardTag
from src.domain.value_objects.attack_pattern import AttackPattern
from src.domain.events.battle_events import CardDrawn
from src.use_cases.draw_cards import DrawCardsUseCase

def _card(id: str) -> Card:
    return Card(id=id, name=id, tags=[CardTag("Blade")], ap_cost=1,
                pattern=AttackPattern.single(), damage=0)

def _make_state(*deck_ids: str) -> BattleState:
    grid = Grid()
    player = Player(id="player", position=Position(0, 0), hp=30, max_hp=30, ap=3, max_ap=3)
    state = BattleState(player=player, grid=grid)
    state.deck = [_card(cid) for cid in deck_ids]
    return state

def _make_use_case(state: BattleState) -> tuple[DrawCardsUseCase, MagicMock, MagicMock]:
    repo = MagicMock()
    repo.get.return_value = state
    bus = MagicMock()
    return DrawCardsUseCase(repo, bus), repo, bus

def test_draw_moves_cards_to_hand():
    state = _make_state("a", "b", "c")
    use_case, _, _ = _make_use_case(state)
    use_case.execute(2)
    assert len(state.hand) == 2
    assert len(state.deck) == 1

def test_draw_publishes_card_drawn_per_card():
    state = _make_state("a", "b")
    use_case, _, bus = _make_use_case(state)
    use_case.execute(2)
    assert bus.publish.call_count == 2
    events = [call[0][0] for call in bus.publish.call_args_list]
    assert all(isinstance(e, CardDrawn) for e in events)
    assert {e.card_id for e in events} == {"a", "b"}

def test_draw_stops_at_deck_and_discard_empty():
    state = _make_state("only")
    use_case, _, bus = _make_use_case(state)
    use_case.execute(5)
    assert len(state.hand) == 1
    assert bus.publish.call_count == 1

def test_draw_shuffles_discard_when_deck_empty():
    state = _make_state()
    state.discard = [_card("x"), _card("y")]
    use_case, _, _ = _make_use_case(state)
    use_case.execute(1)
    assert len(state.hand) == 1
    assert len(state.discard) == 0

def test_draw_saves_state_once():
    state = _make_state("a", "b")
    use_case, repo, _ = _make_use_case(state)
    use_case.execute(2)
    repo.save.assert_called_once_with(state)
```

- [ ] **Step 2: Run test to verify it fails**

```
pytest tests/use_cases/test_draw_cards.py -v
```
Expected: errors — `ModuleNotFoundError: No module named 'src.use_cases.draw_cards'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/use_cases/draw_cards.py
from src.domain.interfaces import IBattleRepository, IEventBus
from src.domain.services.deck_manager import DeckManager

class DrawCardsUseCase:
    def __init__(self, battle_repo: IBattleRepository, event_bus: IEventBus) -> None:
        self._repo = battle_repo
        self._bus = event_bus

    def execute(self, count: int) -> None:
        state = self._repo.get()
        events = []
        for _ in range(count):
            event = DeckManager.draw(state.deck, state.hand, state.discard)
            if event is None:
                break
            events.append(event)
        self._repo.save(state)
        for event in events:
            self._bus.publish(event)
```

- [ ] **Step 4: Run test to verify it passes**

```
pytest tests/use_cases/test_draw_cards.py -v
```
Expected: 5 passed

- [ ] **Step 5: Commit**

```
git add src/use_cases/draw_cards.py tests/use_cases/test_draw_cards.py
git commit -m "feat: add DrawCardsUseCase"
```

---

## Task 6: PlayCardUseCase

**Files:**
- Create: `src/use_cases/play_card.py`
- Create: `tests/use_cases/test_play_card.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/use_cases/test_play_card.py
import pytest
from unittest.mock import MagicMock
from src.domain.battle_state import BattleState
from src.domain.entities.grid import Grid
from src.domain.entities.player import Player, InsufficientAPError
from src.domain.entities.card import Card, CardContext
from src.domain.value_objects.position import Position
from src.domain.value_objects.card_tag import CardTag
from src.domain.value_objects.attack_pattern import AttackPattern
from src.domain.events.battle_events import CardPlayed
from src.use_cases.play_card import PlayCardUseCase

def _card(id: str, ap_cost: int = 1, damage: int = 0, draw_after: int = 0) -> Card:
    return Card(id=id, name=id, tags=[CardTag("Blade")], ap_cost=ap_cost,
                pattern=AttackPattern.single(), damage=damage, draw_after_play=draw_after)

def _extra_deck_card(id: str) -> Card:
    return Card(id=id, name=id, tags=[CardTag("Blade")], ap_cost=1,
                pattern=AttackPattern.single(), damage=0)

def _make_state(hand_cards: list[Card], ap: int = 3) -> BattleState:
    grid = Grid()
    player = Player(id="player", position=Position(1, 1), hp=30, max_hp=30, ap=ap, max_ap=3)
    grid.place("player", Position(1, 1))
    state = BattleState(player=player, grid=grid)
    state.hand = list(hand_cards)
    return state

def _make_use_case(state: BattleState) -> tuple[PlayCardUseCase, MagicMock, MagicMock]:
    repo = MagicMock()
    repo.get.return_value = state
    bus = MagicMock()
    return PlayCardUseCase(repo, bus), repo, bus

def test_play_card_moves_card_to_discard():
    card = _card("slash_1", ap_cost=1)
    state = _make_state([card])
    use_case, _, _ = _make_use_case(state)
    use_case.execute("slash_1")
    assert card not in state.hand
    assert card in state.discard

def test_play_card_deducts_ap():
    card = _card("slash_1", ap_cost=2)
    state = _make_state([card], ap=3)
    use_case, _, _ = _make_use_case(state)
    use_case.execute("slash_1")
    assert state.player.ap == 1

def test_play_card_publishes_card_played_event():
    card = _card("slash_1", ap_cost=1)
    state = _make_state([card])
    use_case, _, bus = _make_use_case(state)
    use_case.execute("slash_1")
    event = bus.publish.call_args_list[0][0][0]
    assert isinstance(event, CardPlayed)
    assert event.card_id == "slash_1"
    assert event.player_id == "player"

def test_play_card_saves_state():
    card = _card("slash_1", ap_cost=1)
    state = _make_state([card])
    use_case, repo, _ = _make_use_case(state)
    use_case.execute("slash_1")
    repo.save.assert_called_once_with(state)

def test_play_card_not_in_hand_raises():
    state = _make_state([])
    use_case, _, _ = _make_use_case(state)
    with pytest.raises(ValueError, match="not in hand"):
        use_case.execute("ghost")

def test_play_card_insufficient_ap_raises():
    card = _card("slash_1", ap_cost=3)
    state = _make_state([card], ap=0)
    use_case, _, _ = _make_use_case(state)
    with pytest.raises(InsufficientAPError):
        use_case.execute("slash_1")

def test_play_card_draw_after_play_draws_from_deck():
    card = _card("charge_1", ap_cost=0, draw_after=1)
    extra = _extra_deck_card("extra_1")
    state = _make_state([card])
    state.deck = [extra]
    use_case, _, _ = _make_use_case(state)
    use_case.execute("charge_1")
    assert extra in state.hand

def test_play_card_zero_ap_cost_allowed():
    card = _card("charge_1", ap_cost=0)
    state = _make_state([card], ap=0)
    use_case, _, _ = _make_use_case(state)
    use_case.execute("charge_1")   # must not raise
    assert card in state.discard
```

- [ ] **Step 2: Run test to verify it fails**

```
pytest tests/use_cases/test_play_card.py -v
```
Expected: errors — `ModuleNotFoundError: No module named 'src.use_cases.play_card'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/use_cases/play_card.py
from src.domain.interfaces import IBattleRepository, IEventBus
from src.domain.entities.card import CardContext
from src.domain.events.battle_events import CardPlayed
from src.domain.services.deck_manager import DeckManager

class PlayCardUseCase:
    def __init__(self, battle_repo: IBattleRepository, event_bus: IEventBus) -> None:
        self._repo = battle_repo
        self._bus = event_bus

    def execute(self, card_id: str) -> None:
        state = self._repo.get()

        card = next((c for c in state.hand if c.id == card_id), None)
        if card is None:
            raise ValueError(f"Card '{card_id}' not in hand")

        state.player.spend_ap(card.ap_cost)

        targets = state.grid.get_targets(state.player.position, card.pattern)
        context = CardContext(player=state.player, targets=targets, enemies=state.enemies)
        side_events = card.apply(context)

        state.hand.remove(card)
        state.discard.append(card)

        for _ in range(card.draw_after_play):
            DeckManager.draw(state.deck, state.hand, state.discard)

        self._repo.save(state)

        self._bus.publish(CardPlayed(
            card_id=card.id,
            player_id=state.player.id,
            targets=tuple(targets),
        ))
        for event in side_events:
            self._bus.publish(event)
```

- [ ] **Step 4: Run test to verify it passes**

```
pytest tests/use_cases/test_play_card.py -v
```
Expected: 8 passed

- [ ] **Step 5: Commit**

```
git add src/use_cases/play_card.py tests/use_cases/test_play_card.py
git commit -m "feat: add PlayCardUseCase"
```

---

## Task 7: MoveEntityUseCase — require Move card in hand

**Files:**
- Modify: `src/use_cases/move_entity.py`
- Modify: `tests/use_cases/test_move_entity.py` (update helper + add 2 tests)

- [ ] **Step 1: Add two new tests and update the helper**

Replace the entire `tests/use_cases/test_move_entity.py` with the version below. The `make_state` helper now accepts `with_move_card=True` so all existing tests get a Move card by default. The two new tests (`test_move_without_move_card_raises` and `test_move_discards_move_card`) are the failing ones.

```python
# tests/use_cases/test_move_entity.py
import pytest
from unittest.mock import MagicMock
from src.domain.battle_state import BattleState
from src.domain.entities.grid import Grid
from src.domain.entities.tile import Obstacle
from src.domain.entities.player import Player, InsufficientAPError
from src.domain.entities.card import Card
from src.domain.value_objects.position import Position
from src.domain.value_objects.card_tag import CardTag
from src.domain.value_objects.attack_pattern import AttackPattern
from src.domain.events.battle_events import EntityMoved
from src.use_cases.move_entity import MoveEntityUseCase

def _move_card() -> Card:
    return Card(id="step_1", name="Step", tags=[CardTag("Move")],
                ap_cost=1, pattern=AttackPattern.single(), damage=0)

def make_state(
    player_pos: Position = Position(1, 1),
    player_ap: int = 3,
    with_move_card: bool = True,
) -> BattleState:
    grid = Grid()
    player = Player(
        id="player", position=player_pos,
        hp=30, max_hp=30, ap=player_ap, max_ap=3,
    )
    grid.place("player", player_pos)
    state = BattleState(player=player, grid=grid)
    if with_move_card:
        state.hand = [_move_card()]
    return state

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

# --- New tests for Move card requirement ---

def test_move_without_move_card_raises():
    state = make_state(with_move_card=False)
    use_case, _, _ = make_use_case(state)
    with pytest.raises(ValueError, match="No Move card"):
        use_case.execute("player", Position(1, 2))

def test_move_discards_move_card():
    state = make_state()
    move_card = state.hand[0]
    use_case, _, _ = make_use_case(state)
    use_case.execute("player", Position(1, 2))
    assert move_card not in state.hand
    assert move_card in state.discard
```

- [ ] **Step 2: Run test to verify the two new tests fail**

```
pytest tests/use_cases/test_move_entity.py::test_move_without_move_card_raises tests/use_cases/test_move_entity.py::test_move_discards_move_card -v
```
Expected: 2 FAILED (existing 9 still pass because `make_state` includes Move card but MoveEntityUseCase doesn't check for it yet)

- [ ] **Step 3: Update MoveEntityUseCase**

```python
# src/use_cases/move_entity.py
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

        move_card = next((c for c in state.hand if c.is_move_card()), None)
        if move_card is None:
            raise ValueError("No Move card in hand")

        if not state.grid.is_passable(target_pos):
            raise ValueError(f"Position {target_pos} is not passable")

        state.player.spend_ap(MOVE_AP_COST)

        state.hand.remove(move_card)
        state.discard.append(move_card)

        state.grid.remove(entity_id)
        event = state.player.move_to(target_pos)
        state.grid.place(entity_id, target_pos)

        self._repo.save(state)
        self._bus.publish(event)
```

- [ ] **Step 4: Run all move tests to verify**

```
pytest tests/use_cases/test_move_entity.py -v
```
Expected: 11 passed

- [ ] **Step 5: Commit**

```
git add src/use_cases/move_entity.py tests/use_cases/test_move_entity.py
git commit -m "feat: MoveEntityUseCase requires Move card in hand, discards it on move"
```

---

## Task 8: StartBattleUseCase — deck population + opening hand

**Files:**
- Modify: `src/use_cases/start_battle.py`
- Modify: `tests/use_cases/test_start_battle.py`

- [ ] **Step 1: Add two new tests and update the helper**

Replace `tests/use_cases/test_start_battle.py` in full:

```python
# tests/use_cases/test_start_battle.py
import pytest
from unittest.mock import MagicMock
from src.infrastructure.battle_repository import InMemoryBattleRepository
from src.use_cases.start_battle import StartBattleUseCase, Encounter
from src.domain.value_objects.position import Position
from src.domain.value_objects.card_tag import CardTag
from src.domain.value_objects.attack_pattern import AttackPattern
from src.domain.entities.card import Card
from src.domain.events.battle_events import BattleTurnStarted, CardDrawn

def _card(id: str, move: bool = False) -> Card:
    tags = [CardTag("Move")] if move else [CardTag("Blade")]
    return Card(id=id, name=id, tags=tags, ap_cost=1,
                pattern=AttackPattern.single(), damage=0)

def _make_card_repo(count: int = 10) -> MagicMock:
    repo = MagicMock()
    cards = [_card(f"card_{i}", move=(i < 3)) for i in range(count)]
    repo.get_starting_deck.return_value = cards
    return repo

def make_use_case():
    repo = InMemoryBattleRepository()
    bus = MagicMock()
    card_repo = _make_card_repo()
    return StartBattleUseCase(repo, bus, card_repo), repo, bus

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
    events = [call[0][0] for call in bus.publish.call_args_list]
    turn_events = [e for e in events if isinstance(e, BattleTurnStarted)]
    assert len(turn_events) == 1
    assert turn_events[0].turn_number == 1

def test_start_battle_grid_is_4x4():
    use_case, repo, _ = make_use_case()
    use_case.execute(Encounter(player_start=Position(0, 0)))
    state = repo.get()
    assert len(state.grid.tiles) == 16

# --- New tests for deck + opening hand ---

def test_start_battle_draws_opening_hand_of_five():
    use_case, repo, _ = make_use_case()
    use_case.execute(Encounter(player_start=Position(0, 0)))
    state = repo.get()
    assert len(state.hand) == 5
    assert len(state.deck) == 5   # 10 cards - 5 drawn

def test_start_battle_publishes_card_drawn_events():
    use_case, _, bus = make_use_case()
    use_case.execute(Encounter(player_start=Position(0, 0)))
    events = [call[0][0] for call in bus.publish.call_args_list]
    draw_events = [e for e in events if isinstance(e, CardDrawn)]
    assert len(draw_events) == 5
```

- [ ] **Step 2: Run test to verify the two new tests fail**

```
pytest tests/use_cases/test_start_battle.py::test_start_battle_draws_opening_hand_of_five tests/use_cases/test_start_battle.py::test_start_battle_publishes_card_drawn_events -v
```
Expected: 2 FAILED (existing 5 tests fail too because `make_use_case` now passes `card_repo` to the constructor which doesn't accept it yet)

- [ ] **Step 3: Update StartBattleUseCase**

```python
# src/use_cases/start_battle.py
import random
from dataclasses import dataclass
from src.domain.interfaces import IBattleRepository, IEventBus, ICardRepository
from src.domain.battle_state import BattleState
from src.domain.entities.player import Player
from src.domain.entities.grid import Grid
from src.domain.value_objects.position import Position
from src.domain.events.battle_events import BattleTurnStarted
from src.domain.services.deck_manager import DeckManager

PLAYER_MAX_HP = 30
PLAYER_MAX_AP = 3
OPENING_HAND_SIZE = 5

@dataclass
class Encounter:
    player_start: Position

class StartBattleUseCase:
    def __init__(
        self,
        battle_repo: IBattleRepository,
        event_bus: IEventBus,
        card_repo: ICardRepository,
    ) -> None:
        self._repo = battle_repo
        self._bus = event_bus
        self._card_repo = card_repo

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

        deck = self._card_repo.get_starting_deck()
        random.shuffle(deck)

        state = BattleState(player=player, grid=grid, deck=deck)

        draw_events = []
        for _ in range(OPENING_HAND_SIZE):
            event = DeckManager.draw(state.deck, state.hand, state.discard)
            if event is None:
                break
            draw_events.append(event)

        self._repo.save(state)
        self._bus.publish(BattleTurnStarted(turn_number=1, ap_refreshed=PLAYER_MAX_AP))
        for event in draw_events:
            self._bus.publish(event)
```

- [ ] **Step 4: Run all start_battle tests**

```
pytest tests/use_cases/test_start_battle.py -v
```
Expected: 7 passed

- [ ] **Step 5: Commit**

```
git add src/use_cases/start_battle.py tests/use_cases/test_start_battle.py
git commit -m "feat: StartBattleUseCase loads deck from CardRepository and draws opening hand"
```

---

## Task 9: HandRenderer + screen_to_tile on GridRenderer

**Files:**
- Modify: `src/presentation/renderers/grid_renderer.py` (add `screen_to_tile`)
- Create: `src/presentation/renderers/hand_renderer.py`

No unit tests for renderers (Pygame display required); verified visually in Task 10.

- [ ] **Step 1: Add `screen_to_tile` to GridRenderer**

Add this method to the existing `GridRenderer` class in `src/presentation/renderers/grid_renderer.py`:

```python
# Add inside GridRenderer class, after tile_center():

def screen_to_tile(self, x: int, y: int) -> Position | None:
    rel_x = x - GRID_OFFSET_X
    rel_y = y - GRID_OFFSET_Y
    if rel_x < 0 or rel_y < 0:
        return None
    col = rel_x // (TILE_SIZE + TILE_GAP)
    row = rel_y // (TILE_SIZE + TILE_GAP)
    # Reject clicks that land in the gap between tiles
    if rel_x % (TILE_SIZE + TILE_GAP) >= TILE_SIZE:
        return None
    if rel_y % (TILE_SIZE + TILE_GAP) >= TILE_SIZE:
        return None
    try:
        return Position(col, row)
    except ValueError:
        return None
```

The full updated `src/presentation/renderers/grid_renderer.py`:

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

    def screen_to_tile(self, x: int, y: int) -> Position | None:
        rel_x = x - GRID_OFFSET_X
        rel_y = y - GRID_OFFSET_Y
        if rel_x < 0 or rel_y < 0:
            return None
        col = rel_x // (TILE_SIZE + TILE_GAP)
        row = rel_y // (TILE_SIZE + TILE_GAP)
        if rel_x % (TILE_SIZE + TILE_GAP) >= TILE_SIZE:
            return None
        if rel_y % (TILE_SIZE + TILE_GAP) >= TILE_SIZE:
            return None
        try:
            return Position(col, row)
        except ValueError:
            return None
```

- [ ] **Step 2: Create HandRenderer**

```python
# src/presentation/renderers/hand_renderer.py
from __future__ import annotations
import pygame
from src.domain.entities.card import Card

CARD_W = 80
CARD_H = 110
CARD_GAP = 10
HAND_Y = 490

COLOR_CARD_BG = (220, 200, 160)
COLOR_CARD_SELECTED = (255, 240, 180)
COLOR_TEXT = (30, 20, 10)
COLOR_COST = (80, 60, 30)

_TAG_BORDER: dict[str, tuple[int, int, int]] = {
    "Move":     (60, 160, 80),
    "Blade":    (80, 120, 180),
    "Fire":     (200, 80, 40),
    "Electric": (200, 180, 40),
    "Area":     (140, 60, 180),
}
_DEFAULT_BORDER = (120, 110, 90)

class HandRenderer:
    def __init__(self, window_width: int = 560) -> None:
        self._window_width = window_width
        self._selected_id: str | None = None
        self._font_name: pygame.font.Font | None = None
        self._font_cost: pygame.font.Font | None = None

    def set_selected(self, card_id: str | None) -> None:
        self._selected_id = card_id

    def card_rect(self, index: int, hand_size: int) -> pygame.Rect:
        total_w = hand_size * CARD_W + max(0, hand_size - 1) * CARD_GAP
        start_x = (self._window_width - total_w) // 2
        x = start_x + index * (CARD_W + CARD_GAP)
        return pygame.Rect(x, HAND_Y, CARD_W, CARD_H)

    def card_at_point(self, point: tuple[int, int], hand: list[Card]) -> Card | None:
        for i, card in enumerate(hand):
            if self.card_rect(i, len(hand)).collidepoint(point):
                return card
        return None

    def render(self, surface: pygame.Surface, hand: list[Card]) -> None:
        if not hand:
            return
        if self._font_name is None:
            self._font_name = pygame.font.SysFont("Arial", 10, bold=True)
            self._font_cost = pygame.font.SysFont("Arial", 16, bold=True)

        for i, card in enumerate(hand):
            rect = self.card_rect(i, len(hand))
            is_selected = card.id == self._selected_id

            bg = COLOR_CARD_SELECTED if is_selected else COLOR_CARD_BG
            pygame.draw.rect(surface, bg, rect, border_radius=4)

            first_tag = card.tags[0].value if card.tags else ""
            border_color = _TAG_BORDER.get(first_tag, _DEFAULT_BORDER)
            border_w = 3 if is_selected else 2
            pygame.draw.rect(surface, border_color, rect, width=border_w, border_radius=4)

            name_surf = self._font_name.render(card.name, True, COLOR_TEXT)
            surface.blit(name_surf, (rect.x + 4, rect.y + 4))

            cost_label = f"{card.ap_cost}AP"
            cost_surf = self._font_cost.render(cost_label, True, border_color)
            surface.blit(cost_surf, (rect.x + 4, rect.bottom - 22))

            desc_surf = self._font_name.render(card.description[:18], True, COLOR_TEXT)
            surface.blit(desc_surf, (rect.x + 4, rect.y + 18))
```

- [ ] **Step 3: Run full test suite to confirm nothing broken**

```
pytest -q
```
Expected: all existing tests pass (no regression)

- [ ] **Step 4: Commit**

```
git add src/presentation/renderers/grid_renderer.py src/presentation/renderers/hand_renderer.py
git commit -m "feat: add HandRenderer and GridRenderer.screen_to_tile()"
```

---

## Task 10: Wire everything — BattleScene, InputHandler, main.py

**Files:**
- Modify: `src/presentation/input_handler.py`
- Modify: `src/presentation/scenes/battle_scene.py`
- Modify: `main.py`

- [ ] **Step 1: Update InputHandler**

```python
# src/presentation/input_handler.py
from __future__ import annotations
import pygame
from src.domain.interfaces import IBattleRepository
from src.domain.entities.player import InsufficientAPError
from src.use_cases.move_entity import MoveEntityUseCase
from src.use_cases.play_card import PlayCardUseCase
from src.presentation.renderers.hand_renderer import HandRenderer
from src.presentation.renderers.grid_renderer import GridRenderer

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
        play_use_case: PlayCardUseCase,
        battle_repo: IBattleRepository,
        hand_renderer: HandRenderer,
        grid_renderer: GridRenderer,
    ) -> None:
        self._move = move_use_case
        self._play = play_use_case
        self._repo = battle_repo
        self._hand_renderer = hand_renderer
        self._grid_renderer = grid_renderer
        self._selected_card_id: str | None = None

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            self._handle_key(event)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._handle_click(event.pos)

    def _handle_key(self, event: pygame.event.Event) -> None:
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

    def _handle_click(self, pos: tuple[int, int]) -> None:
        state = self._repo.get()

        clicked_card = self._hand_renderer.card_at_point(pos, state.hand)
        if clicked_card is not None:
            if self._selected_card_id == clicked_card.id:
                self._selected_card_id = None
            else:
                self._selected_card_id = clicked_card.id
            self._hand_renderer.set_selected(self._selected_card_id)
            return

        if self._selected_card_id is None:
            return

        tile_pos = self._grid_renderer.screen_to_tile(*pos)
        if tile_pos is None:
            return

        try:
            self._play.execute(self._selected_card_id)
            self._selected_card_id = None
            self._hand_renderer.set_selected(None)
        except (InsufficientAPError, ValueError):
            pass
```

- [ ] **Step 2: Update BattleScene**

```python
# src/presentation/scenes/battle_scene.py
from __future__ import annotations
import pygame
from src.domain.interfaces import IBattleRepository, IEventBus
from src.use_cases.move_entity import MoveEntityUseCase
from src.use_cases.play_card import PlayCardUseCase
from src.presentation.renderers.grid_renderer import GridRenderer
from src.presentation.renderers.entity_renderer import EntityRenderer
from src.presentation.renderers.hand_renderer import HandRenderer
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
        play_use_case = PlayCardUseCase(battle_repo, event_bus)
        self._grid_renderer = GridRenderer()
        self._entity_renderer = EntityRenderer(self._grid_renderer)
        self._hand_renderer = HandRenderer()
        self._input_handler = InputHandler(
            move_use_case,
            play_use_case,
            battle_repo,
            self._hand_renderer,
            self._grid_renderer,
        )

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
        self._hand_renderer.render(surface, state.hand)
```

- [ ] **Step 3: Update main.py**

```python
# main.py
import pygame
from src.infrastructure.battle_repository import InMemoryBattleRepository
from src.infrastructure.event_bus import PygameEventBus
from src.infrastructure.card_repository import CardRepository
from src.use_cases.start_battle import StartBattleUseCase, Encounter
from src.domain.value_objects.position import Position
from src.presentation.game_state_manager import GameStateManager
from src.presentation.scenes.battle_scene import BattleScene

WINDOW_WIDTH = 560
WINDOW_HEIGHT = 700
FPS = 60
WINDOW_TITLE = "Dungeon Card Roguelike"

def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)
    clock = pygame.time.Clock()

    event_bus = PygameEventBus()
    battle_repo = InMemoryBattleRepository()
    card_repo = CardRepository()

    StartBattleUseCase(battle_repo, event_bus, card_repo).execute(
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

- [ ] **Step 4: Run the full test suite**

```
pytest -q
```
Expected: all tests pass (49 original + new ones from this plan)

- [ ] **Step 5: Commit**

```
git add src/presentation/input_handler.py src/presentation/scenes/battle_scene.py main.py
git commit -m "feat: wire HandRenderer, PlayCardUseCase, and card click UI — Phase 2 complete"
```

---

## Self-review

**Spec coverage:**
- CardTag ✓ Task 1
- Card entity with `apply()`, `is_move_card()`, `can_fuse_with()` ✓ Task 2
- DeckManager (draw, shuffle-discard-into-deck) ✓ Task 3
- cards.json with 6 card definitions + starting deck ✓ Task 4
- ICardRepository Protocol ✓ Task 4
- CardRepository loading cards.json with unique instance IDs ✓ Task 4
- DrawCardsUseCase ✓ Task 5
- PlayCardUseCase (AP guard, apply, discard, draw_after_play) ✓ Task 6
- MoveEntityUseCase Move card requirement ✓ Task 7
- StartBattleUseCase opens with 5-card hand ✓ Task 8
- HandRenderer with parchment bg, tag-colour border, selected highlight ✓ Task 9
- GridRenderer.screen_to_tile ✓ Task 9
- BattleScene wired with HandRenderer + PlayCardUseCase ✓ Task 10
- InputHandler click-to-select card + click-tile-to-play ✓ Task 10
- WINDOW_HEIGHT 520→700 ✓ Task 10

**Placeholder scan:** No TBDs, no "similar to Task N" references, all steps contain full code.

**Type consistency:**
- `Card.is_move_card()` — defined Task 2, used Task 7 ✓
- `DeckManager.draw(deck, hand, discard)` — defined Task 3, used Tasks 5, 6, 8 ✓
- `CardRepository.get_starting_deck()` — defined Task 4, used Task 8 ✓
- `ICardRepository` added to interfaces — used by StartBattleUseCase Task 8 ✓
- `HandRenderer.card_at_point(pos, hand)` — defined Task 9, used Task 10 ✓
- `HandRenderer.set_selected(card_id)` — defined Task 9, used Task 10 ✓
- `GridRenderer.screen_to_tile(x, y)` — defined Task 9, used Task 10 ✓
- `PlayCardUseCase.execute(card_id)` — defined Task 6, used Task 10 ✓
