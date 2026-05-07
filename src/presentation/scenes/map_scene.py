from __future__ import annotations
import pygame
from typing import Callable, TYPE_CHECKING
from src.presentation.renderers.map_renderer import MapRenderer

if TYPE_CHECKING:
    from src.domain.interfaces import IRunRepository
    from src.domain.run_state import MapNode


class MapScene:
    def __init__(
        self,
        run_repo: IRunRepository,
        on_node_selected: Callable[[MapNode], None],
    ) -> None:
        self._repo = run_repo
        self._on_node_selected = on_node_selected
        self._renderer = MapRenderer()

    def on_enter(self) -> None:
        pass

    def on_exit(self) -> None:
        pass

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            run = self._repo.get()
            current_idx = run.node_idx
            rect = self._renderer.node_rect(current_idx)
            if rect.collidepoint(event.pos):
                self._on_node_selected(run.current_node())

    def update(self, dt: float) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        run = self._repo.get()
        self._renderer.render(surface, run.nodes, run.node_idx, run.floor)
