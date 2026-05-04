# Graph Report - .  (2026-05-04)

## Corpus Check
- Corpus is ~14,826 words - fits in a single context window. You may not need a graph.

## Summary
- 250 nodes · 433 edges · 15 communities detected
- Extraction: 61% EXTRACTED · 39% INFERRED · 0% AMBIGUOUS · INFERRED: 169 edges (avg confidence: 0.68)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Grid Entity Methods|Grid Entity Methods]]
- [[_COMMUNITY_Infrastructure & Presentation|Infrastructure & Presentation]]
- [[_COMMUNITY_Event Handling|Event Handling]]
- [[_COMMUNITY_Test Suite|Test Suite]]
- [[_COMMUNITY_Player Domain|Player Domain]]
- [[_COMMUNITY_Battle State & Interfaces|Battle State & Interfaces]]
- [[_COMMUNITY_Domain Events|Domain Events]]
- [[_COMMUNITY_Scene Management|Scene Management]]
- [[_COMMUNITY_Player Tests|Player Tests]]
- [[_COMMUNITY_Repository Tests|Repository Tests]]
- [[_COMMUNITY_Attack Patterns|Attack Patterns]]
- [[_COMMUNITY_Event Bus|Event Bus]]
- [[_COMMUNITY_AP Error|AP Error]]
- [[_COMMUNITY_Obstacle Type|Obstacle Type]]
- [[_COMMUNITY_Phase 2 Card System|Phase 2 Card System]]

## God Nodes (most connected - your core abstractions)
1. `Position` - 58 edges
2. `Grid` - 33 edges
3. `Player` - 17 edges
4. `DomainEvent` - 14 edges
5. `BattleScene` - 14 edges
6. `Encounter` - 14 edges
7. `make_state()` - 13 edges
8. `StartBattleUseCase` - 12 edges
9. `BattleState` - 11 edges
10. `IEventBus` - 11 edges

## Surprising Connections (you probably didn't know these)
- `DrawCardsUseCase (Phase 2)` --semantically_similar_to--> `MoveEntityUseCase`  [INFERRED] [semantically similar]
  docs/superpowers/plans/2026-05-04-phase2-card-system.md → src/use_cases/move_entity.py
- `Phase 1: Domain + Grid + Movement Plan` --references--> `Position Value Object Tests`  [EXTRACTED]
  docs/superpowers/plans/2026-05-02-phase1-domain-grid-movement.md → tests/domain/value_objects/test_position.py
- `Domain Isolation Principle` --rationale_for--> `IBattleRepository Protocol`  [INFERRED]
  docs/superpowers/specs/2026-05-02-dungeon-card-roguelike-design.md → src/domain/interfaces.py
- `Unidirectional Event Flow` --rationale_for--> `PygameEventBus`  [INFERRED]
  docs/superpowers/specs/2026-05-02-dungeon-card-roguelike-design.md → src/infrastructure/event_bus.py
- `Phase 1: Domain + Grid + Movement Plan` --references--> `Player Entity Tests`  [EXTRACTED]
  docs/superpowers/plans/2026-05-02-phase1-domain-grid-movement.md → tests/domain/entities/test_player.py

## Hyperedges (group relationships)
- **Battle Aggregate Root** — battle_state_BattleState, player_Player, grid_Grid [INFERRED 0.95]
- **Card Lifecycle Events** — battle_events_CardDrawn, battle_events_CardPlayed, battle_events_CardsFused [INFERRED 0.85]
- **Spatial Value Object Cluster** — position_Position, attack_pattern_AttackPattern, grid_Grid [INFERRED 0.85]
- **Render Pipeline** — battle_scene_BattleScene, grid_renderer_GridRenderer, entity_renderer_EntityRenderer [EXTRACTED 0.95]
- **Move Action Flow** — input_handler_InputHandler, move_entity_MoveEntityUseCase, event_bus_PygameEventBus [INFERRED 0.85]
- **Scene Lifecycle Pattern** — game_state_manager_GameStateManager, game_state_manager_Scene, battle_scene_BattleScene [INFERRED 0.85]
- **TDD Workflow** — phase1_plan, test_move_entity_tests, test_start_battle_tests, test_player_tests [INFERRED 0.85]
- **Architecture Principles** — rationale_domain_isolation, rationale_usecase_controllers, rationale_unidirectional_events [EXTRACTED 0.95]
- **Phase 2 Card System** — phase2_CardTag, phase2_DeckManager, phase2_CardRepository, phase2_DrawCardsUseCase, phase2_PlayCardUseCase [EXTRACTED 0.95]

