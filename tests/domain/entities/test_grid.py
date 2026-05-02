import pytest
from src.domain.entities.grid import Grid
from src.domain.entities.tile import Obstacle
from src.domain.value_objects.position import Position
from src.domain.value_objects.attack_pattern import AttackPattern

def test_grid_has_16_tiles():
    grid = Grid()
    assert len(grid.tiles) == 16

def test_all_tiles_passable_on_init():
    grid = Grid()
    for pos in grid.tiles:
        assert grid.is_passable(pos)

def test_place_makes_tile_occupied():
    grid = Grid()
    pos = Position(0, 0)
    grid.place("player", pos)
    assert grid.is_occupied(pos)
    assert not grid.is_passable(pos)

def test_remove_clears_occupant():
    grid = Grid()
    pos = Position(2, 2)
    grid.place("player", pos)
    grid.remove("player")
    assert not grid.is_occupied(pos)
    assert grid.is_passable(pos)

def test_get_entity_position_returns_current_pos():
    grid = Grid()
    pos = Position(1, 3)
    grid.place("player", pos)
    assert grid.get_entity_position("player") == pos

def test_get_entity_position_returns_none_when_absent():
    grid = Grid()
    assert grid.get_entity_position("ghost") is None

def test_wall_obstacle_blocks_movement():
    grid = Grid()
    pos = Position(1, 0)
    grid.place_obstacle(pos, Obstacle(type="wall"))
    assert not grid.is_passable(pos)

def test_pit_obstacle_blocks_movement():
    grid = Grid()
    pos = Position(2, 1)
    grid.place_obstacle(pos, Obstacle(type="pit"))
    assert not grid.is_passable(pos)

def test_get_targets_single_hits_origin():
    grid = Grid()
    origin = Position(1, 1)
    targets = grid.get_targets(origin, AttackPattern.single())
    assert Position(1, 1) in targets

def test_get_targets_cross_from_corner_excludes_oob():
    grid = Grid()
    origin = Position(0, 0)
    targets = grid.get_targets(origin, AttackPattern.cross())
    assert all(grid.in_bounds(t) for t in targets)
    assert Position(0, 0) in targets
    assert Position(1, 0) in targets
    assert Position(0, 1) in targets

def test_get_targets_wall_excluded_from_pattern():
    grid = Grid()
    grid.place_obstacle(Position(2, 1), Obstacle(type="wall"))
    origin = Position(1, 1)
    targets = grid.get_targets(origin, AttackPattern.cross())
    assert Position(2, 1) not in targets

def test_get_targets_pit_not_excluded_from_pattern():
    grid = Grid()
    grid.place_obstacle(Position(2, 1), Obstacle(type="pit"))
    origin = Position(1, 1)
    targets = grid.get_targets(origin, AttackPattern.cross())
    assert Position(2, 1) in targets
