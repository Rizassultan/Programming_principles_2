import os
import sys
import pygame
from player import MusicPlayer


def format_seconds(sec: float) -> str:
    minutes = int(sec) // 60
    seconds = int(sec) % 60
    return f"{minutes:02d}:{seconds:02d}"


def main() -> None:
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()

    width, height = 640, 400
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Pygame Music Player")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    music_dir = os.path.join(base_dir, "music")
    player = MusicPlayer(music_dir)

    font_title = pygame.font.SysFont("Arial", 26, bold=True)
    font_body = pygame.font.SysFont("Arial", 20)
    font_small = pygame.font.SysFont("Arial", 16)

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    player.play()
                elif event.key == pygame.K_s:
                    player.stop()
                elif event.key == pygame.K_n:
                    player.next_track()
                elif event.key == pygame.K_b:
                    player.prev_track()
                elif event.key == pygame.K_q:
                    running = False

        player.update()

        # Render UI
        screen.fill((28, 32, 38))

        header = font_title.render("Pygame Music Player", True, (240, 244, 248))
        screen.blit(header, (30, 25))

        status_str = "PLAYING" if player.is_playing else "STOPPED"
        status_color = (80, 220, 120) if player.is_playing else (235, 95, 95)
        status_surf = font_body.render(f"Status: {status_str}", True, status_color)
        screen.blit(status_surf, (30, 80))

        track_num = f"[{player.current_index + 1}/{len(player.playlist)}]" if player.playlist else "[0/0]"
        track_surf = font_body.render(f"Track {track_num}: {player.current_track_name}", True, (255, 255, 255))
        screen.blit(track_surf, (30, 120))

        # Progress bar
        elapsed, total = player.get_progress()
        bar_x, bar_y, bar_w, bar_h = 30, 175, 580, 18
        pygame.draw.rect(screen, (60, 68, 80), (bar_x, bar_y, bar_w, bar_h), border_radius=6)

        ratio = min(1.0, elapsed / total) if total > 0 else 0.0
        if ratio > 0:
            pygame.draw.rect(screen, (70, 160, 255), (bar_x, bar_y, int(bar_w * ratio), bar_h), border_radius=6)

        time_label = font_small.render(
            f"{format_seconds(elapsed)} / {format_seconds(total)}", True, (200, 210, 220)
        )
        screen.blit(time_label, (30, 205))

        # Keyboard controls legend
        controls = [
            "Controls:",
            "[P] Play    [S] Stop    [N] Next Track    [B] Previous Track    [Q] Quit",
        ]
        for idx, line in enumerate(controls):
            color = (180, 190, 200) if idx == 0 else (140, 200, 255)
            ctrl_surf = font_small.render(line, True, color)
            screen.blit(ctrl_surf, (30, 275 + idx * 28))

        pygame.display.flip()
        clock.tick(30)

    player.stop()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
    