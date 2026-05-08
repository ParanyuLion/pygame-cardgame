from __future__ import annotations
from typing import TYPE_CHECKING
from src.domain.interfaces import IBattleRepository, IEventBus
from src.domain.entities.card import CardContext
from src.domain.events.battle_events import CardPlayed, CardDrawn, BattleEnded
from src.domain.services.deck_manager import DeckManager

if TYPE_CHECKING:
    from src.domain.value_objects.position import Position

class PlayCardUseCase:
    def __init__(self, battle_repo: IBattleRepository, event_bus: IEventBus) -> None:
        self._repo = battle_repo
        self._bus = event_bus

    def execute(self, card_id: str, target_pos: Position | None = None) -> None:
        state = self._repo.get()

        card = next((c for c in state.hand if c.id == card_id), None)
        if card is None:
            raise ValueError(f"Card '{card_id}' not in hand")

        if target_pos is not None:
            p = state.player.position
            if abs(target_pos.col - p.col) + abs(target_pos.row - p.row) > 1:
                raise ValueError("Target out of range")

        if card.is_move_card():
            if target_pos is None:
                raise ValueError("Move card requires a target tile")
            if not state.grid.is_passable(target_pos):
                raise ValueError("Target tile is not passable")

        state.player.spend_ap(card.ap_cost)
        if card.grants_ap:
            state.player.ap = min(state.player.ap + card.grants_ap, state.player.max_ap)

        if card.is_move_card():
            state.grid.remove(state.player.id)
            move_event = state.player.move_to(target_pos)
            state.grid.place(state.player.id, target_pos)
            targets: list = []
            side_events: list = [move_event]
        else:
            origin = target_pos if target_pos is not None else state.player.position
            targets = state.grid.get_targets(origin, card.pattern)
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
        if state.enemies and all(not e.is_alive() for e in state.enemies):
            self._bus.publish(BattleEnded(outcome="victory"))
