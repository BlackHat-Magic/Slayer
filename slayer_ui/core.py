from .layout import layoutNode, Window, ContentType


class UI:
    def __init__(self, draw_rect, draw_text, measure_text, measure_text_height=None, node=None):
        self.draw_rect = draw_rect
        self.draw_text = draw_text
        self.measure_text = measure_text
        self.measure_text_height = measure_text_height
        self.node = node

    def _render_node(self, node):
        bb = node.border_box
        if bb.x is not None and bb.y is not None and bb.w is not None and bb.h is not None and bb.w > 0 and bb.h > 0:
            self.draw_rect(
                bb.x, bb.y, bb.w, bb.h,
                color=node.style.background_color,
                border=node.style.border_color,
            )

        pb = node.padding_box
        if pb.x is not None and pb.y is not None and node.content:
            if node.content_type == ContentType.TEXT:
                self.draw_text(
                    str(node.content),
                    pb.x, pb.y,
                    color=node.style.color,
                )

        for child in node.children:
            self._render_node(child)

    def render(self, window_width=800, window_height=600):
        if self.node is None:
            return

        window = Window(window_width, window_height)

        def getStringSize(text, direction):
            if direction.name.startswith("COLUMN") and self.measure_text_height:
                return self.measure_text_height(text)
            return self.measure_text(text)

        def getImageSize(img, direction):
            return 0

        layoutNode(
            self.node,
            0, 0,
            float(window.width), float(window.height),
            window,
            getStringSize,
            getImageSize,
        )
        self._render_node(self.node)
