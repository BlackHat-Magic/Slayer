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
	GRID = auto()


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
	basis: float | None = None

	direction: Direction = Direction.ROW
	wrap: Wrap = Wrap.NOWRAP

	justify_content: JustifyContent = JustifyContent.START
	align_items: Align = Align.STRETCH
	align_content: Align = Align.START
	align_self: Align | None = None
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
	border_widths: list[float] = field(default_factory=lambda: [0.0, 0.0, 0.0, 0.0])


@dataclass
class RenderText:
	text: str
	x: float
	y: float
	color: list[float] = field(default_factory=lambda: [0.0, 0.0, 0.0, 1.0])


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

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


def _mt(node: Node) -> float:
	return _to_px(node.style.margin[0])


def _mr(node: Node) -> float:
	return _to_px(node.style.margin[1])


def _mb(node: Node) -> float:
	return _to_px(node.style.margin[2])


def _ml(node: Node) -> float:
	return _to_px(node.style.margin[3])


def _bt(node: Node) -> float:
	return _to_px(node.style.border[0])


def _br(node: Node) -> float:
	return _to_px(node.style.border[1])


def _bb(node: Node) -> float:
	return _to_px(node.style.border[2])


def _bl(node: Node) -> float:
	return _to_px(node.style.border[3])


def _pt(node: Node) -> float:
	return _to_px(node.style.padding[0])


def _pr(node: Node) -> float:
	return _to_px(node.style.padding[1])


def _pb(node: Node) -> float:
	return _to_px(node.style.padding[2])


def _pl(node: Node) -> float:
	return _to_px(node.style.padding[3])


def _main_margin(node: Node, direction: Direction) -> float:
	if direction in _ROW_DIRECTIONS:
		return _ml(node) + _mr(node)
	return _mt(node) + _mb(node)


def _cross_margin(node: Node, direction: Direction) -> float:
	if direction in _ROW_DIRECTIONS:
		return _mt(node) + _mb(node)
	return _ml(node) + _mr(node)

# ---------------------------------------------------------------------------
# Line packing
# ---------------------------------------------------------------------------

def packNodeLines(
	node: Node,
	parent_width: float,
	parent_height: float,
	window: Window,
	getStringSize: Callable[[str, Direction], float],
	getImageSize: Callable[[Any, Direction], float],
	main_gap: float = 0.0,
) -> list[list[Node]]:
	if node.isLeaf():
		return []
	if node.style.wrap == Wrap.NOWRAP:
		return [list(node.children)]

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
									 window, getStringSize, getImageSize)
		child_margin = _main_margin(child, direction)
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

	if node.style.wrap == Wrap.REVERSE:
		lines.reverse()
	elif node.style.direction in (Direction.ROW_REVERSE, Direction.COLUMN_REVERSE):
		for i in range(len(lines)):
			lines[i].reverse()

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
			raw = min(max(min_s, raw), max_s)
			return raw + _bl(node) + _br(node) + _pl(node) + _pr(node)
		max_s = max_s + _bl(node) + _br(node) + _pl(node) + _pr(node) if node.style.max_width is not None else float("inf")
		min_s = min_s + _bl(node) + _br(node) + _pl(node) + _pr(node) if node.style.min_width is not None else 0.0
		return min(max(min_s, raw), max_s)
	if direction in _COL_DIRECTIONS and node.style.height is not None:
		raw = _to_px(node.style.height, parent_h)
		max_s = _to_px(node.style.max_height, parent_h, float("inf"))
		min_s = _to_px(node.style.min_height, parent_h, 0.0)
		if node.style.box_sizing == BoxSizing.CONTENT_BOX:
			raw = min(max(min_s, raw), max_s)
			return raw + _bt(node) + _bb(node) + _pt(node) + _pb(node)
		max_s = max_s + _bt(node) + _bb(node) + _pt(node) + _pb(node) if node.style.max_height is not None else float("inf")
		min_s = min_s + _bt(node) + _bb(node) + _pt(node) + _pb(node) if node.style.min_height is not None else 0.0
		return min(max(min_s, raw), max_s)

	content_size = 0.0
	if node.content_type == ContentType.TEXT and node.content is not None:
		content_size = getStringSize(str(node.content), direction)
	elif node.content_type == ContentType.IMAGE and node.content is not None:
		content_size = getImageSize(node.content, direction)

	bp = _bl(node) + _br(node) + _pl(node) + _pr(node) if direction in _ROW_DIRECTIONS \
		else _bt(node) + _bb(node) + _pt(node) + _pb(node)
	result = content_size + bp

	if direction in _ROW_DIRECTIONS:
		max_s = _to_px(node.style.max_width, parent_w, float("inf"))
		min_s = _to_px(node.style.min_width, parent_w, 0.0)
	else:
		max_s = _to_px(node.style.max_height, parent_h, float("inf"))
		min_s = _to_px(node.style.min_height, parent_h, 0.0)

	return min(max(min_s, result), max_s)

