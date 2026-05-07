from __future__ import annotations
import random
from src.domain.entities.card import Card
from src.domain.events.battle_events import CardDrawn


class DeckManager:
    @staticmethod
    def draw(
        deck: list[Card],
        hand: list[Card],
        discard: list[Card],
    ) -> CardDrawn | None:
        if not deck and not discard:
            return None
        if not deck:
            shuffled = list(discard)
            random.shuffle(shuffled)
            deck[:] = shuffled
            discard.clear()
        card = deck.pop(0)
        hand.append(card)
        return CardDrawn(card_id=card.id)
