import json, pathlib

data = {
  "nodes": [
    {"id": "test_player_test_player", "label": "Player Entity Tests", "file_type": "code", "source_file": "tests/domain/entities/test_player.py", "source_location": None, "source_url": None, "captured_at": None, "author": None, "contributor": None},
    {"id": "test_position_test_position", "label": "Position Value Object Tests", "file_type": "code", "source_file": "tests/domain/value_objects/test_position.py", "source_location": None, "source_url": None, "captured_at": None, "author": None, "contributor": None},
    {"id": "test_battle_repository_test_battle_repository", "label": "InMemoryBattleRepository Tests", "file_type": "code", "source_file": "tests/infrastructure/test_battle_repository.py", "source_location": None, "source_url": None, "captured_at": None, "author": None, "contributor": None},
    {"id": "test_move_entity_test_move_entity", "label": "MoveEntityUseCase Tests", "file_type": "code", "source_file": "tests/use_cases/test_move_entity.py", "source_location": None, "source_url": None, "captured_at": None, "author": None, "contributor": None},
    {"id": "test_start_battle_test_start_battle", "label": "StartBattleUseCase Tests", "file_type": "code", "source_file": "tests/use_cases/test_start_battle.py", "source_location": None, "source_url": None, "captured_at": None, "author": None, "contributor": None},
    {"id": "requirements_requirements", "label": "Project Requirements (pygame + pytest)", "file_type": "document", "source_file": "requirements.txt", "source_location": None, "source_url": None, "captured_at": None, "author": None, "contributor": None},
    {"id": "phase1_plan_phase1", "label": "Phase 1 Implementation Plan: Domain Foundation + Grid + Player Movement", "file_type": "document", "source_file": "docs/superpowers/plans/2026-05-02-phase1-domain-grid-movement.md", "source_location": None, "source_url": None, "captured_at": None, "author": None, "contributor": None},
    {"id": "phase2_plan_phase2", "label": "Phase 2 Implementation Plan: Card System", "file_type": "document", "source_file": "docs/superpowers/plans/2026-05-04-phase2-card-system.md", "source_location": None, "source_url": None, "captured_at": None, "author": None, "contributor": None},
    {"id": "design_spec_dungeon_card_roguelike", "label": "Dungeon Card Roguelike Design Spec", "file_type": "document", "source_file": "docs/superpowers/specs/2026-05-02-dungeon-card-roguelike-design.md", "source_location": None, "source_url": None, "captured_at": None, "author": None, "contributor": None},
    {"id": "design_principle_domain_isolation", "label": "Domain Isolation Principle (no Pygame imports in domain/)", "file_type": "rationale", "source_file": "docs/superpowers/specs/2026-05-02-dungeon-card-roguelike-design.md", "source_location": None, "source_url": None, "captured_at": None, "author": None, "contributor": None},
    {"id": "design_principle_unidirectional_event_flow", "label": "Unidirectional Event Flow (use cases publish, renderers subscribe)", "file_type": "rationale", "source_file": "docs/superpowers/specs/2026-05-02-dungeon-card-roguelike-design.md", "source_location": None, "source_url": None, "captured_at": None, "author": None, "contributor": None},
    {"id": "design_principle_use_case_controllers", "label": "Use-Case Controllers Pattern (one action per class, orchestrates domain, emits events)", "file_type": "rationale", "source_file": "docs/superpowers/specs/2026-05-02-dungeon-card-roguelike-design.md", "source_location": None, "source_url": None, "captured_at": None, "author": None, "contributor": None},
    {"id": "design_decision_move_card_required", "label": "Design Decision: Movement Requires Move Card in Hand", "file_type": "rationale", "source_file": "docs/superpowers/specs/2026-05-02-dungeon-card-roguelike-design.md", "source_location": None, "source_url": None, "captured_at": None, "author": None, "contributor": None},
    {"id": "design_decision_ap_refresh_each_turn", "label": "Design Decision: AP Refreshes Each Turn, Some Cards Grant Bonus AP", "file_type": "rationale", "source_file": "docs/superpowers/specs/2026-05-02-dungeon-card-roguelike-design.md", "source_location": None, "source_url": None, "captured_at": None, "author": None, "contributor": None},
    {"id": "design_decision_fusion_2for1", "label": "Design Decision: Fusion is 2-for-1 (both source cards discarded)", "file_type": "rationale", "source_file": "docs/superpowers/specs/2026-05-02-dungeon-card-roguelike-design.md", "source_location": None, "source_url": None, "captured_at": None, "author": None, "contributor": None},
    {"id": "design_decision_4x4_grid", "label": "Design Decision: 4x4 Grid Size", "file_type": "rationale", "source_file": "docs/superpowers/specs/2026-05-02-dungeon-card-roguelike-design.md", "source_location": None, "source_url": None, "captured_at": None, "author": None, "contributor": None},
    {"id": "concept_card_economy", "label": "Card Economy Rule (fused cards must exceed source card value)", "file_type": "rationale", "source_file": "docs/superpowers/specs/2026-05-02-dungeon-card-roguelike-design.md", "source_location": None, "source_url": None, "captured_at": None, "author": None, "contributor": None},
    {"id": "phase2_concept_card_tag", "label": "Phase 2 Feature: CardTag Value Object", "file_type": "document", "source_file": "docs/superpowers/plans/2026-05-04-phase2-card-system.md", "source_location": None, "source_url": None, "captured_at": None, "author": None, "contributor": None},
    {"id": "phase2_concept_deck_manager", "label": "Phase 2 Feature: DeckManager Domain Service", "file_type": "document", "source_file": "docs/superpowers/plans/2026-05-04-phase2-card-system.md", "source_location": None, "source_url": None, "captured_at": None, "author": None, "contributor": None},
    {"id": "phase2_concept_hand_renderer", "label": "Phase 2 Feature: HandRenderer (click-to-select, click-to-play)", "file_type": "document", "source_file": "docs/superpowers/plans/2026-05-04-phase2-card-system.md", "source_location": None, "source_url": None, "captured_at": None, "author": None, "contributor": None},
    {"id": "phase2_concept_card_repository", "label": "Phase 2 Feature: CardRepository loading from cards.json", "file_type": "document", "source_file": "docs/superpowers/plans/2026-05-04-phase2-card-system.md", "source_location": None, "source_url": None, "captured_at": None, "author": None, "contributor": None},
    {"id": "phase2_concept_play_card_use_case", "label": "Phase 2 Feature: PlayCardUseCase", "file_type": "document", "source_file": "docs/superpowers/plans/2026-05-04-phase2-card-system.md", "source_location": None, "source_url": None, "captured_at": None, "author": None, "contributor": None},
    {"id": "phase2_concept_draw_cards_use_case", "label": "Phase 2 Feature: DrawCardsUseCase", "file_type": "document", "source_file": "docs/superpowers/plans/2026-05-04-phase2-card-system.md", "source_location": None, "source_url": None, "captured_at": None, "author": None, "contributor": None}
  ],
  "edges": [
    {"source": "test_player_test_player", "target": "test_position_test_position", "relation": "shares_data_with", "confidence": "INFERRED", "confidence_score": 0.85, "source_file": "tests/domain/entities/test_player.py", "source_location": None, "weight": 1.0},
    {"source": "test_player_test_player", "target": "design_decision_ap_refresh_each_turn", "relation": "references", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "tests/domain/entities/test_player.py", "source_location": None, "weight": 1.0},
    {"source": "test_position_test_position", "target": "design_decision_4x4_grid", "relation": "references", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "tests/domain/value_objects/test_position.py", "source_location": None, "weight": 1.0},
    {"source": "test_battle_repository_test_battle_repository", "target": "design_principle_use_case_controllers", "relation": "references", "confidence": "INFERRED", "confidence_score": 0.65, "source_file": "tests/infrastructure/test_battle_repository.py", "source_location": None, "weight": 1.0},
    {"source": "test_move_entity_test_move_entity", "target": "design_decision_move_card_required", "relation": "references", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "tests/use_cases/test_move_entity.py", "source_location": None, "weight": 1.0},
    {"source": "test_move_entity_test_move_entity", "target": "design_decision_ap_refresh_each_turn", "relation": "references", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "tests/use_cases/test_move_entity.py", "source_location": None, "weight": 1.0},
    {"source": "test_move_entity_test_move_entity", "target": "design_principle_use_case_controllers", "relation": "references", "confidence": "INFERRED", "confidence_score": 0.85, "source_file": "tests/use_cases/test_move_entity.py", "source_location": None, "weight": 1.0},
    {"source": "test_start_battle_test_start_battle", "target": "design_principle_use_case_controllers", "relation": "references", "confidence": "INFERRED", "confidence_score": 0.85, "source_file": "tests/use_cases/test_start_battle.py", "source_location": None, "weight": 1.0},
    {"source": "test_start_battle_test_start_battle", "target": "design_decision_4x4_grid", "relation": "references", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "tests/use_cases/test_start_battle.py", "source_location": None, "weight": 1.0},
    {"source": "test_start_battle_test_start_battle", "target": "design_decision_ap_refresh_each_turn", "relation": "references", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "tests/use_cases/test_start_battle.py", "source_location": None, "weight": 1.0},
    {"source": "phase1_plan_phase1", "target": "design_spec_dungeon_card_roguelike", "relation": "references", "confidence": "INFERRED", "confidence_score": 0.95, "source_file": "docs/superpowers/plans/2026-05-02-phase1-domain-grid-movement.md", "source_location": None, "weight": 1.0},
    {"source": "phase2_plan_phase2", "target": "design_spec_dungeon_card_roguelike", "relation": "references", "confidence": "INFERRED", "confidence_score": 0.95, "source_file": "docs/superpowers/plans/2026-05-04-phase2-card-system.md", "source_location": None, "weight": 1.0},
    {"source": "phase2_plan_phase2", "target": "phase1_plan_phase1", "relation": "references", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "docs/superpowers/plans/2026-05-04-phase2-card-system.md", "source_location": None, "weight": 1.0},
    {"source": "design_spec_dungeon_card_roguelike", "target": "design_principle_domain_isolation", "relation": "rationale_for", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "docs/superpowers/specs/2026-05-02-dungeon-card-roguelike-design.md", "source_location": None, "weight": 1.0},
    {"source": "design_spec_dungeon_card_roguelike", "target": "design_principle_unidirectional_event_flow", "relation": "rationale_for", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "docs/superpowers/specs/2026-05-02-dungeon-card-roguelike-design.md", "source_location": None, "weight": 1.0},
    {"source": "design_spec_dungeon_card_roguelike", "target": "design_principle_use_case_controllers", "relation": "rationale_for", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "docs/superpowers/specs/2026-05-02-dungeon-card-roguelike-design.md", "source_location": None, "weight": 1.0},
    {"source": "design_spec_dungeon_card_roguelike", "target": "design_decision_move_card_required", "relation": "rationale_for", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "docs/superpowers/specs/2026-05-02-dungeon-card-roguelike-design.md", "source_location": None, "weight": 1.0},
    {"source": "design_spec_dungeon_card_roguelike", "target": "design_decision_ap_refresh_each_turn", "relation": "rationale_for", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "docs/superpowers/specs/2026-05-02-dungeon-card-roguelike-design.md", "source_location": None, "weight": 1.0},
    {"source": "design_spec_dungeon_card_roguelike", "target": "design_decision_fusion_2for1", "relation": "rationale_for", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "docs/superpowers/specs/2026-05-02-dungeon-card-roguelike-design.md", "source_location": None, "weight": 1.0},
    {"source": "design_spec_dungeon_card_roguelike", "target": "design_decision_4x4_grid", "relation": "rationale_for", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "docs/superpowers/specs/2026-05-02-dungeon-card-roguelike-design.md", "source_location": None, "weight": 1.0},
    {"source": "design_spec_dungeon_card_roguelike", "target": "concept_card_economy", "relation": "rationale_for", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "docs/superpowers/specs/2026-05-02-dungeon-card-roguelike-design.md", "source_location": None, "weight": 1.0},
    {"source": "design_decision_fusion_2for1", "target": "concept_card_economy", "relation": "conceptually_related_to", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "docs/superpowers/specs/2026-05-02-dungeon-card-roguelike-design.md", "source_location": None, "weight": 1.0},
    {"source": "phase2_plan_phase2", "target": "phase2_concept_card_tag", "relation": "references", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "docs/superpowers/plans/2026-05-04-phase2-card-system.md", "source_location": None, "weight": 1.0},
    {"source": "phase2_plan_phase2", "target": "phase2_concept_deck_manager", "relation": "references", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "docs/superpowers/plans/2026-05-04-phase2-card-system.md", "source_location": None, "weight": 1.0},
    {"source": "phase2_plan_phase2", "target": "phase2_concept_hand_renderer", "relation": "references", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "docs/superpowers/plans/2026-05-04-phase2-card-system.md", "source_location": None, "weight": 1.0},
    {"source": "phase2_plan_phase2", "target": "phase2_concept_card_repository", "relation": "references", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "docs/superpowers/plans/2026-05-04-phase2-card-system.md", "source_location": None, "weight": 1.0},
    {"source": "phase2_plan_phase2", "target": "phase2_concept_play_card_use_case", "relation": "references", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "docs/superpowers/plans/2026-05-04-phase2-card-system.md", "source_location": None, "weight": 1.0},
    {"source": "phase2_plan_phase2", "target": "phase2_concept_draw_cards_use_case", "relation": "references", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "docs/superpowers/plans/2026-05-04-phase2-card-system.md", "source_location": None, "weight": 1.0},
    {"source": "phase2_plan_phase2", "target": "design_decision_move_card_required", "relation": "references", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "docs/superpowers/plans/2026-05-04-phase2-card-system.md", "source_location": None, "weight": 1.0},
    {"source": "phase2_concept_deck_manager", "target": "phase2_concept_draw_cards_use_case", "relation": "conceptually_related_to", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "docs/superpowers/plans/2026-05-04-phase2-card-system.md", "source_location": None, "weight": 1.0},
    {"source": "phase2_concept_hand_renderer", "target": "phase2_concept_play_card_use_case", "relation": "conceptually_related_to", "confidence": "INFERRED", "confidence_score": 0.95, "source_file": "docs/superpowers/plans/2026-05-04-phase2-card-system.md", "source_location": None, "weight": 1.0},
    {"source": "phase2_concept_card_repository", "target": "phase2_concept_card_tag", "relation": "shares_data_with", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "docs/superpowers/plans/2026-05-04-phase2-card-system.md", "source_location": None, "weight": 1.0},
    {"source": "test_move_entity_test_move_entity", "target": "phase2_plan_phase2", "relation": "references", "confidence": "INFERRED", "confidence_score": 0.85, "source_file": "tests/use_cases/test_move_entity.py", "source_location": None, "weight": 1.0},
    {"source": "test_start_battle_test_start_battle", "target": "phase2_plan_phase2", "relation": "references", "confidence": "INFERRED", "confidence_score": 0.85, "source_file": "tests/use_cases/test_start_battle.py", "source_location": None, "weight": 1.0},
    {"source": "phase1_plan_phase1", "target": "test_player_test_player", "relation": "references", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "docs/superpowers/plans/2026-05-02-phase1-domain-grid-movement.md", "source_location": None, "weight": 1.0},
    {"source": "phase1_plan_phase1", "target": "test_position_test_position", "relation": "references", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "docs/superpowers/plans/2026-05-02-phase1-domain-grid-movement.md", "source_location": None, "weight": 1.0},
    {"source": "phase1_plan_phase1", "target": "test_battle_repository_test_battle_repository", "relation": "references", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "docs/superpowers/plans/2026-05-02-phase1-domain-grid-movement.md", "source_location": None, "weight": 1.0},
    {"source": "phase1_plan_phase1", "target": "test_move_entity_test_move_entity", "relation": "references", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "docs/superpowers/plans/2026-05-02-phase1-domain-grid-movement.md", "source_location": None, "weight": 1.0},
    {"source": "phase1_plan_phase1", "target": "test_start_battle_test_start_battle", "relation": "references", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "docs/superpowers/plans/2026-05-02-phase1-domain-grid-movement.md", "source_location": None, "weight": 1.0},
    {"source": "phase1_plan_phase1", "target": "requirements_requirements", "relation": "references", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "docs/superpowers/plans/2026-05-02-phase1-domain-grid-movement.md", "source_location": None, "weight": 1.0},
    {"source": "design_principle_use_case_controllers", "target": "design_principle_domain_isolation", "relation": "conceptually_related_to", "confidence": "INFERRED", "confidence_score": 0.85, "source_file": "docs/superpowers/specs/2026-05-02-dungeon-card-roguelike-design.md", "source_location": None, "weight": 1.0},
    {"source": "design_principle_unidirectional_event_flow", "target": "design_principle_use_case_controllers", "relation": "conceptually_related_to", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "docs/superpowers/specs/2026-05-02-dungeon-card-roguelike-design.md", "source_location": None, "weight": 1.0}
  ],
  "hyperedges": [
    {
      "id": "hyperedge_tdd_workflow",
      "label": "TDD Workflow: Plan specifies test, test verifies implementation, plan references test file",
      "nodes": ["phase1_plan_phase1", "test_player_test_player", "test_move_entity_test_move_entity", "test_start_battle_test_start_battle", "test_battle_repository_test_battle_repository", "test_position_test_position"],
      "relation": "conceptually_related_to",
      "confidence": "INFERRED",
      "confidence_score": 0.95,
      "source_file": "docs/superpowers/plans/2026-05-02-phase1-domain-grid-movement.md"
    },
    {
      "id": "hyperedge_architecture_principles",
      "label": "Layered Architecture Principles: domain isolation + use-case controllers + unidirectional events",
      "nodes": ["design_principle_domain_isolation", "design_principle_use_case_controllers", "design_principle_unidirectional_event_flow"],
      "relation": "conceptually_related_to",
      "confidence": "EXTRACTED",
      "confidence_score": 1.0,
      "source_file": "docs/superpowers/specs/2026-05-02-dungeon-card-roguelike-design.md"
    },
    {
      "id": "hyperedge_card_system_phase2",
      "label": "Card System (Phase 2): CardTag + DeckManager + CardRepository + DrawCards + PlayCard",
      "nodes": ["phase2_concept_card_tag", "phase2_concept_deck_manager", "phase2_concept_card_repository", "phase2_concept_draw_cards_use_case", "phase2_concept_play_card_use_case"],
      "relation": "conceptually_related_to",
      "confidence": "EXTRACTED",
      "confidence_score": 1.0,
      "source_file": "docs/superpowers/plans/2026-05-04-phase2-card-system.md"
    }
  ],
  "input_tokens": 4200,
  "output_tokens": 1100
}

out = pathlib.Path("E:/Coding/pygame/graphify-out/.graphify_chunk_03.json")
out.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
print("Written:", out)
print("Nodes:", len(data["nodes"]), "Edges:", len(data["edges"]), "Hyperedges:", len(data["hyperedges"]))
