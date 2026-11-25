import datetime
import os
import pygame


class MickeyClock:
    """Manages time calculation and rendering for Mickey's Clock."""

    def __init__(self, center: tuple[int, int], hand_image_path: str):
        self.center = center
        self.hand_image_path = hand_image_path
        self.base_hand = self._load_hand_surface()

        # Create distinct surfaces for minutes (right/shorter) and seconds (left/longer)
        self.minute_hand = pygame.transform.smoothscale(self.base_hand, (44, 150))
        # Flip horizontally so left hand mirrors right hand
        flipped = pygame.transform.flip(self.base_hand, True, False)
        self.second_hand = pygame.transform.smoothscale(flipped, (34, 195))

        self.font_digital = pygame.font.SysFont("Arial", 32, bold=True)
        self.font_label = pygame.font.SysFont("Arial", 18)

    def _load_hand_surface(self) -> pygame.Surface:
        """Loads mickey_hand.png or draws a stylized white glove fallback."""
        if os.path.exists(self.hand_image_path):
            image = pygame.image.load(self.hand_image_path).convert_alpha()
            return image

        # Fallback graphic if mickey_hand.png is not yet placed in images/
        surf = pygame.Surface((60, 200), pygame.SRCALPHA)
        # Arm / cuff
        pygame.draw.rect(surf, (30, 30, 30), (22, 110, 16, 90), border_radius=6)
        pygame.draw.ellipse(surf, (255, 255, 255), (14, 95, 32, 22))
        pygame.draw.ellipse(surf, (0, 0, 0), (14, 95, 32, 22), 2)
        # Glove palm and pointing finger
        pygame.draw.ellipse(surf, (255, 255, 255), (10, 45, 40, 58))
        pygame.draw.ellipse(surf, (0, 0, 0), (10, 45, 40, 58), 2)
        pygame.draw.rect(surf, (255, 255, 255), (22, 5, 16, 50), border_radius=8)
        pygame.draw.rect(surf, (0, 0, 0), (22, 5, 16, 50), 2, border_radius=8)
        return surf

    def get_current_time(self) -> tuple[int, int]:
        """Returns current system (minutes, seconds), clamping leap seconds to 59."""
        now = datetime.datetime.now()
        minutes = now.minute
        seconds = min(now.second, 59)  # Handle leap second edge case (second == 60)
        return minutes, seconds

    def _blit_rotated_pivot(
        self,
        surface: pygame.Surface,
        image: pygame.Surface,
        angle: float,
    ) -> None:
        """
        Rotates an image around its bottom-center pivot so the wrist stays anchored
        at the clock center while the hand points outward.
        """
        w, h = image.get_size()
        # Vector from image center to bottom-center pivot
        pivot_offset = pygame.math.Vector2(0, h / 2 - 15)
        rotated_offset = pivot_offset.rotate(-angle)

        rotated_image = pygame.transform.rotate(image, angle)
        rect = rotated_image.get_rect(
            center=(
                self.center[0] - rotated_offset.x,
                self.center[1] - rotated_offset.y,
            )
        )
        surface.blit(rotated_image, rect)

    def draw(self, surface: pygame.Surface) -> None:
        """Draws clock face, rotated hands, and digital MM:SS readout."""
        minutes, seconds = self.get_current_time()

        # Draw clock dial background
        pygame.draw.circle(surface, (245, 245, 245), self.center, 230)
        pygame.draw.circle(surface, (20, 20, 20), self.center, 230, 5)

        # Draw 60 tick marks
        for i in range(60):
            tick_angle = pygame.math.Vector2(0, -1).rotate(i * 6)
            outer = pygame.math.Vector2(self.center) + tick_angle * 218
            inner_len = 198 if i % 5 == 0 else 208
            inner = pygame.math.Vector2(self.center) + tick_angle * inner_len
            width = 4 if i % 5 == 0 else 1
            pygame.draw.line(surface, (40, 40, 40), inner, outer, width)

        # Pygame rotates counter-clockwise for positive angles, so negate clockwise angles
        minute_angle = -(minutes * 6)
        second_angle = -(seconds * 6)

        # Right hand = minutes, Left hand = seconds
        self._blit_rotated_pivot(surface, self.minute_hand, minute_angle)
        self._blit_rotated_pivot(surface, self.second_hand, second_angle)

        # Center pin
        pygame.draw.circle(surface, (220, 40, 40), self.center, 10)
        pygame.draw.circle(surface, (0, 0, 0), self.center, 10, 2)

        # Digital MM:SS display and legend
        time_text = self.font_digital.render(f"{minutes:02d}:{seconds:02d}", True, (20, 20, 20))
        surface.blit(time_text, time_text.get_rect(center=(self.center[0], self.center[1] + 275)))

        legend_text = self.font_label.render(
            "Right Hand = Minutes  |  Left Hand = Seconds", True, (90, 90, 90)
        )
        surface.blit(legend_text, legend_text.get_rect(center=(self.center[0], 30)))