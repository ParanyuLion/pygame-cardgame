import pytest
from src.domain.entities.card import Card
from src.domain.value_objects.card_tag import CardTag
from src.domain.value_objects.attack_pattern import AttackPattern
from src.domain.services.fusion_engine import FusionEngine


def _card(
    id: str,
    tags: list[str],
    ap: int = 1,
    dmg: int = 0,
    pattern: str = "single",
    grants_ap: int = 0,
    draw_after: int = 0,
) -> Card:
    return Card(
        id=id,
        name=id,
        tags=[CardTag(t) for t in tags],
        ap_cost=ap,
        pattern=AttackPattern.from_name(pattern),
        damage=dmg,
        grants_ap=grants_ap,
        draw_after_play=draw_after,
    )


def test_fuse_produces_correct_id_and_name():
    a = _card("strike_1", ["Blade"], ap=1, dmg=2)
    b = _card("slash_1", ["Blade"], ap=2, dmg=4)
    result = FusionEngine.fuse(a, b)
    assert result.id == "fused_strike_1_slash_1"
    assert result.name == "strike_1+slash_1"


def test_fuse_damage_is_sum_plus_one():
    a = _card("a_1", ["Blade"], ap=1, dmg=2)
    b = _card("b_1", ["Blade"], ap=1, dmg=3)
    result = FusionEngine.fuse(a, b)
    assert result.damage == 6  # 2 + 3 + 1


def test_fuse_ap_cost_is_max():
    a = _card("a_1", ["Blade"], ap=1, dmg=0)
    b = _card("b_1", ["Blade"], ap=3, dmg=0)
    result = FusionEngine.fuse(a, b)
    assert result.ap_cost == 3


def test_fuse_tags_are_union():
    a = _card("a_1", ["Blade", "Fire"], ap=1, dmg=0)
    b = _card("b_1", ["Blade", "Electric"], ap=1, dmg=0)
    result = FusionEngine.fuse(a, b)
    tag_values = {t.value for t in result.tags}
    assert tag_values == {"Blade", "Fire", "Electric"}


def test_fuse_pattern_takes_larger():
    a = _card("a_1", ["Blade"], ap=1, dmg=0, pattern="single")  # 1 tile
    b = _card("b_1", ["Blade"], ap=1, dmg=0, pattern="cross")   # 5 tiles
    result = FusionEngine.fuse(a, b)
    assert result.pattern == AttackPattern.from_name("cross")


def test_fuse_no_shared_tag_raises():
    a = _card("a_1", ["Blade"], ap=1, dmg=0)
    b = _card("b_1", ["Fire"], ap=1, dmg=0)
    with pytest.raises(ValueError, match="cannot fuse"):
        FusionEngine.fuse(a, b)


def test_fuse_grants_ap_summed():
    a = _card("a_1", ["Blade"], ap=0, dmg=0, grants_ap=1)
    b = _card("b_1", ["Blade"], ap=0, dmg=0, grants_ap=2)
    result = FusionEngine.fuse(a, b)
    assert result.grants_ap == 3


def test_fuse_draw_after_play_summed():
    a = _card("a_1", ["Blade"], ap=0, dmg=0, draw_after=1)
    b = _card("b_1", ["Blade"], ap=0, dmg=0, draw_after=1)
    result = FusionEngine.fuse(a, b)
    assert result.draw_after_play == 2
