import os
from datetime import datetime
import pygame
from tools import draw_shape, flood_fill

# Window & Layout Constants
WIDTH, HEIGHT = 1100, 720
TOOLBAR_HEIGHT = 95
CANVAS_HEIGHT = HEIGHT - TOOLBAR_HEIGHT
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (230, 230, 235)
DARK_GRAY = (160, 160, 170)
ACCENT = (50, 120, 220)

PALETTE = [
    (0, 0, 0),       # Black
    (255, 255, 255), # White
    (220, 40, 40),   # Red
    (40, 170, 60),   # Green
    (40, 100, 220),  # Blue
    (240, 200, 20),  # Yellow
    (240, 120, 20),  # Orange
    (150, 50, 200),  # Purple
    (20, 190, 200),  # Cyan
    (130, 80, 40),   # Brown
]

TOOLS = [
    ("pencil", "Pencil"),
    ("line", "Line"),
    ("rect", "Rect"),
    ("circle", "Circle"),
    ("square", "Square"),
    ("right_triangle", "R-Tri"),
    ("equilateral_triangle", "Eq-Tri"),
    ("rhombus", "Rhombus"),
    ("fill", "Fill"),
    ("text", "Text"),
    ("eraser", "Eraser"),
]

BRUSH_SIZES = [
    ("S (2px)", 2),
    ("M (5px)", 5),
    ("L (10px)", 10),
]


class PaintApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("TSIS 2 - Extended Paint Application")
        self.clock = pygame.time.Clock()

        # Separate persistent drawing canvas below the toolbar
        self.canvas = pygame.Surface((WIDTH, CANVAS_HEIGHT))
        self.canvas.fill(WHITE)

        # Fonts
        self.ui_font = pygame.font.SysFont("Arial", 14, bold=True)
        self.text_font = pygame.font.SysFont("Arial", 24)

        # Tool State
        self.current_tool = "pencil"
        self.current_color = BLACK
        self.brush_size = 2

        # Drawing State
        self.drawing = False
        self.start_pos = None
        self.last_pos = None

        # Text Tool State
        self.text_active = False
        self.text_pos = None
        self.text_buffer = ""

        # Status Notification
        self.status_msg = "Shortcuts: [1/2/3] Brush Size | [Ctrl+S] Save PNG | [Enter/Esc] Text"
        self.status_timer = 0

        # Build UI Hitboxes
        self.tool_buttons = []
        self.size_buttons = []
        self.color_buttons = []
        self._setup_ui()

    def _setup_ui(self):
        # Row 1: Tool buttons
        x_offset = 10
        for tool_id, label in TOOLS:
            rect = pygame.Rect(x_offset, 10, 72, 32)
            self.tool_buttons.append((rect, tool_id, label))
            x_offset += 76

        # Row 2 Left: Brush Size buttons
        x_offset = 10
        for label, size in BRUSH_SIZES:
            rect = pygame.Rect(x_offset, 52, 72, 32)
            self.size_buttons.append((rect, size, label))
            x_offset += 76

        # Row 2 Right: Color Palette
        x_offset = 270
        for color in PALETTE:
            rect = pygame.Rect(x_offset, 52, 32, 32)
            self.color_buttons.append((rect, color))
            x_offset += 38

    def set_status(self, message, duration_ms=3000):
        self.status_msg = message
        self.status_timer = pygame.time.get_ticks() + duration_ms

    def to_canvas_coords(self, screen_pos):
        return (screen_pos[0], screen_pos[1] - TOOLBAR_HEIGHT)

    def commit_text(self):
        if self.text_active and self.text_buffer and self.text_pos:
            text_surf = self.text_font.render(self.text_buffer, True, self.current_color)
            self.canvas.blit(text_surf, self.text_pos)
        self.text_active = False
        self.text_buffer = ""
        self.text_pos = None

    def save_canvas(self):
        # Commit any pending text before saving
        if self.text_active:
            self.commit_text()

        os.makedirs("saves", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join("saves", f"painting_{timestamp}.png")
        pygame.image.save(self.canvas, filename)
        self.set_status(f"Saved: {filename}")

    def handle_toolbar_click(self, pos):
        for rect, tool_id, _ in self.tool_buttons:
            if rect.collidepoint(pos):
                if self.text_active:
                    self.commit_text()
                self.current_tool = tool_id
                return

        for rect, size, _ in self.size_buttons:
            if rect.collidepoint(pos):
                self.brush_size = size
                return

        for rect, color in self.color_buttons:
            if rect.collidepoint(pos):
                self.current_color = color
                return

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            # --- Keyboard Events ---
            elif event.type == pygame.KEYDOWN:
                mods = pygame.key.get_mods()

                # Ctrl + S -> Save Canvas
                if (mods & pygame.KMOD_CTRL) and event.key == pygame.K_s:
                    self.save_canvas()
                    continue

                # Active Text Input Mode
                if self.text_active:
                    if event.key == pygame.K_RETURN:
                        self.commit_text()
                    elif event.key == pygame.K_ESCAPE:
                        self.text_active = False
                        self.text_buffer = ""
                        self.text_pos = None
                    elif event.key == pygame.K_BACKSPACE:
                        self.text_buffer = self.text_buffer[:-1]
                    else:
                        if event.unicode and event.unicode.isprintable():
                            self.text_buffer += event.unicode
                    continue

                # Brush Size Shortcuts (1, 2, 3)
                if event.key == pygame.K_1:
                    self.brush_size = 2
                elif event.key == pygame.K_2:
                    self.brush_size = 5
                elif event.key == pygame.K_3:
                    self.brush_size = 10

            # --- Mouse Button Down ---
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if event.pos[1] < TOOLBAR_HEIGHT:
                    self.handle_toolbar_click(event.pos)
                else:
                    canvas_pos = self.to_canvas_coords(event.pos)

                    if self.current_tool == "text":
                        if self.text_active:
                            self.commit_text()
                        self.text_active = True
                        self.text_pos = canvas_pos
                        self.text_buffer = ""

                    elif self.current_tool == "fill":
                        flood_fill(self.canvas, canvas_pos, self.current_color)

                    else:
                        self.drawing = True
                        self.start_pos = canvas_pos
                        self.last_pos = canvas_pos
                        if self.current_tool in ("pencil", "eraser"):
                            draw_color = WHITE if self.current_tool == "eraser" else self.current_color
                            pygame.draw.circle(self.canvas, draw_color, canvas_pos, self.brush_size // 2)

            # --- Mouse Motion ---
            elif event.type == pygame.MOUSEMOTION:
                if self.drawing:
                    canvas_pos = self.to_canvas_coords(event.pos)
                    if self.current_tool == "pencil":
                        pygame.draw.line(self.canvas, self.current_color, self.last_pos, canvas_pos, self.brush_size)
                        pygame.draw.circle(self.canvas, self.current_color, canvas_pos, self.brush_size // 2)
                        self.last_pos = canvas_pos
                    elif self.current_tool == "eraser":
                        pygame.draw.line(self.canvas, WHITE, self.last_pos, canvas_pos, self.brush_size * 2)
                        pygame.draw.circle(self.canvas, WHITE, canvas_pos, self.brush_size)
                        self.last_pos = canvas_pos

            # --- Mouse Button Up ---
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.drawing:
                    end_pos = self.to_canvas_coords(event.pos)
                    if self.current_tool not in ("pencil", "eraser", "fill", "text"):
                        draw_shape(
                            self.canvas,
                            self.current_tool,
                            self.start_pos,
                            end_pos,
                            self.current_color,
                            self.brush_size,
                        )
                    self.drawing = False
                    self.start_pos = None
                    self.last_pos = None

        return True

    def render(self):
        # 1. Blit persistent canvas
        self.screen.blit(self.canvas, (0, TOOLBAR_HEIGHT))

        # 2. Live Preview for dragged shapes/lines
        if self.drawing and self.current_tool not in ("pencil", "eraser", "fill", "text"):
            preview_surface = self.canvas.copy()
            current_canvas_pos = self.to_canvas_coords(pygame.mouse.get_pos())
            draw_shape(
                preview_surface,
                self.current_tool,
                self.start_pos,
                current_canvas_pos,
                self.current_color,
                self.brush_size,
            )
            self.screen.blit(preview_surface, (0, TOOLBAR_HEIGHT))

        # 3. Live Preview for Text Tool + Blinking Cursor
        if self.text_active and self.text_pos:
            cursor = "|" if (pygame.time.get_ticks() // 500) % 2 == 0 else ""
            display_text = self.text_buffer + cursor
            text_surf = self.text_font.render(display_text, True, self.current_color)
            screen_x = self.text_pos[0]
            screen_y = self.text_pos[1] + TOOLBAR_HEIGHT
            self.screen.blit(text_surf, (screen_x, screen_y))

        # 4. Draw Toolbar Background
        pygame.draw.rect(self.screen, GRAY, (0, 0, WIDTH, TOOLBAR_HEIGHT))
        pygame.draw.line(self.screen, DARK_GRAY, (0, TOOLBAR_HEIGHT - 1), (WIDTH, TOOLBAR_HEIGHT - 1), 2)

        # Draw Tool Buttons
        for rect, tool_id, label in self.tool_buttons:
            is_selected = self.current_tool == tool_id
            bg = ACCENT if is_selected else WHITE
            fg = WHITE if is_selected else BLACK
            pygame.draw.rect(self.screen, bg, rect, border_radius=5)
            pygame.draw.rect(self.screen, DARK_GRAY, rect, 1, border_radius=5)
            txt = self.ui_font.render(label, True, fg)
            self.screen.blit(txt, txt.get_rect(center=rect.center))

        # Draw Brush Size Buttons
        for rect, size, label in self.size_buttons:
            is_selected = self.brush_size == size
            bg = ACCENT if is_selected else WHITE
            fg = WHITE if is_selected else BLACK
            pygame.draw.rect(self.screen, bg, rect, border_radius=5)
            pygame.draw.rect(self.screen, DARK_GRAY, rect, 1, border_radius=5)
            txt = self.ui_font.render(label, True, fg)
            self.screen.blit(txt, txt.get_rect(center=rect.center))

        # Draw Color Palette
        for rect, color in self.color_buttons:
            pygame.draw.rect(self.screen, color, rect, border_radius=4)
            border_color = ACCENT if self.current_color == color else DARK_GRAY
            border_width = 3 if self.current_color == color else 1
            pygame.draw.rect(self.screen, border_color, rect, border_width, border_radius=4)

        # Draw Status / Help Text
        if self.status_timer and pygame.time.get_ticks() > self.status_timer:
            self.status_msg = "Shortcuts: [1/2/3] Brush Size | [Ctrl+S] Save PNG | [Enter/Esc] Text"
            self.status_timer = 0

        status_surf = self.ui_font.render(self.status_msg, True, (60, 60, 70))
        self.screen.blit(status_surf, (665, 60))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.render()
            self.clock.tick(FPS)
        pygame.quit()


if __name__ == "__main__":
    app = PaintApp()
    app.run()
    