def getNodeLineSize(
	node: Node,
	direction: Direction,
	parent_width: float,
	parent_height: float,
	window: Window,
	getStringSize: Callable[[str, Direction], float],
	getImageSize: Callable[[Any, Direction], float],
) -> float:
	if node.isLeaf():
		return _leaf_main_size(node, direction, parent_width, parent_height, getStringSize, getImageSize)

	if direction in _ROW_DIRECTIONS and node.style.width is not None:
		raw = _to_px(node.style.width, parent_width)
		max_s = _to_px(node.style.max_width, parent_width, float("inf"))
		min_s = _to_px(node.style.min_width, parent_width, 0.0)
		if node.style.box_sizing == BoxSizing.CONTENT_BOX:
			raw = min(max(min_s, raw), max_s)
			return raw + _bl(node) + _br(node) + _pl(node) + _pr(node)
		max_s = max_s + _bl(node) + _br(node) + _pl(node) + _pr(node) if node.style.max_width is not None else float("inf")
		min_s = min_s + _bl(node) + _br(node) + _pl(node) + _pr(node) if node.style.min_width is not None else 0.0
		return min(max(min_s, raw), max_s)
	if direction in _COL_DIRECTIONS and node.style.height is not None:
		raw = _to_px(node.style.height, parent_height)
		max_s = _to_px(node.style.max_height, parent_height, float("inf"))
		min_s = _to_px(node.style.min_height, parent_height, 0.0)
		if node.style.box_sizing == BoxSizing.CONTENT_BOX:
			raw = min(max(min_s, raw), max_s)
			return raw + _bt(node) + _bb(node) + _pt(node) + _pb(node)
		max_s = max_s + _bt(node) + _bb(node) + _pt(node) + _pb(node) if node.style.max_height is not None else float("inf")
		min_s = min_s + _bt(node) + _bb(node) + _pt(node) + _pb(node) if node.style.min_height is not None else 0.0
		return min(max(min_s, raw), max_s)

	if node.style.wrap == Wrap.NOWRAP:
		same_axis = (direction in _ROW_DIRECTIONS and node.style.direction in _ROW_DIRECTIONS) or \
					(direction in _COL_DIRECTIONS and node.style.direction in _COL_DIRECTIONS)
		if same_axis:
			return sum(
				getNodeLineSize(c, direction, parent_width, parent_height,
								window, getStringSize, getImageSize)
				for c in node.children
			)
		else:
			children_sizes = [
				getNodeLineSize(c, direction, parent_width, parent_height,
								window, getStringSize, getImageSize)
				for c in node.children
			]
			return max(children_sizes) if children_sizes else 0.0

	node_inner_w = parent_width
	node_inner_h = parent_height

	if node.style.width is not None:
		node_inner_w = _to_px(node.style.width, parent_width)
	if node.style.max_width is not None:
		node_inner_w = min(node_inner_w, _to_px(node.style.max_width, parent_width, float("inf")))

	if node.style.height is not None:
		node_inner_h = _to_px(node.style.height, parent_height)
	if node.style.max_height is not None:
		node_inner_h = min(node_inner_h, _to_px(node.style.max_height, parent_height, float("inf")))

	content_w = node_inner_w - _bl(node) - _br(node) - _pl(node) - _pr(node)
	content_h = node_inner_h - _bt(node) - _bb(node) - _pt(node) - _pb(node)
	lines = packNodeLines(node, content_w, content_h, window, getStringSize, getImageSize)
	if not lines:
		return 0.0

	return max(
		sum(
			getNodeLineSize(c, direction, content_w, content_h, window, getStringSize, getImageSize)
			for c in line
		)
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
	window: Window,
	getStringSize: Callable[[str, Direction], float],
	getImageSize: Callable[[Any, Direction], float],
) -> None:
	direction = node.style.direction
	is_row = direction in _ROW_DIRECTIONS

	border_left = _bl(node)
	border_right = _br(node)
	border_top = _bt(node)
	border_bottom = _bb(node)
	padding_left = _pl(node)
	padding_right = _pr(node)
	padding_top = _pt(node)
	padding_bottom = _pb(node)

	node.border_box.x = x
	node.border_box.y = y
	node.padding_box.x = x + border_left
	node.padding_box.y = y + border_top
	node.content_box.x = x + border_left + padding_left
	node.content_box.y = y + border_top + padding_top

	resolved_w = _to_px(node.style.width, parent_width) if node.style.width is not None else parent_width
	resolved_h = _to_px(node.style.height, parent_height) if node.style.height is not None else parent_height
	resolved_w = min(resolved_w, _to_px(node.style.max_width, parent_width, float("inf")))
	resolved_w = max(resolved_w, _to_px(node.style.min_width, parent_width, 0.0))
	resolved_h = min(resolved_h, _to_px(node.style.max_height, parent_height, float("inf")))
	resolved_h = max(resolved_h, _to_px(node.style.min_height, parent_height, 0.0))

	if node.parent is not None:
		inner_width = parent_width
		inner_height = parent_height
	else:
		inner_width = resolved_w - border_left - border_right - padding_left - padding_right
		inner_height = resolved_h - border_top - border_bottom - padding_top - padding_bottom

	main_gap = _to_px(node.style.column_gap if is_row else node.style.row_gap, inner_width if is_row else inner_height)
	cross_gap = _to_px(node.style.row_gap if is_row else node.style.column_gap, inner_height if is_row else inner_width)

	lines = packNodeLines(node, inner_width, inner_height, window, getStringSize, getImageSize, main_gap)

	if node.isLeaf() or not lines:
		_resolve_leaf_or_empty(node, resolved_w, resolved_h,
							   getStringSize, getImageSize)
		return

	_process_lines(node, lines, direction, is_row,
				   inner_width, inner_height, parent_width, parent_height,
				   getStringSize, getImageSize, window)

	_resolve_container_size(node, lines, direction, is_row,
							inner_width, inner_height, parent_width, parent_height,
							cross_gap, main_gap)

	_justify_content(node, lines, direction, is_row, main_gap)

	_align_items(node, lines, direction, is_row)

	if len(lines) > 1:
		_align_content(node, lines, direction, is_row, cross_gap)

	for child in node.children:
		if child.isLeaf():
			continue
		if child.border_box.x is None or child.border_box.y is None:
			continue
		cw = _ensure(child.content_box.w)
		ch = _ensure(child.content_box.h)
		layoutNode(child, _ensure(child.border_box.x), _ensure(child.border_box.y),
				   cw, ch, window, getStringSize, getImageSize)


