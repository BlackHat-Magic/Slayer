from __future__ import annotations

from dataclasses import dataclass, field
from enum import auto, Enum
from typing import Any, Callable


class ContentType(Enum):
	TEXT = auto()
	IMAGE = auto()


class Unit(Enum):
	PX = auto()
	PERCENT = auto()


@dataclass
class Measurement:
	unit: Unit
	value: float


class Display(Enum):
	FLEX = auto()
	GRID = auto()  # NOTE: reserved for future grid support


class BoxSizing(Enum):
	BORDER_BOX = auto()
	CONTENT_BOX = auto()


class Direction(Enum):
	ROW = auto()
	ROW_REVERSE = auto()
	COLUMN = auto()
	COLUMN_REVERSE = auto()


class JustifyContent(Enum):
	START = auto()
	END = auto()
	CENTER = auto()
	BETWEEN = auto()
	AROUND = auto()
	EVENLY = auto()


class Align(Enum):
	AUTO = auto()
	START = auto()
	END = auto()
	CENTER = auto()
	BASELINE = auto()
	STRETCH = auto()
	SPACE_BETWEEN = auto()
	SPACE_AROUND = auto()
	SPACE_EVENLY = auto()


class Wrap(Enum):
	NOWRAP = auto()
	WRAP = auto()
	REVERSE = auto()


@dataclass
class Style:
	grow: float = 0.0
	shrink: float = 1.0
	basis: Measurement | None = None

	direction: Direction = Direction.ROW
	wrap: Wrap = Wrap.NOWRAP

	justify_content: JustifyContent = JustifyContent.START
	align_items: Align = Align.STRETCH
	align_content: Align = Align.STRETCH
	align_self: Align | None = None
	display: Display = Display.FLEX
	box_sizing: BoxSizing = BoxSizing.BORDER_BOX

	margin: list[Measurement] = field(default_factory=lambda: [
		Measurement(Unit.PX, 0.0),
		Measurement(Unit.PX, 0.0),
		Measurement(Unit.PX, 0.0),
		Measurement(Unit.PX, 0.0),
	])
	border: list[Measurement] = field(default_factory=lambda: [
		Measurement(Unit.PX, 0.0),
		Measurement(Unit.PX, 0.0),
		Measurement(Unit.PX, 0.0),
		Measurement(Unit.PX, 0.0),
	])
	padding: list[Measurement] = field(default_factory=lambda: [
		Measurement(Unit.PX, 0.0),
		Measurement(Unit.PX, 0.0),
		Measurement(Unit.PX, 0.0),
		Measurement(Unit.PX, 0.0),
	])
	row_gap: Measurement = field(default_factory=lambda: Measurement(Unit.PX, 0.0))
	column_gap: Measurement = field(default_factory=lambda: Measurement(Unit.PX, 0.0))

	background_color: list[float] = field(default_factory=lambda: [1.0, 1.0, 1.0, 1.0])
	border_color: list[float] = field(default_factory=lambda: [0.0, 0.0, 0.0, 0.0])
	color: list[float] = field(default_factory=lambda: [0.0, 0.0, 0.0, 1.0])

	width: Measurement | None = None
	min_width: Measurement | None = None
	max_width: Measurement | None = None
	height: Measurement | None = None
	min_height: Measurement | None = None
	max_height: Measurement | None = None


@dataclass
class Rect:
	x: float | None = None
	y: float | None = None
	w: float | None = None
	h: float | None = None


@dataclass
class Node:
	style: Style = field(default_factory=Style)
	parent: Node | None = None
	children: list[Node] = field(default_factory=list)
	content: Any = None
	content_type: ContentType = ContentType.TEXT

	border_box: Rect = field(default_factory=Rect)
	padding_box: Rect = field(default_factory=Rect)
	content_box: Rect = field(default_factory=Rect)

	def addChild(self, child: "Node") -> None:
		self.children.append(child)
		child.parent = self

	def removeChild(self, child: "Node") -> None:
		self.children.remove(child)
		child.parent = None

	def popChild(self, index: int = -1) -> "Node":
		child = self.children.pop(index)
		child.parent = None
		return child

	def isLeaf(self) -> bool:
		return len(self.children) == 0


@dataclass
class Window:
	width: int
	height: int


@dataclass
class RenderRect:
	x: float
	y: float
	w: float
	h: float
	background_color: list[float] = field(default_factory=lambda: [1.0, 1.0, 1.0, 1.0])
	border_color: list[float] = field(default_factory=lambda: [0.0, 0.0, 0.0, 0.0])


@dataclass
class RenderText:
	text: str
	x: float
	y: float
	color: list[float] = field(default_factory=lambda: [0.0, 0.0, 0.0, 1.0])


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_FLEX_EPSILON = 0.01
_FLEX_MAX_ITER = 100

_ROW_DIRECTIONS = (Direction.ROW, Direction.ROW_REVERSE)
_COL_DIRECTIONS = (Direction.COLUMN, Direction.COLUMN_REVERSE)


def _to_px(m: Measurement | None, parent_size: float = 0.0, default: float = 0.0) -> float:
	if m is None:
		return default
	if m.unit == Unit.PX:
		return m.value
	if m.unit == Unit.PERCENT:
		return m.value / 100.0 * parent_size
	return default


def _ensure(val: float | None) -> float:
	return val if val is not None else 0.0


def _mt(node: Node, parent_width: float = 0.0) -> float:
	return _to_px(node.style.margin[0], parent_width, 0.0)


def _mr(node: Node, parent_width: float = 0.0) -> float:
	return _to_px(node.style.margin[1], parent_width, 0.0)


def _mb(node: Node, parent_width: float = 0.0) -> float:
	return _to_px(node.style.margin[2], parent_width, 0.0)


def _ml(node: Node, parent_width: float = 0.0) -> float:
	return _to_px(node.style.margin[3], parent_width, 0.0)


def _bt(node: Node, parent_width: float = 0.0) -> float:
	return _to_px(node.style.border[0], parent_width, 0.0)


def _br(node: Node, parent_width: float = 0.0) -> float:
	return _to_px(node.style.border[1], parent_width, 0.0)


def _bb(node: Node, parent_width: float = 0.0) -> float:
	return _to_px(node.style.border[2], parent_width, 0.0)


def _bl(node: Node, parent_width: float = 0.0) -> float:
	return _to_px(node.style.border[3], parent_width, 0.0)


def _pt(node: Node, parent_width: float = 0.0) -> float:
	return _to_px(node.style.padding[0], parent_width, 0.0)


def _pr(node: Node, parent_width: float = 0.0) -> float:
	return _to_px(node.style.padding[1], parent_width, 0.0)


def _pb(node: Node, parent_width: float = 0.0) -> float:
	return _to_px(node.style.padding[2], parent_width, 0.0)


def _pl(node: Node, parent_width: float = 0.0) -> float:
	return _to_px(node.style.padding[3], parent_width, 0.0)


def _main_margin(node: Node, direction: Direction, parent_width: float = 0.0) -> float:
	# NOTE: percentage margins (including top/bottom) resolve against containing
	# block width, not height.  Per CSS 2.1 and flexbox specs, the containing
	# block width is always used for percentage margin resolution, so passing
	# parent_width for all directions is correct.
	if direction in _ROW_DIRECTIONS:
		return _ml(node, parent_width) + _mr(node, parent_width)
	return _mt(node, parent_width) + _mb(node, parent_width)


def _cross_margin(node: Node, direction: Direction, parent_width: float = 0.0) -> float:
	if direction in _ROW_DIRECTIONS:
		return _mt(node, parent_width) + _mb(node, parent_width)
	return _ml(node, parent_width) + _mr(node, parent_width)

# ---------------------------------------------------------------------------
# Line packing
# ---------------------------------------------------------------------------

