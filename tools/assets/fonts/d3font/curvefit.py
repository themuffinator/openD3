"""Curve-fitting tracer for antialiased bitmap glyphs of drawn typefaces.

``trace.py`` was written for openQ4's faces, which are built from stems, a few
diagonals and simple arcs: it classifies each stretch between two corners as one
line or one arc.  Doom 3's faces are renders of drawn typefaces - a narrow
grotesque, engraver's capitals, an extended square sans - whose bowls change
curvature continuously and whose strokes are only about three texels wide at 48
point.  Traced that way their curves come out faceted and their joins lumpy.

This tracer works in four stages, all in the source atlas's pixel space:

1. **Contour.**  The coverage block is resampled bicubically to several times
   its size, lightly blurred and contoured at the 50% level.  That gives a dense,
   smooth outline that is close to the drawn edge but not exact: interpolating
   area samples pulls an edge towards a saturated neighbour, rounds corners and
   thins any stroke narrower than about a texel and a half.
2. **Refinement.**  The dense outline is rasterised with exact area coverage -
   the way the retail glyph was made - and compared with the retail block.
   Where the render has too little ink the outline is moved outwards, where it
   has too much, inwards, each texel's residual being shared among the outline
   points near it.  Repeated a few times, the outline converges on one whose
   render reproduces the retail coverage, which undoes all three faults above.
3. **Structure.**  Corners are found from the turning angle over a short arc.
   Between corners, axis-parallel straight stretches (stems, bars) become exact
   lines whose offsets are shared across the glyph, and curved stretches are
   cut at their horizontal and vertical extrema, where an outline wants its
   on-curve points and its tangent is known exactly.
4. **Fitting.**  Each curved piece is fitted with cubic Beziers that meet with a
   common tangent (Schneider's algorithm), then converted to the quadratics a
   TrueType outline holds.  A corner is rebuilt as the intersection of the two
   edges that meet in it, so it comes back sharp.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from PIL import Image

from .path import Contour, Path2D
from .raster import rasterize
from .trace import _orient


@dataclass
class CurveOptions:
	# Every distance is in source pixels at a 48 pixel em; ``scaled`` adapts
	# them to another source size.
	factor: int = 6
	blur_sigma: float = 0.28
	pad: int = 3
	step: float = 0.125
	# refinement against the retail coverage
	refine_iterations: int = 8
	refine_step: float = 0.2
	refine_gain: float = 0.85
	refine_reach: float = 0.55
	refine_smooth: float = 0.45
	refine_limit: float = 0.3
	refine_corner_reach: float = 0.0
	# structure
	corner_window: float = 2.6
	corner_angle_deg: float = 38.0
	corner_ratio: float = 0.62
	corner_trim: float = 1.3
	tangent_span: float = 1.2
	max_corner_extension: float = 2.2
	line_tolerance: float = 0.05
	line_ratio: float = 0.004
	axis_angle_deg: float = 2.0
	axis_min_length: float = 2.4
	axis_cluster: float = 0.14
	min_extremum_gap: float = 1.5
	short_edge: float = 4.6
	min_curve_length: float = 1.6
	vertex_ink: float = 0.06
	short_edge_reach: float = 3.5
	extremum_chord: float = 0.6
	extremum_guard: float = 1.5
	extremum_swing_deg: float = 3.0
	fit_smooth: float = 0.3
	# fitting
	curve_tolerance: float = 0.075
	# corner cuts
	cut_passes: int = 2
	cut_reach: float = 2.6
	cut_min_area: float = 0.05
	cut_min_length: float = 0.35
	cut_max: float = 3.2
	quadratic_tolerance: float = 0.02
	min_area: float = 0.06
	# Off by default. A level above 0.5 turns on the recovery of counters too
	# small to empty a texel (see _dense_contours); the console sheet needs it.
	counter_level: float = 0.0
	counter_min_area: float = 0.02

	def scaled(self, point_size: float, reference: float = 48.0) -> "CurveOptions":
		if point_size <= 0.0 or abs(point_size - reference) < 1e-6:
			return self
		k = point_size / reference
		from dataclasses import replace
		return replace(
			self,
			corner_window=self.corner_window * k,
			corner_trim=self.corner_trim * k,
			tangent_span=self.tangent_span * k,
			max_corner_extension=self.max_corner_extension * k,
			short_edge=self.short_edge * k,
			min_curve_length=self.min_curve_length * k,
			short_edge_reach=self.short_edge_reach * k,
			cut_reach=self.cut_reach * k,
			cut_min_area=self.cut_min_area * k * k,
			cut_min_length=self.cut_min_length * k,
			cut_max=self.cut_max * k,
			axis_min_length=self.axis_min_length * k,
			min_extremum_gap=self.min_extremum_gap * k,
			extremum_chord=self.extremum_chord * k,
			extremum_guard=self.extremum_guard * k,
			min_area=self.min_area * k * k,
		)


# ---------------------------------------------------------------------------
# dense contour
# ---------------------------------------------------------------------------


def _gaussian(field: np.ndarray, sigma: float) -> np.ndarray:
	if sigma <= 0.0:
		return field
	radius = int(math.ceil(3.0 * sigma))
	taps = np.arange(-radius, radius + 1, dtype=np.float64)
	kernel = np.exp(-0.5 * (taps / sigma) ** 2)
	kernel /= kernel.sum()
	field = np.apply_along_axis(lambda row: np.convolve(row, kernel, mode="same"), 1, field)
	return np.apply_along_axis(lambda column: np.convolve(column, kernel, mode="same"), 0, field)


def _dense_contours(padded: np.ndarray, options: CurveOptions) -> list[np.ndarray]:
	"""Closed 50% contours of the padded block, in padded pixel space."""
	import contourpy

	k = options.factor
	height, width = padded.shape
	big = Image.fromarray(padded.astype(np.float32)).resize((width * k, height * k), Image.BICUBIC)
	field = np.clip(_gaussian(np.asarray(big, dtype=np.float64), options.blur_sigma * k), 0.0, 1.0)
	generator = contourpy.contour_generator(z=field, name="serial")

	def closed(level: float) -> list[np.ndarray]:
		found = []
		for line in generator.lines(level):
			if len(line) < 8:
				continue
			if np.hypot(*(line[0] - line[-1])) > 1e-6:
				continue  # open: cannot happen with a blank margin
			found.append((np.asarray(line[:-1], dtype=np.float64) + 0.5) / k)
		return found

	contours = closed(0.5)
	if options.counter_level > 0.5:
		# A counter narrower than a texel never empties its texel: the eye of a
		# 16 pixel "e" is a dip to two thirds coverage, not a hole, so the 50%
		# contour closes it up. Such a dip is still a counter. Take it from a
		# higher contour, where it does show, and let the refinement size it:
		# the ink the dip is short of is the area of the counter.
		def inside(point: np.ndarray, polygon: np.ndarray) -> bool:
			x, y = point
			x0, y0 = polygon[:, 0], polygon[:, 1]
			x1, y1 = np.roll(x0, -1), np.roll(y0, -1)
			crosses = ((y0 > y) != (y1 > y)) & (x < x0 + (y - y0) / np.where(y1 != y0, y1 - y0, 1.0) * (x1 - x0))
			return bool(np.count_nonzero(crosses) % 2)

		for candidate in closed(options.counter_level):
			centre = candidate.mean(axis=0)
			row = int(np.clip(centre[1] * k, 0, field.shape[0] - 1))
			column = int(np.clip(centre[0] * k, 0, field.shape[1] - 1))
			if field[row, column] >= options.counter_level:
				continue  # a bump of ink, not a dip
			if not inside(centre, candidate):
				continue
			# Already a hole at 50%, or the outside of the glyph: nothing to add.
			if any(inside(existing.mean(axis=0), candidate) or inside(centre, existing) and
			       abs(_signed_area(existing)) < 4.0 * abs(_signed_area(candidate)) for existing in contours):
				continue
			if not any(inside(centre, existing) for existing in contours):
				continue  # not enclosed by ink
			if abs(_signed_area(candidate)) < options.counter_min_area:
				continue
			contours.append(candidate)
	return contours


def _resample(points: np.ndarray, step: float) -> np.ndarray:
	"""A closed polyline resampled to near-uniform spacing along its length."""
	closed = np.vstack([points, points[:1]])
	lengths = np.hypot(*np.diff(closed, axis=0).T)
	cumulative = np.concatenate([[0.0], np.cumsum(lengths)])
	total = float(cumulative[-1])
	count = max(8, int(round(total / step)))
	targets = np.arange(count) * (total / count)
	x = np.interp(targets, cumulative, closed[:, 0])
	y = np.interp(targets, cumulative, closed[:, 1])
	return np.column_stack([x, y])


def _circular_smooth(values: np.ndarray, sigma_samples: float) -> np.ndarray:
	if sigma_samples <= 0.05 or len(values) < 5:
		return values
	radius = min(int(math.ceil(3.0 * sigma_samples)), (len(values) - 1) // 2)
	taps = np.arange(-radius, radius + 1, dtype=np.float64)
	kernel = np.exp(-0.5 * (taps / sigma_samples) ** 2)
	kernel /= kernel.sum()
	wrapped = np.concatenate([values[-radius:], values, values[:radius]])
	if values.ndim == 1:
		return np.convolve(wrapped, kernel, mode="valid")
	return np.column_stack([np.convolve(wrapped[:, d], kernel, mode="valid") for d in range(values.shape[1])])


def _signed_area(points: np.ndarray) -> float:
	x, y = points[:, 0], points[:, 1]
	return 0.5 * float(np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y))


def _bilinear(image: np.ndarray, x: np.ndarray, y: np.ndarray) -> np.ndarray:
	"""Sample ``image`` (texel centres at +0.5) at pixel-space positions."""
	fx = np.clip(x - 0.5, 0.0, image.shape[1] - 1.001)
	fy = np.clip(y - 0.5, 0.0, image.shape[0] - 1.001)
	x0 = np.floor(fx).astype(int)
	y0 = np.floor(fy).astype(int)
	tx = fx - x0
	ty = fy - y0
	return ((1 - tx) * (1 - ty) * image[y0, x0] + tx * (1 - ty) * image[y0, x0 + 1]
	        + (1 - tx) * ty * image[y0 + 1, x0] + tx * ty * image[y0 + 1, x0 + 1])


def _outward_normals(points: np.ndarray, source: np.ndarray) -> np.ndarray:
	tangent = np.roll(points, -1, axis=0) - np.roll(points, 1, axis=0)
	length = np.hypot(tangent[:, 0], tangent[:, 1])
	length[length < 1e-12] = 1.0
	normal = np.column_stack([tangent[:, 1], -tangent[:, 0]]) / length[:, None]
	# Outward is the side with less ink. One vote per point, decided together,
	# so a noisy sample cannot flip a single normal.
	probe = 0.45
	outer = _bilinear(source, points[:, 0] + probe * normal[:, 0], points[:, 1] + probe * normal[:, 1])
	inner = _bilinear(source, points[:, 0] - probe * normal[:, 0], points[:, 1] - probe * normal[:, 1])
	if float(np.sum(outer - inner)) > 0.0:
		normal = -normal
	return normal


def _polygons_path(contours: list[np.ndarray]) -> Path2D:
	path = Path2D()
	for points in contours:
		contour = Contour((float(points[0][0]), float(points[0][1])))
		for point in points[1:]:
			contour.line_to((float(point[0]), float(point[1])))
		path.contours.append(contour)
	return path


def _corner_damping(points: np.ndarray, step: float, options: CurveOptions) -> np.ndarray:
	"""Weight that falls to zero at corners.

	Left free, the refinement digs a slit into every acute crotch and raises a
	spike on every sharp tip, chasing the last few percent of a texel.  Those
	shapes then read as corners of their own.  A corner is rebuilt later from
	the two edges that meet in it, so the outline only has to be right along
	the edges; near the vertex it is left as contoured.
	"""
	count = len(points)
	turning = np.abs(_turning(points, step, options))
	threshold = math.radians(options.corner_angle_deg) * 0.8
	weight = np.ones(count)
	reach = max(2, int(round(options.refine_corner_reach / step)))
	offsets = np.arange(-reach, reach + 1)
	falloff = np.abs(offsets) / reach
	falloff = falloff * falloff * (3.0 - 2.0 * falloff)
	for index in np.nonzero(turning >= threshold)[0]:
		positions = (index + offsets) % count
		weight[positions] = np.minimum(weight[positions], falloff)
	return weight


def _refine(contours: list[np.ndarray], source: np.ndarray, options: CurveOptions) -> list[np.ndarray]:
	"""Move the outlines until their exact-area render matches ``source``."""
	height, width = source.shape
	reach2 = (3.0 * options.refine_reach) ** 2
	for _ in range(options.refine_iterations):
		contours = [_resample(points, options.refine_step) for points in contours]
		render = rasterize(_polygons_path(contours), width, height)
		residual = source - render
		ys, xs = np.nonzero(np.abs(residual) > 0.004)
		if len(ys) == 0:
			break
		centres = np.column_stack([xs + 0.5, ys + 0.5])
		values = residual[ys, xs].astype(np.float64)

		everything = np.vstack(contours)
		delta = centres[None, :, :] - everything[:, None, :]
		distance2 = delta[:, :, 0] ** 2 + delta[:, :, 1] ** 2
		kernel = np.exp(-0.5 * distance2 / options.refine_reach ** 2)
		kernel[distance2 > reach2] = 0.0
		share = kernel.sum(axis=0)
		share[share < 1e-9] = 1.0
		# Area each outline point is short of (positive) or over by (negative).
		area = (kernel / share) @ values

		moved = []
		offset = 0
		worst = 0.0
		for points in contours:
			count = len(points)
			spacing = np.hypot(*(np.roll(points, -1, axis=0) - points).T)
			spacing = 0.5 * (spacing + np.roll(spacing, 1))
			spacing[spacing < 1e-6] = options.refine_step
			shift = area[offset:offset + count] / spacing
			shift = _circular_smooth(shift, options.refine_smooth / options.refine_step)
			shift = np.clip(options.refine_gain * shift, -options.refine_limit, options.refine_limit)
			if options.refine_corner_reach > 0.0:
				shift = shift * _corner_damping(points, options.refine_step, options)
			worst = max(worst, float(np.abs(shift).max()))
			normal = _outward_normals(points, source)
			moved.append(points + shift[:, None] * normal)
			offset += count
		contours = moved
		if worst < 0.004:
			break
	return contours


# ---------------------------------------------------------------------------
# structure
# ---------------------------------------------------------------------------


def _unit(vector: np.ndarray) -> np.ndarray:
	length = float(np.hypot(vector[0], vector[1]))
	return vector / length if length > 1e-12 else np.array([1.0, 0.0])


def _fit_line(points: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
	"""Total least squares: (centre, unit direction, worst deviation)."""
	centre = points.mean(axis=0)
	_, _, vt = np.linalg.svd(points - centre, full_matrices=False)
	direction = vt[0]
	if float(direction @ (points[-1] - points[0])) < 0.0:
		direction = -direction
	normal = np.array([-direction[1], direction[0]])
	return centre, direction, float(np.abs((points - centre) @ normal).max())


def _turning(points: np.ndarray, step: float, options: CurveOptions) -> np.ndarray:
	"""Signed direction change over ``corner_window`` centred on each sample."""
	half = max(1, int(round(0.5 * options.corner_window / step)))
	before = points - np.roll(points, half, axis=0)
	after = np.roll(points, -half, axis=0) - points
	cross = before[:, 0] * after[:, 1] - before[:, 1] * after[:, 0]
	dot = before[:, 0] * after[:, 0] + before[:, 1] * after[:, 1]
	return np.arctan2(cross, dot)


def _find_corners(points: np.ndarray, step: float, options: CurveOptions) -> list[int]:
	"""Samples where the outline turns sharply rather than curves.

	Contouring rounds a corner over about a texel either side, so the turn has
	to be measured across a window that wide - which a tight curve also fills.
	What tells them apart is what happens beyond the window: a corner's edges
	run on straight, so doubling the window adds little, while an arc keeps
	turning and doubles the angle.
	"""
	from dataclasses import replace

	count = len(points)
	turning = np.abs(_turning(points, step, options))
	wide = np.abs(_turning(points, step, replace(options, corner_window=2.0 * options.corner_window)))
	threshold = math.radians(options.corner_angle_deg)
	guard = max(2, int(round(0.6 * options.corner_window / step)))
	corners: list[int] = []
	for index in np.argsort(-turning):
		if turning[index] < threshold:
			break
		if turning[index] < options.corner_ratio * wide[index]:
			continue
		if all(min((index - c) % count, (c - index) % count) > guard for c in corners):
			corners.append(int(index))
	return sorted(corners)


@dataclass
class _Node:
	index: int                      # sample index on the dense contour
	position: np.ndarray
	corner: bool = False
	tangent: np.ndarray | None = None  # direction of travel, for smooth nodes
	# For a corner rebuilt as the intersection of its two edges: unit vectors
	# from the vertex back along the incoming edge and on along the outgoing one.
	back: np.ndarray | None = None
	ahead: np.ndarray | None = None
	# Set when the corner is cut: where the incoming piece ends, where the
	# outgoing one starts, and whether a bevel or a curve joins them.
	entry: np.ndarray | None = None
	exit: np.ndarray | None = None
	style: str | None = None
	cut_area: float = 0.0

	def leave(self) -> np.ndarray:
		return self.exit if self.exit is not None else self.position

	def arrive(self) -> np.ndarray:
		return self.entry if self.entry is not None else self.position


@dataclass
class _Piece:
	kind: str                       # "line" or "curve"
	first: int                      # node positions in the contour's node list
	last: int
	samples: np.ndarray | None = None
	line: tuple[np.ndarray, np.ndarray] | None = None   # (point, direction)
	axis: str | None = None         # "h" or "v" when snapped


def _span(first: int, last: int, count: int) -> np.ndarray:
	"""Sample indices from ``first`` to ``last`` going forwards, inclusive."""
	length = (last - first) % count
	if length == 0:
		length = count
	return (first + np.arange(length + 1)) % count


def _axis_runs(points: np.ndarray, indices: np.ndarray, step: float, options: CurveOptions) -> list[tuple[int, int, str]]:
	"""Stretches of ``indices`` that run parallel to an axis, as positions in it."""
	if len(indices) < 5:
		return []
	block = points[indices]
	# Direction over a short chord, so one noisy sample does not break a run.
	reach = max(1, int(round(0.35 / step)))
	forward = np.minimum(np.arange(len(block)) + reach, len(block) - 1)
	backward = np.maximum(np.arange(len(block)) - reach, 0)
	chord = block[forward] - block[backward]
	length = np.hypot(chord[:, 0], chord[:, 1])
	length[length < 1e-9] = 1.0
	limit = math.sin(math.radians(options.axis_angle_deg))
	horizontal = np.abs(chord[:, 1]) / length <= limit
	vertical = np.abs(chord[:, 0]) / length <= limit

	runs: list[tuple[int, int, str]] = []
	for mask, axis in ((horizontal, "h"), (vertical, "v")):
		start = None
		for position in range(len(mask) + 1):
			on = position < len(mask) and bool(mask[position])
			if on and start is None:
				start = position
			elif not on and start is not None:
				end = position - 1
				if (end - start) * step >= options.axis_min_length:
					# Confirm with a real fit: the chord test alone admits a very
					# shallow arc.
					piece = block[start:end + 1]
					_, _, deviation = _fit_line(piece)
					if deviation <= options.line_tolerance + options.line_ratio * (end - start) * step:
						runs.append((start, end, axis))
				start = None
	runs.sort()
	return runs


def _extrema(points: np.ndarray, indices: np.ndarray, step: float, options: CurveOptions,
             circular: bool = False) -> list[tuple[int, str]]:
	"""Positions in ``indices`` where the outline turns back along x or y.

	Found from the direction of a short chord rather than from the coordinates:
	a round bowl is so flat at its extremum that the coordinate barely changes
	within a texel, while its direction swings steadily through the axis.  A
	straight axis-parallel edge has a direction that hovers at the axis without
	crossing it, so the direction must also differ clearly either side.
	"""
	block = points[indices[:-1]] if circular else points[indices]
	count = len(block)
	reach = max(2, int(round(options.extremum_chord / step)))
	guard = max(reach, int(round(options.extremum_guard / step)))
	if count < 2 * guard + 3:
		return []

	positions = np.arange(count)
	if circular:
		ahead = block[(positions + reach) % count]
		behind = block[(positions - reach) % count]
	else:
		ahead = block[np.minimum(positions + reach, count - 1)]
		behind = block[np.maximum(positions - reach, 0)]
	chord = ahead - behind
	length = np.hypot(chord[:, 0], chord[:, 1])
	length[length < 1e-9] = 1.0
	swing = math.sin(math.radians(options.extremum_swing_deg))

	found: list[tuple[int, str]] = []
	for axis, column in (("h", 1), ("v", 0)):
		# A horizontal tangent has no y component; a vertical one, no x.
		component = chord[:, column] / length
		last = count if circular else count - 1
		for position in range(last):
			following = (position + 1) % count
			if component[position] * component[following] > 0.0:
				continue
			if component[position] == 0.0 and component[following] == 0.0:
				continue
			if circular:
				before = component[(position - guard) % count]
				after = component[(following + guard) % count]
			else:
				if position < guard or following > count - 1 - guard:
					continue
				before = component[position - guard]
				after = component[following + guard]
			if before * after >= 0.0 or abs(after - before) < swing:
				continue
			best = position if abs(component[position]) <= abs(component[following]) else following
			found.append((int(best), axis))
	found.sort()
	gap = max(2, int(round(options.min_extremum_gap / step)))
	merged: list[tuple[int, str]] = []
	for item in found:
		if merged and item[0] - merged[-1][0] < gap:
			continue
		merged.append(item)
	if circular and len(merged) > 1 and merged[0][0] + count - merged[-1][0] < gap:
		merged.pop()
	return merged


# ---------------------------------------------------------------------------
# cubic fitting (Schneider, "An Algorithm for Automatically Fitting Digitized
# Curves", Graphics Gems, 1990)
# ---------------------------------------------------------------------------


def _bezier(control: np.ndarray, t: np.ndarray) -> np.ndarray:
	inv = 1.0 - t
	return ((inv ** 3)[:, None] * control[0] + (3 * inv * inv * t)[:, None] * control[1]
	        + (3 * inv * t * t)[:, None] * control[2] + (t ** 3)[:, None] * control[3])


def _chord_parameters(points: np.ndarray) -> np.ndarray:
	lengths = np.hypot(*np.diff(points, axis=0).T)
	cumulative = np.concatenate([[0.0], np.cumsum(lengths)])
	return cumulative / cumulative[-1] if cumulative[-1] > 1e-12 else np.linspace(0.0, 1.0, len(points))


def _generate(points: np.ndarray, u: np.ndarray, tan1: np.ndarray, tan2: np.ndarray) -> np.ndarray:
	first, last = points[0], points[-1]
	inv = 1.0 - u
	b0, b1, b2, b3 = inv ** 3, 3 * inv * inv * u, 3 * inv * u * u, u ** 3
	a1 = b1[:, None] * tan1
	a2 = b2[:, None] * tan2
	c00 = float(np.sum(a1 * a1))
	c01 = float(np.sum(a1 * a2))
	c11 = float(np.sum(a2 * a2))
	rest = points - ((b0 + b1)[:, None] * first + (b2 + b3)[:, None] * last)
	x0 = float(np.sum(a1 * rest))
	x1 = float(np.sum(a2 * rest))
	det = c00 * c11 - c01 * c01
	chord = float(np.hypot(*(last - first)))
	if abs(det) > 1e-12:
		alpha1 = (x0 * c11 - x1 * c01) / det
		alpha2 = (c00 * x1 - c01 * x0) / det
	else:
		alpha1 = alpha2 = 0.0
	# A wild or reversed handle means the system was ill-conditioned; the
	# classical fallback is a third of the chord.
	epsilon = 1e-6 * chord
	if alpha1 < epsilon or alpha2 < epsilon or alpha1 > 1.5 * chord or alpha2 > 1.5 * chord:
		alpha1 = alpha2 = chord / 3.0
	return np.array([first, first + alpha1 * tan1, last + alpha2 * tan2, last])


def _reparameterize(points: np.ndarray, control: np.ndarray, u: np.ndarray) -> np.ndarray:
	d1 = 3.0 * (control[1:] - control[:-1])
	d2 = 2.0 * (d1[1:] - d1[:-1])
	inv = 1.0 - u
	q = _bezier(control, u)
	q1 = (inv * inv)[:, None] * d1[0] + (2 * inv * u)[:, None] * d1[1] + (u * u)[:, None] * d1[2]
	q2 = inv[:, None] * d2[0] + u[:, None] * d2[1]
	numerator = np.sum((q - points) * q1, axis=1)
	denominator = np.sum(q1 * q1, axis=1) + np.sum((q - points) * q2, axis=1)
	safe = np.abs(denominator) > 1e-12
	result = u.copy()
	result[safe] = u[safe] - numerator[safe] / denominator[safe]
	result = np.clip(result, 0.0, 1.0)
	result[0], result[-1] = 0.0, 1.0
	# Parameters must stay ordered or the next fit folds back on itself.
	return np.maximum.accumulate(result)


_CURVE_SAMPLES = np.linspace(0.0, 1.0, 97)


def _distance_to_curve(points: np.ndarray, control: np.ndarray) -> np.ndarray:
	"""Distance from each point to the cubic, measured against a fine polyline."""
	curve = _bezier(control, _CURVE_SAMPLES)
	start = curve[:-1]
	edge = curve[1:] - start
	length2 = np.maximum(np.sum(edge * edge, axis=1), 1e-18)
	offset = points[:, None, :] - start[None, :, :]
	along = np.clip(np.sum(offset * edge[None, :, :], axis=2) / length2[None, :], 0.0, 1.0)
	nearest = start[None, :, :] + along[:, :, None] * edge[None, :, :]
	gap = points[:, None, :] - nearest
	return np.sqrt(np.sum(gap * gap, axis=2).min(axis=1))


def _fit_one(points: np.ndarray, tan1: np.ndarray, tan2: np.ndarray) -> tuple[np.ndarray, float]:
	"""Best single cubic through ``points`` with fixed end directions, and its worst error.

	With both ends and both end directions fixed, a cubic has two numbers left:
	the lengths of its handles.  The classical fit solves for them against a
	guessed parameterisation and then improves the guess, which converges very
	slowly when the two lengths can trade against each other - on a plain
	quarter ellipse it stalls at ten times the error of the best cubic.  So the
	classical answer is only the starting point here, and the two lengths are
	then optimised directly against the true distance from the data to the curve.
	"""
	from scipy.optimize import least_squares

	count = len(points)
	first, last = points[0], points[-1]
	chord = float(np.hypot(*(last - first)))
	if count <= 2 or chord < 1e-9:
		third = chord / 3.0
		return np.array([first, first + third * tan1, last + third * tan2, last]), 0.0

	u = _chord_parameters(points)
	control = _generate(points, u, tan1, tan2)
	for _ in range(3):
		u = _reparameterize(points, control, u)
		control = _generate(points, u, tan1, tan2)

	# Enough of the data to pin the shape; every point is used for the verdict.
	stride = max(1, count // 48)
	sample = points[::stride]
	# A handle longer than this belongs to a curve that loops or doubles back.
	limit = 1.5 * chord

	def build(lengths: np.ndarray) -> np.ndarray:
		return np.array([first, first + lengths[0] * tan1, last + lengths[1] * tan2, last])

	start = np.array([
		np.clip(float((control[1] - first) @ tan1), 0.02 * chord, limit),
		np.clip(float((control[2] - last) @ tan2), 0.02 * chord, limit),
	])
	result = least_squares(lambda lengths: _distance_to_curve(sample, build(lengths)), start,
	                       bounds=([0.0, 0.0], [limit, limit]), xtol=1e-6, ftol=1e-9, max_nfev=60)
	control = build(result.x)
	return control, float(_distance_to_curve(points, control).max())


def _fit_cubics(points: np.ndarray, tan1: np.ndarray, tan2: np.ndarray, tolerance: float,
                tangent_reach: int = 5, most: int = 10) -> list[np.ndarray]:
	"""Cubics through ``points`` leaving along ``tan1`` and arriving against ``tan2``.

	The piece is cut into equal lengths, one more each time, until every cut
	fits within ``tolerance``; neighbours share the tangent measured at their
	joint, so the pieces meet smoothly.  Cutting evenly, rather than at the
	point of worst error as the classical algorithm does, keeps the count low
	and the same for the mirror image of a shape.
	"""
	count = len(points)
	if count < 2:
		return []
	lengths = np.hypot(*np.diff(points, axis=0).T)
	cumulative = np.concatenate([[0.0], np.cumsum(lengths)])
	total = float(cumulative[-1])
	best: tuple[float, list[np.ndarray]] | None = None
	for pieces in range(1, most + 1):
		if pieces > 1 and count < 4 * pieces:
			break
		cuts = [0]
		for k in range(1, pieces):
			cuts.append(int(np.searchsorted(cumulative, total * k / pieces)))
		cuts.append(count - 1)
		if any(b - a < 2 for a, b in zip(cuts, cuts[1:])):
			break
		tangents = [tan1]
		for cut in cuts[1:-1]:
			reach = min(tangent_reach, cut, count - 1 - cut)
			tangents.append(_unit(points[cut + reach] - points[cut - reach]))
		controls = []
		worst = 0.0
		for index in range(pieces):
			leave = tangents[index]
			arrive = tan2 if index == pieces - 1 else -tangents[index + 1]
			control, error = _fit_one(points[cuts[index]:cuts[index + 1] + 1], leave, arrive)
			controls.append(control)
			worst = max(worst, error)
		if best is None or worst < best[0]:
			best = (worst, controls)
		if worst <= tolerance:
			return controls
	return best[1] if best is not None else []


def _emit_cubic(contour: Contour, control: np.ndarray, options: CurveOptions) -> None:
	from fontTools.cu2qu import curve_to_quadratic

	chord = control[3] - control[0]
	length = float(np.hypot(chord[0], chord[1]))
	if length > 1e-9:
		normal = np.array([-chord[1], chord[0]]) / length
		bulge = max(abs(float((control[1] - control[0]) @ normal)), abs(float((control[2] - control[0]) @ normal)))
		if bulge < 0.25 * options.curve_tolerance:
			contour.line_to((float(control[3][0]), float(control[3][1])))
			return
	spline = curve_to_quadratic([tuple(map(float, point)) for point in control], options.quadratic_tolerance)
	# A quadratic B-spline: on-curve points are implied midway between
	# consecutive off-curve points.
	controls = spline[1:-1]
	for index, point in enumerate(controls):
		if index + 1 < len(controls):
			following = controls[index + 1]
			end = (0.5 * (point[0] + following[0]), 0.5 * (point[1] + following[1]))
		else:
			end = spline[-1]
		contour.quad_to((float(point[0]), float(point[1])), (float(end[0]), float(end[1])))


# ---------------------------------------------------------------------------
# assembling one contour
# ---------------------------------------------------------------------------


class _ContourPlan:
	"""Nodes and pieces of one dense contour, before axis offsets are shared."""

	def __init__(self, points: np.ndarray, step: float, options: CurveOptions, source: np.ndarray | None = None):
		self.points = points
		self.step = step
		self.options = options
		self.source = source
		self.normals = _outward_normals(points, source) if source is not None else None
		self.count = len(points)
		self.nodes: list[_Node] = []
		self.pieces: list[_Piece] = []
		self._build()

	def _build(self) -> None:
		points, step, options, count = self.points, self.step, self.options, self.count
		corners = _find_corners(points, step, options)

		# (sample index, kind, axis) in order round the contour.
		marks: list[tuple[int, str, str | None]] = [(c, "corner", None) for c in corners]
		line_spans: list[tuple[int, int, str]] = []

		if corners:
			stretches = [(corners[i], corners[(i + 1) % len(corners)]) for i in range(len(corners))]
		else:
			stretches = [(0, 0)]
		trim = int(round(options.corner_trim / step))

		for first, last in stretches:
			indices = _span(first, last, count)
			# Keep clear of the corner fillets when looking for structure.
			low = trim if corners else 0
			high = len(indices) - 1 - trim if corners else len(indices) - 1
			if high - low < 4:
				continue
			inner = indices[low:high + 1]

			if corners:
				centre, direction, deviation = _fit_line(points[inner])
				length = (len(inner) - 1) * step
				if deviation <= options.line_tolerance + options.line_ratio * length:
					# The whole stretch between two corners is one straight edge.
					line_spans.append((int(indices[0]), int(indices[-1]), "whole"))
					continue

			axis_runs = _axis_runs(points, inner, step, options)
			taken = np.zeros(len(inner), dtype=bool)
			for start, end, axis in axis_runs:
				taken[start:end + 1] = True
				# A run that reaches the trimmed end of the stretch runs on into
				# the corner there: the corner, not a join a texel short of it,
				# ends the line. Otherwise a sliver of curve is left between the
				# two, with nothing to fit it to.
				at_first = bool(corners) and start <= 2
				at_last = bool(corners) and end >= len(inner) - 3
				first_index = int(indices[0]) if at_first else int(inner[start])
				last_index = int(indices[-1]) if at_last else int(inner[end])
				if not at_first:
					marks.append((first_index, "join", axis))
				if not at_last:
					marks.append((last_index, "join", axis))
				line_spans.append((first_index, last_index, axis))
			for position, axis in _extrema(points, inner, step, options, circular=not corners):
				near = taken[max(0, position - 3):position + 4]
				if near.any():
					continue
				marks.append((int(inner[position]), "extremum", axis))

		if not marks:
			# A featureless loop: cut it into four so every piece is a simple arc.
			marks = [(int(round(i * count / 4)) % count, "free", None) for i in range(4)]
		elif len(marks) == 1:
			marks.append(((marks[0][0] + count // 2) % count, "free", None))

		marks.sort(key=lambda mark: mark[0])
		deduped: list[tuple[int, str, str | None]] = []
		for mark in marks:
			if deduped and mark[0] == deduped[-1][0]:
				if mark[1] == "corner":
					deduped[-1] = mark
				continue
			deduped.append(mark)
		marks = deduped

		whole = {(a, b) for a, b, axis in line_spans if axis == "whole"}
		axis_of = {(a, b): axis for a, b, axis in line_spans if axis != "whole"}

		for index, kind, axis in marks:
			node = _Node(index, points[index].copy(), corner=(kind == "corner"))
			if kind in ("join", "extremum") and axis is not None:
				ahead = points[(index + 2) % count] - points[(index - 2) % count]
				if axis == "h":
					node.tangent = np.array([1.0 if ahead[0] >= 0 else -1.0, 0.0])
				else:
					node.tangent = np.array([0.0, 1.0 if ahead[1] >= 0 else -1.0])
			self.nodes.append(node)

		total = len(self.nodes)
		for position in range(total):
			following = (position + 1) % total
			a = self.nodes[position].index
			b = self.nodes[following].index
			if (a, b) in whole:
				indices = _span(a, b, count)
				inner = indices[trim:len(indices) - trim] if len(indices) > 2 * trim + 3 else indices
				centre, direction, _ = _fit_line(points[inner])
				piece = _Piece("line", position, following, line=(centre, direction))
				limit = math.sin(math.radians(options.axis_angle_deg))
				if abs(direction[1]) <= limit:
					piece.axis = "h"
				elif abs(direction[0]) <= limit:
					piece.axis = "v"
				self.pieces.append(piece)
			elif (a, b) in axis_of:
				indices = _span(a, b, count)
				low = trim if self.nodes[position].corner else 0
				high = len(indices) - (trim if self.nodes[following].corner else 0)
				if high - low >= 4:
					indices = indices[low:high]
				centre, direction, _ = _fit_line(points[indices])
				self.pieces.append(_Piece("line", position, following, line=(centre, direction), axis=axis_of[(a, b)]))
			else:
				self.pieces.append(_Piece("curve", position, following, samples=_span(a, b, count)))

	def axis_lines(self) -> list[_Piece]:
		return [piece for piece in self.pieces if piece.kind == "line" and piece.axis is not None]

	def length_of(self, piece: _Piece) -> float:
		a = self.nodes[piece.first].index
		b = self.nodes[piece.last].index
		return ((b - a) % self.count or self.count) * self.step

	def _end_line(self, piece: _Piece, at_start: bool) -> tuple[np.ndarray, np.ndarray] | None:
		"""The straight line a piece follows as it reaches one of its ends."""
		if piece.kind == "line":
			return piece.line
		samples = piece.samples
		trim = int(round(self.options.corner_trim / self.step))
		span = max(3, int(round(self.options.tangent_span / self.step)))
		if len(samples) < trim + 4:
			return None
		if at_start:
			chosen = samples[trim:min(len(samples), trim + span + 1)]
		else:
			chosen = samples[max(0, len(samples) - trim - span - 1):len(samples) - trim]
		if len(chosen) < 3:
			return None
		centre, direction, _ = _fit_line(self.points[chosen])
		anchor = self.points[chosen[0] if at_start else chosen[-1]]
		return anchor, direction

	def _clip_vertex(self, node: _Node, candidate: np.ndarray) -> np.ndarray:
		"""Pull a rebuilt vertex back to where the retail glyph has ink to show for it.

		Two edges that meet at a shallow angle intersect a long way out, and a
		small error in either direction moves the intersection further still.
		The retail coverage settles it: the tip of a convex corner must have
		some ink just inside it, and the tip of a notch some paper.  A vertex
		that fails is walked back toward the contoured corner until it passes,
		which turns a spike into the blunt tip the glyph really has.
		"""
		if self.source is None or self.normals is None:
			return candidate
		outward = self.normals[node.index]
		travel = node.position - candidate
		distance = float(np.hypot(*travel))
		if distance < 0.3:
			return candidate
		steps = max(2, int(math.ceil(distance / 0.1)))
		for index in range(steps + 1):
			point = candidate + travel * (index / steps)
			probe = point - 0.3 * outward
			ink = float(_bilinear(self.source, np.array([probe[0]]), np.array([probe[1]]))[0])
			# The outline's outward side at a convex corner is paper; at a notch
			# the same test runs the other way round, on the paper it must keep.
			paper_probe = point + 0.3 * outward
			paper = 1.0 - float(_bilinear(self.source, np.array([paper_probe[0]]), np.array([paper_probe[1]]))[0])
			if ink >= self.options.vertex_ink and paper >= self.options.vertex_ink:
				return point
		return node.position

	def resolve(self) -> None:
		"""Fix node positions once the axis lines have their final offsets."""
		options = self.options
		total = len(self.nodes)
		for position, node in enumerate(self.nodes):
			incoming = self.pieces[(position - 1) % total]
			outgoing = self.pieces[position]
			if node.corner:
				a = self._end_line(incoming, at_start=False)
				b = self._end_line(outgoing, at_start=True)
				vertex = None
				if a is not None and b is not None:
					cross = a[1][0] * b[1][1] - a[1][1] * b[1][0]
					if abs(cross) > 0.26:  # the edges meet at 15 degrees or more
						offset = b[0] - a[0]
						t = (offset[0] * b[1][1] - offset[1] * b[1][0]) / cross
						candidate = a[0] + t * a[1]
						if float(np.hypot(*(candidate - node.position))) <= options.max_corner_extension:
							vertex = self._clip_vertex(node, candidate)
							node.back = -_unit(np.asarray(a[1], dtype=np.float64))
							node.ahead = _unit(np.asarray(b[1], dtype=np.float64))
				if vertex is None:
					# No clean intersection: keep the traced point, but put it
					# on a straight neighbour so that edge stays straight.
					vertex = node.position
					for line in (incoming, outgoing):
						if line.kind == "line":
							point, direction = line.line
							vertex = point + direction * float((vertex - point) @ direction)
							break
				node.position = np.asarray(vertex, dtype=np.float64)
			else:
				for line in (incoming, outgoing):
					if line.kind == "line":
						point, direction = line.line
						node.position = point + direction * float((node.position - point) @ direction)
						break

	def fit_short_edges(self) -> None:
		"""Place the two corners of a short edge by matching its coverage.

		A stroke's end, the foot of a serif and the flat of a crotch are edges
		only a few texels long with a corner at each end.  Contouring rounds
		both corners, so almost nothing of such an edge is left to fit a line
		to, and a line fitted to the little that is can come out nearly parallel
		to a neighbouring edge - their intersection is then far away, and the
		stroke grows a spike.  The two neighbours are long and well determined,
		so the short edge has only two unknowns: how far along each neighbour
		its corners lie.  Those are found by drawing the quadrilateral they make
		and matching its coverage to that of the contoured outline over the same
		stretch, which the refinement has already matched to the retail glyph.
		"""
		from scipy.optimize import least_squares

		options, step, count = self.options, self.step, self.count
		total = len(self.pieces)
		if total < 3:
			return
		for position, piece in enumerate(self.pieces):
			first = self.nodes[piece.first]
			last = self.nodes[piece.last]
			if not (first.corner and last.corner):
				continue
			length = self.length_of(piece)
			if length > options.short_edge or length < 0.5:
				continue
			before = self.pieces[(position - 1) % total]
			after = self.pieces[(position + 1) % total]
			if min(self.length_of(before), self.length_of(after)) <= options.short_edge:
				continue
			line_a = self._end_line(before, at_start=False)
			line_b = self._end_line(after, at_start=True)
			if line_a is None or line_b is None:
				continue
			dir_a = _unit(np.asarray(line_a[1], dtype=np.float64))
			dir_b = _unit(np.asarray(line_b[1], dtype=np.float64))

			# The stretch from a point back along the first neighbour to a
			# point on along the second: the outline as contoured.
			reach_a = min(options.short_edge_reach, 0.6 * self.length_of(before))
			reach_b = min(options.short_edge_reach, 0.6 * self.length_of(after))
			start = (first.index - int(round(reach_a / step))) % count
			stop = (last.index + int(round(reach_b / step))) % count
			stretch = self.points[_span(start, stop, count)]
			far_a = line_a[0] + dir_a * float((stretch[0] - line_a[0]) @ dir_a)
			far_b = line_b[0] + dir_b * float((stretch[-1] - line_b[0]) @ dir_b)
			stretch = np.vstack([far_a[None, :], stretch[1:-1], far_b[None, :]])

			low = np.floor(stretch.min(axis=0) - 3.0)
			high = np.ceil(stretch.max(axis=0) + 3.0)
			width = int(high[0] - low[0])
			height = int(high[1] - low[1])
			if width <= 0 or height <= 0 or width * height > 4096:
				continue
			target = rasterize(_polygons_path([stretch - low]), width, height)

			def quad(lengths: np.ndarray) -> np.ndarray:
				return np.array([far_a, far_a + lengths[0] * dir_a, far_b - lengths[1] * dir_b, far_b])

			def residual(lengths: np.ndarray) -> np.ndarray:
				return (rasterize(_polygons_path([quad(lengths) - low]), width, height) - target).ravel()

			guess = np.array([
				max(0.2, float((self.points[first.index] - far_a) @ dir_a) + 0.3),
				max(0.2, float((far_b - self.points[last.index]) @ dir_b) + 0.3),
			])
			upper = guess + options.max_corner_extension
			result = least_squares(residual, guess, bounds=([0.05, 0.05], upper), diff_step=0.02,
			                       xtol=1e-4, ftol=1e-6, max_nfev=40)
			vertices = quad(result.x)
			edge = vertices[2] - vertices[1]
			if float(np.hypot(*edge)) < 0.25:
				continue
			edge = _unit(edge)
			vertices[1] = self._clip_vertex(first, vertices[1])
			vertices[2] = self._clip_vertex(last, vertices[2])
			edge = vertices[2] - vertices[1]
			if float(np.hypot(*edge)) < 0.25:
				continue
			edge = _unit(edge)
			first.position = vertices[1]
			last.position = vertices[2]
			first.back, first.ahead = -dir_a, edge
			last.back, last.ahead = -edge, dir_b
			piece.kind = "line"
			piece.line = (vertices[1], edge)
			piece.axis = None

	def contour(self) -> Contour | None:
		options, step = self.options, self.step
		trim = int(round(options.corner_trim / step))
		origin = self.nodes[0].leave()
		outline = Contour((float(origin[0]), float(origin[1])))

		def close_corner(node: _Node) -> None:
			if node.exit is None:
				return
			target = (float(node.exit[0]), float(node.exit[1]))
			if node.style == "round":
				outline.quad_to((float(node.position[0]), float(node.position[1])), target)
			else:
				outline.line_to(target)

		for piece in self.pieces:
			start = self.nodes[piece.first]
			end = self.nodes[piece.last]
			begin = start.leave()
			finish = end.arrive()
			if piece.kind == "line":
				outline.line_to((float(finish[0]), float(finish[1])))
				close_corner(end)
				continue

			samples = piece.samples
			low = trim if start.corner else 1
			high = len(samples) - trim if end.corner else len(samples) - 1
			interior = self.points[samples[low:high]] if high - low >= 1 else np.zeros((0, 2))
			# A cut corner ends the piece short of the vertex; samples beyond
			# the cut would fold the curve back on itself.
			if len(interior) and start.exit is not None and start.ahead is not None:
				interior = interior[(interior - begin) @ start.ahead >= 0.1]
			if len(interior) and end.entry is not None and end.back is not None:
				interior = interior[(interior - finish) @ end.back >= 0.1]
			block = np.vstack([begin[None, :], interior, finish[None, :]])

			if (len(block) < 4 or float(np.hypot(*(finish - begin))) < 1e-6
					or len(samples) * step < options.min_curve_length):
				outline.line_to((float(finish[0]), float(finish[1])))
				close_corner(end)
				continue

			if start.tangent is not None:
				tan1 = start.tangent
			else:
				line = self._end_line(piece, at_start=True) if start.corner else None
				tan1 = line[1] if line is not None else _unit(block[min(3, len(block) - 1)] - block[0])
			if end.tangent is not None:
				tan2 = -end.tangent
			else:
				line = self._end_line(piece, at_start=False) if end.corner else None
				tan2 = -line[1] if line is not None else _unit(block[max(0, len(block) - 4)] - block[-1])

			reach = max(3, int(round(0.75 / step)))
			for control in _fit_cubics(block, _unit(np.asarray(tan1, float)), _unit(np.asarray(tan2, float)),
			                           options.curve_tolerance, tangent_reach=reach):
				_emit_cubic(outline, control, options)
			close_corner(end)

		if not outline.segments:
			return None
		last = outline.segments[-1][-1]
		if outline.segments[-1][0] == "L" and math.hypot(last[0] - outline.start[0], last[1] - outline.start[1]) < 1e-6:
			outline.segments.pop()
		return outline if outline.segments else None


def _cut_corners(plans: list["_ContourPlan"], source: np.ndarray, options: CurveOptions) -> None:
	"""Bevel or round each corner by the area its sharp vertex gets wrong.

	A corner rebuilt as the intersection of its two edges is as sharp as a
	corner can be, and the drawn one often was not: the apex of a W is cut
	flat, the corners of a square-sided bowl are small arcs, a crotch is filled
	by the ink of the two strokes.  Contouring cannot show which - it rounds
	every corner alike - but the coverage can: rendered sharp, a vertex that
	was really cut puts ink where the retail glyph has none (or leaves a notch
	where it has ink), and the amount is the area of the missing cut.  The
	corner is cut back along both edges until that area is accounted for: flat
	across an acute corner, with a curve at a right or obtuse one.
	"""
	height, width = source.shape
	corners: list[tuple[_ContourPlan, int, _Node, bool]] = []
	for plan in plans:
		normals = _outward_normals(plan.points, source)
		for position, node in enumerate(plan.nodes):
			if not node.corner or node.back is None or node.ahead is None:
				continue
			bisector = node.back + node.ahead
			if float(np.hypot(*bisector)) < 1e-6:
				continue
			# The wedge between the two edges holds ink when it opens away
			# from the outline's outward side.
			convex = float(bisector @ normals[node.index]) < 0.0
			corners.append((plan, position, node, convex))
	if not corners:
		return
	centres = np.array([node.position for _, _, node, _ in corners])

	for _ in range(options.cut_passes):
		path = Path2D()
		for plan in plans:
			contour = plan.contour()
			if contour is not None:
				path.contours.append(contour)
		difference = rasterize(path, width, height) - source
		ys, xs = np.nonzero(np.abs(difference) > 0.02)
		if len(ys) == 0:
			return
		texels = np.column_stack([xs + 0.5, ys + 0.5])
		values = difference[ys, xs]
		distance = np.hypot(texels[:, None, 0] - centres[None, :, 0], texels[:, None, 1] - centres[None, :, 1])
		nearest = distance.argmin(axis=1)
		within = distance[np.arange(len(texels)), nearest] <= options.cut_reach

		for number, (plan, position, node, convex) in enumerate(corners):
			chosen = within & (nearest == number)
			excess = float(values[chosen].sum())
			area = node.cut_area + (excess if convex else -excess)
			sine = abs(float(node.back[0] * node.ahead[1] - node.back[1] * node.ahead[0]))
			node.entry = node.exit = None
			node.style = None
			node.cut_area = max(0.0, area)
			if area < options.cut_min_area or sine < 0.05:
				continue
			acute = float(node.back @ node.ahead) > 0.17      # the edges meet at under 80 degrees
			length = math.sqrt((2.0 if acute else 6.0) * area / sine)
			total = len(plan.nodes)
			before = plan.nodes[(position - 1) % total].position
			after = plan.nodes[(position + 1) % total].position
			room = 0.45 * min(float(np.hypot(*(before - node.position))), float(np.hypot(*(after - node.position))))
			length = min(length, room, options.cut_max)
			if length < options.cut_min_length:
				continue
			node.style = "bevel" if acute else "round"
			node.entry = node.position + length * node.back
			node.exit = node.position + length * node.ahead


def _share_axis_offsets(plans: list[_ContourPlan], options: CurveOptions) -> None:
	"""Snap axis lines exactly onto their axis and merge near-equal offsets."""
	for axis, column in (("h", 1), ("v", 0)):
		entries = []
		for plan in plans:
			for piece in plan.axis_lines():
				if piece.axis != axis:
					continue
				point, direction = piece.line
				entries.append((float(point[column]), plan.length_of(piece), piece, direction))
		if not entries:
			continue
		entries.sort(key=lambda entry: entry[0])
		clusters: list[list] = [[entries[0]]]
		for entry in entries[1:]:
			if entry[0] - clusters[-1][-1][0] > options.axis_cluster:
				clusters.append([])
			clusters[-1].append(entry)
		for cluster in clusters:
			weight = sum(entry[1] for entry in cluster)
			merged = sum(entry[0] * entry[1] for entry in cluster) / weight if weight > 0 else cluster[0][0]
			for _, _, piece, direction in cluster:
				point = piece.line[0].copy()
				point[column] = merged
				if axis == "h":
					snapped = np.array([1.0 if direction[0] >= 0 else -1.0, 0.0])
				else:
					snapped = np.array([0.0, 1.0 if direction[1] >= 0 else -1.0])
				piece.line = (point, snapped)


def trace_glyph(coverage: np.ndarray, options: CurveOptions | None = None) -> Path2D:
	"""Outline of one antialiased glyph block, in the block's pixel space (y down)."""
	options = options or CurveOptions()
	height, width = coverage.shape
	if height == 0 or width == 0:
		return Path2D()
	pad = options.pad
	source = np.pad(np.clip(coverage, 0.0, 1.0).astype(np.float64), pad)

	contours = _dense_contours(source, options)
	contours = [points for points in contours if abs(_signed_area(points)) >= options.min_area]
	if not contours:
		return Path2D()
	contours = _refine(contours, source, options)

	plans = []
	for points in contours:
		if abs(_signed_area(points)) < options.min_area:
			continue
		dense = _resample(points, options.step)
		# The refinement leaves a ripple of a hundredth of a texel or two at
		# the texel pitch; fitted as it is, every curve splits to follow it.
		dense = _circular_smooth(dense, options.fit_smooth / options.step)
		plans.append(_ContourPlan(dense, options.step, options, source))
	_share_axis_offsets(plans, options)

	for plan in plans:
		plan.resolve()
		plan.fit_short_edges()
	_cut_corners(plans, source, options)

	path = Path2D()
	for plan in plans:
		contour = plan.contour()
		if contour is not None and abs(contour.signed_area()) >= options.min_area:
			path.contours.append(contour)
	_orient(path)
	return path.transformed(1.0, 1.0, -pad, -pad)
