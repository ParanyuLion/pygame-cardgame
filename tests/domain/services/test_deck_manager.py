from src.domain.services.deck_manager import DeckManager
from src.domain.entities.card import Card
from src.domain.value_objects.card_tag import CardTag
from src.domain.value_objects.attack_pattern import AttackPattern
from src.domain.events.battle_events import CardDrawn


def _card(id: str) -> Card:
    return Card(id=id, name=id, tags=[CardTag("Blade")], ap_cost=1,
                pattern=AttackPattern.single(), damage=0)


def test_draw_moves_top_card_to_hand():
    deck = [_card("a"), _card("b")]
    hand: list[Card] = []
    discard: list[Card] = []
    event = DeckManager.draw(deck, hand, discard)
    assert isinstance(event, CardDrawn)
    assert event.card_id == "a"
    assert hand[0].id == "a"
    assert len(deck) == 1


def test_draw_shuffles_discard_into_deck_when_deck_empty():
    deck: list[Card] = []
    hand: list[Card] = []
    discard = [_card("x"), _card("y")]
    event = DeckManager.draw(deck, hand, discard)
    assert event is not None
    assert len(hand) == 1
    assert len(discard) == 0
    assert len(deck) == 1   # one card remains in deck after drawing one


def test_draw_returns_none_when_both_empty():
    event = DeckManager.draw([], [], [])
    assert event is None


def test_draw_does_not_add_to_hand_when_empty():
    hand: list[Card] = []
    DeckManager.draw([], hand, [])
    assert hand == []


def test_draw_depletes_deck_in_order():
    deck = [_card("first"), _card("second")]
    hand: list[Card] = []
    DeckManager.draw(deck, hand, [])
    DeckManager.draw(deck, hand, [])
    assert hand[0].id == "first"
    assert hand[1].id == "second"