def packNodeLines(
	node: Node,
	parent_width: float,
	parent_height: float,
	getStringSize: Callable[[str, Direction], float],
	getImageSize: Callable[[Any, Direction], float],
	main_gap: float = 0.0,
) -> list[list[Node]]:
	if node.isLeaf():
		return []
	if node.style.wrap == Wrap.NOWRAP:
		line = list(node.children)
		return [line]

	direction = node.style.direction
	if direction in _ROW_DIRECTIONS:
		inner_size = parent_width
	else:
		inner_size = parent_height

	current_size = 0.0
	lines: list[list[Node]] = []
	current_line: list[Node] = []

	for child in node.children:
		child_size = getNodeLineSize(child, direction, parent_width, parent_height,
									 getStringSize, getImageSize)
		child_margin = _main_margin(child, direction, parent_width)
		total = child_size + child_margin

		if not current_line:
			current_line.append(child)
			current_size = total
		elif current_size + total + main_gap <= inner_size:
			current_line.append(child)
			current_size += total + main_gap
		else:
			lines.append(current_line)
			current_line = [child]
			current_size = total

	if current_line:
		lines.append(current_line)

	# NOTE: packNodeLines rebuilds lines from scratch each call,
	# so multiple calls are safe and won't double-reverse.
	if node.style.wrap == Wrap.REVERSE:
		lines.reverse()

	return lines


# ---------------------------------------------------------------------------
# Node size helpers (for line-breaking decisions — returns main-axis size)
# ---------------------------------------------------------------------------

def _leaf_main_size(node: Node, direction: Direction, parent_w: float, parent_h: float,
					 getStringSize: Callable[[str, Direction], float],
					 getImageSize: Callable[[Any, Direction], float]) -> float:
	if direction in _ROW_DIRECTIONS and node.style.width is not None:
		raw = _to_px(node.style.width, parent_w)
		max_s = _to_px(node.style.max_width, parent_w, float("inf"))
		min_s = _to_px(node.style.min_width, parent_w, 0.0)
		if node.style.box_sizing == BoxSizing.CONTENT_BOX:
			bp = _bl(node, parent_w) + _br(node, parent_w) + _pl(node, parent_w) + _pr(node, parent_w)
			max_s = max_s + bp if max_s != float("inf") else float("inf")
			min_s = min_s + bp
			border_box = raw + bp
			return max(min_s, min(border_box, max_s))
		return max(min_s, min(raw, max_s))
	if direction in _COL_DIRECTIONS and node.style.height is not None:
		raw = _to_px(node.style.height, parent_h)
		max_s = _to_px(node.style.max_height, parent_h, float("inf"))
		min_s = _to_px(node.style.min_height, parent_h, 0.0)
		if node.style.box_sizing == BoxSizing.CONTENT_BOX:
			bp = _bt(node, parent_w) + _bb(node, parent_w) + _pt(node, parent_w) + _pb(node, parent_w)
			max_s = max_s + bp if max_s != float("inf") else float("inf")
			min_s = min_s + bp
			border_box = raw + bp
			return max(min_s, min(border_box, max_s))
		return max(min_s, min(raw, max_s))

	content_size = 0.0
	if node.content_type == ContentType.TEXT and node.content is not None:
		content_size = getStringSize(str(node.content), direction)
	elif node.content_type == ContentType.IMAGE and node.content is not None:
		content_size = getImageSize(node.content, direction)

	bp = _bl(node, parent_w) + _br(node, parent_w) + _pl(node, parent_w) + _pr(node, parent_w) if direction in _ROW_DIRECTIONS \
		else _bt(node, parent_w) + _bb(node, parent_w) + _pt(node, parent_w) + _pb(node, parent_w)

	if direction in _ROW_DIRECTIONS:
		max_s = _to_px(node.style.max_width, parent_w, float("inf"))
		min_s = _to_px(node.style.min_width, parent_w, 0.0)
	else:
		max_s = _to_px(node.style.max_height, parent_h, float("inf"))
		min_s = _to_px(node.style.min_height, parent_h, 0.0)

	if node.style.box_sizing == BoxSizing.CONTENT_BOX:
		max_s = max_s + bp if max_s != float("inf") else float("inf")
		min_s = min_s + bp
		border_box = content_size + bp
		return max(min_s, min(border_box, max_s))
	result = content_size + bp
	return max(min_s, min(result, max_s))

def getNodeLineSize(
	node: Node,
	direction: Direction,
	parent_width: float,
	parent_height: float,
	getStringSize: Callable[[str, Direction], float],
	getImageSize: Callable[[Any, Direction], float],
) -> float:
	if node.isLeaf():
		return _leaf_main_size(node, direction, parent_width, parent_height, getStringSize, getImageSize)

	if node.style.wrap == Wrap.NOWRAP:
		same_axis = (direction in _ROW_DIRECTIONS and node.style.direction in _ROW_DIRECTIONS) or \
					(direction in _COL_DIRECTIONS and node.style.direction in _COL_DIRECTIONS)
		if same_axis:
			wrapper_gap = _to_px(node.style.column_gap,
								 parent_width if direction in _ROW_DIRECTIONS else parent_height)
			result = sum(
				getNodeLineSize(c, direction, parent_width, parent_height,
								getStringSize, getImageSize)
				for c in node.children
			)
			n = len(node.children)
			if n > 1:
				result += (n - 1) * wrapper_gap
		else:
			children_sizes = [
				getNodeLineSize(c, direction, parent_width, parent_height,
								getStringSize, getImageSize)
				for c in node.children
			]
			result = max(children_sizes) if children_sizes else 0.0

		if direction in _ROW_DIRECTIONS:
			result += _bl(node, parent_width) + _br(node, parent_width) + _pl(node, parent_width) + _pr(node, parent_width)
		else:
			result += _bt(node, parent_width) + _bb(node, parent_width) + _pt(node, parent_width) + _pb(node, parent_width)

		# NOTE: explicit width/height replaces the gap-inclusive computed result.
		# This is by design — when the author specifies an explicit size the
		# gap contribution from the children is discarded.
		if direction in _ROW_DIRECTIONS and node.style.width is not None:
			result = _to_px(node.style.width, parent_width)
		elif direction in _COL_DIRECTIONS and node.style.height is not None:
			result = _to_px(node.style.height, parent_height)

		bp_w = _bl(node, parent_width) + _br(node, parent_width) + _pl(node, parent_width) + _pr(node, parent_width)
		bp_h = _bt(node, parent_width) + _bb(node, parent_width) + _pt(node, parent_width) + _pb(node, parent_width)
		if direction in _ROW_DIRECTIONS:
			if node.style.box_sizing == BoxSizing.CONTENT_BOX and node.style.width is not None:
				result += bp_w
			max_w = _to_px(node.style.max_width, parent_width, float("inf"))
			min_w = _to_px(node.style.min_width, parent_width, 0.0)
			if node.style.box_sizing == BoxSizing.CONTENT_BOX:
				max_w = max_w + bp_w if max_w != float("inf") else float("inf")
				min_w = min_w + bp_w
			result = max(min_w, min(result, max_w))
		else:
			if node.style.box_sizing == BoxSizing.CONTENT_BOX and node.style.height is not None:
				result += bp_h
			max_h = _to_px(node.style.max_height, parent_height, float("inf"))
			min_h = _to_px(node.style.min_height, parent_height, 0.0)
			if node.style.box_sizing == BoxSizing.CONTENT_BOX:
				max_h = max_h + bp_h if max_h != float("inf") else float("inf")
				min_h = min_h + bp_h
			result = max(min_h, min(result, max_h))
		return result

	bp_w = _bl(node, parent_width) + _br(node, parent_width) + _pl(node, parent_width) + _pr(node, parent_width)
	bp_h = _bt(node, parent_width) + _bb(node, parent_width) + _pt(node, parent_width) + _pb(node, parent_width)

	if node.style.box_sizing == BoxSizing.CONTENT_BOX:
		if node.style.width is not None:
			node_inner_w = _to_px(node.style.width, parent_width) + bp_w
		else:
			node_inner_w = parent_width
		max_w = _to_px(node.style.max_width, parent_width, float("inf"))
		min_w = _to_px(node.style.min_width, parent_width, 0.0)
		max_w = max_w + bp_w if max_w != float("inf") else float("inf")
		min_w = min_w + bp_w
		node_inner_w = max(min_w, min(node_inner_w, max_w))

		if node.style.height is not None:
			node_inner_h = _to_px(node.style.height, parent_height) + bp_h
		else:
			node_inner_h = parent_height
		max_h = _to_px(node.style.max_height, parent_height, float("inf"))
		min_h = _to_px(node.style.min_height, parent_height, 0.0)
		max_h = max_h + bp_h if max_h != float("inf") else float("inf")
		min_h = min_h + bp_h
		node_inner_h = max(min_h, min(node_inner_h, max_h))
	else:
		node_inner_w = parent_width
		node_inner_h = parent_height
		if node.style.width is not None:
			node_inner_w = _to_px(node.style.width, parent_width)
		if node.style.max_width is not None:
			node_inner_w = min(node_inner_w, _to_px(node.style.max_width, parent_width, float("inf")))
		if node.style.min_width is not None:
			node_inner_w = max(node_inner_w, _to_px(node.style.min_width, parent_width, 0.0))
		if node.style.height is not None:
			node_inner_h = _to_px(node.style.height, parent_height)
		if node.style.max_height is not None:
			node_inner_h = min(node_inner_h, _to_px(node.style.max_height, parent_height, float("inf")))
		if node.style.min_height is not None:
			node_inner_h = max(node_inner_h, _to_px(node.style.min_height, parent_height, 0.0))

	if direction in _ROW_DIRECTIONS and node.style.width is not None:
		return node_inner_w
	if direction in _COL_DIRECTIONS and node.style.height is not None:
		return node_inner_h

	content_w = node_inner_w - bp_w
	content_h = node_inner_h - bp_h
	is_row_wrapper = node.style.direction in _ROW_DIRECTIONS
	wrapper_main_gap = _to_px(node.style.column_gap, content_w if is_row_wrapper else content_h)
	lines = packNodeLines(node, content_w, content_h, getStringSize, getImageSize, wrapper_main_gap)
	if not lines:
		return 0.0

	return max(
		sum(
			getNodeLineSize(c, direction, content_w, content_h, getStringSize, getImageSize)
			for c in line
		) + (len(line) - 1) * wrapper_main_gap
		for line in lines
	)


