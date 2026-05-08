import pytest
from src.domain.entities.enemy import Enemy
from src.domain.value_objects.intent import Intent
from src.domain.value_objects.grid_snapshot import GridSnapshot
from src.domain.value_objects.attack_pattern import AttackPattern
from src.domain.value_objects.position import Position
from src.domain.entities.player import Player
from src.domain.events.battle_events import DamageTaken


def _intent(countdown: int = 2, damage: int = 4) -> Intent:
    return Intent(type="ATTACK", pattern=AttackPattern.cross(), countdown=countdown, damage=damage)


def _enemy(id: str = "e1", hp: int = 20) -> Enemy:
    return Enemy(id=id, position=Position(3, 3), hp=hp, max_hp=20, base_damage=4, intent=_intent())


def _player() -> Player:
    return Player(id="player", position=Position(0, 0), hp=30, max_hp=30, ap=3, max_ap=3)


def test_enemy_take_damage_reduces_hp():
    e = _enemy()
    e.take_damage(5)
    assert e.hp == 15


def test_enemy_take_damage_clamps_to_zero():
    e = _enemy(hp=3)
    e.take_damage(10)
    assert e.hp == 0


def test_enemy_take_damage_returns_event():
    e = _enemy()
    event = e.take_damage(5)
    assert isinstance(event, DamageTaken)
    assert event.entity_id == "e1"
    assert event.amount == 5
    assert event.source == "player"


def test_enemy_is_alive_true_when_hp_positive():
    assert _enemy(hp=1).is_alive()


def test_enemy_is_alive_false_when_hp_zero():
    assert not _enemy(hp=0).is_alive()


def test_enemy_choose_intent_returns_attack_when_adjacent_to_player():
    e = _enemy()  # position (3,3)
    snapshot = GridSnapshot(positions={"e1": Position(3, 3), "player": Position(3, 2)}, hp={"e1": 20, "player": 30})
    intent = e.choose_intent(snapshot)
    assert intent.type == "ATTACK"
    assert intent.countdown == 2
    assert intent.damage == e.base_damage
    assert intent.pattern == AttackPattern.cross()


def test_enemy_choose_intent_returns_move_when_far_from_player():
    e = _enemy()  # position (3,3)
    snapshot = GridSnapshot(positions={"e1": Position(3, 3), "player": Position(0, 0)}, hp={"e1": 20, "player": 30})
    intent = e.choose_intent(snapshot)
    assert intent.type == "MOVE"
    assert intent.countdown == 1
    assert intent.damage == 0


def test_enemy_tick_intent_decrements_countdown_without_mutating_original():
    e = _enemy()
    original_countdown = e.intent.countdown
    new_intent = e.tick_intent()
    assert new_intent.countdown == original_countdown - 1
    assert e.intent.countdown == original_countdown  # frozen, unchanged


def test_enemy_resolve_attack_damages_player():
    e = _enemy()
    player = _player()
    event = e.resolve_attack(player)
    assert isinstance(event, DamageTaken)
    assert event.entity_id == "player"
    assert event.amount == 4
    assert player.hp == 26