def _resolve_leaf_or_empty(node: Node,
						   parent_width: float, parent_height: float,
						   getStringSize, getImageSize) -> None:
	border_left = _bl(node)
	border_right = _br(node)
	border_top = _bt(node)
	border_bottom = _bb(node)
	padding_left = _pl(node)
	padding_right = _pr(node)
	padding_top = _pt(node)
	padding_bottom = _pb(node)

	content_box = node.style.box_sizing == BoxSizing.CONTENT_BOX

	if node.style.width is not None:
		raw = _to_px(node.style.width, parent_width)
		max_s = _to_px(node.style.max_width, parent_width, float("inf"))
		min_s = _to_px(node.style.min_width, parent_width, 0.0)
		if content_box:
			content_w = min(max(min_s, raw), max_s)
		else:
			max_s = max_s + border_left + border_right + padding_left + padding_right if node.style.max_width is not None else float("inf")
			min_s = min_s + border_left + border_right + padding_left + padding_right if node.style.min_width is not None else 0.0
			content_w = min(max(min_s, raw), max_s) - border_left - border_right - padding_left - padding_right
	else:
		content_w = 0.0
		if node.content_type == ContentType.TEXT and node.content is not None:
			content_w = getStringSize(str(node.content), Direction.ROW)
		elif node.content_type == ContentType.IMAGE and node.content is not None:
			content_w = getImageSize(node.content, Direction.ROW)
		max_w = _to_px(node.style.max_width, parent_width, float("inf"))
		min_w = _to_px(node.style.min_width, parent_width, 0.0)
		content_w = min(max(min_w, content_w), max_w)

	if node.style.height is not None:
		raw = _to_px(node.style.height, parent_height)
		max_s = _to_px(node.style.max_height, parent_height, float("inf"))
		min_s = _to_px(node.style.min_height, parent_height, 0.0)
		if content_box:
			content_h = min(max(min_s, raw), max_s)
		else:
			max_s = max_s + border_top + border_bottom + padding_top + padding_bottom if node.style.max_height is not None else float("inf")
			min_s = min_s + border_top + border_bottom + padding_top + padding_bottom if node.style.min_height is not None else 0.0
			content_h = min(max(min_s, raw), max_s) - border_top - border_bottom - padding_top - padding_bottom
	else:
		content_h = 0.0
		if node.content_type == ContentType.TEXT and node.content is not None:
			content_h = getStringSize(str(node.content), Direction.COLUMN)
		elif node.content_type == ContentType.IMAGE and node.content is not None:
			content_h = getImageSize(node.content, Direction.COLUMN)
		max_h = _to_px(node.style.max_height, parent_height, float("inf"))
		min_h = _to_px(node.style.min_height, parent_height, 0.0)
		content_h = min(max(min_h, content_h), max_h)

	node.content_box.w = content_w
	node.content_box.h = content_h
	node.padding_box.w = content_w + padding_left + padding_right
	node.padding_box.h = content_h + padding_top + padding_bottom
	node.border_box.w = node.padding_box.w + border_left + border_right
	node.border_box.h = node.padding_box.h + border_top + border_bottom


