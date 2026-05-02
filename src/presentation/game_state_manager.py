from __future__ import annotations
import pygame
from typing import Protocol

class Scene(Protocol):
    def on_enter(self) -> None: ...
    def on_exit(self) -> None: ...
    def handle_event(self, event: pygame.event.Event) -> None: ...
    def update(self, dt: float) -> None: ...
    def render(self, surface: pygame.Surface) -> None: ...

class GameStateManager:
    def __init__(self, initial_scene: Scene) -> None:
        self._scene = initial_scene
        self._scene.on_enter()

    def transition_to(self, scene: Scene) -> None:
        self._scene.on_exit()
        self._scene = scene
        self._scene.on_enter()

    def handle_event(self, event: pygame.event.Event) -> None:
        self._scene.handle_event(event)

    def update(self, dt: float) -> None:
        self._scene.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        self._scene.render(surface)
