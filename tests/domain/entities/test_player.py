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