def _process_lines(node: Node, lines: list[list[Node]], direction: Direction, is_row: bool,
				   inner_width: float, inner_height: float,
				   parent_width: float, parent_height: float,
				   getStringSize, getImageSize, window: Window) -> None:
	for line in lines:
		_initialize_child_sizes(line, direction, is_row, inner_width, inner_height,
								parent_width, parent_height, getStringSize, getImageSize, window)
		_apply_flex_grow_shrink(line, direction, is_row, inner_width, inner_height,
								parent_width, parent_height)


def _initialize_child_sizes(line: list[Node], direction: Direction, is_row: bool,
							inner_w: float, inner_h: float,
							parent_w: float, parent_h: float,
							getStringSize, getImageSize, window: Window) -> None:
	for child in line:
		main_size = getNodeLineSize(child, direction, inner_w, inner_h,
									window, getStringSize, getImageSize)

		if is_row:
			cross_dir = Direction.COLUMN
		else:
			cross_dir = Direction.ROW
		cross_size = getNodeLineSize(child, cross_dir, inner_w, inner_h,
									 window, getStringSize, getImageSize)

		if is_row:
			child.border_box.w = main_size
			child.border_box.h = cross_size
			child.padding_box.w = child.border_box.w - _bl(child) - _br(child)
			child.padding_box.h = child.border_box.h - _bt(child) - _bb(child)
			child.content_box.w = child.padding_box.w - _pl(child) - _pr(child)
			child.content_box.h = child.padding_box.h - _pt(child) - _pb(child)
		else:
			child.border_box.h = main_size
			child.border_box.w = cross_size
			child.padding_box.h = child.border_box.h - _bt(child) - _bb(child)
			child.padding_box.w = child.border_box.w - _bl(child) - _br(child)
			child.content_box.h = child.padding_box.h - _pt(child) - _pb(child)
			child.content_box.w = child.padding_box.w - _pl(child) - _pr(child)


