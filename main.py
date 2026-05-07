from __future__ import annotations
import pygame
from src.infrastructure.battle_repository import InMemoryBattleRepository
from src.infrastructure.run_repository import InMemoryRunRepository
from src.infrastructure.event_bus import PygameEventBus
from src.infrastructure.card_repository import CardRepository
from src.presentation.game_state_manager import GameStateManager
from src.presentation.scenes.menu_scene import MenuScene
from src.presentation.game_controller import GameController

WINDOW_WIDTH = 560
WINDOW_HEIGHT = 700
FPS = 60
WINDOW_TITLE = "Dungeon Card Roguelike"


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)
    clock = pygame.time.Clock()

    event_bus = PygameEventBus()
    battle_repo = InMemoryBattleRepository()
    run_repo = InMemoryRunRepository()
    card_repo = CardRepository()

    # start_new_run is a closure — controller is assigned below and captured by reference
    def start_new_run() -> None:
        controller.start_new_run()

    menu_scene = MenuScene(on_start_run=start_new_run)
    gsm = GameStateManager(initial_scene=menu_scene)
    controller = GameController(gsm, run_repo, battle_repo, event_bus, card_repo)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                gsm.handle_event(event)
        gsm.update(dt)
        screen.fill((10, 8, 6))
        gsm.render(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