# ---------------------------------------------------------------------------
# Main layout
# ---------------------------------------------------------------------------

def layoutNode(
	node: Node,
	x: float,
	y: float,
	parent_width: float,
	parent_height: float,
	getStringSize: Callable[[str, Direction], float],
	getImageSize: Callable[[Any, Direction], float],
	measureBaseline: Callable[[Node], float] | None = None,
) -> None:
	if node.style.display == Display.GRID:
		raise NotImplementedError("Display.GRID is not yet supported")
	direction = node.style.direction
	is_row = direction in _ROW_DIRECTIONS

	border_left = _bl(node, parent_width)
	border_right = _br(node, parent_width)
	border_top = _bt(node, parent_width)
	border_bottom = _bb(node, parent_width)
	padding_left = _pl(node, parent_width)
	padding_right = _pr(node, parent_width)
	padding_top = _pt(node, parent_width)
	padding_bottom = _pb(node, parent_width)

	node.border_box.x = x
	node.border_box.y = y
	node.padding_box.x = x + border_left
	node.padding_box.y = y + border_top
	node.content_box.x = x + border_left + padding_left
	node.content_box.y = y + border_top + padding_top

	if node.parent is not None:
		resolved_w = parent_width
		resolved_h = parent_height
		if node.style.box_sizing == BoxSizing.CONTENT_BOX:
			if node.style.max_width is not None:
				max_w_val = _to_px(node.style.max_width, parent_width, float("inf"))
				resolved_w = min(resolved_w, max_w_val + border_left + border_right + padding_left + padding_right)
			if node.style.min_width is not None:
				min_w_val = _to_px(node.style.min_width, parent_width, 0.0)
				resolved_w = max(resolved_w, min_w_val + border_left + border_right + padding_left + padding_right)
			if node.style.max_height is not None:
				max_h_val = _to_px(node.style.max_height, parent_height, float("inf"))
				resolved_h = min(resolved_h, max_h_val + border_top + border_bottom + padding_top + padding_bottom)
			if node.style.min_height is not None:
				min_h_val = _to_px(node.style.min_height, parent_height, 0.0)
				resolved_h = max(resolved_h, min_h_val + border_top + border_bottom + padding_top + padding_bottom)
		else:
			resolved_w = min(resolved_w, _to_px(node.style.max_width, parent_width, float("inf")))
			resolved_w = max(resolved_w, _to_px(node.style.min_width, parent_width, 0.0))
			resolved_h = min(resolved_h, _to_px(node.style.max_height, parent_height, float("inf")))
			resolved_h = max(resolved_h, _to_px(node.style.min_height, parent_height, 0.0))
	else:
		resolved_w = _to_px(node.style.width, parent_width) if node.style.width is not None else parent_width
		resolved_h = _to_px(node.style.height, parent_height) if node.style.height is not None else parent_height
		resolved_w = min(resolved_w, _to_px(node.style.max_width, parent_width, float("inf")))
		resolved_w = max(resolved_w, _to_px(node.style.min_width, parent_width, 0.0))
		resolved_h = min(resolved_h, _to_px(node.style.max_height, parent_height, float("inf")))
		resolved_h = max(resolved_h, _to_px(node.style.min_height, parent_height, 0.0))

	inner_width = max(0.0, resolved_w - border_left - border_right - padding_left - padding_right)
	inner_height = max(0.0, resolved_h - border_top - border_bottom - padding_top - padding_bottom)

	main_gap = _to_px(node.style.column_gap, inner_width if is_row else inner_height)
	cross_gap = _to_px(node.style.row_gap, inner_height if is_row else inner_width)

	lines = packNodeLines(node, inner_width, inner_height, getStringSize, getImageSize, main_gap)

	if node.isLeaf() or not lines:
		_resolve_leaf_or_empty(node, resolved_w, resolved_h,
							   parent_width, parent_height,
							   getStringSize, getImageSize)
		return

	_process_lines(lines, direction, is_row,
				   inner_width, inner_height, parent_width,
				   getStringSize, getImageSize, main_gap)

	_resolve_container_size(node, lines, direction, is_row,
							inner_width, inner_height, parent_width, parent_height,
							cross_gap, main_gap)

	_justify_content(node, lines, direction, is_row, inner_width, main_gap)

	_align_items(node, lines, direction, is_row, inner_width, measureBaseline)

	if len(lines) > 1:
		_align_content(node, lines, direction, is_row, inner_width, cross_gap, measureBaseline)

	for child in node.children:
		if child.isLeaf():
			continue
		if child.border_box.x is None or child.border_box.y is None:
			continue
		if child.border_box.w is None or child.border_box.h is None:
			continue
		# NOTE: passing child's own border_box as parent_width/parent_height
		# is intentional.  For flex items the border_box IS the containing
		# block against which percentage grandchild widths resolve (per CSS
		# flexbox spec), and percentage heights resolve against the used
		# block-size of the parent — which for a flex container is the
		# border_box height computed by this engine.
		cw = _ensure(child.border_box.w)
		ch = _ensure(child.border_box.h)
		layoutNode(child, _ensure(child.border_box.x), _ensure(child.border_box.y),
				   cw, ch, getStringSize, getImageSize, measureBaseline)


