# Phase 3: Fusion Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add card fusion — a `FusionEngine` domain service that merges two hand cards sharing a tag into a stronger combined card, a `FuseCardsUseCase` that orchestrates the operation, and a drag-to-fuse UI where the player presses on one card and releases over another to trigger fusion.

**Architecture:** `FusionEngine` is a pure domain service with zero Pygame imports. `FuseCardsUseCase` follows the same `(battle_repo, event_bus)` pattern as `PlayCardUseCase`. `HandRenderer` gains drag ghost rendering (`set_drag` / `clear_drag` / `_render_drag_ghost`). `InputHandler` gains a four-state drag machine: idle → potential drag → dragging → released. `BattleScene` creates `FuseCardsUseCase` and passes it as the third argument to `InputHandler`.

**Tech Stack:** Python 3.11, Pygame 2, pytest, dataclasses.

---

## Existing codebase — key facts for this plan

- `Card.can_fuse_with(other)` already implemented in `src/domain/entities/card.py` — returns True when cards share at least one `CardTag`.
- `CardsFused(card_a_id, card_b_id, result_card_id)` already defined in `src/domain/events/battle_events.py`.
- `BattleState.fused_card_ids: set` already a field in `src/domain/battle_state.py`.
- `AttackPattern.offsets: tuple[tuple[int,int],...]` — larger pattern = more offsets. `single`=1, `line`=3, `cross`=5, `square`=9.
- `HandRenderer.card_rect(index, hand_size)` returns `pygame.Rect` for card slot — used for hit-testing.
- `InputHandler` currently 5 params: `(move_use_case, play_use_case, battle_repo, hand_renderer, grid_renderer)` — Task 4 inserts `fuse_use_case` as the third parameter.
- `CARD_W=80`, `CARD_H=110`, `HAND_Y=490`, `CARD_GAP=10` in `hand_renderer.py`.
- `COLOR_CARD_BG=(220,200,160)`, `_TAG_BORDER` dict, `_DEFAULT_BORDER=(120,110,90)` in `hand_renderer.py`.
- Existing 88 tests all pass: `pytest -q`.

---

## File map

| Action | Path | Responsibility |
|--------|------|----------------|
| Create | `src/domain/services/fusion_engine.py` | Pure fusion logic — produce fused `Card` from two source cards |
| Create | `src/use_cases/fuse_cards.py` | Orchestrate fusion: consume two hand cards, emit `CardsFused` |
| Modify | `src/presentation/renderers/hand_renderer.py` | `set_drag`, `clear_drag`, `_render_drag_ghost` |
| Modify | `src/presentation/input_handler.py` | Drag state machine; new `fuse_use_case` third param |
| Modify | `src/presentation/scenes/battle_scene.py` | Create `FuseCardsUseCase`; pass to updated `InputHandler` |
| Create | `tests/domain/services/test_fusion_engine.py` | 8 FusionEngine tests |
| Create | `tests/use_cases/test_fuse_cards.py` | 7 FuseCardsUseCase tests |
| Create | `tests/presentation/__init__.py` | Package marker |
| Create | `tests/presentation/conftest.py` | `pygame.init()` session fixture |
| Create | `tests/presentation/test_input_handler_drag.py` | 3 drag gesture integration tests |

---

## Task 1: FusionEngine domain service

**Files:**
- Create: `src/domain/services/fusion_engine.py`
- Test: `tests/domain/services/test_fusion_engine.py`

**Fusion rules:**
- `id = f"fused_{card_a.id}_{card_b.id}"`
- `name = f"{card_a.name}+{card_b.name}"`
- `tags` = union of both cards' tags (order-stable via dict keys)
- `ap_cost = max(card_a.ap_cost, card_b.ap_cost)`
- `damage = card_a.damage + card_b.damage + 1`
- `pattern` = whichever card has more offsets (larger area)
- `grants_ap = card_a.grants_ap + card_b.grants_ap`
- `draw_after_play = card_a.draw_after_play + card_b.draw_after_play`
- Raises `ValueError` if cards share no tags.

