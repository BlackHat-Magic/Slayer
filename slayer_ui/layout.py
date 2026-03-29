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
	basis: float | None = None	# i forgor why i put this here

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

	# top: Measurement = Measurement(Unit.PX, 0.0)
	# left: Measurement = Measurement(Unit.PX, 0.0)

@dataclass
class Rect:
	x: float | None = None
	y: float | None = None
	w: float | None = None
	h: float | None = None

@dataclass
class Node:
	style: Style = Style()
	parent: Node | None = None
	children: list[Node] = []
	content: Any

	border_box: Rect = Rect()
	padding_box: Rect = Rect()
	content_box: Rect = Rect()

	def addChild(self, child: Node) -> None:
		self.children.append(child)
		child.parent = self

	def removeChild(self, child: Node) -> None:
		self.children.remove(child)
		child.parent = None

	def popChild(self, index=-1) -> Node:
		child = self.children[index]
		self.children.remove(child)
		child.parent = None
		return child

	def isLeaf(self) -> bool:
		return len(self.children) == 0

@dataclass
class Window:
	"""
	Placeholder window  struct
	"""
	width: int
	height: int

def measurementToPX(measurement: Measurement) -> float:
	"""
	Helper to get a measurement as pixels based on window dimensions
	"""

	if measurement.unit == Unit.PX:
		return measurement.value
	raise NotImplementedError("Percent units not implemented yet")