def _apply_flex_grow_shrink(line: list[Node], direction: Direction, is_row: bool,
							inner_width: float, inner_height: float,
							parent_width: float, parent_height: float) -> None:
	container_size = inner_width if is_row else inner_height
	total_growth = sum(c.style.grow for c in line)
	total_shrink = sum(c.style.shrink for c in line)
	total_size = 0.0

	for child in line:
		m = _main_margin(child, direction)
		if is_row:
			total_size += _ensure(child.border_box.w) + m
		else:
			total_size += _ensure(child.border_box.h) + m

	free_space = container_size - total_size

	_grow_children(line, direction, is_row, free_space, total_growth,
				   parent_width, parent_height)
	total_size = _recalc_total(line, direction, is_row)
	free_space = container_size - total_size
	_shrink_children(line, direction, is_row, free_space, total_shrink,
					 parent_width, parent_height)


def _recalc_total(line: list[Node], direction: Direction, is_row: bool) -> float:
	total = 0.0
	for child in line:
		m = _main_margin(child, direction)
		if is_row:
			total += _ensure(child.border_box.w) + m
		else:
			total += _ensure(child.border_box.h) + m
	return total


def _grow_children(line: list[Node], direction: Direction, is_row: bool,
				   free_space: float, total_growth: float,
				   parent_width: float, parent_height: float) -> None:
	_iterations = 0
	while free_space > 0.01 and total_growth > 0.0 and _iterations < 100:
		iter_space = free_space
		for child in line:
			if child.style.grow == 0.0:
				continue
			extra = iter_space * (child.style.grow / total_growth)
			diff = 0.0

			if is_row:
				max_constraint = _to_px(child.style.max_width, parent_width, float("inf"))
				current = _ensure(child.border_box.w)
				if current >= max_constraint:
					continue
				new_main = min(current + extra, max_constraint)
				diff = new_main - current

				child.border_box.w = new_main
				child.padding_box.w = new_main - _bl(child) - _br(child)
				child.content_box.w = child.padding_box.w - _pl(child) - _pr(child)
			else:
				max_constraint = _to_px(child.style.max_height, parent_height, float("inf"))
				current = _ensure(child.border_box.h)
				if current >= max_constraint:
					continue
				new_main = min(current + extra, max_constraint)
				diff = new_main - current

				child.border_box.h = new_main
				child.padding_box.h = new_main - _bt(child) - _bb(child)
				child.content_box.h = child.padding_box.h - _pt(child) - _pb(child)

			free_space -= diff
		total_growth = 0.0
		for child in line:
			if is_row:
				max_c = _to_px(child.style.max_width, parent_width, float("inf"))
				if _ensure(child.border_box.w) < max_c - 0.01:
					total_growth += child.style.grow
			else:
				max_c = _to_px(child.style.max_height, parent_height, float("inf"))
				if _ensure(child.border_box.h) < max_c - 0.01:
					total_growth += child.style.grow

		_iterations += 1


