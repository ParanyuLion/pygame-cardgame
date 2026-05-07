import pygame
from src.infrastructure.battle_repository import InMemoryBattleRepository
from src.infrastructure.event_bus import PygameEventBus
from src.infrastructure.card_repository import CardRepository
from src.use_cases.start_battle import StartBattleUseCase, Encounter
from src.domain.value_objects.position import Position
from src.presentation.game_state_manager import GameStateManager
from src.presentation.scenes.battle_scene import BattleScene

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
    card_repo = CardRepository()

    StartBattleUseCase(battle_repo, event_bus, card_repo).execute(
        Encounter(player_start=Position(0, 0))
    )

    battle_scene = BattleScene(battle_repo, event_bus)
    gsm = GameStateManager(initial_scene=battle_scene)

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
