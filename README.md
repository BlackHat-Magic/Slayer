<div align="center">

# Slayer

A simple, immediate-mode UI library

</div>


## Overview

Slayer is a simple, immediate-mode UI library that aims to replicate the functionality of CSS's box model, flexbox, and grid.

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
from slayer_ui import UI

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

def draw_rect(
	x: int, y: int, w: int, h: int,
	color: list[float] | None = None,
	border: list[float] | None = None
) -> None:
	# Your super-awesome rect drawing function
	# e.g., wrapper around pygame.draw.rect()

def draw_text(text: str, x: int, y: int, color: list[float] | None = None) -> None:
	# Your super-awesome text drawing function
	# e.g., wrapper around pygame.screen.blit()

def measure_text(text: str) -> float:
	# a function to measure the width of a given string of text as rendered with your renderer
	# e.g., wrapper around pygame.font.Font.size()

def measure_text_height(text: str) -> float:
	# a function to measure the height of a given string of text as rendered with your renderer
	# e.g., wrapper around pygame.font.Font.size()

ui = UI(
	draw_rect,				# Slayer will use your function to draw the UI rects
	draw_text,				# Slayer will use your function to draw the UI text strings
	measure_text,			# Slayer will use your function to measure UI text (e.g., line wrapping)
	measure_text_height,	# Slayer will use your function to measure UI text height
)
ui.render(WINDOW_WIDTH, WINDOW_HEIGHT)	# Draw the UI to the screen
```

