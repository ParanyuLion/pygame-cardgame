from __future__ import annotations
import pygame
from typing import Callable
from src.presentation.renderers.menu_renderer import MenuRenderer


class MenuScene:
    def __init__(self, on_start_run: Callable[[], None]) -> None:
        self._on_start_run = on_start_run
        self._renderer = MenuRenderer()

    def on_enter(self) -> None:
        pass

    def on_exit(self) -> None:
        pass

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self._on_start_run()

    def update(self, dt: float) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        self._renderer.render(surface)
