from __future__ import annotations
from unittest.mock import MagicMock, call
from src.domain.events.battle_events import BattleEnded
from src.presentation.game_controller import GameController
from src.presentation.scenes.menu_scene import MenuScene
from src.presentation.scenes.reward_scene import RewardScene


def _make_controller():
    gsm = MagicMock()
    run_repo = MagicMock()
    battle_repo = MagicMock()
    event_bus = MagicMock()
    card_repo = MagicMock()

    # Capture subscriber so we can fire events directly
    subscribers = {}
    def subscribe(event_type, handler):
        subscribers[event_type] = handler
    event_bus.subscribe.side_effect = subscribe

    ctrl = GameController(gsm, run_repo, battle_repo, event_bus, card_repo)
    # Register handler directly — in production this happens via _start_current_node_battle
    subscribers[BattleEnded] = ctrl._on_battle_ended
    return ctrl, gsm, run_repo, battle_repo, card_repo, subscribers


def test_defeat_transitions_to_menu_scene():
    ctrl, gsm, _, _, _, subscribers = _make_controller()
    subscribers[BattleEnded](BattleEnded(outcome="defeat"))
    gsm.transition_to.assert_called_once()
    scene = gsm.transition_to.call_args[0][0]
    assert isinstance(scene, MenuScene)


def test_victory_transitions_to_reward_scene():
    ctrl, gsm, run_repo, battle_repo, card_repo, subscribers = _make_controller()

    # Set up run state: 1 node on floor 1, not yet complete
    from src.domain.run_state import RunState, MapNode
    node = MapNode(id="n1", node_type="combat", enemies=[])
    run = RunState(deck=[], player_hp=30, player_max_hp=30, floor=1,
                   floors=[[node], [MapNode(id="n2", node_type="combat", enemies=[])], [MapNode(id="n3", node_type="combat", enemies=[])]])
    run_repo.get.return_value = run

    from src.domain.entities.player import Player
    from src.domain.entities.grid import Grid
    from src.domain.battle_state import BattleState
    from src.domain.value_objects.position import Position
    player = Player(id="player", position=Position(0, 0), hp=20, max_hp=30, ap=3, max_ap=3)
    battle_state = BattleState(player=player, grid=Grid())
    battle_repo.get.return_value = battle_state

    card_repo.get_random_cards.return_value = []

    subscribers[BattleEnded](BattleEnded(outcome="victory"))
    gsm.transition_to.assert_called_once()
    scene = gsm.transition_to.call_args[0][0]
    assert isinstance(scene, RewardScene)


def test_victory_persists_player_hp_to_run_state():
    ctrl, gsm, run_repo, battle_repo, card_repo, subscribers = _make_controller()

    from src.domain.run_state import RunState, MapNode
    node = MapNode(id="n1", node_type="combat", enemies=[])
    run = RunState(deck=[], player_hp=30, player_max_hp=30, floor=1,
                   floors=[[node], [MapNode(id="n2", node_type="combat", enemies=[])], [MapNode(id="n3", node_type="combat", enemies=[])]])
    run_repo.get.return_value = run

    from src.domain.entities.player import Player
    from src.domain.entities.grid import Grid
    from src.domain.battle_state import BattleState
    from src.domain.value_objects.position import Position
    player = Player(id="player", position=Position(0, 0), hp=17, max_hp=30, ap=3, max_ap=3)
    battle_repo.get.return_value = BattleState(player=player, grid=Grid())
    card_repo.get_random_cards.return_value = []

    subscribers[BattleEnded](BattleEnded(outcome="victory"))
    assert run.player_hp == 17


