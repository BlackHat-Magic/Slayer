from dataclasses import dataclass
from enum import auto, Enum
from typing import Any, Callable

class ContentType(Enum):
    """
    Type of content inside of a node
    e.g., image, text, etc.
    """

    TEXT = auto()
    IMAGE = auto()
    SVG = auto()

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
    row_gap: Measurement = Measurement(Unit.PX, 0.0)
    column_gap: Measurement = Measurement(Unit.PX, 0.0)

    background_color: list[float] = [1.0, 1.0, 1.0, 1.0]	# rgba
    border_color: list[float] = [0.0, 0.0, 0.0, 0.0]		# rgba
    color: list[float] = [0.0, 0.0, 0.0, 1.0]				# rgba

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

    def isLeaf(self) -> bool:
        return len(self.children) == 0

def getNodeLineSize(
	node: Node,
	direction: Direction,
	getStringWidth: Callable[[str], float],
	getImageWidth: Callable[[Image], float],
	getSVGWidth: Callable[[str], float],
) -> float:
    """
    Gets the size of a node in a line
    	width for nodes in flex-direction=row or flex-direction=row-reverse
    	height for nodes in flex-direction=column or flex-direction=column-reverse
    """

	if direction == Direction.ROW or direction == Direction.ROW_REVERSE:
	    if node.isLeaf():
	        content_width = 0
	        if node.content_type == ContentType.STRING:
	            content_width = getStringWidth(node.content)
	        elif node.content_type == ContentType.IMAGE:
	            content_width = getImageWidth(node.content)
	        elif node.content_type == ContentType.SVG:
	            content_width = getSVGWidth(node.content)
	       	else:
	           	raise NotImplementedError("Only getters for string, image, svg width are implemented")

	        return node.style.border[1] + node.style.border[3] + \
	        	node.style.border[0] + node.style.border[0] + \
	        	content_width
	    if node.style.direction == Direction.ROW or node.style.direction == Direction.ROW_REVERSE:
    	    

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