def _resolve_leaf_or_empty(node: Node,
						   resolved_w: float, resolved_h: float,
						   parent_width: float, parent_height: float,
						   getStringSize, getImageSize) -> None:
	border_left = _bl(node, parent_width)
	border_right = _br(node, parent_width)
	border_top = _bt(node, parent_width)
	border_bottom = _bb(node, parent_width)
	padding_left = _pl(node, parent_width)
	padding_right = _pr(node, parent_width)
	padding_top = _pt(node, parent_width)
	padding_bottom = _pb(node, parent_width)

	content_box = node.style.box_sizing == BoxSizing.CONTENT_BOX

	if node.style.width is not None:
		max_s = _to_px(node.style.max_width, parent_width, float("inf"))
		min_s = _to_px(node.style.min_width, parent_width, 0.0)
		if content_box:
			bp_w = border_left + border_right + padding_left + padding_right
			max_s = max_s + bp_w if max_s != float("inf") else float("inf")
			min_s = min_s + bp_w
			if node.parent is not None:
				border_box = max(min_s, min(resolved_w, max_s))
			else:
				border_box = max(min_s, min(resolved_w + bp_w, max_s))
			content_w = max(0.0, border_box - bp_w)
		else:
			resolved_w = max(min_s, min(resolved_w, max_s))
			content_w = max(0.0, resolved_w - border_left - border_right - padding_left - padding_right)
	else:
		content_w = 0.0
		if node.content_type == ContentType.TEXT and node.content is not None:
			content_w = getStringSize(str(node.content), Direction.ROW)
		elif node.content_type == ContentType.IMAGE and node.content is not None:
			content_w = getImageSize(node.content, Direction.ROW)
		max_w = _to_px(node.style.max_width, parent_width, float("inf"))
		min_w = _to_px(node.style.min_width, parent_width, 0.0)
		if not content_box:
			bp_w = border_left + border_right + padding_left + padding_right
			if node.style.max_width is not None:
				max_w = max(0.0, max_w - bp_w)
			if node.style.min_width is not None:
				min_w = max(0.0, min_w - bp_w)
		content_w = max(min_w, min(content_w, max_w))

	if node.style.height is not None:
		max_s = _to_px(node.style.max_height, parent_height, float("inf"))
		min_s = _to_px(node.style.min_height, parent_height, 0.0)
		if content_box:
			bp_h = border_top + border_bottom + padding_top + padding_bottom
			max_s = max_s + bp_h if max_s != float("inf") else float("inf")
			min_s = min_s + bp_h
			if node.parent is not None:
				border_box = max(min_s, min(resolved_h, max_s))
			else:
				border_box = max(min_s, min(resolved_h + bp_h, max_s))
			content_h = max(0.0, border_box - bp_h)
		else:
			resolved_h = max(min_s, min(resolved_h, max_s))
			content_h = max(0.0, resolved_h - border_top - border_bottom - padding_top - padding_bottom)
	else:
		content_h = 0.0
		if node.content_type == ContentType.TEXT and node.content is not None:
			content_h = getStringSize(str(node.content), Direction.COLUMN)
		elif node.content_type == ContentType.IMAGE and node.content is not None:
			content_h = getImageSize(node.content, Direction.COLUMN)
		max_h = _to_px(node.style.max_height, parent_height, float("inf"))
		min_h = _to_px(node.style.min_height, parent_height, 0.0)
		if not content_box:
			bp_h = border_top + border_bottom + padding_top + padding_bottom
			if node.style.max_height is not None:
				max_h = max(0.0, max_h - bp_h)
			if node.style.min_height is not None:
				min_h = max(0.0, min_h - bp_h)
		content_h = max(min_h, min(content_h, max_h))

	node.content_box.w = content_w
	node.content_box.h = content_h
	node.padding_box.w = content_w + padding_left + padding_right
	node.padding_box.h = content_h + padding_top + padding_bottom
	node.border_box.w = node.padding_box.w + border_left + border_right
	node.border_box.h = node.padding_box.h + border_top + border_bottom


def _process_lines(lines: list[list[Node]], direction: Direction, is_row: bool,
				   inner_width: float, inner_height: float,
				   parent_width: float,
				   getStringSize, getImageSize, main_gap: float = 0.0) -> None:
	for line in lines:
		_initialize_child_sizes(line, direction, is_row, inner_width, inner_height,
								getStringSize, getImageSize)
		_apply_flex_grow_shrink(line, direction, is_row, inner_width, inner_height,
								main_gap)


def _initialize_child_sizes(line: list[Node], direction: Direction, is_row: bool,
							inner_w: float, inner_h: float,
							getStringSize, getImageSize) -> None:
	for child in line:
		main_size = getNodeLineSize(child, direction, inner_w, inner_h,
									getStringSize, getImageSize)
		basis = child.style.basis
		if basis is not None:
			main_size = _to_px(basis, inner_w if is_row else inner_h)
			if is_row:
				max_s = _to_px(child.style.max_width, inner_w, float("inf"))
				min_s = _to_px(child.style.min_width, inner_w, 0.0)
			else:
				max_s = _to_px(child.style.max_height, inner_h, float("inf"))
				min_s = _to_px(child.style.min_height, inner_h, 0.0)
			if child.style.box_sizing == BoxSizing.CONTENT_BOX:
				bp = (_bl(child, inner_w) + _br(child, inner_w) + _pl(child, inner_w) + _pr(child, inner_w)
					  if is_row else _bt(child, inner_w) + _bb(child, inner_w) + _pt(child, inner_w) + _pb(child, inner_w))
				max_s = max_s + bp if max_s != float("inf") else float("inf")
				min_s = min_s + bp
				border_box = main_size + bp
				main_size = max(min_s, min(border_box, max_s))
			else:
				main_size = max(min_s, min(main_size, max_s))

		if is_row:
			cross_dir = Direction.COLUMN
		else:
			cross_dir = Direction.ROW
		cross_size = getNodeLineSize(child, cross_dir, inner_w, inner_h,
									 getStringSize, getImageSize)

		if is_row:
			max_cross = _to_px(child.style.max_height, inner_h, float("inf"))
			min_cross = _to_px(child.style.min_height, inner_h, 0.0)
			if child.style.box_sizing == BoxSizing.CONTENT_BOX:
				bp_cross = _bt(child, inner_w) + _bb(child, inner_w) + _pt(child, inner_w) + _pb(child, inner_w)
				max_cross = max_cross + bp_cross if max_cross != float("inf") else float("inf")
				min_cross = min_cross + bp_cross
			cross_size = max(min_cross, min(cross_size, max_cross))
		else:
			max_cross = _to_px(child.style.max_width, inner_w, float("inf"))
			min_cross = _to_px(child.style.min_width, inner_w, 0.0)
			if child.style.box_sizing == BoxSizing.CONTENT_BOX:
				bp_cross = _bl(child, inner_w) + _br(child, inner_w) + _pl(child, inner_w) + _pr(child, inner_w)
				max_cross = max_cross + bp_cross if max_cross != float("inf") else float("inf")
				min_cross = min_cross + bp_cross
			cross_size = max(min_cross, min(cross_size, max_cross))

		if is_row:
			child.border_box.w = main_size
			child.border_box.h = cross_size
			child.padding_box.w = max(0.0, child.border_box.w - _bl(child, inner_w) - _br(child, inner_w))
			child.padding_box.h = max(0.0, child.border_box.h - _bt(child, inner_w) - _bb(child, inner_w))
			child.content_box.w = max(0.0, child.padding_box.w - _pl(child, inner_w) - _pr(child, inner_w))
			child.content_box.h = max(0.0, child.padding_box.h - _pt(child, inner_w) - _pb(child, inner_w))
		else:
			child.border_box.h = main_size
			child.border_box.w = cross_size
			child.padding_box.h = max(0.0, child.border_box.h - _bt(child, inner_w) - _bb(child, inner_w))
			child.padding_box.w = max(0.0, child.border_box.w - _bl(child, inner_w) - _br(child, inner_w))
			child.content_box.h = max(0.0, child.padding_box.h - _pt(child, inner_w) - _pb(child, inner_w))
			child.content_box.w = max(0.0, child.padding_box.w - _pl(child, inner_w) - _pr(child, inner_w))


def _apply_flex_grow_shrink(line: list[Node], direction: Direction, is_row: bool,
							inner_width: float, inner_height: float,
							main_gap: float = 0.0) -> None:
	container_size = inner_width if is_row else inner_height
	total_growth = sum(c.style.grow for c in line)
	total_size = (len(line) - 1) * main_gap

	for child in line:
		m = _main_margin(child, direction, inner_width)
		if is_row:
			total_size += _ensure(child.border_box.w) + m
		else:
			total_size += _ensure(child.border_box.h) + m

	free_space = container_size - total_size

	_grow_children(line, is_row, free_space, total_growth,
				   inner_width, inner_height)
	total_size = _recalc_total(line, direction, is_row, inner_width, main_gap)
	free_space = container_size - total_size
	_shrink_children(line, is_row, free_space,
					 inner_width, inner_height)
	total_size = _recalc_total(line, direction, is_row, inner_width, main_gap)
	free_space = container_size - total_size
	if free_space > _FLEX_EPSILON:
		total_growth = sum(c.style.grow for c in line)
		_grow_children(line, is_row, free_space, total_growth,
					   inner_width, inner_height)


def _recalc_total(line: list[Node], direction: Direction, is_row: bool, container_width: float, main_gap: float = 0.0) -> float:
	total = (len(line) - 1) * main_gap
	for child in line:
		m = _main_margin(child, direction, container_width)
		if is_row:
			total += _ensure(child.border_box.w) + m
		else:
			total += _ensure(child.border_box.h) + m
	return total


