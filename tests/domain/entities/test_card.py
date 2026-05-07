from src.domain.entities.card import Card, CardContext
from src.domain.value_objects.card_tag import CardTag
from src.domain.value_objects.attack_pattern import AttackPattern
from src.domain.value_objects.position import Position


def _make_card(id: str, tags: list[CardTag], ap_cost: int = 1, damage: int = 0) -> Card:
    return Card(
        id=id, name=id, tags=tags, ap_cost=ap_cost,
        pattern=AttackPattern.single(), damage=damage,
    )


def test_is_move_card_true():
    card = _make_card("step_1", [CardTag("Move")])
    assert card.is_move_card() is True


def test_is_move_card_false():
    card = _make_card("slash_1", [CardTag("Blade")])
    assert card.is_move_card() is False


def test_can_fuse_with_shared_tag():
    a = _make_card("a", [CardTag("Fire"), CardTag("Blade")])
    b = _make_card("b", [CardTag("Blade")])
    assert a.can_fuse_with(b) is True


def test_can_fuse_with_no_shared_tag():
    a = _make_card("a", [CardTag("Fire")])
    b = _make_card("b", [CardTag("Electric")])
    assert a.can_fuse_with(b) is False


def test_apply_returns_empty_with_no_enemies():
    card = _make_card("slash_1", [CardTag("Blade")], damage=4)
    ctx = CardContext(player=None, targets=[Position(1, 0)], enemies=[])
    assert card.apply(ctx) == []


def test_card_defaults():
    card = _make_card("x", [CardTag("Blade")])
    assert card.grants_ap == 0
    assert card.draw_after_play == 0
    assert card.status_effect is None
    assert card.description == ""
