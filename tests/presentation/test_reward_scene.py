from __future__ import annotations
import pygame
from src.domain.entities.card import Card
from src.domain.value_objects.card_tag import CardTag
from src.domain.value_objects.attack_pattern import AttackPattern
from src.presentation.renderers.card_reward_renderer import CardRewardRenderer
from src.presentation.scenes.reward_scene import RewardScene


def _card(id: str) -> Card:
    return Card(id=id, name=id, tags=[CardTag("Blade")], ap_cost=1,
                pattern=AttackPattern.single(), damage=2)


def test_click_first_card_triggers_callback_with_that_card():
    cards = [_card("a"), _card("b"), _card("c")]
    chosen = []
    scene = RewardScene(choices=cards, on_card_chosen=chosen.append)
    renderer = CardRewardRenderer()
    rect = renderer.card_rect(0)
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=rect.center)
    scene.handle_event(event)
    assert chosen == [cards[0]]


def test_click_third_card_triggers_callback_with_that_card():
    cards = [_card("a"), _card("b"), _card("c")]
    chosen = []
    scene = RewardScene(choices=cards, on_card_chosen=chosen.append)
    renderer = CardRewardRenderer()
    rect = renderer.card_rect(2)
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=rect.center)
    scene.handle_event(event)
    assert chosen == [cards[2]]


def test_click_outside_cards_does_not_trigger():
    cards = [_card("a"), _card("b"), _card("c")]
    chosen = []
    scene = RewardScene(choices=cards, on_card_chosen=chosen.append)
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(1, 1))
    scene.handle_event(event)
    assert chosen == []


def test_card_rects_are_three_distinct_non_overlapping_areas():
    renderer = CardRewardRenderer()
    rects = [renderer.card_rect(i) for i in range(3)]
    # No two rects overlap
    for i in range(3):
        for j in range(3):
            if i != j:
                assert not rects[i].colliderect(rects[j])
