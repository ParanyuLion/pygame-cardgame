import pytest
from src.domain.value_objects.card_tag import CardTag

def test_card_tag_equality():
    assert CardTag("Blade") == CardTag("Blade")

def test_card_tag_different_values_not_equal():
    assert CardTag("Blade") != CardTag("Fire")

def test_card_tag_hashable_in_set():
    s = {CardTag("Blade"), CardTag("Fire"), CardTag("Blade")}
    assert len(s) == 2

def test_card_tag_value_attribute():
    tag = CardTag("Electric")
    assert tag.value == "Electric"
