# Dungeon Card Roguelike — Design Spec
**Date:** 2026-05-02  
**Status:** Approved

---

## Overview

A tactical card-based roguelike built in Pygame. The player navigates a 3-floor dungeon map, fights pack encounters on a 4×4 grid using a deck of cards, and fuses cards turn-by-turn for powerful synergies. Art style: Dark Dungeon/Fantasy. Target session: 30–45 minutes.

---

## Confirmed Design Decisions

| Decision | Choice |
|---|---|
| Grid size | 4×4 |
| Art style | Dark Dungeon / Fantasy (stone tiles, torchlight, warm browns/reds) |
| Player movement | Move card in deck — costs AP, consumes deck/hand space |
| Energy system | Action Points (AP) — refresh each turn; some cards grant bonus AP |
| Fusion | Turn-only — two cards combine into one super-card; both source cards discarded |
| Enemies per fight | 1–3 (pack encounters) |
| Run length | Medium — 3 floors, ~5–6 nodes each, mini-boss (floor 1 end), final boss (floor 3 end) |

---

## Architecture: Layered Modules with Event Bus + Use-Case Controllers

### Guiding Principles

- **Use-case controllers, not facade controllers** — each use case class handles one action, orchestrates domain objects, and emits events. No use case contains business logic; that lives in domain entities.
- **Single Responsibility** — every class has one reason to change.
- **Dependency Inversion** — use cases depend on domain interfaces (`IBattleRepository`, `IEventBus`), never on concrete Pygame or file I/O.
- **Domain isolation** — `domain/` has zero imports from `infrastructure/` or `presentation/`. Pygame lives exclusively in `presentation/`.
- **Unidirectional event flow** — use cases publish events; renderers subscribe. Renderers never publish.

---

## Layer Structure

```
src/
├── domain/
│   ├── entities/        # Player, Enemy, Card, Grid, Tile
│   ├── value_objects/   # Position, CardTag, AttackPattern, Intent
│   ├── events/          # Domain events (CardPlayed, DamageTaken, ...)
│   └── services/        # FusionEngine (domain service)
│
├── use_cases/
│   ├── play_card.py
│   ├── fuse_cards.py
│   ├── move_entity.py
│   ├── draw_cards.py
│   ├── enemy_take_turn.py
│   └── start_battle.py
│
├── infrastructure/
│   ├── event_bus.py         # PygameEventBus implements IEventBus
│   ├── card_repository.py   # Loads cards.json, implements ICardRepository
│   └── run_repository.py    # Saves/loads roguelike run state
│
├── presentation/
│   ├── scenes/              # BattleScene, MapScene, MenuScene, RewardScene
│   ├── renderers/           # GridRenderer, HandRenderer, IntentRenderer, HUDRenderer
│   └── input_handler.py     # Translates raw Pygame events → use case calls
│
├── data/
│   └── cards.json
└── main.py
```

---

## Domain Layer

### Value Objects (immutable)

```python
Position(col: int, row: int)
  - validates 0 <= col, row < 4
  - offset(dcol, drow) -> Position | None

CardTag(value: str)
  - e.g. "Fire", "Blade", "Area", "Electric", "Buffer"

AttackPattern(offsets: list[Position])
  - named patterns: "cross", "line", "square", "single"

Intent(type: str, pattern: list[Position], countdown: int)
  - types: "ATTACK", "MOVE", "BUFF"
```

### Entities

```python
Card
  - id, name, tags: list[CardTag], ap_cost: int, pattern: AttackPattern
  - can_fuse_with(other: Card) -> bool
  - apply(context: CardContext) -> list[DomainEvent]   # side-effect free

Player
  - position: Position, hp: int, max_hp: int, ap: int, max_ap: int
  - take_damage(amount: int) -> DamageTaken
  - move_to(pos: Position) -> PlayerMoved
  - spend_ap(amount: int) -> APSpent | InsufficientAPError

Enemy
  - id, position: Position, hp: int, intent: Intent
  - choose_intent(grid_state: GridSnapshot) -> Intent   # AI logic here
  - take_damage(amount: int) -> DamageTaken
  - resolve_attack(player: Player) -> list[DomainEvent]

Grid
  - size: int = 4
  - tiles: dict[Position, Tile]
  - in_bounds(pos: Position) -> bool
  - is_occupied(pos: Position) -> bool
  - is_passable(pos: Position) -> bool          # false for walls, pits
  - get_targets(origin: Position, pattern: AttackPattern) -> list[Position]
  - place(entity_id, pos: Position)
  - remove(entity_id)

Tile
  - position: Position
  - obstacle: Obstacle | None
  - occupant_id: str | None

Obstacle(type: Literal["wall", "pit", "boulder"])
  - wall: blocks movement and attack patterns (line blocked)
  - pit: blocks movement only (attack patterns pass over)
  - boulder: blocks movement; can be destroyed by AoE cards
```

