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