- [ ] **Step 1: Write the failing tests**

```python
# tests/domain/services/test_fusion_engine.py
import pytest
from src.domain.entities.card import Card
from src.domain.value_objects.card_tag import CardTag
from src.domain.value_objects.attack_pattern import AttackPattern
from src.domain.services.fusion_engine import FusionEngine


def _card(
    id: str,
    tags: list[str],
    ap: int = 1,
    dmg: int = 0,
    pattern: str = "single",
    grants_ap: int = 0,
    draw_after: int = 0,
) -> Card:
    return Card(
        id=id,
        name=id,
        tags=[CardTag(t) for t in tags],
        ap_cost=ap,
        pattern=AttackPattern.from_name(pattern),
        damage=dmg,
        grants_ap=grants_ap,
        draw_after_play=draw_after,
    )


def test_fuse_produces_correct_id_and_name():
    a = _card("strike_1", ["Blade"], ap=1, dmg=2)
    b = _card("slash_1", ["Blade"], ap=2, dmg=4)
    result = FusionEngine.fuse(a, b)
    assert result.id == "fused_strike_1_slash_1"
    assert result.name == "strike_1+slash_1"


def test_fuse_damage_is_sum_plus_one():
    a = _card("a_1", ["Blade"], ap=1, dmg=2)
    b = _card("b_1", ["Blade"], ap=1, dmg=3)
    result = FusionEngine.fuse(a, b)
    assert result.damage == 6  # 2 + 3 + 1


def test_fuse_ap_cost_is_max():
    a = _card("a_1", ["Blade"], ap=1, dmg=0)
    b = _card("b_1", ["Blade"], ap=3, dmg=0)
    result = FusionEngine.fuse(a, b)
    assert result.ap_cost == 3


def test_fuse_tags_are_union():
    a = _card("a_1", ["Blade", "Fire"], ap=1, dmg=0)
    b = _card("b_1", ["Blade", "Electric"], ap=1, dmg=0)
    result = FusionEngine.fuse(a, b)
    tag_values = {t.value for t in result.tags}
    assert tag_values == {"Blade", "Fire", "Electric"}


def test_fuse_pattern_takes_larger():
    a = _card("a_1", ["Blade"], ap=1, dmg=0, pattern="single")  # 1 tile
    b = _card("b_1", ["Blade"], ap=1, dmg=0, pattern="cross")   # 5 tiles
    result = FusionEngine.fuse(a, b)
    assert result.pattern == AttackPattern.from_name("cross")


def test_fuse_no_shared_tag_raises():
    a = _card("a_1", ["Blade"], ap=1, dmg=0)
    b = _card("b_1", ["Fire"], ap=1, dmg=0)
    with pytest.raises(ValueError, match="cannot fuse"):
        FusionEngine.fuse(a, b)


def test_fuse_grants_ap_summed():
    a = _card("a_1", ["Blade"], ap=0, dmg=0, grants_ap=1)
    b = _card("b_1", ["Blade"], ap=0, dmg=0, grants_ap=2)
    result = FusionEngine.fuse(a, b)
    assert result.grants_ap == 3


def test_fuse_draw_after_play_summed():
    a = _card("a_1", ["Blade"], ap=0, dmg=0, draw_after=1)
    b = _card("b_1", ["Blade"], ap=0, dmg=0, draw_after=1)
    result = FusionEngine.fuse(a, b)
    assert result.draw_after_play == 2
```

- [ ] **Step 2: Run tests to verify they fail**

```
pytest tests/domain/services/test_fusion_engine.py -v
```
Expected: `ERROR` — `ModuleNotFoundError: No module named 'src.domain.services.fusion_engine'`

- [ ] **Step 3: Implement FusionEngine**

