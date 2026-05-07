from __future__ import annotations
import json
from pathlib import Path
from src.domain.entities.card import Card
from src.domain.value_objects.card_tag import CardTag
from src.domain.value_objects.attack_pattern import AttackPattern

_DEFAULT_PATH = Path(__file__).parent.parent.parent / "data" / "cards.json"

class CardRepository:
    def __init__(self, path: Path = _DEFAULT_PATH) -> None:
        raw = json.loads(path.read_text())
        self._definitions: dict[str, dict] = {c["id"]: c for c in raw["cards"]}
        self._starting_deck_ids: list[str] = raw["starting_deck"]

    def get_starting_deck(self) -> list[Card]:
        counts: dict[str, int] = {}
        result: list[Card] = []
        for def_id in self._starting_deck_ids:
            counts[def_id] = counts.get(def_id, 0) + 1
            defn = self._definitions[def_id]
            card = Card(
                id=f"{def_id}_{counts[def_id]}",
                name=defn["name"],
                tags=[CardTag(t) for t in defn["tags"]],
                ap_cost=defn["ap_cost"],
                pattern=AttackPattern.from_name(defn["pattern"]),
                damage=defn["damage"],
                grants_ap=defn.get("grants_ap", 0),
                draw_after_play=defn.get("draw_after_play", 0),
                status_effect=defn.get("status_effect"),
                description=defn.get("description", ""),
            )
            result.append(card)
        return result

    def get_random_cards(self, n: int) -> list[Card]:
        import random
        pool = list(self._definitions.keys())
        chosen = random.sample(pool, min(n, len(pool)))
        result: list[Card] = []
        for i, def_id in enumerate(chosen):
            defn = self._definitions[def_id]
            result.append(Card(
                id=f"reward_{def_id}_{i}",
                name=defn["name"],
                tags=[CardTag(t) for t in defn["tags"]],
                ap_cost=defn["ap_cost"],
                pattern=AttackPattern.from_name(defn["pattern"]),
                damage=defn["damage"],
                grants_ap=defn.get("grants_ap", 0),
                draw_after_play=defn.get("draw_after_play", 0),
                status_effect=defn.get("status_effect"),
                description=defn.get("description", ""),
            ))
        return result
