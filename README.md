<div align="center">

# Slayer

A simple UI layout library

</div>


## Overview

Slayer is a simple UI library that aims to replicate the functionality of CSS's box model, flexbox, and grid.

### Features

- [X] Box model
- [X] Flexbox
- [ ] Grid

### Software Stack / Technologies Used

- Language: Python (initial implementation), Zig (final implementation), C (bindings planned), C++ (bindings planned)
- Framework: Pygame (initial renderer), SDL3 (planned example renderer), SFML (may make renderer in the future), Raylib (planned example renderer)

## Quickstart

Install Slayer:

```sh
uv add "git+https://github.com/BlackHat-Magic/Slayer"
```

Inside your business logic:

```python
from slayer_ui.layout import Node, Style, Direction, Unit, Measurement, JustifyContent, Align, Wrap
from slayer_ui import UI, RenderRect, RenderText

M = Measurement	# Not necessary; just a QOL thing

WINDOW_WIDTH: int = 800
WINDOW_HEIGHT: int = 600

root = Node(style=Style(
    direction=Direction.ROW,
    justify_content=JustifyContent.START,
    align_items=Align.STRETCH,
    width=M(Unit.PX, 790),
    height=M(Unit.PX, 390),
    background_color=[0.2, 0.2, 0.3, 1.0],
    border_color=[0.4, 0.4, 0.5, 1.0],
    border=[M(Unit.PX, 5)] * 4,
    padding=[M(Unit.PX, 10)] * 4,
))

header = Node(content="Hello, World!", style=Style(
    background_color=[0.3, 0.3, 0.45, 1.0],
    border_color=[0.5, 0.5, 0.6, 1.0],
    border=[M(Unit.PX, 2)] * 4,
    padding=[M(Unit.PX, 8)] * 4,
    margin=[M(Unit.PX, 0), M(Unit.PX, 0), M(Unit.PX, 8), M(Unit.PX, 0)],
    color=[1.0, 1.0, 1.0, 1.0],
))
root.addChild(header)

def measure_text(text: str) -> float:
    return len(text) * 8.0

def measure_text_height(text: str) -> float:
    return 16.0

ui = UI(measure_text, measure_text_height)

commands = ui.compute_layout(root, WINDOW_WIDTH, WINDOW_HEIGHT)
for cmd in commands:
    if isinstance(cmd, RenderRect):
        your_draw_rect(cmd.x, cmd.y, cmd.w, cmd.h, cmd.background_color, cmd.border_color, cmd.border_widths)
    elif isinstance(cmd, RenderText):
        your_draw_text(cmd.text, cmd.x, cmd.y, cmd.color)
```

