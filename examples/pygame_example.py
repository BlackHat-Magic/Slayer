import pygame
from slayer_ui import UI


class PygameRenderer:
    def __init__(self, width, height, title="Slayer UI"):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)
        self.font = pygame.font.Font(None, 24)
        self.clock = pygame.time.Clock()
        self.running = True

    def draw_rect(self, x, y, width, height, color=(200, 200, 200), border=None):
        if color:
            pygame.draw.rect(self.screen, color, (x, y, width, height))
        if border:
            pygame.draw.rect(self.screen, border, (x, y, width, height), 2)

    def draw_text(self, text, x, y, color=(0, 0, 0), font_size=None):
        font = pygame.font.Font(None, font_size * 4 if font_size else 24)
        surface = font.render(text, True, color)
        self.screen.blit(surface, (x, y))

    def measure_text(self, text, font_size=None):
        font = pygame.font.Font(None, font_size * 4 if font_size else 24)
        surface = font.render(text, True, (0, 0, 0))
        return surface.get_width()

    def run(self, ui_callback):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.screen.fill((240, 240, 240))

            ui_callback(self)

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()


def main():
    renderer = PygameRenderer(800, 600, "Slayer UI - Pygame Renderer")
    ui = UI(renderer.draw_rect, renderer.draw_text, renderer.measure_text)

    def demo_ui(r):
        r.draw_rect(50, 50, 300, 200, color=(100, 150, 200), border=(50, 100, 150))
        r.draw_text("Hello, Slayer UI!", 70, 70, color=(255, 255, 255), font_size=16)

        r.draw_rect(50, 280, 300, 200, color=(200, 150, 100), border=(150, 100, 50))
        r.draw_text(
            "Pygame Renderer Example", 70, 300, color=(255, 255, 255), font_size=14
        )

        text = "This is a demonstration of the renderer interface."
        width = r.measure_text(text, font_size=12)
        r.draw_text(
            f"Text width: {width}px", 70, 330, color=(255, 255, 255), font_size=12
        )
        r.draw_text(text, 70, 350, color=(255, 255, 255), font_size=12)

    renderer.run(demo_ui)


if __name__ == "__main__":
    main()