def _shrink_children(line: list[Node], direction: Direction, is_row: bool,
					 free_space: float, total_shrink: float,
					 parent_width: float, parent_height: float) -> None:
	_iterations = 0
	while free_space < -0.01 and total_shrink > 0.0 and _iterations < 100:
		iter_space = abs(free_space)
		for child in line:
			if child.style.shrink == 0.0:
				continue
			diff = 0.0
			shrink_amount = iter_space * (child.style.shrink / total_shrink)

			if is_row:
				min_constraint = _to_px(child.style.min_width, parent_width, 0.0)
				current = _ensure(child.border_box.w)
				if current <= min_constraint:
					continue
				new_main = max(current - shrink_amount, min_constraint)
				diff = new_main - current

				child.border_box.w = new_main
				child.padding_box.w = new_main - _bl(child) - _br(child)
				child.content_box.w = child.padding_box.w - _pl(child) - _pr(child)
			else:
				min_constraint = _to_px(child.style.min_height, parent_height, 0.0)
				current = _ensure(child.border_box.h)
				if current <= min_constraint:
					continue
				new_main = max(current - shrink_amount, min_constraint)
				diff = new_main - current

				child.border_box.h = new_main
				child.padding_box.h = new_main - _bt(child) - _bb(child)
				child.content_box.h = child.padding_box.h - _pt(child) - _pb(child)

			free_space -= diff

		total_shrink = 0.0
		for child in line:
			if is_row:
				min_c = _to_px(child.style.min_width, parent_width, 0.0)
				if _ensure(child.border_box.w) > min_c + 0.01:
					total_shrink += child.style.shrink
			else:
				min_c = _to_px(child.style.min_height, parent_height, 0.0)
				if _ensure(child.border_box.h) > min_c + 0.01:
					total_shrink += child.style.shrink

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
				line_main += _ensure(child.border_box.w) + _main_margin(child, direction)
				line_cross = max(line_cross, _ensure(child.border_box.h) + _cross_margin(child, direction))
			else:
				line_main += _ensure(child.border_box.h) + _main_margin(child, direction)
				line_cross = max(line_cross, _ensure(child.border_box.w) + _cross_margin(child, direction))
		if len(line) > 1:
			line_main += (len(line) - 1) * main_gap
		main_axis_total = max(main_axis_total, line_main)
		cross_axis_total += line_cross
		if i < len(lines) - 1:
			cross_axis_total += cross_gap

	border_left = _bl(node)
	border_right = _br(node)
	border_top = _bt(node)
	border_bottom = _bb(node)
	padding_left = _pl(node)
	padding_right = _pr(node)
	padding_top = _pt(node)
	padding_bottom = _pb(node)

	if is_row:
		if node.parent is not None:
			content_w = max(main_axis_total, inner_width)
		elif node.style.width is not None:
			raw = _to_px(node.style.width, parent_width)
			max_w = _to_px(node.style.max_width, parent_width, float("inf"))
			min_w = _to_px(node.style.min_width, parent_width, 0.0)
			if node.style.box_sizing == BoxSizing.CONTENT_BOX:
				content_w = min(max(min_w, raw), max_w)
			else:
				max_w = max_w + border_left + border_right + padding_left + padding_right if node.style.max_width is not None else float("inf")
				min_w = min_w + border_left + border_right + padding_left + padding_right if node.style.min_width is not None else 0.0
				content_w = min(max(min_w, raw), max_w) - border_left - border_right - padding_left - padding_right
		elif node.style.wrap == Wrap.WRAP:
			content_w = inner_width
		else:
			content_w = max(main_axis_total, inner_width)
			max_w = _to_px(node.style.max_width, parent_width, float("inf"))
			min_w = _to_px(node.style.min_width, parent_width, 0.0)
			content_w = min(max(min_w, content_w), max_w)

		if node.parent is not None:
			content_h = max(cross_axis_total, inner_height)
		elif node.style.height is not None:
			raw = _to_px(node.style.height, parent_height)
			max_h = _to_px(node.style.max_height, parent_height, float("inf"))
			min_h = _to_px(node.style.min_height, parent_height, 0.0)
			if node.style.box_sizing == BoxSizing.CONTENT_BOX:
				content_h = min(max(min_h, raw), max_h)
			else:
				max_h = max_h + border_top + border_bottom + padding_top + padding_bottom if node.style.max_height is not None else float("inf")
				min_h = min_h + border_top + border_bottom + padding_top + padding_bottom if node.style.min_height is not None else 0.0
				content_h = min(max(min_h, raw), max_h) - border_top - border_bottom - padding_top - padding_bottom
		else:
			content_h = max(cross_axis_total, inner_height)
			max_h = _to_px(node.style.max_height, parent_height, float("inf"))
			min_h = _to_px(node.style.min_height, parent_height, 0.0)
			content_h = min(max(min_h, content_h), max_h)

		node.content_box.w = content_w
		node.content_box.h = content_h
	else:
		if node.parent is not None:
			content_h = max(main_axis_total, inner_height)
		elif node.style.height is not None:
			raw = _to_px(node.style.height, parent_height)
			max_h = _to_px(node.style.max_height, parent_height, float("inf"))
			min_h = _to_px(node.style.min_height, parent_height, 0.0)
			if node.style.box_sizing == BoxSizing.CONTENT_BOX:
				content_h = min(max(min_h, raw), max_h)
			else:
				max_h = max_h + border_top + border_bottom + padding_top + padding_bottom if node.style.max_height is not None else float("inf")
				min_h = min_h + border_top + border_bottom + padding_top + padding_bottom if node.style.min_height is not None else 0.0
				content_h = min(max(min_h, raw), max_h) - border_top - border_bottom - padding_top - padding_bottom
		elif node.style.wrap == Wrap.WRAP:
			content_h = inner_height
		else:
			content_h = max(main_axis_total, inner_height)
			max_h = _to_px(node.style.max_height, parent_height, float("inf"))
			min_h = _to_px(node.style.min_height, parent_height, 0.0)
			content_h = min(max(min_h, content_h), max_h)

		if node.parent is not None:
			content_w = inner_width
		elif node.style.width is not None:
			raw = _to_px(node.style.width, parent_width)
			max_w = _to_px(node.style.max_width, parent_width, float("inf"))
			min_w = _to_px(node.style.min_width, parent_width, 0.0)
			if node.style.box_sizing == BoxSizing.CONTENT_BOX:
				content_w = min(max(min_w, raw), max_w)
			else:
				max_w = max_w + border_left + border_right + padding_left + padding_right if node.style.max_width is not None else float("inf")
				min_w = min_w + border_left + border_right + padding_left + padding_right if node.style.min_width is not None else 0.0
				content_w = min(max(min_w, raw), max_w) - border_left - border_right - padding_left - padding_right
		else:
			content_w = max(cross_axis_total, inner_width)
			max_w = _to_px(node.style.max_width, parent_width, float("inf"))
			min_w = _to_px(node.style.min_width, parent_width, 0.0)
			content_w = min(max(min_w, content_w), max_w)

		node.content_box.w = content_w
		node.content_box.h = content_h

	node.padding_box.w = node.content_box.w + padding_left + padding_right
	node.padding_box.h = node.content_box.h + padding_top + padding_bottom
	node.border_box.w = node.padding_box.w + border_left + border_right
	node.border_box.h = node.padding_box.h + border_top + border_bottom