def _grow_children(line: list[Node], is_row: bool,
				   free_space: float, total_growth: float,
				   container_width: float, container_height: float) -> None:
	_iterations = 0
	while free_space > _FLEX_EPSILON and total_growth > 0.0 and _iterations < _FLEX_MAX_ITER:
		iter_space = free_space
		for child in line:
			if child.style.grow == 0.0:
				continue
			extra = iter_space * (child.style.grow / total_growth)
			diff = 0.0

			if is_row:
				max_constraint = _to_px(child.style.max_width, container_width, float("inf"))
				if child.style.box_sizing == BoxSizing.CONTENT_BOX:
					max_constraint += _bl(child, container_width) + _br(child, container_width) + _pl(child, container_width) + _pr(child, container_width)
				current = _ensure(child.border_box.w)
				if current >= max_constraint:
					continue
				new_main = min(current + extra, max_constraint)
				diff = new_main - current

				child.border_box.w = new_main
				child.padding_box.w = max(0.0, new_main - _bl(child, container_width) - _br(child, container_width))
				child.content_box.w = max(0.0, child.padding_box.w - _pl(child, container_width) - _pr(child, container_width))
			else:
				max_constraint = _to_px(child.style.max_height, container_height, float("inf"))
				if child.style.box_sizing == BoxSizing.CONTENT_BOX:
					max_constraint += _bt(child, container_width) + _bb(child, container_width) + _pt(child, container_width) + _pb(child, container_width)
				current = _ensure(child.border_box.h)
				if current >= max_constraint:
					continue
				new_main = min(current + extra, max_constraint)
				diff = new_main - current

				child.border_box.h = new_main
				child.padding_box.h = max(0.0, new_main - _bt(child, container_width) - _bb(child, container_width))
				child.content_box.h = max(0.0, child.padding_box.h - _pt(child, container_width) - _pb(child, container_width))

			free_space -= diff
		total_growth = 0.0
		for child in line:
			if is_row:
				max_c = _to_px(child.style.max_width, container_width, float("inf"))
				if child.style.box_sizing == BoxSizing.CONTENT_BOX:
					max_c += _bl(child, container_width) + _br(child, container_width) + _pl(child, container_width) + _pr(child, container_width)
				if _ensure(child.border_box.w) < max_c - _FLEX_EPSILON:
					total_growth += child.style.grow
			else:
				max_c = _to_px(child.style.max_height, container_height, float("inf"))
				if child.style.box_sizing == BoxSizing.CONTENT_BOX:
					max_c += _bt(child, container_width) + _bb(child, container_width) + _pt(child, container_width) + _pb(child, container_width)
				if _ensure(child.border_box.h) < max_c - _FLEX_EPSILON:
					total_growth += child.style.grow

		_iterations += 1


def _shrink_children(line: list[Node], is_row: bool,
					 free_space: float,
					 container_width: float, container_height: float) -> None:
	_iterations = 0
	total_weighted_shrink = 0.0
	base_sizes: dict[int, float] = {}
	for idx, child in enumerate(line):
		if child.style.shrink == 0.0:
			continue
		if is_row:
			min_c = _to_px(child.style.min_width, container_width, 0.0)
			if child.style.box_sizing == BoxSizing.CONTENT_BOX:
				min_c += _bl(child, container_width) + _br(child, container_width) + _pl(child, container_width) + _pr(child, container_width)
			if _ensure(child.border_box.w) <= min_c + _FLEX_EPSILON:
				continue
		else:
			min_c = _to_px(child.style.min_height, container_height, 0.0)
			if child.style.box_sizing == BoxSizing.CONTENT_BOX:
				min_c += _bt(child, container_width) + _bb(child, container_width) + _pt(child, container_width) + _pb(child, container_width)
			if _ensure(child.border_box.h) <= min_c + _FLEX_EPSILON:
				continue
		base = _ensure(child.border_box.w) if is_row else _ensure(child.border_box.h)
		weight = child.style.shrink * base
		base_sizes[idx] = weight
		total_weighted_shrink += weight

	while free_space < -_FLEX_EPSILON and total_weighted_shrink > 0.0 and _iterations < _FLEX_MAX_ITER:
		iter_space = abs(free_space)
		for idx, child in enumerate(line):
			weight = base_sizes.get(idx, 0.0)
			if weight <= 0.0:
				continue
			diff = 0.0
			shrink_amount = iter_space * (weight / total_weighted_shrink)

			if is_row:
				min_constraint = _to_px(child.style.min_width, container_width, 0.0)
				if child.style.box_sizing == BoxSizing.CONTENT_BOX:
					min_constraint += _bl(child, container_width) + _br(child, container_width) + _pl(child, container_width) + _pr(child, container_width)
				current = _ensure(child.border_box.w)
				if current <= min_constraint:
					continue
				new_main = max(current - shrink_amount, min_constraint, 0.0)
				diff = new_main - current

				child.border_box.w = new_main
				child.padding_box.w = max(0.0, new_main - _bl(child, container_width) - _br(child, container_width))
				child.content_box.w = max(0.0, child.padding_box.w - _pl(child, container_width) - _pr(child, container_width))
			else:
				min_constraint = _to_px(child.style.min_height, container_height, 0.0)
				if child.style.box_sizing == BoxSizing.CONTENT_BOX:
					min_constraint += _bt(child, container_width) + _bb(child, container_width) + _pt(child, container_width) + _pb(child, container_width)
				current = _ensure(child.border_box.h)
				if current <= min_constraint:
					continue
				new_main = max(current - shrink_amount, min_constraint, 0.0)
				diff = new_main - current

				child.border_box.h = new_main
				child.padding_box.h = max(0.0, new_main - _bt(child, container_width) - _bb(child, container_width))
				child.content_box.h = max(0.0, child.padding_box.h - _pt(child, container_width) - _pb(child, container_width))

			free_space -= diff

		total_weighted_shrink = 0.0
		base_sizes = {}
		for idx, child in enumerate(line):
			if child.style.shrink == 0.0:
				continue
			if is_row:
				min_c = _to_px(child.style.min_width, container_width, 0.0)
				if child.style.box_sizing == BoxSizing.CONTENT_BOX:
					min_c += _bl(child, container_width) + _br(child, container_width) + _pl(child, container_width) + _pr(child, container_width)
				if _ensure(child.border_box.w) <= min_c + _FLEX_EPSILON:
					continue
			else:
				min_c = _to_px(child.style.min_height, container_height, 0.0)
				if child.style.box_sizing == BoxSizing.CONTENT_BOX:
					min_c += _bt(child, container_width) + _bb(child, container_width) + _pt(child, container_width) + _pb(child, container_width)
				if _ensure(child.border_box.h) <= min_c + _FLEX_EPSILON:
					continue
			base = _ensure(child.border_box.w) if is_row else _ensure(child.border_box.h)
			weight = child.style.shrink * base
			base_sizes[idx] = weight
			total_weighted_shrink += weight

		_iterations += 1


