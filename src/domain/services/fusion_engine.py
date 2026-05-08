from __future__ import annotations
from src.domain.entities.card import Card


class FusionEngine:
    @staticmethod
    def fuse(card_a: Card, card_b: Card) -> Card:
        if not card_a.can_fuse_with(card_b):
            raise ValueError(
                f"Cards '{card_a.id}' and '{card_b.id}' share no tags and cannot fuse"
            )
        tags = list({t: None for t in [*card_a.tags, *card_b.tags]}.keys())
        pattern = (
            card_a.pattern
            if len(card_a.pattern.offsets) >= len(card_b.pattern.offsets)
            else card_b.pattern
        )
        both_move = card_a.is_move_card() and card_b.is_move_card()
        return Card(
            id=f"fused_{card_a.id}_{card_b.id}",
            name=f"{card_a.name}+{card_b.name}",
            tags=tags,
            ap_cost=max(card_a.ap_cost, card_b.ap_cost),
            damage=card_a.damage + card_b.damage + 1,
            pattern=pattern,
            grants_ap=card_a.grants_ap + card_b.grants_ap,
            draw_after_play=card_a.draw_after_play + card_b.draw_after_play,
            move_distance=card_a.move_distance + card_b.move_distance if both_move else 1,
        )
