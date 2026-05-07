from unittest.mock import MagicMock
from src.domain.battle_state import BattleState
from src.domain.entities.grid import Grid
from src.domain.entities.player import Player
from src.domain.entities.enemy import Enemy
from src.domain.entities.card import Card
from src.domain.value_objects.position import Position
from src.domain.value_objects.intent import Intent
from src.domain.value_objects.attack_pattern import AttackPattern
from src.domain.value_objects.card_tag import CardTag
from src.domain.events.battle_events import (
    BattleTurnStarted, IntentBroadcast, DamageTaken, BattleEnded, CardDrawn,
)
from src.use_cases.end_turn import EndTurnUseCase


def _intent(countdown: int = 2, damage: int = 5) -> Intent:
    return Intent(type="ATTACK", pattern=AttackPattern.cross(), countdown=countdown, damage=damage)


def _enemy(
    id: str = "e1",
    pos: Position = Position(3, 3),
    hp: int = 20,
    countdown: int = 2,
) -> Enemy:
    return Enemy(id=id, position=pos, hp=hp, max_hp=20, base_damage=5, intent=_intent(countdown=countdown))


def _player(pos: Position = Position(0, 0), hp: int = 30, ap: int = 0) -> Player:
    return Player(id="player", position=pos, hp=hp, max_hp=30, ap=ap, max_ap=3)


def _card(id: str) -> Card:
    return Card(
        id=id, name=id, tags=[CardTag("Blade")], ap_cost=1,
        pattern=AttackPattern.single(), damage=0,
    )


def _make_state(
    player: Player | None = None,
    enemies: list[Enemy] | None = None,
    hand: list[Card] | None = None,
    deck: list[Card] | None = None,
) -> BattleState:
    grid = Grid()
    p = player or _player()
    grid.place("player", p.position)
    state = BattleState(player=p, grid=grid)
    state.enemies = enemies or []
    state.hand = hand or []
    state.deck = deck or []
    for e in state.enemies:
        grid.place(e.id, e.position)
    return state


def _make_use_case(state: BattleState) -> tuple[EndTurnUseCase, MagicMock]:
    repo = MagicMock()
    repo.get.return_value = state
    bus = MagicMock()
    return EndTurnUseCase(repo, bus), bus


def _published_events(bus: MagicMock) -> list:
    return [call[0][0] for call in bus.publish.call_args_list]


def test_end_turn_publishes_battle_turn_started():
    state = _make_state()
    use_case, bus = _make_use_case(state)
    use_case.execute()
    assert any(isinstance(e, BattleTurnStarted) for e in _published_events(bus))


def test_end_turn_refreshes_player_ap():
    state = _make_state(player=_player(ap=0))
    use_case, bus = _make_use_case(state)
    use_case.execute()
    assert state.player.ap == 3


def test_end_turn_increments_turn_number():
    state = _make_state()
    state.turn_number = 1
    use_case, bus = _make_use_case(state)
    use_case.execute()
    assert state.turn_number == 2


def test_end_turn_enemy_countdown_decrements():
    enemy = _enemy(countdown=2)
    state = _make_state(enemies=[enemy])
    use_case, bus = _make_use_case(state)
    use_case.execute()
    assert state.enemies[0].intent.countdown == 1


def test_end_turn_publishes_intent_broadcast_per_enemy():
    enemy = _enemy()
    state = _make_state(enemies=[enemy])
    use_case, bus = _make_use_case(state)
    use_case.execute()
    events = _published_events(bus)
    assert any(isinstance(e, IntentBroadcast) and e.enemy_id == "e1" for e in events)


def test_end_turn_enemy_attacks_player_when_in_cross_pattern():
    # Enemy at (2,2); cross() offset (0,-1) → target (2,1); player at (2,1)
    enemy = _enemy(pos=Position(2, 2), countdown=1)
    player = _player(pos=Position(2, 1), hp=30)
    state = _make_state(player=player, enemies=[enemy])
    use_case, bus = _make_use_case(state)
    use_case.execute()
    events = _published_events(bus)
    assert any(isinstance(e, DamageTaken) and e.entity_id == "player" for e in events)
    assert state.player.hp == 25  # 30 - 5


def test_end_turn_no_damage_when_player_outside_pattern():
    # Enemy at (3,3); cross targets (3,3),(2,3),(3,2) etc. Player at (0,0) — not in pattern
    enemy = _enemy(pos=Position(3, 3), countdown=1)
    player = _player(pos=Position(0, 0), hp=30)
    state = _make_state(player=player, enemies=[enemy])
    use_case, bus = _make_use_case(state)
    use_case.execute()
    assert state.player.hp == 30


def test_end_turn_after_attack_enemy_gets_fresh_intent():
    enemy = _enemy(pos=Position(2, 2), countdown=1)
    state = _make_state(enemies=[enemy])
    use_case, bus = _make_use_case(state)
    use_case.execute()
    assert state.enemies[0].intent.countdown == 2  # fresh intent chosen


def test_end_turn_draws_cards_to_fill_hand():
    deck_card = _card("c1")
    state = _make_state(deck=[deck_card])
    state.hand = []
    use_case, bus = _make_use_case(state)
    use_case.execute()
    assert deck_card in state.hand


def test_end_turn_publishes_card_drawn():
    deck_card = _card("c1")
    state = _make_state(deck=[deck_card])
    state.hand = []
    use_case, bus = _make_use_case(state)
    use_case.execute()
    events = _published_events(bus)
    assert any(isinstance(e, CardDrawn) and e.card_id == "c1" for e in events)


def test_end_turn_publishes_battle_ended_defeat_when_player_killed():
    # Enemy at (2,2) with lethal damage; player at (2,1) — in cross pattern
    enemy = _enemy(pos=Position(2, 2), countdown=1)
    enemy.intent = Intent(type="ATTACK", pattern=AttackPattern.cross(), countdown=1, damage=30)
    player = _player(pos=Position(2, 1), hp=30)
    state = _make_state(player=player, enemies=[enemy])
    use_case, bus = _make_use_case(state)
    use_case.execute()
    events = _published_events(bus)
    assert any(isinstance(e, BattleEnded) and e.outcome == "defeat" for e in events)


def test_end_turn_enemies_act_in_lowest_hp_first_order():
    e1 = Enemy(id="e1", position=Position(0, 1), hp=15, max_hp=20, base_damage=5, intent=_intent())
    e2 = Enemy(id="e2", position=Position(0, 2), hp=5, max_hp=20, base_damage=5, intent=_intent())
    state = _make_state(enemies=[e1, e2])
    use_case, bus = _make_use_case(state)
    use_case.execute()
    broadcasts = [e for e in _published_events(bus) if isinstance(e, IntentBroadcast)]
    ids = [e.enemy_id for e in broadcasts]
    assert ids == ["e2", "e1"]  # e2 lower HP → acts first


def test_end_turn_does_nothing_if_player_already_dead():
    state = _make_state(player=_player(hp=0))
    repo = MagicMock()
    repo.get.return_value = state
    bus = MagicMock()
    use_case = EndTurnUseCase(repo, bus)
    use_case.execute()
    bus.publish.assert_not_called()
    repo.save.assert_not_called()