def packNodeLines(
	node: Node,
	parent_width: float,	# in px
	parent_height: float,	# in px
	window: Window,
	getStringSize: Callable[[str, Direction], float],
	getImageSize: Callable[[Image, Direction], float],
) -> list[list[Node]]:
	"""
	Pack the lines of a node if it has line wrapping
		node: Node
		parent_width: inner width of parent in px; assumes padding already subtracted
		parent_height: inner_width of parent in px; assumes padding already subtracted
		getStringSize: renderer function/method for getting the size of a string given a direction
		getImageSize: renderer function/method for getting the size of an image given a direction
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
			node.style.margin[0] - node.style.margin[2] - \
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
			inner_size,
			getStringSize,
			getImageSize,
		) <= inner_size:
			current_line.append(child)
			current_size += getNodeLineSize(
				node,
				node.style.direction,
				inner_size,
				window,
				getStringSize,
				getImageSize,
			)
			continue
		lines.append(current_line)
		current_line = []
	lines.append(current_line)	# append last current line
	return lines

def getNodeLineSize(
	node: Node,
	direction: Direction,	# parent direction
	parent_width: float,	# in px
	parent_height: float,	# in px
	window: Window,
	getStringSize: Callable[[str, Direction], float],
	getImageSize: Callable[[Image, Direction], float],
) -> float: # returns px
	"""
	Gets the size of a node in a line
	width for nodes in flex-direction=row or flex-direction=row-reverse
	height for nodes in flex-direction=column or flex-direction=column-reverse
		node: Node
		direction: Direction of parent
		parent_width: float in px; assumes padding already subtracted
		parent_height: float in px; assumes padding already subtracted
		getStringSize: renderer method/function for getting the size of a string given a direction
		getImageSize: renderer method/function for getting the size of an image given a direction
	TODO: consider flex-shrink for line breaks
	"""
	content_size = 0
	if node.isLeaf():
		if node.style.width is not None \
			and (node.style.direction in [Direction.ROW, Direction.ROW_REVERSE]):
			return measurementToPX(node.style.width)
		elif node.style.height is not None \
			and (node.style.direction in [Direction.COLUMN, Direction.COLUMN_REVERSE]):
			return measurementToPX(node.style.height)
		elif node.content_type == ContentType.STRING:
			content_size = getStringSize(node.content, direction)
		elif node.content_type == ContentType.IMAGE:
			content_size = getImageSize(node.content, direction)
		else:
			raise NotImplementedError("Only getters for string, image width are implemented")

		inner_size = content_size
		if direction == Direction.ROW or direction == Direction.ROW_REVERSE:
			inner_size += node.style.border[1] + node.style.border[3] + \
				node.style.padding[1] + node.style.padding[3]
			if node.style.max_width is not None:
				max_size = measurementToPX(node.style.max_width)
			else:
				max_size = float("inf")
			if node.style.min_width is not None:
				min_size = measurementToPX(node.style.min_width)
			else:
				min_size = 0
		elif direction == Direction.COLUMN or direction == Direction.COLUMN_REVERSE:
			inner_size = node.style.border[0] + node.style.border[2] + \
				node.style.padding[0] + node.style.padding[2]
			if node.style.max_height is not None:
				max_size = measurementToPX(node.style.max_height)
			else:
				max_size = float("inf")
			if node.style.min_height is not None:
				min_size = measurementToPX(node.style.min_height)
			else:
				min_size = 0
		else:
			raise ValueError("Invalid flex-direction")

		return min(max(min_size, content_size), max_size)

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

	if node.style.width is not None:
		parent_width_measurement = node.style.width
	elif node.style.max_width is not None:
		parent_width_measurement = node.style.max_width
	else:
		parent_width_measurement = Measurement(Unit.PX, float("inf"))
	if node.style.height is not None:
		parent_height = node.style.height
	elif node.style.max_height is not None:
		parent_height_measurement = node.style.max_height
	else:
		parent_width_measurement = Measurement(Unit.PX, float("inf"))
	parent_width = measurementToPX(parent_width_measurement)
	parent_height = measurementToPX(parent_height_measurement)
	lines = packNodeLines(
		node,
		parent_width,
		parent_height,
		window,
		getStringSize,
		getImageSize
	)

	inner_width = parent_width - node.style.margin[1] - node.style.margin[3] - \
		node.style.border[1] - node.style.border[3] - \
		node.style.padding[1] - node.style.padding[1]
	inner_height = parent_height - node.style.margin[0] - node.style.margin[2] - \
		node.style.border[0] - node.style.border[2] - \
		node.style.padding[0] - node.style.padding[2]

	return max(lines, key=lambda line: sum([getNodeLineSize(
		node,
		direction,
		inner_width,
		inner_height,
		window,
		getStringSize,
		getImageSize,
	) for node in line]))

def layoutNode(
	node: Node,
	x: float,
	y: float,
	parent_width: float,
	parent_height: float,
	window: Window,
	getStringSize: Callable[[str, Direction], float],
	getImageSize: Callable[[Image, Direction], float],
) -> None:
	"""
	Compute the layout for a node
	"""

	node.border_box.x = x
	node.border_box.y = y
	node.padding_box.x = node.border_box.x - node.border[3]
	node.padding_box.y = node.border_box.y - node.border[0]
	node.content_box.x = node.padding_box.x - node.padding[3]
	node.content_box.y = node.padding_box.y - node.padding[0]

	inner_width = parent_width - node.border[1] - node.border[3] - \
		node.padding[1] - node.padding[3]
	inner_height = parent_height - node.border[0] - node.border[2] - \
		node.padding[0] - node.padding[0]

	lines = packNodeLines(node, inner_width, inner_height, window)

	# process each line
	# TODO: margin???
	for line in lines:
		# resolve main axis sizes (grow/shrink)
		free_space = 0
		if node.style.direction in [Direction.ROW, Direction.ROW_REVERSE]:
			free_space = inner_width
		else:
			free_space = inner_height
		for child in line:
			# compute basis
			child_size = getNodeLineSize(
				node,
				node.style.direction,
				inner_width,
				inner_height,
				window,
				getStringSize,
				getImageSize
			)
			free_space -= child_size
			if node.style.direction in [Direction.ROW, Direction.ROW_REVERSE]:
				free_space -= child.style.margin[1] - child.style.margin[3]
				child.border_box.x = x + inner_width - free_space - child_size
				child.padding_box.x = child.border_box.x + child.style.border[3]
				child.content_box.x = child.padding_box.x + child.style.padding[3]
				child.border_box.w = child_size
				child.padding_box.w = child.border_box.w - \
					child.style.border[1] - child.style.border[3]
				child.content_box.w = child.padding_box.w - \
					child.style.padding[1] - child.style.padding[3]
			else:
				free_space -= child.style.margin[0] - child.style.margin[2]
				child.border_box.y = y + inner_width - free_space - child_size
				child.padding_box.x = child.border_box.x + child.style.border[0]
				child.content_box.x = child.padding_box.x + child.style.padding[0]
				child.padding_box.h = child.border_box.h - \
					child.style.border[0] - child.style.border[2]
				child.content_box.h = child.padding_box.h - \
					child.style.padding[0] - child.style.padding[2]
		total_growth = sum([child.style.grow for child in line])
		total_shrink = sum([child.style.shrink for child in line])
		total_size = 0
		if node.style.direction in [Direction.ROW, Direction.ROW_REVERSE]:
			total_size = inner_width - free_space
		else:
			total_size = inner_height - free_space
		while free_space > 0 and total_growth > 0:
			for child in line:
				child_growth = child.style.grow / total_growth * free_space
				if node.style.direction in [Direction.ROW, Direction.ROW_REVERSE]:
					new_width = min(child.border_box.w + child_growth, child.style.max_width)
					w_diff = new_width - child.border_box.w
					child.border_box.w += child_growth
					child.padding_box.w += child_growth
					child.content_box.w += child_growth
					free_space -= w_diff
				else:
					new_height = min(child.border_box.h + child_growth, child.style.max_height)
					h_diff = new_width - child.border_box.h
					child.border_box.h += child_growth
					child.padding_box.h += child_growth
					child.content_box.h += child_growth
					free_space -= h_diff
			total_growth = 0
			if node.style.direction in [Direction.ROW, Direction.ROW_REVERSE]:
				for child in line:
					if child.style.max_width <= child.border_box.w:
						continue
					total_growth += child.style.grow
			else:
				for child in line:
					if child.style.max_height <= child.border_box.h:
						continue
					total_growth += child.style.grow
		while free_space < 0 and total_shrink > 0:
			# remember: free_space is negative for math
			for child in line:
				child_portion = child.border_box.w / total_size * len(line)
				child_shrink = child.style.shrink / total_shrink * free_space * child_portion
				if node.style.direction in [Direction.ROW, Direction.ROW_REVERSE]:
					new_width = max(child.border_box.w + child_shrink, child.style.min_width)
					w_diff = new_width - child.border_box.w
					child.border_box.w -= child_shrink
					child.padding_box.w -= child_shrink
					child.content_box.w -= child_shrink
					free_space -= w_diff
				else:
					new_height = max(child.border_box.h + child_shrink, child.style.min_height)
					h_diff = new_height - child.border_box.h
					child.border_box.h -= child_shrink
					child.padding_box.h -= child_shrink
					child.content_box.h -= child_shrink
					free_space -= h_diff
			total_shrink = 0
			if node.style.direction in [Direction.ROW, Direction.ROW_REVERSE]:
				for child in line:
					if child.style.max_width <= child.border_box.w:
						continue
					total_shrink += child.style.shrink
			else:
				for child in line:
					if child.style.max_height <= child.border_box.h:
						continue
					total_shrink += child.style.shrink

	main_axis_size = 0
	cross_axis_size = 0
	if node.style.direction in [Direction.ROW, Direction.ROW_REVERSE]:
		main_axis_size = max(
			lines,
			key=lambda line: sum([
				child.border_box.w + child.style.margin[1] + child.style.margin[3] for child in line
			])
		)
		cross_axis_size = sum(
			[max([
				child.border_box.h + child.style.margin[0] + child.style.margin[2] for child in line
			]) for line in lines]
		)
		if node.style.width is not None:
			node.content_box.w = measurementToPX(node.style.width)
		else:
			node.content_box.w = min(max(main_axis_size, node.style.min_width), node.style.max_width)
		node.padding_box.w = node.content_box.w + node.style.padding[1] + node.style.padding[3]
		node.border_box.w = node.padding_box.w + node.style.border[1] + node.style.border[3]
		if node.style.height is not None:
			node.content_box.h = measurementToPX(node.style.width)
		else:
			node.content_box.h = min(max(cross_axis_size, node.style.min_height), node.style.max_height)
		node.padding_box.h = node.content_box.h + node.style.padding[0] + node.style.padding[2]
		node.border_box.h = node.padding_box.h + node.style.border[0] + node.style.border[2]
	else:
		main_axis_size = max(
			lines,
			key=lambda line: sum([
				child.border_box.h + child.style.margin[0] + child.style.margin[2] for child in line
			])
		)
		cross_axis_size = sum(
			[max([
				child.border_box.2 + child.style.margin[1] + child.style.margin[3] for child in line
			]) for line in lines]
		)
		node.content_box.w = cross_axis_size
		node.padding_box.w = node.content_box.w + node.style.padding[1] + node.style.padding[3]
		node.border_box.w = node.padding_box.w + node.style.border[1] + node.style.border[3]
		node.content_box.h = main_axis_size
		node.padding_box.h = node.content_box.h + node.style.padding[0] + node.style.padding[2]
		node.border_box.h = node.padding_box.h + node.style.border[0] + node.style.border[2]

	for line in lines:
	# align with main axis (justify content)
	# TODO: margin??
		if node.style.direction in [Direction.ROW, Direction.ROW_REVERSE]:
			if node.style.justify_content == JustifyContent.START:
				current_x = node.content_box.x
				for child in line:
					child.border_box.x = current_x
					child.padding_box.x = child.border_box.x + child.style.border[3]
					child.content_box.x = child.padding_box.x + child.style.padding[3]
					current_x += child.border_box.w
			elif node.style.justify_content == JustifyContent.END:
				current_x = node.content_box.x + node.content_box.w - main_axis_size
				for child in line:
					child.border_box.x = current_x
					child.padding_box.x = child.border_box.x + child.style.border[3]
					child.content_box.x = child.padding_box.x + child.style.padding[3]
					current_x += child.border_box.w
			elif node.style.justify_content == JustifyContent.CENTER:
				current_x = node.content_box.x + node.content_box.w / 2
				total_width = sum([child.border_box.w for child in line])
				current_x -= total_width / 2
				for child in line:
					child.border_box.x = current_x
					child.padding_box.x = child.border_box.x + child.style.border[3]
					child.content_box.x = child.padding_box.x + child.style.padding[3]
					current_x += child.border_box.w
			elif node.style.justify_content == JustifyContent.BETWEEN:
			elif node.style.justify_content == JustifyContent.AROUND:
			elif node.style.justify_content == JustifyContent.EVENLY:
		else:
			if node.style.justify_content == JustifyContent.START:
				for child in line:
					child.border_box.y = current_x
					child.padding_box.y = child.border_box.y + child.style.border[3]
					child.content_box.y = child.padding_box.y + child.style.padding[3]
					current_x += child.border_box.h
		# TODO: align cross axis (align items)
		pass

	if len(lines) > 1:
		# TODO: align content if multiple lines exist
		pass

	for child in node.children:
		# child.x and child.y are now set (???)
		# child.width and child.height are now set (???)
		layoutNode(child, child.width, child.height)

