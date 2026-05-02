import pytest
from src.domain.value_objects.position import Position

def test_valid_position_stores_col_row():
    pos = Position(2, 3)
    assert pos.col == 2
    assert pos.row == 3

def test_position_col_negative_raises():
    with pytest.raises(ValueError):
        Position(-1, 0)

def test_position_row_negative_raises():
    with pytest.raises(ValueError):
        Position(0, -1)

def test_position_col_at_grid_size_raises():
    with pytest.raises(ValueError):
        Position(4, 0)

def test_position_row_at_grid_size_raises():
    with pytest.raises(ValueError):
        Position(0, 4)

def test_position_corner_valid():
    pos = Position(3, 3)
    assert pos.col == 3 and pos.row == 3

def test_offset_returns_new_position():
    pos = Position(1, 1)
    result = pos.offset(1, 0)
    assert result == Position(2, 1)

def test_offset_out_of_bounds_returns_none():
    pos = Position(0, 0)
    assert pos.offset(-1, 0) is None
    assert pos.offset(0, -1) is None

def test_offset_to_boundary_valid():
    pos = Position(2, 2)
    assert pos.offset(1, 1) == Position(3, 3)

def test_positions_are_equal_by_value():
    assert Position(1, 2) == Position(1, 2)
    assert Position(1, 2) != Position(2, 1)

def test_position_is_hashable():
    s = {Position(0, 0), Position(1, 1), Position(0, 0)}
    assert len(s) == 2
