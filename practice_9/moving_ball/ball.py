import pygame


class RedBall:
    """Represents a 50x50 (radius 25) red ball constrained within screen boundaries."""

    RADIUS = 25
    STEP = 20
    COLOR = (220, 30, 30)

    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        # Start centered on screen
        self.x = screen_width // 2
        self.y = screen_height // 2

    def move(self, dx: int, dy: int) -> bool:
        """
        Moves the ball by (dx, dy) only if the entire circle remains inside screen bounds.
        Returns True if moved, False if input was ignored due to boundary collision.
        """
        new_x = self.x + dx
        new_y = self.y + dy

        if (
            self.RADIUS <= new_x <= self.screen_width - self.RADIUS
            and self.RADIUS <= new_y <= self.screen_height - self.RADIUS
        ):
            self.x = new_x
            self.y = new_y
            return True

        return False

    def move_up(self) -> bool:
        return self.move(0, -self.STEP)

    def move_down(self) -> bool:
        return self.move(0, self.STEP)

    def move_left(self) -> bool:
        return self.move(-self.STEP, 0)

    def move_right(self) -> bool:
        return self.move(self.STEP, 0)

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.circle(surface, self.COLOR, (self.x, self.y), self.RADIUS)