```python
# src/domain/services/fusion_engine.py
from __future__ import annotations
from src.domain.entities.card import Card
from src.domain.value_objects.card_tag import CardTag


class FusionEngine:
    @staticmethod
    def fuse(card_a: Card, card_b: Card) -> Card:
        if not card_a.can_fuse_with(card_b):
            raise ValueError(
                f"Cards '{card_a.id}' and '{card_b.id}' share no tags and cannot fuse"
            )
        tags = list({t: None for t in [*card_a.tags, *card_b.tags]}.keys())
        pattern = (
            card_a.pattern
            if len(card_a.pattern.offsets) >= len(card_b.pattern.offsets)
            else card_b.pattern
        )
        return Card(
            id=f"fused_{card_a.id}_{card_b.id}",
            name=f"{card_a.name}+{card_b.name}",
            tags=tags,
            ap_cost=max(card_a.ap_cost, card_b.ap_cost),
            damage=card_a.damage + card_b.damage + 1,
            pattern=pattern,
            grants_ap=card_a.grants_ap + card_b.grants_ap,
            draw_after_play=card_a.draw_after_play + card_b.draw_after_play,
        )
```

- [ ] **Step 4: Run tests to verify they pass**

```
pytest tests/domain/services/test_fusion_engine.py -v
```
Expected: `8 passed`

- [ ] **Step 5: Commit**

```
git add src/domain/services/fusion_engine.py tests/domain/services/test_fusion_engine.py
git commit -m "feat: add FusionEngine domain service"
```

---

## Task 2: FuseCardsUseCase

**Files:**
- Create: `src/use_cases/fuse_cards.py`
- Test: `tests/use_cases/test_fuse_cards.py`

**Behavior:**
- Raises `ValueError` if either card is not in hand.
- Calls `FusionEngine.fuse()` — which raises `ValueError` if cards share no tags.
- Removes both source cards from `state.hand`, appends fused card.
- Adds both source IDs to `state.fused_card_ids`.
- Saves state, then publishes `CardsFused`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/use_cases/test_fuse_cards.py
import pytest
from unittest.mock import MagicMock
from src.domain.battle_state import BattleState
from src.domain.entities.grid import Grid
from src.domain.entities.player import Player
from src.domain.entities.card import Card
from src.domain.value_objects.position import Position
from src.domain.value_objects.card_tag import CardTag
from src.domain.value_objects.attack_pattern import AttackPattern
from src.domain.events.battle_events import CardsFused
from src.use_cases.fuse_cards import FuseCardsUseCase


def _card(id: str, tags: list[str], ap: int = 1, dmg: int = 0) -> Card:
    return Card(
        id=id, name=id, tags=[CardTag(t) for t in tags],
        ap_cost=ap, pattern=AttackPattern.single(), damage=dmg,
    )


def _make_state(hand_cards: list[Card]) -> BattleState:
    grid = Grid()
    player = Player(id="player", position=Position(0, 0), hp=30, max_hp=30, ap=3, max_ap=3)
    state = BattleState(player=player, grid=grid)
    state.hand = list(hand_cards)
    return state


def _make_use_case(state: BattleState):
    repo = MagicMock()
    repo.get.return_value = state
    bus = MagicMock()
    return FuseCardsUseCase(repo, bus), repo, bus


def test_fuse_removes_both_source_cards():
    a = _card("strike_1", ["Blade"])
    b = _card("slash_1", ["Blade"])
    state = _make_state([a, b])
    use_case, _, _ = _make_use_case(state)
    use_case.execute("strike_1", "slash_1")
    assert a not in state.hand
    assert b not in state.hand


def test_fuse_adds_fused_card_to_hand():
    a = _card("strike_1", ["Blade"])
    b = _card("slash_1", ["Blade"])
    state = _make_state([a, b])
    use_case, _, _ = _make_use_case(state)
    use_case.execute("strike_1", "slash_1")
    assert len(state.hand) == 1
    assert state.hand[0].id == "fused_strike_1_slash_1"


def test_fuse_tracks_consumed_ids():
    a = _card("strike_1", ["Blade"])
    b = _card("slash_1", ["Blade"])
    state = _make_state([a, b])
    use_case, _, _ = _make_use_case(state)
    use_case.execute("strike_1", "slash_1")
    assert "strike_1" in state.fused_card_ids
    assert "slash_1" in state.fused_card_ids


