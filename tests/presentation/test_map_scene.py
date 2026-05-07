from __future__ import annotations
import pygame
from unittest.mock import MagicMock
from src.domain.run_state import RunState, MapNode
from src.presentation.renderers.map_renderer import MapRenderer
from src.presentation.scenes.map_scene import MapScene


def _node(id: str, node_type: str = "combat") -> MapNode:
    return MapNode(id=id, node_type=node_type, enemies=[])


def _run(nodes: list[MapNode], node_idx: int = 0) -> RunState:
    return RunState(
        deck=[], player_hp=30, player_max_hp=30, floor=1,
        floors=[nodes, [], []],
        node_idx=node_idx,
    )


def _make_scene(run: RunState) -> tuple[MapScene, list]:
    run_repo = MagicMock()
    run_repo.get.return_value = run
    selected = []
    scene = MapScene(run_repo=run_repo, on_node_selected=selected.append)
    return scene, selected


def test_click_current_node_triggers_callback():
    nodes = [_node("n1"), _node("n2")]
    run = _run(nodes, node_idx=0)
    scene, selected = _make_scene(run)
    renderer = MapRenderer()
    rect = renderer.node_rect(0)  # current node is index 0
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=rect.center)
    scene.handle_event(event)
    assert selected == [nodes[0]]


def test_click_future_node_does_not_trigger():
    nodes = [_node("n1"), _node("n2")]
    run = _run(nodes, node_idx=0)
    scene, selected = _make_scene(run)
    renderer = MapRenderer()
    rect = renderer.node_rect(1)  # node 1 is future — not clickable
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=rect.center)
    scene.handle_event(event)
    assert selected == []


def test_click_completed_node_does_not_trigger():
    nodes = [_node("n1"), _node("n2")]
    nodes[0].is_complete = True
    run = _run(nodes, node_idx=1)  # current is n2; n1 is done
    scene, selected = _make_scene(run)
    renderer = MapRenderer()
    rect = renderer.node_rect(0)  # completed node
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=rect.center)
    scene.handle_event(event)
    assert selected == []


def test_node_rects_are_distinct():
    renderer = MapRenderer()
    rects = [renderer.node_rect(i) for i in range(4)]
    for i in range(4):
        for j in range(4):
            if i != j:
                assert not rects[i].colliderect(rects[j])
