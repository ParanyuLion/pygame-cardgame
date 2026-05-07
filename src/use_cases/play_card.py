from src.domain.interfaces import IBattleRepository, IEventBus
from src.domain.entities.card import CardContext
from src.domain.events.battle_events import CardPlayed, CardDrawn
from src.domain.services.deck_manager import DeckManager

class PlayCardUseCase:
    def __init__(self, battle_repo: IBattleRepository, event_bus: IEventBus) -> None:
        self._repo = battle_repo
        self._bus = event_bus

    def execute(self, card_id: str) -> None:
        state = self._repo.get()

        card = next((c for c in state.hand if c.id == card_id), None)
        if card is None:
            raise ValueError(f"Card '{card_id}' not in hand")

        state.player.spend_ap(card.ap_cost)
        if card.grants_ap:
            state.player.ap = min(state.player.ap + card.grants_ap, state.player.max_ap)

        targets = state.grid.get_targets(state.player.position, card.pattern)
        context = CardContext(player=state.player, targets=targets, enemies=state.enemies)
        side_events = card.apply(context)

        state.hand.remove(card)
        state.discard.append(card)

        draw_events: list[CardDrawn] = []
        for _ in range(card.draw_after_play):
            drawn = DeckManager.draw(state.deck, state.hand, state.discard)
            if drawn is not None:
                draw_events.append(drawn)

        self._repo.save(state)

        self._bus.publish(CardPlayed(
            card_id=card.id,
            player_id=state.player.id,
            targets=tuple(targets),
        ))
        for event in side_events:
            self._bus.publish(event)
        for event in draw_events:
            self._bus.publish(event)