### Supporting Types

```python
CardContext(player: Player, targets: list[Position], enemies: list[Enemy])
  - passed to Card.apply(); gives the card everything it needs to resolve effects

GridSnapshot(positions: dict[str, Position], hp: dict[str, int], obstacles: dict[Position, Obstacle])
  - read-only view of the grid passed to enemy.choose_intent()
  - avoids giving Enemy a mutable reference to Grid
  - obstacles included so enemy AI can path around walls/pits

Encounter(enemy_definitions: list[EnemyDef], layout: list[Position])
  - data loaded from run_repository describing which enemies spawn where
```

### Domain Service

```python
FusionEngine
  - SYNERGY_TABLE: dict[frozenset[CardTag], CardDefinition]
    - e.g. {Electric, Area} → "Electric Nova"  (hits all adjacent tiles)
    - e.g. {Fire, Blade}   → "Flame Edge"      (line attack + burn status)
    - e.g. {Buffer, Any}   → fused card gains "Draw 1" effect after resolving
  - fuse(card_a: Card, card_b: Card) -> Card | None
```

**Card Economy rule:** Fusion is a 2-for-1 trade, so fused cards must always be worth more than the sum of their parts. Design constraint: every entry in `SYNERGY_TABLE` must satisfy at least one of:
- Deals damage equal to both source cards combined + a bonus (raw impact)
- Applies a lasting status effect (burn, stun, slow) that pays off over future turns
- Includes "Draw 1" so the hand loss is partially recovered

This is enforced during card design, not in code. The `FusionEngine` is data-driven — the `cards.json` fused card definition carries the `draw_after_play: true` flag if applicable.

### Domain Events

```python
CardPlayed(card_id, player_id, targets: list[Position])
CardsFused(card_a_id, card_b_id, result_card: Card)
DamageTaken(entity_id, amount, source)
EntityMoved(entity_id, from_pos: Position, to_pos: Position)
IntentBroadcast(enemy_id, intent: Intent)
BattleTurnStarted(turn_number, ap_refreshed: int)
BattleEnded(outcome: Literal["victory", "defeat"])
CardDrawn(card_id)
ObstaclePlaced(pos: Position, obstacle: Obstacle)
EnemyOrderAssigned(enemy_id, order: int)
```

---

## Use Cases

Each use case is injected with `IBattleRepository` and `IEventBus`. No use case calls another use case.

```python
PlayCardUseCase.execute(card_id: str) -> None
  # Guards: card in hand, player has AP
  # Calls card.apply(context) → events
  # Publishes CardPlayed + returned events
  # Moves card to discard, deducts AP

FuseCardsUseCase.execute(card_a_id: str, card_b_id: str) -> None
  # Guards: both cards in hand
  # Calls FusionEngine.fuse() — raises NoSynergyError if no match
  # Publishes CardsFused
  # Both source cards → discard; fused card → hand (this turn only)
  # If fused card is not played before End Turn, it is also discarded at turn end

MoveEntityUseCase.execute(entity_id: str, target_pos: Position) -> None
  # Guards: Move card in hand, target in bounds, target unoccupied, AP available
  # Publishes EntityMoved
  # Deducts AP, discards Move card

DrawCardsUseCase.execute(count: int) -> None
  # Draws from deck; if deck empty, shuffles discard pile into deck first
  # Publishes CardDrawn per card

EnemyTakeTurnUseCase.execute(enemy_id: str) -> None
  # Calls enemy.choose_intent() → publishes IntentBroadcast
  # Countdown decrements by 1 each time this use case runs (once per player End Turn)
  # On countdown == 0: resolves attack → publishes DamageTaken if player on targeted tile
  # After resolving, enemy selects a new intent (countdown resets)

StartBattleUseCase.execute(encounter: Encounter) -> None
  # Initialises BattleState, places player + enemies on grid
  # Draws opening hand (5 cards)
  # Publishes BattleTurnStarted
```