def test_fuse_saves_state():
    a = _card("strike_1", ["Blade"])
    b = _card("slash_1", ["Blade"])
    state = _make_state([a, b])
    use_case, repo, _ = _make_use_case(state)
    use_case.execute("strike_1", "slash_1")
    repo.save.assert_called_once_with(state)


def test_fuse_publishes_cards_fused_event():
    a = _card("strike_1", ["Blade"])
    b = _card("slash_1", ["Blade"])
    state = _make_state([a, b])
    use_case, _, bus = _make_use_case(state)
    use_case.execute("strike_1", "slash_1")
    event = bus.publish.call_args[0][0]
    assert isinstance(event, CardsFused)
    assert event.card_a_id == "strike_1"
    assert event.card_b_id == "slash_1"
    assert event.result_card_id == "fused_strike_1_slash_1"


def test_fuse_card_not_in_hand_raises():
    a = _card("strike_1", ["Blade"])
    state = _make_state([a])
    use_case, _, _ = _make_use_case(state)
    with pytest.raises(ValueError, match="not in hand"):
        use_case.execute("strike_1", "ghost")


def test_fuse_incompatible_cards_raises():
    a = _card("strike_1", ["Blade"])
    b = _card("spark_1", ["Electric"])
    state = _make_state([a, b])
    use_case, _, _ = _make_use_case(state)
    with pytest.raises(ValueError, match="cannot fuse"):
        use_case.execute("strike_1", "spark_1")
```

- [ ] **Step 2: Run tests to verify they fail**

```
pytest tests/use_cases/test_fuse_cards.py -v
```
Expected: `ERROR` — `ModuleNotFoundError: No module named 'src.use_cases.fuse_cards'`

- [ ] **Step 3: Implement FuseCardsUseCase**

```python
# src/use_cases/fuse_cards.py
from src.domain.interfaces import IBattleRepository, IEventBus
from src.domain.services.fusion_engine import FusionEngine
from src.domain.events.battle_events import CardsFused


class FuseCardsUseCase:
    def __init__(self, battle_repo: IBattleRepository, event_bus: IEventBus) -> None:
        self._repo = battle_repo
        self._bus = event_bus

    def execute(self, card_a_id: str, card_b_id: str) -> None:
        state = self._repo.get()
        card_a = next((c for c in state.hand if c.id == card_a_id), None)
        if card_a is None:
            raise ValueError(f"Card '{card_a_id}' not in hand")
        card_b = next((c for c in state.hand if c.id == card_b_id), None)
        if card_b is None:
            raise ValueError(f"Card '{card_b_id}' not in hand")
        fused = FusionEngine.fuse(card_a, card_b)
        state.hand.remove(card_a)
        state.hand.remove(card_b)
        state.hand.append(fused)
        state.fused_card_ids.add(card_a_id)
        state.fused_card_ids.add(card_b_id)
        self._repo.save(state)
        self._bus.publish(CardsFused(
            card_a_id=card_a_id,
            card_b_id=card_b_id,
            result_card_id=fused.id,
        ))
```

- [ ] **Step 4: Run tests to verify they pass**

```
pytest tests/use_cases/test_fuse_cards.py -v
```
Expected: `7 passed`

- [ ] **Step 5: Run full suite**

```
pytest -q
```
Expected: `95 passed`

- [ ] **Step 6: Commit**

```
git add src/use_cases/fuse_cards.py tests/use_cases/test_fuse_cards.py
git commit -m "feat: add FuseCardsUseCase"
```

---

## Task 3: HandRenderer drag ghost

**Files:**
- Modify: `src/presentation/renderers/hand_renderer.py`
- Create: `tests/presentation/__init__.py`
- Create: `tests/presentation/conftest.py`
- Create: `tests/presentation/test_hand_renderer_drag.py`

**Additions to HandRenderer:**
- `__init__` gains `self._drag_card: Card | None = None` and `self._drag_pos: tuple[int, int] | None = None`.
- `set_drag(card, pos)` — stores drag card and cursor position; called by InputHandler on every MOUSEMOTION during drag.
- `clear_drag()` — resets both to None; called by InputHandler on MOUSEBUTTONUP.
- `_render_drag_ghost(surface)` — draws a semi-transparent card (alpha=180) centered on `_drag_pos`; does nothing if either is None.
- `render()` calls `_render_drag_ghost(surface)` as its last action so the ghost always appears on top.

- [ ] **Step 1: Write the failing tests**

Create `tests/presentation/__init__.py` (empty):
```python
```

Create `tests/presentation/conftest.py`:
```python
# tests/presentation/conftest.py
import pytest
import pygame