def _resolve_container_size(node: Node, lines: list[list[Node]], direction: Direction,
							is_row: bool, inner_width: float, inner_height: float,
							parent_width: float, parent_height: float,
							cross_gap: float, main_gap: float) -> None:
	main_axis_total = 0.0
	cross_axis_total = 0.0

	for i, line in enumerate(lines):
		line_main = 0.0
		line_cross = 0.0
		for child in line:
			if is_row:
				line_main += _ensure(child.border_box.w) + _main_margin(child, direction, inner_width)
				line_cross = max(line_cross, _ensure(child.border_box.h) + _cross_margin(child, direction, inner_width))
			else:
				line_main += _ensure(child.border_box.h) + _main_margin(child, direction, inner_width)
				line_cross = max(line_cross, _ensure(child.border_box.w) + _cross_margin(child, direction, inner_width))
		if len(line) > 1:
			line_main += (len(line) - 1) * main_gap
		main_axis_total = max(main_axis_total, line_main)
		cross_axis_total += line_cross
		if i < len(lines) - 1:
			cross_axis_total += cross_gap

	border_left = _bl(node, parent_width)
	border_right = _br(node, parent_width)
	border_top = _bt(node, parent_width)
	border_bottom = _bb(node, parent_width)
	padding_left = _pl(node, parent_width)
	padding_right = _pr(node, parent_width)
	padding_top = _pt(node, parent_width)
	padding_bottom = _pb(node, parent_width)

	if is_row:
		if node.style.width is not None:
			max_w = _to_px(node.style.max_width, parent_width, float("inf"))
			min_w = _to_px(node.style.min_width, parent_width, 0.0)
			if node.style.box_sizing == BoxSizing.CONTENT_BOX:
				raw = _to_px(node.style.width, parent_width)
				bp = border_left + border_right + padding_left + padding_right
				max_bp = max_w + bp if max_w != float("inf") else float("inf")
				min_bp = min_w + bp
				content_w = max(main_axis_total, inner_width, max(min_bp, min(raw + bp, max_bp)) - bp)
			else:
				content_w = max(main_axis_total, inner_width)
		elif node.style.wrap in (Wrap.WRAP, Wrap.REVERSE):
			content_w = inner_width
			max_w = _to_px(node.style.max_width, parent_width, float("inf"))
			min_w = _to_px(node.style.min_width, parent_width, 0.0)
			if node.style.box_sizing == BoxSizing.CONTENT_BOX:
				bp = border_left + border_right + padding_left + padding_right
				max_w = max_w + bp if max_w != float("inf") else float("inf")
				min_w = min_w + bp
				content_w = max(min_w, min(content_w + bp, max_w)) - bp
			else:
				content_w = max(min_w, min(content_w, max_w))
		else:
			content_w = max(main_axis_total, inner_width)
			max_w = _to_px(node.style.max_width, parent_width, float("inf"))
			min_w = _to_px(node.style.min_width, parent_width, 0.0)
			if node.style.box_sizing == BoxSizing.CONTENT_BOX:
				bp = border_left + border_right + padding_left + padding_right
				max_w = max_w + bp if max_w != float("inf") else float("inf")
				min_w = min_w + bp
				content_w = max(min_w, min(content_w + bp, max_w)) - bp
			else:
				content_w = max(min_w, min(content_w, max_w))

		if node.style.height is not None:
			max_h = _to_px(node.style.max_height, parent_height, float("inf"))
			min_h = _to_px(node.style.min_height, parent_height, 0.0)
			if node.style.box_sizing == BoxSizing.CONTENT_BOX:
				raw = _to_px(node.style.height, parent_height)
				bp = border_top + border_bottom + padding_top + padding_bottom
				max_bp = max_h + bp if max_h != float("inf") else float("inf")
				min_bp = min_h + bp
				content_h = max(cross_axis_total, inner_height, max(min_bp, min(raw + bp, max_bp)) - bp)
			else:
				content_h = max(cross_axis_total, inner_height)
		else:
			content_h = max(cross_axis_total, inner_height)
			max_h = _to_px(node.style.max_height, parent_height, float("inf"))
			min_h = _to_px(node.style.min_height, parent_height, 0.0)
			if node.style.box_sizing == BoxSizing.CONTENT_BOX:
				bp = border_top + border_bottom + padding_top + padding_bottom
				max_h = max_h + bp if max_h != float("inf") else float("inf")
				min_h = min_h + bp
				content_h = max(min_h, min(content_h + bp, max_h)) - bp
			else:
				content_h = max(min_h, min(content_h, max_h))

		node.content_box.w = content_w
		node.content_box.h = content_h
	else:
		if node.style.height is not None:
			max_h = _to_px(node.style.max_height, parent_height, float("inf"))
			min_h = _to_px(node.style.min_height, parent_height, 0.0)
			if node.style.box_sizing == BoxSizing.CONTENT_BOX:
				raw = _to_px(node.style.height, parent_height)
				bp = border_top + border_bottom + padding_top + padding_bottom
				max_bp = max_h + bp if max_h != float("inf") else float("inf")
				min_bp = min_h + bp
				content_h = max(main_axis_total, inner_height, max(min_bp, min(raw + bp, max_bp)) - bp)
			else:
				content_h = max(main_axis_total, inner_height)
		elif node.style.wrap in (Wrap.WRAP, Wrap.REVERSE):
			content_h = inner_height
			max_h = _to_px(node.style.max_height, parent_height, float("inf"))
			min_h = _to_px(node.style.min_height, parent_height, 0.0)
			if node.style.box_sizing == BoxSizing.CONTENT_BOX:
				bp = border_top + border_bottom + padding_top + padding_bottom
				max_h = max_h + bp if max_h != float("inf") else float("inf")
				min_h = min_h + bp
				content_h = max(min_h, min(content_h + bp, max_h)) - bp
			else:
				content_h = max(min_h, min(content_h, max_h))
		else:
			content_h = max(main_axis_total, inner_height)
			max_h = _to_px(node.style.max_height, parent_height, float("inf"))
			min_h = _to_px(node.style.min_height, parent_height, 0.0)
			if node.style.box_sizing == BoxSizing.CONTENT_BOX:
				bp = border_top + border_bottom + padding_top + padding_bottom
				max_h = max_h + bp if max_h != float("inf") else float("inf")
				min_h = min_h + bp
				content_h = max(min_h, min(content_h + bp, max_h)) - bp
			else:
				content_h = max(min_h, min(content_h, max_h))

		if node.style.width is not None:
			max_w = _to_px(node.style.max_width, parent_width, float("inf"))
			min_w = _to_px(node.style.min_width, parent_width, 0.0)
			if node.style.box_sizing == BoxSizing.CONTENT_BOX:
				raw = _to_px(node.style.width, parent_width)
				bp = border_left + border_right + padding_left + padding_right
				max_bp = max_w + bp if max_w != float("inf") else float("inf")
				min_bp = min_w + bp
				content_w = max(cross_axis_total, inner_width, max(min_bp, min(raw + bp, max_bp)) - bp)
			else:
				content_w = max(cross_axis_total, inner_width)
		else:
			content_w = max(cross_axis_total, inner_width)
			max_w = _to_px(node.style.max_width, parent_width, float("inf"))
			min_w = _to_px(node.style.min_width, parent_width, 0.0)
			if node.style.box_sizing == BoxSizing.CONTENT_BOX:
				bp = border_left + border_right + padding_left + padding_right
				max_w = max_w + bp if max_w != float("inf") else float("inf")
				min_w = min_w + bp
				content_w = max(min_w, min(content_w + bp, max_w)) - bp
			else:
				content_w = max(min_w, min(content_w, max_w))

		node.content_box.w = content_w
		node.content_box.h = content_h

	node.padding_box.w = node.content_box.w + padding_left + padding_right
	node.padding_box.h = node.content_box.h + padding_top + padding_bottom
	node.border_box.w = node.padding_box.w + border_left + border_right
	node.border_box.h = node.padding_box.h + border_top + border_bottom


def _justify_content(node: Node, lines: list[list[Node]], direction: Direction, is_row: bool, resolve_width: float, main_gap: float) -> None:
	content_x = _ensure(node.content_box.x)
	content_y = _ensure(node.content_box.y)
	content_w = _ensure(node.content_box.w)
	content_h = _ensure(node.content_box.h)
	justify = node.style.justify_content

	container_size = content_w if is_row else content_h

	for line in lines:
		total_children = 0.0
		for child in line:
			if is_row:
				total_children += _ensure(child.border_box.w) + _main_margin(child, direction, resolve_width)
			else:
				total_children += _ensure(child.border_box.h) + _main_margin(child, direction, resolve_width)
		total_children += (len(line) - 1) * main_gap

		remaining = container_size - total_children

		_gap, _start = _justify_offsets(justify, remaining, len(line),
													  content_x if is_row else content_y,
													  container_size, direction)

		is_reverse = direction in (Direction.ROW_REVERSE, Direction.COLUMN_REVERSE)

		if is_row:
			if is_reverse:
				for child in line:
					child.border_box.x = _start - _mr(child, resolve_width) - _ensure(child.border_box.w)
					child.padding_box.x = _ensure(child.border_box.x) + _bl(child, resolve_width)
					child.content_box.x = child.padding_box.x + _pl(child, resolve_width)
					_start -= _ensure(child.border_box.w) + _main_margin(child, direction, resolve_width) + _gap + main_gap
			else:
				for child in line:
					child.border_box.x = _start + _ml(child, resolve_width)
					child.padding_box.x = _ensure(child.border_box.x) + _bl(child, resolve_width)
					child.content_box.x = child.padding_box.x + _pl(child, resolve_width)
					_start += _ensure(child.border_box.w) + _main_margin(child, direction, resolve_width) + _gap + main_gap
		else:
			if is_reverse:
				for child in line:
					child.border_box.y = _start - _mb(child, resolve_width) - _ensure(child.border_box.h)
					child.padding_box.y = _ensure(child.border_box.y) + _bt(child, resolve_width)
					child.content_box.y = child.padding_box.y + _pt(child, resolve_width)
					_start -= _ensure(child.border_box.h) + _main_margin(child, direction, resolve_width) + _gap + main_gap
			else:
				for child in line:
					child.border_box.y = _start + _mt(child, resolve_width)
					child.padding_box.y = _ensure(child.border_box.y) + _bt(child, resolve_width)
					child.content_box.y = child.padding_box.y + _pt(child, resolve_width)
					_start += _ensure(child.border_box.h) + _main_margin(child, direction, resolve_width) + _gap + main_gap


