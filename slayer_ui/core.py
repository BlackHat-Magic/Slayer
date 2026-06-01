from .layout import layoutNode, Window, ContentType, RenderRect, RenderText


def collect_render_commands(node) -> list[RenderRect | RenderText]:
    commands: list[RenderRect | RenderText] = []
    _collect(node, commands)
    return commands


def _collect(node, commands: list):
    bb = node.border_box
    if (
        bb.x is not None
        and bb.y is not None
        and bb.w is not None
        and bb.h is not None
        and bb.w > 0
        and bb.h > 0
    ):
        commands.append(
            RenderRect(
                x=bb.x,
                y=bb.y,
                w=bb.w,
                h=bb.h,
                background_color=node.style.background_color,
                border_color=node.style.border_color,
            )
        )

    cb = node.content_box
    if cb.x is not None and cb.y is not None and node.content:
        if node.content_type == ContentType.TEXT:
            commands.append(
                RenderText(
                    x=cb.x,
                    y=cb.y,
                    text=str(node.content),
                    color=node.style.color,
                )
            )

    for child in node.children:
        _collect(child, commands)


class UI:
    def __init__(self, measure_text, measure_text_height=None, measure_baseline=None):
        self.measure_text = measure_text
        self.measure_text_height = measure_text_height
        self.measure_baseline = measure_baseline

    def compute_layout(
        self, node, window_width=800, window_height=600
    ) -> list[RenderRect | RenderText]:
        window = Window(window_width, window_height)

        def getStringSize(text, direction):
            if direction.name.startswith("COLUMN") and self.measure_text_height:
                return self.measure_text_height(text)
            return self.measure_text(text)

        def getImageSize(img, direction):
            return 0

        layoutNode(
            node,
            0,
            0,
            float(window.width),
            float(window.height),
            getStringSize,
            getImageSize,
            self.measure_baseline,
        )
        return collect_render_commands(node)