@pytest.fixture(scope="session", autouse=True)
def pygame_init():
    pygame.init()
    yield
    pygame.quit()
```

Create `tests/presentation/test_hand_renderer_drag.py`:
```python
# tests/presentation/test_hand_renderer_drag.py
from src.domain.entities.card import Card
from src.domain.value_objects.card_tag import CardTag
from src.domain.value_objects.attack_pattern import AttackPattern
from src.presentation.renderers.hand_renderer import HandRenderer


def _card(id: str) -> Card:
    return Card(
        id=id, name=id, tags=[CardTag("Blade")],
        ap_cost=1, pattern=AttackPattern.single(), damage=0,
    )


def test_set_drag_stores_card_and_pos():
    renderer = HandRenderer()
    card = _card("a_1")
    renderer.set_drag(card, (200, 300))
    assert renderer._drag_card is card
    assert renderer._drag_pos == (200, 300)


def test_clear_drag_resets_to_none():
    renderer = HandRenderer()
    card = _card("a_1")
    renderer.set_drag(card, (200, 300))
    renderer.clear_drag()
    assert renderer._drag_card is None
    assert renderer._drag_pos is None


def test_set_drag_updates_pos_on_subsequent_calls():
    renderer = HandRenderer()
    card = _card("a_1")
    renderer.set_drag(card, (100, 100))
    renderer.set_drag(card, (150, 150))
    assert renderer._drag_pos == (150, 150)
```

- [ ] **Step 2: Run tests to verify they fail**

```
pytest tests/presentation/test_hand_renderer_drag.py -v
```
Expected: `FAILED` — `AttributeError: 'HandRenderer' object has no attribute '_drag_card'`

- [ ] **Step 3: Modify HandRenderer**

Full updated `src/presentation/renderers/hand_renderer.py`:

```python
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
        self._drag_card: Card | None = None
        self._drag_pos: tuple[int, int] | None = None

    def set_selected(self, card_id: str | None) -> None:
        self._selected_id = card_id

    def set_drag(self, card: Card, pos: tuple[int, int]) -> None:
        self._drag_card = card
        self._drag_pos = pos

    def clear_drag(self) -> None:
        self._drag_card = None
        self._drag_pos = None

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

        self._render_drag_ghost(surface)

    def _render_drag_ghost(self, surface: pygame.Surface) -> None:
        if self._drag_card is None or self._drag_pos is None:
            return
        ghost = pygame.Surface((CARD_W, CARD_H), pygame.SRCALPHA)
        first_tag = self._drag_card.tags[0].value if self._drag_card.tags else ""
        border_color = _TAG_BORDER.get(first_tag, _DEFAULT_BORDER)
        ghost.fill((*COLOR_CARD_BG, 180))
        pygame.draw.rect(ghost, (*border_color, 220), ghost.get_rect(), width=3, border_radius=4)
        x = self._drag_pos[0] - CARD_W // 2
        y = self._drag_pos[1] - CARD_H // 2
        surface.blit(ghost, (x, y))
