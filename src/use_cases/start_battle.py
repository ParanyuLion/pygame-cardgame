import random
from dataclasses import dataclass, field
from src.domain.interfaces import IBattleRepository, IEventBus, ICardRepository
from src.domain.battle_state import BattleState
from src.domain.entities.player import Player
from src.domain.entities.enemy import Enemy
from src.domain.entities.grid import Grid
from src.domain.value_objects.intent import Intent
from src.domain.value_objects.attack_pattern import AttackPattern
from src.domain.value_objects.position import Position
from src.domain.events.battle_events import BattleTurnStarted
from src.domain.services.deck_manager import DeckManager

PLAYER_MAX_HP = 30
PLAYER_MAX_AP = 3
OPENING_HAND_SIZE = 5


@dataclass
class EnemyDef:
    id: str
    position: Position
    hp: int
    base_damage: int


@dataclass
class Encounter:
    player_start: Position
    enemies: list[EnemyDef] = field(default_factory=list)


class StartBattleUseCase:
    def __init__(
        self,
        battle_repo: IBattleRepository,
        event_bus: IEventBus,
        card_repo: ICardRepository,
    ) -> None:
        self._repo = battle_repo
        self._bus = event_bus
        self._card_repo = card_repo

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

        enemies: list[Enemy] = []
        for enemy_def in encounter.enemies:
            initial_intent = Intent(
                type="ATTACK",
                pattern=AttackPattern.cross(),
                countdown=2,
                damage=enemy_def.base_damage,
            )
            enemy = Enemy(
                id=enemy_def.id,
                position=enemy_def.position,
                hp=enemy_def.hp,
                max_hp=enemy_def.hp,
                base_damage=enemy_def.base_damage,
                intent=initial_intent,
            )
            grid.place(enemy.id, enemy.position)
            enemies.append(enemy)

        deck = self._card_repo.get_starting_deck()
        random.shuffle(deck)

        state = BattleState(player=player, grid=grid, deck=deck, enemies=enemies)

        draw_events = []
        for _ in range(OPENING_HAND_SIZE):
            event = DeckManager.draw(state.deck, state.hand, state.discard)
            if event is None:
                break
            draw_events.append(event)

        self._repo.save(state)
        self._bus.publish(BattleTurnStarted(turn_number=1, ap_refreshed=PLAYER_MAX_AP))
        for event in draw_events:
            self._bus.publish(event)
