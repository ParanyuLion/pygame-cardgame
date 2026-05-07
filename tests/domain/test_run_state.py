import pytest
from src.domain.run_state import RunState, MapNode, EnemySpec
from src.domain.value_objects.position import Position


def _node(id: str, node_type: str = "combat") -> MapNode:
    return MapNode(id=id, node_type=node_type, enemies=[])


def _run(floors=None) -> RunState:
    f = floors or [[_node("n1"), _node("n2")], [_node("n3")], [_node("n4")]]
    return RunState(deck=[], player_hp=30, player_max_hp=30, floor=1, floors=f)


def test_current_node_returns_node_at_idx():
    run = _run()
    assert run.current_node().id == "n1"


def test_is_floor_complete_false_when_nodes_remain():
    run = _run()
    assert run.is_floor_complete() is False


def test_advance_node_marks_complete_and_increments():
    run = _run()
    run.advance_node()
    assert run.nodes[0].is_complete is True
    assert run.node_idx == 1
    assert run.current_node().id == "n2"


def test_is_floor_complete_true_after_all_nodes():
    run = _run(floors=[[_node("n1")], [], []])
    run.advance_node()
    assert run.is_floor_complete() is True


def test_advance_floor_moves_to_next_floor_and_resets_idx():
    run = _run()
    run.advance_node()
    run.advance_node()
    run.advance_floor()
    assert run.floor == 2
    assert run.node_idx == 0
    assert run.current_node().id == "n3"


def test_enemy_spec_is_frozen():
    spec = EnemySpec(id="e1", position=Position(1, 1), hp=10, base_damage=3)
    with pytest.raises(AttributeError):
        spec.hp = 99  # type: ignore[misc]
