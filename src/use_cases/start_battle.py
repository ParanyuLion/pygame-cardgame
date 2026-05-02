from dataclasses import dataclass
from src.domain.interfaces import IBattleRepository, IEventBus
from src.domain.battle_state import BattleState
from src.domain.entities.player import Player
from src.domain.entities.grid import Grid
from src.domain.value_objects.position import Position
from src.domain.events.battle_events import BattleTurnStarted

PLAYER_MAX_HP = 30
PLAYER_MAX_AP = 3

@dataclass
class Encounter:
    player_start: Position

class StartBattleUseCase:
    def __init__(self, battle_repo: IBattleRepository, event_bus: IEventBus) -> None:
        self._repo = battle_repo
        self._bus = event_bus

    def execute(self, encounter: Encounter) -> None:
        grid = Grid()
        player = Player(
            id="player",
            position=encounter.player_start,
            hp=PLAYER_MAX_HP,
            max_hp=PLAYER_MAX_HP,
            ap=PLAYER_MAX_AP,
            max_ap=PLAYER_MAX_AP,
        )
        grid.place("player", encounter.player_start)

        state = BattleState(player=player, grid=grid)
        self._repo.save(state)
        self._bus.publish(BattleTurnStarted(turn_number=1, ap_refreshed=PLAYER_MAX_AP))
