from src.domain.entities.card import Card
from src.domain.value_objects.card_tag import CardTag
from src.domain.value_objects.attack_pattern import AttackPattern
from src.presentation.renderers.hand_renderer import HandRenderer


def _card(id: str) -> Card:
    return Card(
        id=id, name=id, tags=[CardTag("Blade")],
        ap_cost=1, pattern=AttackPattern.single(), damage=0,
    )


def test_set_drag_stores_card_and_pos():
    renderer = HandRenderer()
    card = _card("a_1")
    renderer.set_drag(card, (200, 300))
    assert renderer._drag_card is card
    assert renderer._drag_pos == (200, 300)


def test_clear_drag_resets_to_none():
    renderer = HandRenderer()
    card = _card("a_1")
    renderer.set_drag(card, (200, 300))
    renderer.clear_drag()
    assert renderer._drag_card is None
    assert renderer._drag_pos is None


def test_set_drag_updates_pos_on_subsequent_calls():
    renderer = HandRenderer()
    card = _card("a_1")
    renderer.set_drag(card, (100, 100))
    renderer.set_drag(card, (150, 150))
    assert renderer._drag_pos == (150, 150)