def _justify_offsets(justify: JustifyContent, remaining: float, count: int,
					 content_start: float, container_size: float,
					 direction: Direction) -> tuple[float, float]:
	is_reverse = direction in (Direction.ROW_REVERSE, Direction.COLUMN_REVERSE)
	content_end = content_start + container_size

	if justify == JustifyContent.START:
		if is_reverse:
			return 0.0, content_end
		return 0.0, content_start
	elif justify == JustifyContent.END:
		if is_reverse:
			return 0.0, content_end - remaining
		return 0.0, content_start + remaining
	elif justify == JustifyContent.CENTER:
		if is_reverse:
			return 0.0, content_end - remaining / 2.0
		return 0.0, content_start + remaining / 2.0
	elif justify == JustifyContent.BETWEEN:
		if count > 1 and remaining > 0:
			gap = remaining / (count - 1)
			if is_reverse:
				return gap, content_end
			return gap, content_start
		if is_reverse:
			return 0.0, content_end
		return 0.0, content_start
	elif justify == JustifyContent.AROUND:
		if remaining > 0:
			half = remaining / count / 2.0
			gap = remaining / count
			if is_reverse:
				return gap, content_end - half
			return gap, content_start + half
		if is_reverse:
			return 0.0, content_end
		return 0.0, content_start
	elif justify == JustifyContent.EVENLY:
		if remaining > 0:
			space = remaining / (count + 1)
			if is_reverse:
				return space, content_end - space
			return space, content_start + space
		if is_reverse:
			return 0.0, content_end
		return 0.0, content_start
	return 0.0, content_start


def _align_items(node: Node, lines: list[list[Node]], direction: Direction, is_row: bool, resolve_width: float, measureBaseline: Callable[[Node], float] | None = None) -> None:
	content_x = _ensure(node.content_box.x)
	content_y = _ensure(node.content_box.y)
	container_cross = _ensure(node.content_box.h) if is_row else _ensure(node.content_box.w)
	align = node.style.align_items

	for line in lines:
		line_cross_size = container_cross
		if len(lines) > 1:
			line_cross_size = 0.0
			for child in line:
				if is_row:
					line_cross_size = max(line_cross_size, _ensure(child.border_box.h) + _cross_margin(child, direction, resolve_width))
				else:
					line_cross_size = max(line_cross_size, _ensure(child.border_box.w) + _cross_margin(child, direction, resolve_width))

		for child in line:
			child_align = child.style.align_self if (child.style.align_self is not None and child.style.align_self != Align.AUTO) else align

			if child_align == Align.STRETCH:
				has_explicit_cross = (is_row and child.style.height is not None) or (not is_row and child.style.width is not None)
				if not has_explicit_cross:
					new_cross = line_cross_size - _cross_margin(child, direction, resolve_width)
					if is_row:
						max_h = _to_px(child.style.max_height, _ensure(node.content_box.h), float("inf"))
						min_h = _to_px(child.style.min_height, _ensure(node.content_box.h), 0.0)
						if child.style.box_sizing == BoxSizing.CONTENT_BOX:
							bp = _bt(child, resolve_width) + _bb(child, resolve_width) + _pt(child, resolve_width) + _pb(child, resolve_width)
							max_h = max_h + bp if max_h != float("inf") else float("inf")
							min_h = min_h + bp
							new_cross = max(min_h, min(new_cross, max_h))
							child.border_box.h = new_cross
							child.padding_box.h = max(0.0, new_cross - _bt(child, resolve_width) - _bb(child, resolve_width))
							child.content_box.h = max(0.0, child.padding_box.h - _pt(child, resolve_width) - _pb(child, resolve_width))
						else:
							new_cross = max(min_h, min(new_cross, max_h))
							child.border_box.h = new_cross
							child.padding_box.h = max(0.0, new_cross - _bt(child, resolve_width) - _bb(child, resolve_width))
							child.content_box.h = max(0.0, child.padding_box.h - _pt(child, resolve_width) - _pb(child, resolve_width))
					else:
						max_w = _to_px(child.style.max_width, _ensure(node.content_box.w), float("inf"))
						min_w = _to_px(child.style.min_width, _ensure(node.content_box.w), 0.0)
						if child.style.box_sizing == BoxSizing.CONTENT_BOX:
							bp = _bl(child, resolve_width) + _br(child, resolve_width) + _pl(child, resolve_width) + _pr(child, resolve_width)
							max_w = max_w + bp if max_w != float("inf") else float("inf")
							min_w = min_w + bp
							new_cross = max(min_w, min(new_cross, max_w))
							child.border_box.w = new_cross
							child.padding_box.w = max(0.0, new_cross - _bl(child, resolve_width) - _br(child, resolve_width))
							child.content_box.w = max(0.0, child.padding_box.w - _pl(child, resolve_width) - _pr(child, resolve_width))
						else:
							new_cross = max(min_w, min(new_cross, max_w))
							child.border_box.w = new_cross
							child.padding_box.w = max(0.0, new_cross - _bl(child, resolve_width) - _br(child, resolve_width))
							child.content_box.w = max(0.0, child.padding_box.w - _pl(child, resolve_width) - _pr(child, resolve_width))

		line_max_baseline = None
		if measureBaseline is not None:
			for child in line:
				c_align = child.style.align_self if (child.style.align_self is not None and child.style.align_self != Align.AUTO) else align
				if c_align == Align.BASELINE and child.content_type == ContentType.TEXT:
					bl = measureBaseline(child)
					if line_max_baseline is None or bl > line_max_baseline:
						line_max_baseline = bl

		line_cross_ref = container_cross if len(lines) == 1 else line_cross_size
		for child in line:
			child_align = child.style.align_self if (child.style.align_self is not None and child.style.align_self != Align.AUTO) else align
			if is_row:
				child_h = _ensure(child.border_box.h)
				cross_m = _cross_margin(child, direction, resolve_width)
				remaining = line_cross_ref - child_h - cross_m
				child.border_box.y = content_y + _mt(child, resolve_width) + _cross_pos(child_align, remaining, child, measureBaseline, line_max_baseline)
				child.padding_box.y = _ensure(child.border_box.y) + _bt(child, resolve_width)
				child.content_box.y = child.padding_box.y + _pt(child, resolve_width)
			else:
				child_w = _ensure(child.border_box.w)
				cross_m = _cross_margin(child, direction, resolve_width)
				remaining = line_cross_ref - child_w - cross_m
				child.border_box.x = content_x + _ml(child, resolve_width) + _cross_pos(child_align, remaining, child, measureBaseline, line_max_baseline)
				child.padding_box.x = _ensure(child.border_box.x) + _bl(child, resolve_width)
				child.content_box.x = child.padding_box.x + _pl(child, resolve_width)


def _cross_pos(align: Align, remaining: float, child: Node | None = None, measureBaseline: Callable[[Node], float] | None = None, max_baseline: float | None = None) -> float:
	if align == Align.START:
		return 0.0
	elif align == Align.END:
		return remaining
	elif align == Align.CENTER:
		return remaining / 2.0
	elif align == Align.BASELINE:
		if child is not None and measureBaseline is not None and max_baseline is not None and child.content_type == ContentType.TEXT:
			child_baseline = measureBaseline(child)
			return max_baseline - child_baseline
		return 0.0
	return 0.0

