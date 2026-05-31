import pygame
from slayer_ui.layout import Node, Style, Direction, Unit, Measurement, JustifyContent, Align, Wrap
from slayer_ui import UI, RenderRect, RenderText

M = Measurement


def _to_pygame(c):
    if c is None:
        return None
    return tuple(int(v * 255) for v in c[:3])


class PygameRenderer:
    def __init__(self, width, height, title="Slayer UI"):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        pygame.display.set_caption(title)
        self.font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 18)
        self.clock = pygame.time.Clock()
        self.running = True

    def draw_rect(self, x, y, width, height, color=None, border=None):
        x, y, w, h = int(x), int(y), max(1, int(width)), max(1, int(height))
        if color:
            pygame.draw.rect(self.screen, _to_pygame(color), (x, y, w, h))
        if border and any(v > 0 for v in border[:3]):
            pygame.draw.rect(self.screen, _to_pygame(border), (x, y, w, h), 2)

    def draw_text(self, text, x, y, color=None):
        s = self.font.render(text, True, _to_pygame(color) or (0, 0, 0))
        self.screen.blit(s, (int(x), int(y)))

    def measure_text(self, text):
        return self.font.size(text)[0]

    def measure_text_height(self, text):
        return self.font.size(text)[1]

    def run(self, ui, root):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_f:
                        pygame.display.toggle_fullscreen()
                elif event.type == pygame.WINDOWRESIZED:
                    self.width = event.x
                    self.height = event.y
                elif event.type == pygame.VIDEORESIZE:
                    self.width = event.w
                    self.height = event.h

            self.screen.fill((240, 240, 240))

            commands = ui.compute_layout(root, self.width, self.height)
            for cmd in commands:
                if isinstance(cmd, RenderRect):
                    self.draw_rect(
                        cmd.x, cmd.y, cmd.w, cmd.h,
                        color=cmd.background_color,
                        border=cmd.border_color,
                    )
                elif isinstance(cmd, RenderText):
                    self.draw_text(cmd.text, cmd.x, cmd.y, color=cmd.color)

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()


def build_demo_tree():
    root = Node(style=Style(
        direction=Direction.ROW,
        justify_content=JustifyContent.START,
        align_items=Align.STRETCH,
        width=M(Unit.PERCENT, 100),
        height=M(Unit.PERCENT, 100),
        background_color=[0.2, 0.2, 0.3, 1.0],
        border_color=[0.4, 0.4, 0.5, 1.0],
        border=[M(Unit.PX, 5)] * 4,
        padding=[M(Unit.PX, 10)] * 4,
    ))

    sidebar = Node(content="Sidebar", style=Style(
        width=M(Unit.PERCENT, 25),
        min_width=M(Unit.PX, 120),
        max_width=M(Unit.PX, 300),
        background_color=[0.15, 0.15, 0.25, 1.0],
        border_color=[0.3, 0.3, 0.4, 1.0],
        border=[M(Unit.PX, 2)] * 4,
        padding=[M(Unit.PX, 10)] * 4,
        color=[0.7, 0.7, 0.8, 1.0],
    ))
    root.addChild(sidebar)

    main_area = Node(style=Style(
        grow=1.0,
        direction=Direction.COLUMN,
        justify_content=JustifyContent.START,
        align_items=Align.STRETCH,
        background_color=[0.25, 0.25, 0.35, 1.0],
        border_color=[0.3, 0.3, 0.4, 1.0],
        border=[M(Unit.PX, 2)] * 4,
        padding=[M(Unit.PX, 10)] * 4,
        margin=[M(Unit.PX, 0), M(Unit.PX, 0), M(Unit.PX, 0), M(Unit.PX, 10)],
    ))
    root.addChild(main_area)

    header = Node(content="Flexbox Layout Demo", style=Style(
        background_color=[0.3, 0.3, 0.45, 1.0],
        border_color=[0.5, 0.5, 0.6, 1.0],
        border=[M(Unit.PX, 2)] * 4,
        padding=[M(Unit.PX, 24)] * 4,
        margin=[M(Unit.PX, 0), M(Unit.PX, 0), M(Unit.PX, 8), M(Unit.PX, 0)],
        color=[1.0, 1.0, 1.0, 1.0],
        width=M(Unit.PERCENT, 100)
    ))
    main_area.addChild(header)

    body = Node(style=Style(
        direction=Direction.ROW,
        grow=1.0,
        justify_content=JustifyContent.CENTER,
        align_items=Align.CENTER,
        background_color=[0.2, 0.2, 0.3, 1.0],
        border_color=[0.3, 0.3, 0.4, 1.0],
        border=[M(Unit.PX, 2)] * 4,
        padding=[M(Unit.PX, 10)] * 4,
        wrap=Wrap.WRAP,
        row_gap=M(Unit.PX, 8),
        column_gap=M(Unit.PX, 8),
    ))
    main_area.addChild(body)

    for i in range(8):
        body.addChild(Node(content=f"Card {i + 1}", style=Style(
            width=M(Unit.PX, 140),
            min_width=M(Unit.PX, 100),
            background_color=[0.35, 0.45, 0.55, 1.0],
            border_color=[0.5, 0.6, 0.7, 1.0],
            border=[M(Unit.PX, 2)] * 4,
            padding=[M(Unit.PX, 12)] * 4,
            margin=[M(Unit.PX, 4)] * 4,
            color=[1.0, 1.0, 1.0, 1.0],
        )))

    return root


def main():
    renderer = PygameRenderer(800, 600, "Slayer UI - Flexbox Demo")
    root = build_demo_tree()
    ui = UI(renderer.measure_text, renderer.measure_text_height)
    renderer.run(ui, root)


if __name__ == "__main__":
    main()
