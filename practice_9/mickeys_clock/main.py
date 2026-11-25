import os
import sys
import pygame
from clock import MickeyClock


def main() -> None:
    pygame.init()
    width, height = 600, 620
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Mickey's Clock (Minutes & Seconds)")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    hand_path = os.path.join(base_dir, "images", "mickey_hand.png")

    clock_widget = MickeyClock(center=(width // 2, height // 2 - 10), hand_image_path=hand_path)
    fps_clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((255, 255, 255))
        clock_widget.draw(screen)
        pygame.display.flip()

        # Poll frequently for responsive window close while synchronizing to system clock
        fps_clock.tick(10)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
    