```

- [ ] **Step 4: Run tests to verify they pass**

```
pytest tests/presentation/test_hand_renderer_drag.py -v
```
Expected: `3 passed`

- [ ] **Step 5: Run full suite**

```
pytest -q
```
Expected: `98 passed`

- [ ] **Step 6: Commit**

```
git add src/presentation/renderers/hand_renderer.py tests/presentation/
git commit -m "feat: add HandRenderer drag ghost support"
```

---

## Task 4: InputHandler drag-to-fuse + BattleScene wire

**Files:**
- Modify: `src/presentation/input_handler.py`
- Modify: `src/presentation/scenes/battle_scene.py`
- Create: `tests/presentation/test_input_handler_drag.py`

**InputHandler changes:**

New constructor signature (6 params, `fuse_use_case` inserted third):
```python
def __init__(self, move_use_case, play_use_case, fuse_use_case, battle_repo, hand_renderer, grid_renderer)
```

New drag state attributes:
- `_drag_card_id: str | None = None` — ID of card being dragged
- `_drag_start: tuple[int, int] | None = None` — mouse position at press
- `_drag_pos: tuple[int, int] | None = None` — current mouse position
- `_dragging: bool = False` — True once movement exceeds `_DRAG_THRESHOLD`

New event types handled: `MOUSEMOTION`, `MOUSEBUTTONUP`.
`MOUSEBUTTONDOWN` becomes `_handle_mouse_down` (starts potential drag).
Old `_handle_click` is now called from `_handle_mouse_up` when not dragging.

Drag detection threshold: `_DRAG_THRESHOLD = 8` (Manhattan distance in pixels).

**Drag flow:**
1. `MOUSEBUTTONDOWN` on a card → set `_drag_card_id`, `_drag_start`, `_drag_pos`; no immediate selection change.
2. `MOUSEMOTION` while button held → update `_drag_pos`; if Manhattan distance from `_drag_start` exceeds threshold, set `_dragging = True` and call `hand_renderer.set_drag(card, pos)`.
3. `MOUSEBUTTONUP`:
   - If `_dragging`: call `hand_renderer.clear_drag()`; if cursor is over a *different* card, call `fuse.execute(drag_id, target_id)` (silently ignores `ValueError`); reset all drag state.
   - If not dragging (was a quick click): call existing `_handle_click(pos)` to toggle selection / play card; reset drag state.

**BattleScene change:** Create `FuseCardsUseCase(battle_repo, event_bus)` and pass it as the third arg to `InputHandler`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/presentation/test_input_handler_drag.py
import pygame
from unittest.mock import MagicMock
from src.domain.battle_state import BattleState
from src.domain.entities.grid import Grid
from src.domain.entities.player import Player
from src.domain.entities.card import Card
from src.domain.value_objects.position import Position
from src.domain.value_objects.card_tag import CardTag
from src.domain.value_objects.attack_pattern import AttackPattern
from src.presentation.input_handler import InputHandler
from src.presentation.renderers.hand_renderer import HandRenderer
from src.presentation.renderers.grid_renderer import GridRenderer


def _card(id: str, tags: list[str] | None = None) -> Card:
    return Card(
        id=id, name=id,
        tags=[CardTag(t) for t in (tags or ["Blade"])],
        ap_cost=1, pattern=AttackPattern.single(), damage=0,
    )


def _make_state(hand_cards: list[Card]) -> BattleState:
    grid = Grid()
    player = Player(id="player", position=Position(0, 0), hp=30, max_hp=30, ap=3, max_ap=3)
    state = BattleState(player=player, grid=grid)
    state.hand = list(hand_cards)
    return state


def _make_handler(state: BattleState):
    repo = MagicMock()
    repo.get.return_value = state
    move = MagicMock()
    play = MagicMock()
    fuse = MagicMock()
    hand_renderer = HandRenderer()
    grid_renderer = GridRenderer()
    handler = InputHandler(move, play, fuse, repo, hand_renderer, grid_renderer)
    return handler, fuse, hand_renderer


def test_drag_onto_different_card_calls_fuse():
    card_a = _card("a_1")
    card_b = _card("b_1")
    state = _make_state([card_a, card_b])
    handler, fuse, hand_renderer = _make_handler(state)

    # Card slots: index 0 and 1, hand_size=2
    rect_a = hand_renderer.card_rect(0, 2)
    rect_b = hand_renderer.card_rect(1, 2)
    center_a = rect_a.center
    center_b = rect_b.center

    # Press on card_a
    handler.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=center_a))
    # Move far enough to trigger drag (cards are CARD_W + CARD_GAP = 90px apart)
    handler.handle_event(pygame.event.Event(
        pygame.MOUSEMOTION, pos=center_b, buttons=(1, 0, 0), rel=(0, 0),
    ))
    # Release on card_b
    handler.handle_event(pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=center_b))

    fuse.execute.assert_called_once_with("a_1", "b_1")


def test_drag_onto_same_card_does_not_fuse():
    card_a = _card("a_1")
    card_b = _card("b_1")
    state = _make_state([card_a, card_b])
    handler, fuse, hand_renderer = _make_handler(state)

    rect_a = hand_renderer.card_rect(0, 2)
    center_a = rect_a.center
    # Drag card_a sideways 20px (triggers _dragging) but release back on card_a's slot
    handler.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=center_a))
    handler.handle_event(pygame.event.Event(
        pygame.MOUSEMOTION,
        pos=(center_a[0] + 20, center_a[1]),
        buttons=(1, 0, 0),
        rel=(0, 0),
    ))
    handler.handle_event(pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=center_a))

    fuse.execute.assert_not_called()


def test_click_card_without_drag_selects_it():
    card_a = _card("a_1")
    state = _make_state([card_a])
    handler, fuse, hand_renderer = _make_handler(state)

    rect = hand_renderer.card_rect(0, 1)
    center = rect.center
    # Quick click (no motion event → _dragging stays False)
    handler.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=center))
    handler.handle_event(pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=center))

    assert handler._selected_card_id == "a_1"
    fuse.execute.assert_not_called()
```

