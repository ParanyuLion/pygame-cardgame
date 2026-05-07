import json
import pytest
from pathlib import Path
from src.infrastructure.card_repository import CardRepository
from src.domain.value_objects.card_tag import CardTag

def _minimal_json(cards: list[dict], starting_deck: list[str]) -> str:
    return json.dumps({"cards": cards, "starting_deck": starting_deck})

def _step_def() -> dict:
    return {"id": "step", "name": "Step", "tags": ["Move"], "ap_cost": 1,
            "pattern": "single", "damage": 0, "grants_ap": 0,
            "draw_after_play": 0, "status_effect": None, "description": "Move."}

def _slash_def() -> dict:
    return {"id": "slash", "name": "Iron Slash", "tags": ["Blade"], "ap_cost": 2,
            "pattern": "line", "damage": 4, "grants_ap": 0,
            "draw_after_play": 0, "status_effect": None, "description": "Line attack."}

def test_get_starting_deck_correct_length(tmp_path: Path):
    f = tmp_path / "cards.json"
    f.write_text(_minimal_json([_step_def()], ["step", "step", "step"]))
    repo = CardRepository(path=f)
    deck = repo.get_starting_deck()
    assert len(deck) == 3

def test_get_starting_deck_unique_instance_ids(tmp_path: Path):
    f = tmp_path / "cards.json"
    f.write_text(_minimal_json([_step_def()], ["step", "step"]))
    repo = CardRepository(path=f)
    deck = repo.get_starting_deck()
    assert deck[0].id == "step_1"
    assert deck[1].id == "step_2"

def test_get_starting_deck_correct_tags(tmp_path: Path):
    f = tmp_path / "cards.json"
    f.write_text(_minimal_json([_slash_def()], ["slash"]))
    repo = CardRepository(path=f)
    deck = repo.get_starting_deck()
    assert CardTag("Blade") in deck[0].tags

def test_get_starting_deck_move_card_recognised(tmp_path: Path):
    f = tmp_path / "cards.json"
    f.write_text(_minimal_json([_step_def()], ["step"]))
    repo = CardRepository(path=f)
    deck = repo.get_starting_deck()
    assert deck[0].is_move_card() is True

def test_get_starting_deck_mixed_cards(tmp_path: Path):
    f = tmp_path / "cards.json"
    f.write_text(_minimal_json([_step_def(), _slash_def()], ["step", "slash", "step"]))
    repo = CardRepository(path=f)
    deck = repo.get_starting_deck()
    assert len(deck) == 3
    assert deck[0].id == "step_1"
    assert deck[1].id == "slash_1"
    assert deck[2].id == "step_2"
