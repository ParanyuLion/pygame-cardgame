from src.domain.interfaces import IBattleRepository, IEventBus
from src.domain.value_objects.position import Position

MOVE_AP_COST = 1

class MoveEntityUseCase:
    def __init__(self, battle_repo: IBattleRepository, event_bus: IEventBus) -> None:
        self._repo = battle_repo
        self._bus = event_bus

    def execute(self, entity_id: str, target_pos: Position) -> None:
        state = self._repo.get()

        if state.player.id != entity_id:
            raise ValueError(f"Unknown entity: '{entity_id}'")

        move_card = next((c for c in state.hand if c.is_move_card()), None)
        if move_card is None:
            raise ValueError("No Move card in hand")

        if not state.grid.is_passable(target_pos):
            raise ValueError(
                f"Position {target_pos} is not passable"
            )

        state.player.spend_ap(MOVE_AP_COST)

        state.hand.remove(move_card)
        state.discard.append(move_card)

        state.grid.remove(entity_id)
        event = state.player.move_to(target_pos)
        state.grid.place(entity_id, target_pos)

        self._repo.save(state)
        self._bus.publish(event)