def test_floor3_complete_transitions_to_menu_scene():
    ctrl, gsm, run_repo, battle_repo, card_repo, subscribers = _make_controller()

    from src.domain.run_state import RunState, MapNode
    # Floor 3, one node, not yet complete
    node = MapNode(id="f3_boss", node_type="boss", enemies=[])
    run = RunState(
        deck=[], player_hp=30, player_max_hp=30, floor=3,
        floors=[
            [MapNode(id="f1", node_type="combat", enemies=[])],
            [MapNode(id="f2", node_type="combat", enemies=[])],
            [node],
        ],
    )
    run_repo.get.return_value = run

    from src.domain.entities.player import Player
    from src.domain.entities.grid import Grid
    from src.domain.battle_state import BattleState
    from src.domain.value_objects.position import Position
    player = Player(id="player", position=Position(0, 0), hp=10, max_hp=30, ap=3, max_ap=3)
    battle_repo.get.return_value = BattleState(player=player, grid=Grid())

    subscribers[BattleEnded](BattleEnded(outcome="victory"))
    gsm.transition_to.assert_called_once()
    scene = gsm.transition_to.call_args[0][0]
    assert isinstance(scene, MenuScene)
    assert run.run_complete is True


def test_choosing_reward_card_appends_to_deck_and_shows_map():
    ctrl, gsm, run_repo, battle_repo, card_repo, subscribers = _make_controller()

    from src.domain.run_state import RunState, MapNode
    from src.domain.entities.card import Card
    from src.domain.value_objects.card_tag import CardTag
    from src.domain.value_objects.attack_pattern import AttackPattern

    node = MapNode(id="n1", node_type="combat", enemies=[])
    run = RunState(
        deck=[], player_hp=30, player_max_hp=30, floor=1,
        floors=[[node], [MapNode(id="n2", node_type="combat", enemies=[])], [MapNode(id="n3", node_type="combat", enemies=[])]],
    )
    run_repo.get.return_value = run

    from src.domain.entities.player import Player
    from src.domain.entities.grid import Grid
    from src.domain.battle_state import BattleState
    from src.domain.value_objects.position import Position
    player = Player(id="player", position=Position(0, 0), hp=25, max_hp=30, ap=3, max_ap=3)
    battle_repo.get.return_value = BattleState(player=player, grid=Grid())

    reward_card = Card(id="reward_1", name="Reward", tags=[CardTag("Blade")],
                       ap_cost=1, pattern=AttackPattern.single(), damage=3)
    card_repo.get_random_cards.return_value = [reward_card]

    subscribers[BattleEnded](BattleEnded(outcome="victory"))

    # The RewardScene was shown — extract its on_card_chosen callback and invoke it
    from src.presentation.scenes.reward_scene import RewardScene
    reward_scene = gsm.transition_to.call_args[0][0]
    assert isinstance(reward_scene, RewardScene)
    reward_scene._on_card_chosen(reward_card)

    # Card should be in the deck
    assert reward_card in run.deck

    # Next transition should be to MapScene
    from src.presentation.scenes.map_scene import MapScene
    map_scene = gsm.transition_to.call_args[0][0]
    assert isinstance(map_scene, MapScene)


def test_victory_on_last_floor1_node_advances_to_floor2():
    ctrl, gsm, run_repo, battle_repo, card_repo, subscribers = _make_controller()

    from src.domain.run_state import RunState, MapNode
    node = MapNode(id="n1", node_type="boss", enemies=[])
    run = RunState(
        deck=[], player_hp=30, player_max_hp=30, floor=1,
        floors=[
            [node],  # floor 1 has only 1 node (boss)
            [MapNode(id="n2", node_type="combat", enemies=[])],
            [MapNode(id="n3", node_type="combat", enemies=[])],
        ],
    )
    run_repo.get.return_value = run

    from src.domain.entities.player import Player
    from src.domain.entities.grid import Grid
    from src.domain.battle_state import BattleState
    from src.domain.value_objects.position import Position
    player = Player(id="player", position=Position(0, 0), hp=20, max_hp=30, ap=3, max_ap=3)
    battle_repo.get.return_value = BattleState(player=player, grid=Grid())
    card_repo.get_random_cards.return_value = []

    subscribers[BattleEnded](BattleEnded(outcome="victory"))
    assert run.floor == 2
    assert run.node_idx == 0