def _justify_content(node: Node, lines: list[list[Node]], direction: Direction, is_row: bool, main_gap: float) -> None:
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
				total_children += _ensure(child.border_box.w) + _main_margin(child, direction)
			else:
				total_children += _ensure(child.border_box.h) + _main_margin(child, direction)
		total_children += (len(line) - 1) * main_gap

		remaining = container_size - total_children

		_gap, _start = _justify_offsets(justify, remaining, len(line),
										content_x if is_row else content_y,
										container_size, direction)

		if direction in (Direction.ROW_REVERSE, Direction.COLUMN_REVERSE):
			line = list(reversed(line))

		if is_row:
			for child in line:
				child.border_box.x = _start + _ml(child)
				child.padding_box.x = _ensure(child.border_box.x) + _bl(child)
				child.content_box.x = child.padding_box.x + _pl(child)
				_start += _ensure(child.border_box.w) + _main_margin(child, direction) + _gap + main_gap
		else:
			for child in line:
				child.border_box.y = _start + _mt(child)
				child.padding_box.y = _ensure(child.border_box.y) + _bt(child)
				child.content_box.y = child.padding_box.y + _pt(child)
				_start += _ensure(child.border_box.h) + _main_margin(child, direction) + _gap + main_gap


def _justify_offsets(justify: JustifyContent, remaining: float, count: int,
					 content_start: float, container_size: float,
					 direction: Direction) -> tuple[float, float]:
	is_reverse = direction in (Direction.ROW_REVERSE, Direction.COLUMN_REVERSE)
	if is_reverse:
		content_end = content_start + container_size

	if justify == JustifyContent.START:
		if is_reverse:
			return 0.0, content_end
		return 0.0, content_start
	elif justify == JustifyContent.END:
		if is_reverse:
			return 0.0, content_start
		return 0.0, content_start + remaining
	elif justify == JustifyContent.CENTER:
		return 0.0, content_start + remaining / 2.0
	elif justify == JustifyContent.BETWEEN:
		if count > 1:
			return remaining / (count - 1), content_start
		return 0.0, content_start
	elif justify == JustifyContent.AROUND:
		if remaining > 0:
			half = remaining / count / 2.0
			return remaining / count, content_start + half
		return 0.0, content_start + remaining / 2.0
	elif justify == JustifyContent.EVENLY:
		space = remaining / (count + 1)
		return space, content_start + space
	return 0.0, content_start


