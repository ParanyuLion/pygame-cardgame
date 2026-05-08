from __future__ import annotations
from src.domain.interfaces import IBattleRepository, IEventBus
from src.domain.events.base import DomainEvent
from src.domain.events.battle_events import (
    BattleTurnStarted, IntentBroadcast, BattleEnded, CardDrawn, EntityMoved,
)
from src.domain.services.deck_manager import DeckManager
from src.domain.value_objects.grid_snapshot import GridSnapshot
from src.domain.value_objects.position import Position

HAND_SIZE = 5


def _step_toward(pos: Position, target: Position, grid) -> Position | None:
    """Return the adjacent tile that minimises Manhattan distance to target, or None if blocked."""
    best: tuple[int, Position] | None = None
    for dcol, drow in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        neighbor = pos.offset(dcol, drow)
        if neighbor is None or not grid.is_passable(neighbor):
            continue
        dist = abs(neighbor.col - target.col) + abs(neighbor.row - target.row)
        if best is None or dist < best[0]:
            best = (dist, neighbor)
    return best[1] if best is not None else None


class EndTurnUseCase:
    def __init__(self, battle_repo: IBattleRepository, event_bus: IEventBus) -> None:
        self._repo = battle_repo
        self._bus = event_bus

    def execute(self) -> None:
        state = self._repo.get()
        if not state.player.is_alive():
            return

        events: list[DomainEvent] = []

        positions = {e.id: e.position for e in state.enemies}
        positions["player"] = state.player.position
        hp = {e.id: e.hp for e in state.enemies}
        hp["player"] = state.player.hp
        # Snapshot reflects turn-start state; choose_intent receives stale data for
        # enemies that act after the first. Acceptable while choose_intent ignores it.
        snapshot = GridSnapshot(positions=positions, hp=hp)

        ordered = sorted(
            [e for e in state.enemies if e.is_alive()],
            key=lambda e: e.hp,
        )

        for enemy in ordered:
            new_intent = enemy.tick_intent()
            enemy.intent = new_intent

            if new_intent.countdown <= 0:
                if new_intent.type == "MOVE":
                    new_pos = _step_toward(enemy.position, state.player.position, state.grid)
                    if new_pos is not None:
                        state.grid.remove(enemy.id)
                        old_pos = enemy.position
                        enemy.position = new_pos
                        state.grid.place(enemy.id, new_pos)
                        events.append(EntityMoved(entity_id=enemy.id, from_pos=old_pos, to_pos=new_pos))
                else:
                    targets = state.grid.get_targets(enemy.position, new_intent.pattern)
                    if state.player.position in targets:
                        damage_event = enemy.resolve_attack(state.player)
                        events.append(damage_event)
                enemy.intent = enemy.choose_intent(snapshot)

            events.append(IntentBroadcast(
                enemy_id=enemy.id,
                intent_type=enemy.intent.type,
                countdown=enemy.intent.countdown,
            ))

        if not state.player.is_alive():
            self._repo.save(state)
            for event in events:
                self._bus.publish(event)
            self._bus.publish(BattleEnded(outcome="defeat"))
            return

        refreshed = state.player.refresh_ap()

        draw_events: list[CardDrawn] = []
        cards_to_draw = max(0, HAND_SIZE - len(state.hand))
        for _ in range(cards_to_draw):
            drawn = DeckManager.draw(state.deck, state.hand, state.discard)
            if drawn is not None:
                draw_events.append(drawn)
            else:
                break

        state.turn_number += 1

        self._repo.save(state)

        for event in events:
            self._bus.publish(event)
        self._bus.publish(BattleTurnStarted(
            turn_number=state.turn_number,
            ap_refreshed=refreshed,
        ))
        for event in draw_events:
            self._bus.publish(event)
