from src.domain.interfaces import IBattleRepository, IEventBus
from src.domain.services.deck_manager import DeckManager

class DrawCardsUseCase:
    def __init__(self, battle_repo: IBattleRepository, event_bus: IEventBus) -> None:
        self._repo = battle_repo
        self._bus = event_bus

    def execute(self, count: int) -> None:
        state = self._repo.get()
        events = []
        for _ in range(count):
            event = DeckManager.draw(state.deck, state.hand, state.discard)
            if event is None:
                break
            events.append(event)
        self._repo.save(state)
        for event in events:
            self._bus.publish(event)
