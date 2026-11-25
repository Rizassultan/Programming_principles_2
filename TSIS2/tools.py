import math
from collections import deque
import pygame


def draw_shape(surface, tool, start_pos, end_pos, color, width):
    """Draws lines and geometric shapes (Practice 10–11 + TSIS 2) onto a surface."""
    x1, y1 = start_pos
    x2, y2 = end_pos

    if tool == "line":
        pygame.draw.line(surface, color, start_pos, end_pos, width)

    elif tool == "rect":
        rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
        pygame.draw.rect(surface, color, rect, width)

    elif tool == "circle":
        radius = int(math.hypot(x2 - x1, y2 - y1))
        if radius > 0:
            # Ensure width doesn't exceed radius (Pygame throws ValueError otherwise)
            stroke = min(width, radius)
            pygame.draw.circle(surface, color, start_pos, radius, stroke)

    elif tool == "square":
        side = max(abs(x2 - x1), abs(y2 - y1))
        left = x1 if x2 >= x1 else x1 - side
        top = y1 if y2 >= y1 else y1 - side
        rect = pygame.Rect(left, top, side, side)
        pygame.draw.rect(surface, color, rect, width)

    elif tool == "right_triangle":
        points = [start_pos, (x1, y2), end_pos]
        pygame.draw.polygon(surface, color, points, width)

    elif tool == "equilateral_triangle":
        dx = x2 - x1
        dy = y2 - y1
        # Rotate vector (dx, dy) by 60 degrees to find the third vertex
        angle = math.radians(60)
        x3 = x1 + dx * math.cos(angle) - dy * math.sin(angle)
        y3 = y1 + dx * math.sin(angle) + dy * math.cos(angle)
        points = [start_pos, end_pos, (int(x3), int(y3))]
        pygame.draw.polygon(surface, color, points, width)

    elif tool == "rhombus":
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        points = [(cx, y1), (x2, cy), (cx, y2), (x1, cy)]
        pygame.draw.polygon(surface, color, points, width)


def flood_fill(surface, start_pos, fill_color):
    """Iterative BFS flood-fill using get_at() and set_at() to avoid recursion limits."""
    width, height = surface.get_size()
    x, y = start_pos

    if not (0 <= x < width and 0 <= y < height):
        return

    target_color = surface.get_at((x, y))
    fill_rgba = pygame.Color(*fill_color)

    if target_color == fill_rgba:
        return

    queue = deque([(x, y)])
    visited = set([(x, y)])

    # Lock surface for significantly faster pixel reads/writes
    surface.lock()
    try:
        while queue:
            cx, cy = queue.popleft()
            surface.set_at((cx, cy), fill_rgba)

            for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited:
                    if surface.get_at((nx, ny)) == target_color:
                        visited.add((nx, ny))
                        queue.append((nx, ny))
    finally:
        surface.unlock()