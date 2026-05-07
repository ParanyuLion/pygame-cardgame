from __future__ import annotations
from src.domain.interfaces import IRunRepository, ICardRepository
from src.domain.run_state import RunState, MapNode, EnemySpec
from src.domain.value_objects.position import Position

PLAYER_MAX_HP = 30


def _build_floor(floor: int) -> list[MapNode]:
    combat_hp =  [15, 20, 25][floor - 1]
    combat_dmg = [ 3,  4,  5][floor - 1]
    boss_hp =    [30, 40, 60][floor - 1]
    boss_dmg =   [ 5,  6,  8][floor - 1]

    nodes: list[MapNode] = [
        MapNode(
            id=f"f{floor}_c{i}",
            node_type="combat",
            enemies=[
                EnemySpec(
                    id=f"f{floor}_c{i}_e1",
                    position=Position(3, 3),
                    hp=combat_hp,
                    base_damage=combat_dmg,
                )
            ],
        )
        for i in range(1, 4)
    ]
    nodes.append(
        MapNode(
            id=f"f{floor}_boss",
            node_type="boss",
            enemies=[
                EnemySpec(
                    id=f"f{floor}_boss_e1",
                    position=Position(2, 2),
                    hp=boss_hp,
                    base_damage=boss_dmg,
                ),
                EnemySpec(
                    id=f"f{floor}_boss_e2",
                    position=Position(3, 1),
                    hp=boss_hp // 2,
                    base_damage=combat_dmg,
                ),
            ],
        )
    )
    return nodes


class StartRunUseCase:
    def __init__(self, run_repo: IRunRepository, card_repo: ICardRepository) -> None:
        self._run_repo = run_repo
        self._card_repo = card_repo

    def execute(self) -> RunState:
        deck = self._card_repo.get_starting_deck()
        floors = [_build_floor(f) for f in (1, 2, 3)]
        run = RunState(
            deck=deck,
            player_hp=PLAYER_MAX_HP,
            player_max_hp=PLAYER_MAX_HP,
            floor=1,
            floors=floors,
        )
        self._run_repo.save(run)
        return run
