import pygame
from src.presentation.scenes.menu_scene import MenuScene


def test_space_key_triggers_on_start_run():
    called = []
    scene = MenuScene(on_start_run=lambda: called.append(True))
    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE, mod=0, unicode=" ")
    scene.handle_event(event)
    assert called == [True]


def test_other_key_does_not_trigger():
    called = []
    scene = MenuScene(on_start_run=lambda: called.append(True))
    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, mod=0, unicode="\r")
    scene.handle_event(event)
    assert called == []


def test_on_enter_and_exit_do_not_raise():
    scene = MenuScene(on_start_run=lambda: None)
    scene.on_enter()
    scene.on_exit()
