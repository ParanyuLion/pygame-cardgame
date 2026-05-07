from __future__ import annotations
from typing import TYPE_CHECKING
from src.domain.events.battle_events import BattleEnded
from src.use_cases.start_run import StartRunUseCase
from src.use_cases.start_battle import StartBattleUseCase, Encounter, EnemyDef
from src.domain.value_objects.position import Position
from src.presentation.scenes.menu_scene import MenuScene
from src.presentation.scenes.reward_scene import RewardScene
from src.presentation.scenes.map_scene import MapScene
from src.presentation.scenes.battle_scene import BattleScene

if TYPE_CHECKING:
    from src.domain.interfaces import IBattleRepository, IEventBus, ICardRepository, IRunRepository
    from src.presentation.game_state_manager import GameStateManager
    from src.domain.entities.card import Card
    from src.domain.run_state import MapNode


class GameController:
    def __init__(
        self,
        gsm: GameStateManager,
        run_repo: IRunRepository,
        battle_repo: IBattleRepository,
        event_bus: IEventBus,
        card_repo: ICardRepository,
    ) -> None:
        self._gsm = gsm
        self._run_repo = run_repo
        self._battle_repo = battle_repo
        self._event_bus = event_bus
        self._card_repo = card_repo
        event_bus.subscribe(BattleEnded, self._on_battle_ended)

    def start_new_run(self) -> None:
        StartRunUseCase(self._run_repo, self._card_repo).execute()
        self._start_current_node_battle()

    def _start_current_node_battle(self) -> None:
        run = self._run_repo.get()
        node = run.current_node()
        enemies = [
            EnemyDef(id=s.id, position=s.position, hp=s.hp, base_damage=s.base_damage)
            for s in node.enemies
        ]
        encounter = Encounter(
            player_start=Position(0, 0),
            enemies=enemies,
            player_hp=run.player_hp,
            deck=list(run.deck),
        )
        StartBattleUseCase(self._battle_repo, self._event_bus, self._card_repo).execute(encounter)
        self._gsm.transition_to(BattleScene(self._battle_repo, self._event_bus))

    def _on_battle_ended(self, event: BattleEnded) -> None:
        if event.outcome == "victory":
            self._handle_victory()
        else:
            self._handle_defeat()

    def _handle_victory(self) -> None:
        run = self._run_repo.get()
        run.player_hp = self._battle_repo.get().player.hp
        run.advance_node()

        if run.is_floor_complete():
            if run.floor == len(run.floors):
                run.run_complete = True
                self._run_repo.save(run)
                self._gsm.transition_to(MenuScene(on_start_run=self.start_new_run))
                return
            run.advance_floor()

        self._run_repo.save(run)
        reward_cards = self._card_repo.get_random_cards(3)

        def _on_card_chosen(card: Card) -> None:
            r = self._run_repo.get()
            r.deck.append(card)
            self._run_repo.save(r)
            self._gsm.transition_to(MapScene(
                run_repo=self._run_repo,
                on_node_selected=lambda _node: self._start_current_node_battle(),
            ))

        self._gsm.transition_to(RewardScene(choices=reward_cards, on_card_chosen=_on_card_chosen))

    def _handle_defeat(self) -> None:
        self._gsm.transition_to(MenuScene(on_start_run=self.start_new_run))
