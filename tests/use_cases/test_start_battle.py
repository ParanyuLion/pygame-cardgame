# tests/use_cases/test_start_battle.py
import pytest
from unittest.mock import MagicMock
from src.infrastructure.battle_repository import InMemoryBattleRepository
from src.use_cases.start_battle import StartBattleUseCase, Encounter, EnemyDef
from src.domain.value_objects.position import Position
from src.domain.value_objects.card_tag import CardTag
from src.domain.value_objects.attack_pattern import AttackPattern
from src.domain.entities.card import Card
from src.domain.entities.enemy import Enemy
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


# --- Enemy placement tests ---

def _make_use_case_mock() -> tuple[StartBattleUseCase, MagicMock]:
    battle_repo = MagicMock()
    event_bus = MagicMock()
    card_repo = MagicMock()
    card_repo.get_starting_deck.return_value = []
    use_case = StartBattleUseCase(battle_repo, event_bus, card_repo)
    return use_case, battle_repo


def test_start_battle_no_enemies_leaves_enemies_list_empty():
    use_case, repo = _make_use_case_mock()
    use_case.execute(Encounter(player_start=Position(0, 0)))
    state = repo.save.call_args[0][0]
    assert state.enemies == []


def test_start_battle_places_enemy_on_grid():
    use_case, repo = _make_use_case_mock()
    use_case.execute(Encounter(
        player_start=Position(0, 0),
        enemies=[EnemyDef(id="e1", position=Position(3, 3), hp=20, base_damage=4)],
    ))
    state = repo.save.call_args[0][0]
    assert len(state.enemies) == 1
    assert isinstance(state.enemies[0], Enemy)
    assert state.enemies[0].id == "e1"
    assert state.grid.is_occupied(Position(3, 3))


def test_start_battle_enemy_initial_intent_is_attack_countdown_two():
    use_case, repo = _make_use_case_mock()
    use_case.execute(Encounter(
        player_start=Position(0, 0),
        enemies=[EnemyDef(id="e1", position=Position(3, 3), hp=20, base_damage=5)],
    ))
    state = repo.save.call_args[0][0]
    intent = state.enemies[0].intent
    assert intent.type == "ATTACK"
    assert intent.countdown == 2
    assert intent.damage == 5
