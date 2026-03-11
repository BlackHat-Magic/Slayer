from dataclasses import dataclass
from enum import auto, Enum
from typing import Any

# ===== MEASUREMENT =====

class Unit(Enum):
    """
    Choose what unit a measurement will be
    """

    PX = auto()
    VW = auto()
    VH = auto()
    PERCENT = auto()

@dataclass
class Measurement:
    """
    How wide/tall/etc something is
    """

    unit: Unit
    value: float

# ===== DISPLAY =====

class Display(Enum):
    """
    Display: flex, grid, block, etc
    """

    BLOCK = auto()
    FLEX = auto()
    GRID = auto()

# ===== FLEX =====

class Direction(Enum):
    """
    Flex direction
    """

    ROW = auto()
    ROW_REVERSE = auto()
    COLUMN = auto()
    COLUMN_REVERSE = auto()

class JustifyContent(Enum):
    """
    Justify content
    """

    START = auto()		# flex-start
    END = auto()		# flex-end
    CENTER = auto()
    BETWEEN = auto()	# space-between
    AROUND = auto()		# space-around
    EVENLY = auto()		# space-evenly

class Align(Enum):
    """
    Align items
    """

    AUTO = auto()
    START = auto()	# flex-start
    END = auto()	# flex-end
    CENTER = auto()
    BASELINE = auto()
    STRETCH = auto()

class Wrap(Enum):
    """
    Flex Wrap
    """

    NOWRAP = auto()
    WRAP = auto()
    REVERSE = auto()

@dataclass
class Style:
    """
    Flex style
    """

    grow: float = 0.0
    shrink: float = 1.0
    basis: float | None = None

    direction: Direction = Direction.ROW
    wrap: Wrap = Wrap.NOWRAP

    justify_content: JustifyContent = JustifyContent.START
    align: Align = Align.STRETCH
    align_self: Align | None = None

    margin: list[Measurement] = [
		Measurement(Unit.PX, 0.0),	# top
		Measurement(Unit.PX, 0.0),	# right
		Measurement(Unit.PX, 0.0),	# bottom
		Measurement(Unit.PX, 0.0),	# left
    ]
    border: list[Measurement] = [
		Measurement(Unit.PX, 0.0),	# top
		Measurement(Unit.PX, 0.0),	# right
		Measurement(Unit.PX, 0.0),	# bottom
		Measurement(Unit.PX, 0.0),	# left
    ]
    padding: list[Measurement] = [
		Measurement(Unit.PX, 0.0),	# top
		Measurement(Unit.PX, 0.0),	# right
		Measurement(Unit.PX, 0.0),	# bottom
		Measurement(Unit.PX, 0.0),	# left
    ]
    width: Measurement | None = None
    min_width: Measurement | None = None
    max_width: Measurement | None = None
    height: Measurement | None = None
    min_height: Measurement | None = None
    max_height: Measurement | None = None

    top: Measurement = Measurement(Unit.PX, 0.0)
    left: Measurement = Measurement(Unit.PX, 0.0)

class Node:
    style: Style = Style()
    parent: Node | None = None
    children: list[Node] = []
    content: Any

    computed: dict = {
		"border_box": {
			"x": None,
			"y": None,
			"w": None,
			"h": None
		},
		"padding_box": {
			"x": None,
			"y": None,
			"w": None,
			"h": None,
		},
		"content_box": {
			"x": None,
			"y": None,
			"w": None,
			"h": None,
		},
    }

def layoutNode(node: Node, parent_width: float, parent_height: float) -> None:
    """
    Compute the layout for a node
    """

	# determine available space (border-box by default)
    inner_width: float = parent_width - \
    	node.style.border[1] - node.style.border[3] - \
    	node.style.padding[1] - node.style.padding[3]
    inner_height: float = parent_height - \
    	node.style.border[0] - node.style.border[2] - \
    	node.style.padding[0] - node.style.padding[2]

    # TODO: split children into lines

    # process each line (???)
    for line in lines:
        # TODO: resolve main axis sizes (grow/shrink)
        # TODO: align with main axis (justify content)
        # TODO: align cross axis (align items)
        pass

    if len(lines) > 1:
        # TODO: align content if multiple lines exist
        pass

    for child in node.children:
        # child.x and child.y are now set (???)
        # child.width and child.height are now set (???)
        layoutNode(child, child.width, child.height)