def _align_content(node: Node, lines: list[list[Node]], direction: Direction,
				   is_row: bool, resolve_width: float, base_gap: float,
				   measureBaseline: Callable[[Node], float] | None = None) -> None:
	container_cross = _ensure(node.content_box.h) if is_row else _ensure(node.content_box.w)
	align_content = node.style.align_content

	n = len(lines)

	total_cross = 0.0
	line_sizes: list[float] = []
	for line in lines:
		line_cross = 0.0
		for child in line:
			if is_row:
				line_cross = max(line_cross, _ensure(child.border_box.h) + _cross_margin(child, direction, resolve_width))
			else:
				line_cross = max(line_cross, _ensure(child.border_box.w) + _cross_margin(child, direction, resolve_width))
		line_sizes.append(line_cross)
		total_cross += line_cross

	remaining = container_cross - total_cross - (n - 1) * base_gap

	if align_content == Align.STRETCH and remaining > 0 and n > 0:
		extra_per_line = remaining / n
		for i in range(n):
			orig_line_size = line_sizes[i]
			for child in lines[i]:
				has_explicit_cross = (is_row and child.style.height is not None) or (not is_row and child.style.width is not None)
				if has_explicit_cross:
					continue
				child_align = child.style.align_self if (child.style.align_self is not None and child.style.align_self != Align.AUTO) else node.style.align_items
				if child_align != Align.STRETCH:
					continue
				if is_row:
					child_cross = _ensure(child.border_box.h) + _cross_margin(child, direction, resolve_width)
				else:
					child_cross = _ensure(child.border_box.w) + _cross_margin(child, direction, resolve_width)
				if child_cross >= orig_line_size - _FLEX_EPSILON:
					continue
				if is_row:
					max_h = _to_px(child.style.max_height, _ensure(child.parent.content_box.h) if child.parent else 0.0, float("inf"))
					min_h = _to_px(child.style.min_height, _ensure(child.parent.content_box.h) if child.parent else 0.0, 0.0)
					if child.style.box_sizing == BoxSizing.CONTENT_BOX:
						bp = _bt(child, resolve_width) + _bb(child, resolve_width) + _pt(child, resolve_width) + _pb(child, resolve_width)
						max_h = max_h + bp if max_h != float("inf") else float("inf")
						min_h = min_h + bp
						new_cross = max(min_h, min(_ensure(child.border_box.h) + extra_per_line, max_h))
						child.border_box.h = new_cross
						child.padding_box.h = max(0.0, new_cross - _bt(child, resolve_width) - _bb(child, resolve_width))
						child.content_box.h = max(0.0, child.padding_box.h - _pt(child, resolve_width) - _pb(child, resolve_width))
					else:
						new_cross = max(min_h, min(_ensure(child.border_box.h) + extra_per_line, max_h))
						child.border_box.h = new_cross
						child.padding_box.h = max(0.0, new_cross - _bt(child, resolve_width) - _bb(child, resolve_width))
						child.content_box.h = max(0.0, child.padding_box.h - _pt(child, resolve_width) - _pb(child, resolve_width))
				else:
					max_w = _to_px(child.style.max_width, _ensure(child.parent.content_box.w) if child.parent else 0.0, float("inf"))
					min_w = _to_px(child.style.min_width, _ensure(child.parent.content_box.w) if child.parent else 0.0, 0.0)
					if child.style.box_sizing == BoxSizing.CONTENT_BOX:
						bp = _bl(child, resolve_width) + _br(child, resolve_width) + _pl(child, resolve_width) + _pr(child, resolve_width)
						max_w = max_w + bp if max_w != float("inf") else float("inf")
						min_w = min_w + bp
						new_cross = max(min_w, min(_ensure(child.border_box.w) + extra_per_line, max_w))
						child.border_box.w = new_cross
						child.padding_box.w = max(0.0, new_cross - _bl(child, resolve_width) - _br(child, resolve_width))
						child.content_box.w = max(0.0, child.padding_box.w - _pl(child, resolve_width) - _pr(child, resolve_width))
					else:
						new_cross = max(min_w, min(_ensure(child.border_box.w) + extra_per_line, max_w))
						child.border_box.w = new_cross
						child.padding_box.w = max(0.0, new_cross - _bl(child, resolve_width) - _br(child, resolve_width))
						child.content_box.w = max(0.0, child.padding_box.w - _pl(child, resolve_width) - _pr(child, resolve_width))
			# Recompute actual line cross from children after stretching;
			# max-clamped children may not have consumed their full extra_per_line.
			actual_cross = 0.0
			for child in lines[i]:
				if is_row:
					actual_cross = max(actual_cross, _ensure(child.border_box.h) + _cross_margin(child, direction, resolve_width))
				else:
					actual_cross = max(actual_cross, _ensure(child.border_box.w) + _cross_margin(child, direction, resolve_width))
			line_sizes[i] = max(actual_cross, orig_line_size)
		remaining = max(0.0, container_cross - sum(line_sizes) - (n - 1) * base_gap)

		align = node.style.align_items
		content_y = _ensure(node.content_box.y)
		content_x = _ensure(node.content_box.x)
		for i in range(n):
			line_max_baseline = None
			if measureBaseline is not None:
				for child in lines[i]:
					c_align = child.style.align_self if (child.style.align_self is not None and child.style.align_self != Align.AUTO) else align
					if c_align == Align.BASELINE and child.content_type == ContentType.TEXT:
						bl = measureBaseline(child)
						if line_max_baseline is None or bl > line_max_baseline:
							line_max_baseline = bl
			for child in lines[i]:
				child_align = child.style.align_self if (child.style.align_self is not None and child.style.align_self != Align.AUTO) else align
				if child_align == Align.START:
					continue
				if is_row:
					child_cross_size = _ensure(child.border_box.h) + _cross_margin(child, direction, resolve_width)
					remaining_cross = line_sizes[i] - child_cross_size
					child.border_box.y = content_y + _mt(child, resolve_width) + _cross_pos(child_align, remaining_cross, child, measureBaseline, line_max_baseline)
					child.padding_box.y = _ensure(child.border_box.y) + _bt(child, resolve_width)
					child.content_box.y = child.padding_box.y + _pt(child, resolve_width)
				else:
					child_cross_size = _ensure(child.border_box.w) + _cross_margin(child, direction, resolve_width)
					remaining_cross = line_sizes[i] - child_cross_size
					child.border_box.x = content_x + _ml(child, resolve_width) + _cross_pos(child_align, remaining_cross, child, measureBaseline, line_max_baseline)
					child.padding_box.x = _ensure(child.border_box.x) + _bl(child, resolve_width)
					child.content_box.x = child.padding_box.x + _pl(child, resolve_width)

	wrap_reverse = node.style.wrap == Wrap.REVERSE
	_start_align = Align.END if wrap_reverse else Align.START
	_end_align = Align.START if wrap_reverse else Align.END

	if align_content == _end_align:
		offset = max(remaining, 0.0)
		gap = base_gap
	elif align_content == Align.CENTER:
		offset = max(remaining / 2.0, 0.0)
		gap = base_gap
	elif align_content == _start_align:
		offset = 0.0
		gap = base_gap
	elif align_content == Align.STRETCH:
		offset = 0.0
		gap = base_gap
	elif align_content == Align.SPACE_BETWEEN:
		if n > 1 and remaining > 0:
			gap = base_gap + remaining / (n - 1)
		else:
			gap = base_gap
		offset = 0.0
	elif align_content == Align.SPACE_AROUND:
		if remaining > 0:
			gap = base_gap + remaining / n
			offset = remaining / (2.0 * n)
		else:
			gap = base_gap
			offset = 0.0
	elif align_content == Align.SPACE_EVENLY:
		if remaining > 0:
			extra = remaining / (n + 1)
			gap = base_gap + extra
			offset = extra
		else:
			gap = base_gap
			offset = 0.0
	else:
		offset = 0.0
		gap = base_gap

	current_cross = offset
	for i, line in enumerate(lines):
		for child in line:
			if is_row:
				child.border_box.y = _ensure(child.border_box.y) + current_cross
				child.padding_box.y = _ensure(child.padding_box.y) + current_cross
				child.content_box.y = _ensure(child.content_box.y) + current_cross
			else:
				child.border_box.x = _ensure(child.border_box.x) + current_cross
				child.padding_box.x = _ensure(child.padding_box.x) + current_cross
				child.content_box.x = _ensure(child.content_box.x) + current_cross

		current_cross += line_sizes[i] + gap