---

## Event Bus

```python
class IEventBus(Protocol):
    def publish(self, event: DomainEvent) -> None: ...
    def subscribe(self, event_type: type, handler: Callable) -> None: ...
    def unsubscribe(self, event_type: type, handler: Callable) -> None: ...

# Concrete: PygameEventBus wraps pygame.event.post() for delivery
```

Flow example — card played:
```
InputHandler (mouse click on card + tile)
  → PlayCardUseCase.execute("slash_01")
    → card.apply() → [DamageTaken(enemy_id, 4)]
    → bus.publish(CardPlayed(...))
    → bus.publish(DamageTaken(...))
      ↳ HandRenderer.on_card_played()    → removes card from hand display
      ↳ GridRenderer.on_damage_taken()   → flashes hit tile red
      ↳ EnemyRenderer.on_damage_taken()  → updates enemy HP bar
```

---

## Presentation Layer

### Scenes (managed by GameStateManager — State Pattern)

```
MENU → BATTLE → REWARD → MAP → BATTLE → ... → BOSS → MENU
```

Each scene subscribes to relevant domain events on enter and unsubscribes on exit.

| Scene | Renderers active |
|---|---|
| BattleScene | GridRenderer, HandRenderer, IntentRenderer, HUDRenderer, EnemyRenderer |
| MapScene | MapRenderer, NodeRenderer |
| RewardScene | CardRewardRenderer |
| MenuScene | MenuRenderer |

### Input Handler

`InputHandler` is the single entry point for all raw Pygame input. It maps:
- Arrow keys / WASD → `MoveEntityUseCase`
- Click on card → selection state
- Click on card + drag onto another card → `FuseCardsUseCase`
- Click card + click tile → `PlayCardUseCase`
- End Turn button → `EnemyTakeTurnUseCase` (for each enemy), then `BattleTurnStarted`

### Visual Details (Dark Dungeon / Fantasy)

- Grid tiles: stone texture, dark brown border, subtle inner shadow
- Player tile highlight: warm gold glow
- Enemy intent preview: targeted tiles tint red, countdown number displayed
- **Order of Action**: when 2+ enemies are present, each enemy displays its action order number (1, 2, 3) above its sprite. Order is determined at turn start by `EnemyTakeTurnUseCase` processing sequence (fastest/lowest HP first). Players use this to prioritise which enemy to eliminate before taking damage.
- Cards: parchment-style background, tag color-coded border, hover → slight scale-up (Lerp)
- Lerp used for all entity movement between tiles (snappy ~150ms slide)

---

## Data

### `cards.json` entry format

```json
{
  "id": "slash_01",
  "name": "Iron Slash",
  "tags": ["Blade"],
  "ap_cost": 2,
  "pattern": "line",
  "damage": 4,
  "grants_ap": 0,
  "draw_after_play": 0,
  "status_effect": null,
  "description": "Strike in a line of 3 tiles."
}
```

Fused card example:
```json
{
  "id": "flame_edge",
  "name": "Flame Edge",
  "tags": ["Fire", "Blade"],
  "ap_cost": 0,
  "pattern": "line",
  "damage": 9,
  "grants_ap": 0,
  "draw_after_play": 1,
  "status_effect": "burn_1",
  "description": "Fused. Line attack with burn. Draw 1 after."
}
```

Pattern names map to `AttackPattern` value objects in `CardRepository`.

---

## Roguelike Run Structure

- **3 floors**, each with **5–6 nodes**
- Node types: `Combat`, `Fusion Lab` (safe fuse + card upgrade), `Data Cache` (shop — buy/remove cards)
- **Floor 1 end:** Mini-boss (2-phase intent, telegraphed AoE)
- **Floor 3 end:** Final boss (3-phase, multi-enemy adds in phase 2)
- On victory: Reward screen — choose 1 of 3 cards to add to deck
- On defeat: Run ends, return to Menu

---

## Testing Strategy

- Domain entities and use cases are pure Python — no Pygame dependency, fully unit-testable
- `FusionEngine` synergy table covered by parameterised tests
- `PlayCardUseCase` tested with an `InMemoryBattleRepository` and a mock `IEventBus`
- Integration tests cover full turn sequences (draw → fuse → play → enemy turn)
- Presentation layer not unit-tested; verified by running the game
