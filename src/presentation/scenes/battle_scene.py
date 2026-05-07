from __future__ import annotations
import pygame
from src.domain.interfaces import IBattleRepository, IEventBus
from src.use_cases.move_entity import MoveEntityUseCase
from src.use_cases.play_card import PlayCardUseCase
from src.use_cases.fuse_cards import FuseCardsUseCase
from src.use_cases.end_turn import EndTurnUseCase
from src.presentation.renderers.grid_renderer import GridRenderer
from src.presentation.renderers.entity_renderer import EntityRenderer
from src.presentation.renderers.hand_renderer import HandRenderer
from src.presentation.renderers.enemy_renderer import EnemyRenderer
from src.presentation.renderers.intent_renderer import IntentRenderer
from src.presentation.input_handler import InputHandler

COLOR_BG = (10, 8, 6)


class BattleScene:
    def __init__(
        self,
        battle_repo: IBattleRepository,
        event_bus: IEventBus,
    ) -> None:
        self._repo = battle_repo
        move_use_case = MoveEntityUseCase(battle_repo, event_bus)
        play_use_case = PlayCardUseCase(battle_repo, event_bus)
        fuse_use_case = FuseCardsUseCase(battle_repo, event_bus)
        end_turn_use_case = EndTurnUseCase(battle_repo, event_bus)
        self._grid_renderer = GridRenderer()
        self._entity_renderer = EntityRenderer(self._grid_renderer)
        self._hand_renderer = HandRenderer()
        self._enemy_renderer = EnemyRenderer(self._grid_renderer)
        self._intent_renderer = IntentRenderer(self._grid_renderer)
        self._input_handler = InputHandler(
            move_use_case,
            play_use_case,
            fuse_use_case,
            end_turn_use_case,
            battle_repo,
            self._hand_renderer,
            self._grid_renderer,
        )

    def on_enter(self) -> None:
        pass

    def on_exit(self) -> None:
        pass

    def handle_event(self, event: pygame.event.Event) -> None:
        self._input_handler.handle_event(event)

    def update(self, dt: float) -> None:
        state = self._repo.get()
        self._entity_renderer.update(dt, state.player)

    def render(self, surface: pygame.Surface) -> None:
        state = self._repo.get()
        self._grid_renderer.render(surface, state.grid)
        self._intent_renderer.render(surface, state.enemies, state.grid)
        self._entity_renderer.render(surface, state.player)
        self._enemy_renderer.render(surface, state.enemies)
        self._hand_renderer.render(surface, state.hand)
