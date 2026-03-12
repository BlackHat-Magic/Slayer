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

def packNodeLines(
	node: Node,
	parent_width: float,
	parent_height: float,
	getStringSize: Callable[[str, Direction], float],
	getImageSize: Callable[[Image, Direction], float],
) -> list[list[Node]]:
	"""
	Pack the lines of a node if it has line wrapping
	"""

	if node.isLeaf():
		return []
	if node.style.wrap == Wrap.NOWRAP:
   		return [node.children]

	inner_size = 0
	if node.style.direction == Direction.ROW or node.style.direction == Direction.ROW_REVERSE:
		inner_size: float = parent_width - \
			node.style.margin[1] - node.style.margin[3] - \
			node.style.border[1] - node.style.border[3] - \
			node.style.padding[1] - node.style.padding[3]
	if node.style.direction == Direction.COLUMN or node.style.direction == Direction.COLUMN_REVERSE:
		inner_size: float = parent_height - \
			node.style.border[0] - node.style.border[2] - \
			node.style.padding[0] - node.style.padding[2]

	current_size = 0
	lines = []
	current_line = []

	for child in node.children:
		if current_size == 0:
			current_line.append(child)
			continue
		if current_size + getNodeLineSize(
			child,
			node.style.direction,
			getStringSize,
			getImageSize,
		) <= inner_size:
   			current_line.append(child)
   			continue
   		lines.append(current_line)
   		current_line = []
   	lines.append(current_line)	# append last current line
   	return lines

def getNodeLineSize(
	node: Node,
	direction: Direction,	# parent direction
	parent_size: float,
	getStringSize: Callable[[str, Direction], float],
	getImageSize: Callable[[Image, Direction], float],
) -> float:
	"""
	Gets the size of a node in a line
		width for nodes in flex-direction=row or flex-direction=row-reverse
		height for nodes in flex-direction=column or flex-direction=column-reverse
	"""
	content_size = 0
	if node.isLeaf():
		if node.content_type == ContentType.STRING:
			content_size = getStringSize(node.content, direction)
		elif node.content_type == ContentType.IMAGE:
			content_size = getImageSize(node.content, direction)
		else:
		   	raise NotImplementedError("Only getters for string, image width are implemented")
		if direction == Direction.ROW or direction == Direction.ROW_REVERSE:
			return node.style.border[1] + node.style.border[3] + \
				node.style.border[1] + node.style.border[3] + \
				content_size
		elif direction == Direction.COLUMN or direction == Direction.COLUMN_REVERSE:
			return node.style.border[0] + node.style.border[2] + \
				node.style.padding[0] + node.style.padding[2] + \
				content_size

	row_styles = [Direction.ROW, Direction.ROW_REVERSE]
	column_styles = [Direction.COLUMN, Direction.COLUMN_REVERSE]

	if node.style.wrap == Wrap.NOWRAP:
		if (direction in row_styles and node.style.direction in row_styles) \
			or (direction in column_styles and node.style.direction in column_styles):
			return sum([getNodeLineSize(
				child,
				direction,
				getStringSize,
				getImageSize,
			) for child in node.children])
		elif (direction in row_styles and node.style.direction in column_styles) \
			or (direction in column_styles and node.style.direction in row_styles):
			return max([getNodeLineSize(
				child,
				direction,
				getStringSize,
				getImageSize,
			) for child in node.children])
		else:
			raise ValueError("Invalid flex-direction")

	if direction == Direction.ROW or direction == Direction.ROW_REVERSE:

		lines = packNodeLines(node, 

def layoutNode(node: Node, parent_width: float, parent_height: float) -> None:
	"""
	Compute the layout for a node
	"""


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

