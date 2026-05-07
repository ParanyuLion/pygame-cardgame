import pygame
from src.domain.entities.enemy import Enemy
from src.domain.value_objects.position import Position
from src.domain.value_objects.intent import Intent
from src.domain.value_objects.attack_pattern import AttackPattern
from src.presentation.renderers.enemy_renderer import EnemyRenderer
from src.presentation.renderers.intent_renderer import IntentRenderer
from src.presentation.renderers.grid_renderer import GridRenderer
from src.domain.entities.grid import Grid


def _intent() -> Intent:
    return Intent(type="ATTACK", pattern=AttackPattern.cross(), countdown=2, damage=5)


def _enemy(id: str = "e1", pos: Position = Position(3, 3), hp: int = 20) -> Enemy:
    return Enemy(id=id, position=pos, hp=hp, max_hp=20, base_damage=5, intent=_intent())


def test_enemy_renderer_renders_alive_enemies_without_crash():
    surface = pygame.Surface((560, 700))
    grid_renderer = GridRenderer()
    renderer = EnemyRenderer(grid_renderer)
    enemies = [_enemy("e1", Position(3, 3)), _enemy("e2", Position(2, 2), hp=5)]
    renderer.render(surface, enemies)  # must not raise


def test_enemy_renderer_skips_dead_enemies_without_crash():
    surface = pygame.Surface((560, 700))
    grid_renderer = GridRenderer()
    renderer = EnemyRenderer(grid_renderer)
    renderer.render(surface, [_enemy(hp=0)])  # must not raise


def test_intent_renderer_renders_attack_intent_without_crash():
    surface = pygame.Surface((560, 700))
    grid_renderer = GridRenderer()
    renderer = IntentRenderer(grid_renderer)
    grid = Grid()
    renderer.render(surface, [_enemy()], grid)  # must not raise