## Communities (30 total, 5 thin omitted)

### Community 0 - "Grid Entity Methods"
Cohesion: 0.1
Nodes (15): Grid, test_all_tiles_passable_on_init(), test_get_entity_position_returns_current_pos(), test_get_entity_position_returns_none_when_absent(), test_get_targets_cross_from_corner_excludes_oob(), test_get_targets_pit_not_excluded_from_pattern(), test_get_targets_single_hits_origin(), test_get_targets_wall_excluded_from_pattern() (+7 more)

### Community 1 - "Infrastructure & Presentation"
Cohesion: 0.09
Nodes (29): InMemoryBattleRepository, BattleScene, Dungeon Card Roguelike Design Spec, EntityRenderer, PygameEventBus, GameStateManager, Scene Protocol, GridRenderer (+21 more)

### Community 2 - "Event Handling"
Cohesion: 0.1
Nodes (5): InputHandler, EntityRenderer, GridRenderer, BattleScene, MoveEntityUseCase

### Community 3 - "Test Suite"
Cohesion: 0.18
Nodes (23): make_state(), make_use_case(), test_move_deducts_ap(), test_move_publishes_entity_moved_event(), test_move_saves_state(), test_move_to_occupied_tile_raises(), test_move_to_wall_raises(), test_move_unknown_entity_raises() (+15 more)

### Community 4 - "Player Domain"
Cohesion: 0.16
Nodes (15): DomainEvent, InsufficientAPError, Player, DomainEvent, BattleEnded, BattleTurnStarted, CardDrawn, CardPlayed (+7 more)

### Community 5 - "Battle State & Interfaces"
Cohesion: 0.15
Nodes (12): BattleState, IBattleRepository, IEventBus, main(), Encounter, StartBattleUseCase, make_use_case(), test_start_battle_grid_is_4x4() (+4 more)

### Community 6 - "Domain Events"
Cohesion: 0.13
Nodes (18): AttackPattern, DomainEvent, BattleEnded, BattleTurnStarted, CardDrawn, CardPlayed, CardsFused, DamageTaken (+10 more)

### Community 7 - "Scene Management"
Cohesion: 0.18
Nodes (3): GameStateManager, Scene, Protocol

### Community 8 - "Player Tests"
Cohesion: 0.35
Nodes (10): make_player(), test_is_alive_false_when_hp_zero(), test_is_alive_true_when_hp_positive(), test_move_to_updates_position_and_returns_event(), test_refresh_ap_restores_to_max(), test_spend_ap_deducts_amount(), test_spend_ap_exact_amount_succeeds(), test_spend_ap_raises_when_insufficient() (+2 more)

### Community 9 - "Repository Tests"
Cohesion: 0.29
Nodes (5): InMemoryBattleRepository, make_state(), test_get_raises_before_save(), test_save_and_get_returns_same_state(), test_save_overwrites_previous_state()

## Knowledge Gaps
- **18 isolated node(s):** `InsufficientAPError`, `Tile`, `Obstacle`, `BattleTurnStarted`, `BattleEnded` (+13 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Position` connect `Test Suite` to `Grid Entity Methods`, `Event Handling`, `Player Domain`, `Battle State & Interfaces`, `Player Tests`, `Repository Tests`?**
  _High betweenness centrality (0.251) - this node is a cross-community bridge._
- **Why does `Grid` connect `Grid Entity Methods` to `Event Handling`, `Test Suite`, `Battle State & Interfaces`, `Repository Tests`, `Attack Patterns`?**
  _High betweenness centrality (0.138) - this node is a cross-community bridge._
- **Why does `main()` connect `Battle State & Interfaces` to `Event Handling`, `Test Suite`, `Scene Management`, `Repository Tests`, `Event Bus`?**
  _High betweenness centrality (0.091) - this node is a cross-community bridge._
- **Are the 55 inferred relationships involving `Position` (e.g. with `Grid` and `InsufficientAPError`) actually correct?**
  _`Position` has 55 INFERRED edges - model-reasoned connections that need verification._
- **Are the 23 inferred relationships involving `Grid` (e.g. with `BattleState` and `Position`) actually correct?**
  _`Grid` has 23 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `Player` (e.g. with `BattleState` and `Position`) actually correct?**
  _`Player` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `DomainEvent` (e.g. with `IEventBus` and `IBattleRepository`) actually correct?**
  _`DomainEvent` has 13 INFERRED edges - model-reasoned connections that need verification._