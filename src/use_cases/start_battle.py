from __future__ import annotations

import random
from dataclasses import dataclass, field
from src.domain.interfaces import IBattleRepository, IEventBus, ICardRepository
from src.domain.battle_state import BattleState
from src.domain.entities.card import Card
from src.domain.entities.player import Player
from src.domain.entities.enemy import Enemy
from src.domain.entities.grid import Grid
from src.domain.value_objects.intent import Intent
from src.domain.value_objects.attack_pattern import AttackPattern
from src.domain.value_objects.grid_snapshot import GridSnapshot
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
    player_hp: int | None = None    # None → use PLAYER_MAX_HP
    deck: list[Card] | None = None  # None → use card_repo.get_starting_deck()


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
            hp=encounter.player_hp if encounter.player_hp is not None else PLAYER_MAX_HP,
            max_hp=PLAYER_MAX_HP,
            ap=PLAYER_MAX_AP,
            max_ap=PLAYER_MAX_AP,
        )
        grid.place("player", encounter.player_start)

        enemies: list[Enemy] = []
        for enemy_def in encounter.enemies:
            enemy = Enemy(
                id=enemy_def.id,
                position=enemy_def.position,
                hp=enemy_def.hp,
                max_hp=enemy_def.hp,
                base_damage=enemy_def.base_damage,
                intent=Intent(type="MOVE", pattern=AttackPattern.single(), countdown=1, damage=0),
            )
            grid.place(enemy.id, enemy.position)
            enemies.append(enemy)

        snapshot = GridSnapshot(
            positions={e.id: e.position for e in enemies} | {"player": encounter.player_start},
            hp={e.id: e.hp for e in enemies} | {"player": player.hp},
        )
        for enemy in enemies:
            enemy.intent = enemy.choose_intent(snapshot)

        deck = list(encounter.deck) if encounter.deck is not None else self._card_repo.get_starting_deck()
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