- [ ] **Step 2: Run tests to verify they fail**

```
pytest tests/presentation/test_input_handler_drag.py -v
```
Expected: `FAILED` — `TypeError: InputHandler.__init__() takes 6 positional arguments but 7 were given` (because `fuse_use_case` doesn't exist yet)

- [ ] **Step 3: Rewrite InputHandler**

Full updated `src/presentation/input_handler.py`:

```python
from __future__ import annotations
import pygame
from src.domain.interfaces import IBattleRepository
from src.domain.entities.player import InsufficientAPError
from src.use_cases.move_entity import MoveEntityUseCase
from src.use_cases.play_card import PlayCardUseCase
from src.use_cases.fuse_cards import FuseCardsUseCase
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

_DRAG_THRESHOLD = 8  # Manhattan distance in pixels to confirm drag intent


class InputHandler:
    def __init__(
        self,
        move_use_case: MoveEntityUseCase,
        play_use_case: PlayCardUseCase,
        fuse_use_case: FuseCardsUseCase,
        battle_repo: IBattleRepository,
        hand_renderer: HandRenderer,
        grid_renderer: GridRenderer,
    ) -> None:
        self._move = move_use_case
        self._play = play_use_case
        self._fuse = fuse_use_case
        self._repo = battle_repo
        self._hand_renderer = hand_renderer
        self._grid_renderer = grid_renderer
        self._selected_card_id: str | None = None
        self._drag_card_id: str | None = None
        self._drag_start: tuple[int, int] | None = None
        self._drag_pos: tuple[int, int] | None = None
        self._dragging: bool = False

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            self._handle_key(event)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._handle_mouse_down(event.pos)
        elif event.type == pygame.MOUSEMOTION:
            self._handle_mouse_motion(event.pos, event.buttons)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._handle_mouse_up(event.pos)

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

    def _handle_mouse_down(self, pos: tuple[int, int]) -> None:
        state = self._repo.get()
        clicked_card = self._hand_renderer.card_at_point(pos, state.hand)
        if clicked_card is not None:
            self._drag_card_id = clicked_card.id
            self._drag_start = pos
            self._drag_pos = pos
            self._dragging = False

    def _handle_mouse_motion(
        self, pos: tuple[int, int], buttons: tuple[int, int, int]
    ) -> None:
        if not buttons[0] or self._drag_card_id is None:
            return
        self._drag_pos = pos
        if not self._dragging and self._drag_start is not None:
            dx = abs(pos[0] - self._drag_start[0])
            dy = abs(pos[1] - self._drag_start[1])
            if dx + dy > _DRAG_THRESHOLD:
                self._dragging = True
        if self._dragging:
            state = self._repo.get()
            drag_card = next(
                (c for c in state.hand if c.id == self._drag_card_id), None
            )
            if drag_card is not None:
                self._hand_renderer.set_drag(drag_card, pos)

    def _handle_mouse_up(self, pos: tuple[int, int]) -> None:
        if self._dragging and self._drag_card_id is not None:
            self._hand_renderer.clear_drag()
            state = self._repo.get()
            target_card = self._hand_renderer.card_at_point(pos, state.hand)
            if target_card is not None and target_card.id != self._drag_card_id:
                try:
                    self._fuse.execute(self._drag_card_id, target_card.id)
                except ValueError:
                    pass
        else:
            self._handle_click(pos)
        self._drag_card_id = None
        self._drag_start = None
        self._drag_pos = None
        self._dragging = False

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
        try:
            self._play.execute(self._selected_card_id)
            self._selected_card_id = None
            self._hand_renderer.set_selected(None)
        except (InsufficientAPError, ValueError):
            pass
```

- [ ] **Step 4: Update BattleScene to create FuseCardsUseCase and pass it to InputHandler**

Full updated `src/presentation/scenes/battle_scene.py`:

```python
from __future__ import annotations
import pygame
from src.domain.interfaces import IBattleRepository, IEventBus
from src.use_cases.move_entity import MoveEntityUseCase
from src.use_cases.play_card import PlayCardUseCase
from src.use_cases.fuse_cards import FuseCardsUseCase
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
        fuse_use_case = FuseCardsUseCase(battle_repo, event_bus)
        self._grid_renderer = GridRenderer()
        self._entity_renderer = EntityRenderer(self._grid_renderer)
        self._hand_renderer = HandRenderer()
        self._input_handler = InputHandler(
            move_use_case,
            play_use_case,
            fuse_use_case,
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

- [ ] **Step 5: Run the drag tests to verify they pass**

```
pytest tests/presentation/test_input_handler_drag.py -v
```
Expected: `3 passed`

- [ ] **Step 6: Run full suite**

```
pytest -q
```
Expected: `101 passed`

- [ ] **Step 7: Commit**

```
git add src/presentation/input_handler.py src/presentation/scenes/battle_scene.py tests/presentation/test_input_handler_drag.py
git commit -m "feat: wire drag-to-fuse UI — Phase 3 complete"
```

---

## Self-review

**Spec coverage:**
- FusionEngine domain service — Task 1 ✓
- FuseCardsUseCase — Task 2 ✓
- Drag-to-fuse UI — Tasks 3 + 4 ✓
- CardsFused event published — Task 2 ✓
- fused_card_ids tracked — Task 2 ✓
- Ghost card follows cursor — Task 3 + 4 ✓

**Placeholder scan:** No TBD, TODO, or vague steps. All code is complete.

**Type consistency:**
- `FusionEngine.fuse(card_a, card_b) -> Card` — used identically in Tasks 1, 2, 4.
- `HandRenderer.set_drag(card, pos)` — defined Task 3, called Task 4.
- `HandRenderer.clear_drag()` — defined Task 3, called Task 4.
- `InputHandler(move, play, fuse, repo, hand_renderer, grid_renderer)` — 6-param signature used consistently in Tasks 4 (implementation) and 4 (tests) and BattleScene update.
- `FuseCardsUseCase.execute(card_a_id, card_b_id)` — consistent across Tasks 2 and 4.
