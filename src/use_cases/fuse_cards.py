from src.domain.interfaces import IBattleRepository, IEventBus
from src.domain.services.fusion_engine import FusionEngine
from src.domain.events.battle_events import CardsFused


class FuseCardsUseCase:
    def __init__(self, battle_repo: IBattleRepository, event_bus: IEventBus) -> None:
        self._repo = battle_repo
        self._bus = event_bus

    def execute(self, card_a_id: str, card_b_id: str) -> None:
        state = self._repo.get()
        card_a = next((c for c in state.hand if c.id == card_a_id), None)
        if card_a is None:
            raise ValueError(f"Card '{card_a_id}' not in hand")
        card_b = next((c for c in state.hand if c.id == card_b_id), None)
        if card_b is None:
            raise ValueError(f"Card '{card_b_id}' not in hand")
        fused = FusionEngine.fuse(card_a, card_b)
        state.hand.remove(card_a)
        state.hand.remove(card_b)
        state.hand.append(fused)
        state.fused_card_ids.add(card_a_id)
        state.fused_card_ids.add(card_b_id)
        self._repo.save(state)
        self._bus.publish(CardsFused(
            card_a_id=card_a_id,
            card_b_id=card_b_id,
            result_card_id=fused.id,
        ))
