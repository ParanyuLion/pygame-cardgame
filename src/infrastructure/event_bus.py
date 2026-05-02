from __future__ import annotations
from collections import defaultdict
from typing import Callable
from src.domain.events.base import DomainEvent

class PygameEventBus:
    def __init__(self) -> None:
        self._handlers: dict[type, list[Callable]] = defaultdict(list)

    def publish(self, event: DomainEvent) -> None:
        for handler in list(self._handlers[type(event)]):
            handler(event)

    def subscribe(self, event_type: type, handler: Callable) -> None:
        self._handlers[event_type].append(handler)

    def unsubscribe(self, event_type: type, handler: Callable) -> None:
        try:
            self._handlers[event_type].remove(handler)
        except ValueError:
            pass