def _align_items(node: Node, lines: list[list[Node]], direction: Direction, is_row: bool) -> None:
	content_x = _ensure(node.content_box.x)
	content_y = _ensure(node.content_box.y)
	container_cross = _ensure(node.content_box.h) if is_row else _ensure(node.content_box.w)
	align = node.style.align_items

	for line in lines:
		for child in line:
			child_align = child.style.align_self if (child.style.align_self is not None and child.style.align_self != Align.AUTO) else align

		if child_align == Align.STRETCH:
			if is_row and child.style.height is not None:
				pass
			elif not is_row and child.style.width is not None:
				pass
			else:
				new_cross = container_cross - _cross_margin(child, direction)
				if is_row:
					child.border_box.h = new_cross
					child.padding_box.h = new_cross - _bt(child) - _bb(child)
					child.content_box.h = child.padding_box.h - _pt(child) - _pb(child)
				else:
					child.border_box.w = new_cross
					child.padding_box.w = new_cross - _bl(child) - _br(child)
					child.content_box.w = child.padding_box.w - _pl(child) - _pr(child)

		for child in line:
			child_align = child.style.align_self if (child.style.align_self is not None and child.style.align_self != Align.AUTO) else align

			if is_row:
				child_h = _ensure(child.border_box.h) + _cross_margin(child, direction)
				remaining = container_cross - child_h
				child.border_box.y = content_y + _cross_pos(child_align, remaining)
				child.padding_box.y = _ensure(child.border_box.y) + _bt(child)
				child.content_box.y = child.padding_box.y + _pt(child)
			else:
				child_w = _ensure(child.border_box.w) + _cross_margin(child, direction)
				remaining = container_cross - child_w
				child.border_box.x = content_x + _cross_pos(child_align, remaining)
				child.padding_box.x = _ensure(child.border_box.x) + _bl(child)
				child.content_box.x = child.padding_box.x + _pl(child)


def _cross_pos(align: Align, remaining: float) -> float:
	if align == Align.START:
		return 0.0
	elif align == Align.END:
		return remaining
	elif align == Align.CENTER:
		return remaining / 2.0
	elif align == Align.BASELINE:
		return 0.0
	else:
		return 0.0


def _align_content(node: Node, lines: list[list[Node]], direction: Direction,
				   is_row: bool, base_gap: float) -> None:
	container_cross = _ensure(node.content_box.h) if is_row else _ensure(node.content_box.w)
	align_content = node.style.align_content
	n = len(lines)

	total_cross = 0.0
	line_sizes: list[float] = []
	for line in lines:
		line_cross = 0.0
		for child in line:
			if is_row:
				line_cross = max(line_cross, _ensure(child.border_box.h) + _cross_margin(child, direction))
			else:
				line_cross = max(line_cross, _ensure(child.border_box.w) + _cross_margin(child, direction))
		line_sizes.append(line_cross)
		total_cross += line_cross

	remaining = container_cross - total_cross - (n - 1) * base_gap

	if align_content == Align.STRETCH and remaining > 0 and n > 0:
		extra_per_line = remaining / n
		for i in range(n):
			line_sizes[i] += extra_per_line
			for child in lines[i]:
				if is_row:
					child.border_box.h = _ensure(child.border_box.h) + extra_per_line
					child.padding_box.h = _ensure(child.padding_box.h) + extra_per_line
					child.content_box.h = _ensure(child.content_box.h) + extra_per_line
				else:
					child.border_box.w = _ensure(child.border_box.w) + extra_per_line
					child.padding_box.w = _ensure(child.padding_box.w) + extra_per_line
					child.content_box.w = _ensure(child.content_box.w) + extra_per_line
		remaining = 0.0

	if align_content == Align.END:
		offset = max(remaining, 0.0)
		gap = base_gap
	elif align_content == Align.CENTER:
		offset = max(remaining / 2.0, 0.0)
		gap = base_gap
	elif align_content == Align.START:
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
			offset = gap / 2.0
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

