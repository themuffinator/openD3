#!/usr/bin/env python3
"""Render openD3's banner, assets/docs/img/banner.png.

The banner is a variant of openQ4's: the "open" lettering is openQ4's own
pixels, kept as a layer in assets/docs/img/src/banner-open.png, and everything
else is drawn here. "D3" is lettered after the DOOM 3 wordmark (plated metal
running from steel blue to rust, a gold rim, an extrusion lit from below), on a
plate with openQ4's outline, lit as an orange-red glow with a pentagram behind
the lettering. The lettering covers the pentagram's middle, so only its ring
and two of its points show, a little hotter than the glow around them.

Nothing here is traced or copied from Doom 3's artwork: the letterforms are the
polygons below and every texture is procedural.

Usage:
    python tools/assets/build_banner.py
    python tools/assets/build_banner.py --extract-open path/to/openQ4/assets/docs/img/banner.png

The second form rebuilds the "open" layer from openQ4's banner. It is only
needed if that banner's lettering changes.

Requires numpy, opencv-python and Pillow.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

REPO = Path(__file__).resolve().parents[2]
OPEN_LAYER = REPO / "assets" / "docs" / "img" / "src" / "banner-open.png"
OUTPUT = REPO / "assets" / "docs" / "img" / "banner.png"

WIDTH, HEIGHT = 904, 386
LAYER_WIDTH = 1024  # openQ4's banner, and so the "open" layer, is wider
SS = 4  # supersampling factor; all geometry below is in final pixels

# The plate, clockwise from top left. openQ4's plate has the same outline.
PLATE = ((478.0, 88.0), (884.0, 81.0), (765.0, 310.0), (343.0, 347.0))

# Lettering. Glyph units: one unit is the D's width before stretching.
GLYPH_SCALE = 108.0      # pixels per unit, vertically
GLYPH_STRETCH = 1.12     # horizontal stretch
GLYPH_ORIGIN = (430.0, 58.0)
GLYPH_GAP = 0.13         # between the D and the 3, in units
GLYPH_HEIGHT = 2.59      # top edge to the tips of the spikes, in units
EXTRUDE = (3.5, 10.0)    # depth of the lettering, towards lower right

D_OUTER = ((0, 0.03), (0.03, 0), (0.86, 0), (1, 0.12), (1, 1.81), (0, GLYPH_HEIGHT))
D_COUNTER = ((0.35, 0.36), (0.68, 0.36), (0.68, 1.45), (0.35, 1.70))
# An angular 3: two bars joined by a chevron, its foot a mirror of the D's.
_BAR = 1.45
_ARM = 0.28 + (_BAR - 0.90) / 1.53
THREE = (
    (0, 0), (0.90, 0), (1, 0.10), (1, 0.40), (0.70, 0.90), (1, 1.36),
    (1, GLYPH_HEIGHT), (0, 1.81), (0, _BAR), (_ARM, _BAR), (0.28, 0.90),
    (0.60, 0.36), (0, 0.36),
)

# The pentagram: centre, radius of the ring the star is inscribed in.
PENTAGRAM_CENTRE = (573.0, 204.0)
PENTAGRAM_RADIUS = 208.0
PENTAGRAM_LINE = 0.32    # how far the lines move towards the hotter colour
PENTAGRAM_BLOOM = 0.08

FACE_STOPS = (
    (0.00, (124, 144, 178)),
    (0.16, (88, 106, 142)),
    (0.34, (96, 92, 100)),
    (0.48, (146, 98, 60)),
    (0.68, (196, 120, 44)),
    (0.88, (220, 126, 34)),
    (1.00, (236, 140, 38)),
)
GLOW_STOPS = (
    (0.00, (3, 1, 1)),
    (0.18, (14, 2, 1)),
    (0.36, (64, 6, 3)),
    (0.54, (136, 16, 5)),
    (0.70, (196, 40, 7)),
    (0.84, (232, 84, 12)),
    (0.94, (248, 130, 24)),
    (1.00, (255, 184, 60)),
)


def ramp(t: np.ndarray, stops) -> np.ndarray:
    xs = [s[0] for s in stops]
    out = np.empty(t.shape + (3,), np.float32)
    for c in range(3):
        out[..., c] = np.interp(t, xs, [s[1][c] for s in stops])
    return out / 255.0


def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def fbm(shape, rng, cell, octaves=4, stretch=(1.0, 1.0)) -> np.ndarray:
    """Value noise in roughly [-1, 1]; `cell` is the coarsest feature size."""
    acc = np.zeros(shape, np.float32)
    amp, total = 1.0, 0.0
    for _ in range(octaves):
        gh = max(2, int(shape[0] / (cell * stretch[1])) + 2)
        gw = max(2, int(shape[1] / (cell * stretch[0])) + 2)
        grid = rng.random((gh, gw)).astype(np.float32)
        acc += amp * cv2.resize(grid, (shape[1], shape[0]), interpolation=cv2.INTER_CUBIC)
        total += amp
        amp *= 0.5
        cell /= 2.0
    return acc / total * 2.0 - 1.0


def edge_distance(X, Y, p, q):
    """Signed distance to the line p->q, positive on the inside of a clockwise polygon."""
    dx, dy = q[0] - p[0], q[1] - p[1]
    length = math.hypot(dx, dy)
    return ((Y - p[1]) * dx - (X - p[0]) * dy) / length


def segment_distance(X, Y, p, q):
    dx, dy = q[0] - p[0], q[1] - p[1]
    t = np.clip(((X - p[0]) * dx + (Y - p[1]) * dy) / (dx * dx + dy * dy), 0.0, 1.0)
    return np.hypot(X - (p[0] + t * dx), Y - (p[1] + t * dy))


def over(dst_rgb, dst_a, src_rgb, src_a):
    """Composite straight-alpha `src` over premultiplied `dst`, in place."""
    src_a = src_a[..., None]
    dst_rgb *= 1.0 - src_a
    dst_rgb += src_rgb * src_a
    dst_a *= 1.0 - src_a[..., 0]
    dst_a += src_a[..., 0]


def glyph_points(points, x_units):
    ox, oy = GLYPH_ORIGIN
    return [
        (ox + (x + x_units) * GLYPH_SCALE * GLYPH_STRETCH, oy + y * GLYPH_SCALE)
        for x, y in points
    ]


def fill_polygon(mask, points, value):
    pts = np.round(np.array(points, np.float64) * SS * 16).astype(np.int32)
    cv2.fillPoly(mask, [pts], value, lineType=cv2.LINE_8, shift=4)


def render_plate(X, Y, rng):
    tl, tr, br, bl = PLATE
    d_top = edge_distance(X, Y, tl, tr)
    d_right = edge_distance(X, Y, tr, br)
    d_bottom = edge_distance(X, Y, br, bl)
    d_left = edge_distance(X, Y, bl, tl)

    shape = X.shape
    hard = np.clip(np.minimum(np.minimum(d_top, d_right), d_bottom) + 0.5, 0.0, 1.0)
    # The left edge has no line: the plate dissolves, further towards the bottom.
    down = np.clip((Y - tl[1]) / (bl[1] - tl[1]), 0.0, 1.0)
    alpha = hard * smoothstep(-(62.0 + 58.0 * down), 26.0, d_left)

    across = np.clip(d_left / np.maximum(d_left + d_right, 1e-3), 0.0, 1.0)
    haze = fbm(shape, rng, 150 * SS, octaves=4, stretch=(2.2, 1.0))
    wisps = fbm(shape, rng, 46 * SS, octaves=4, stretch=(3.0, 1.0))
    heat = np.clip(across ** 1.2 + 0.12 * haze + 0.04 * wisps, 0.0, 1.0)
    rgb = ramp(heat, GLOW_STOPS)
    rgb *= (1.0 + 0.26 * wisps)[..., None]

    # A hot line along the three hard edges, as on openQ4's plate.
    d_edge = np.minimum(np.minimum(d_top, d_right), d_bottom)
    lit = smoothstep(0.30, 0.85, across)
    rim = np.exp(-((d_edge - 1.2) / 1.5) ** 2) * lit
    inner = np.exp(-np.maximum(d_edge, 0.0) / 13.0) * lit
    rgb += rim[..., None] * np.array([1.0, 0.80, 0.42], np.float32) * 0.85
    rgb += inner[..., None] * np.array([1.0, 0.45, 0.10], np.float32) * 0.22
    return rgb, alpha, heat


def render_pentagram(X, Y):
    """Line coverage and soft halo of the ring and star, both in 0..1."""
    cx, cy = PENTAGRAM_CENTRE
    radius = PENTAGRAM_RADIUS
    r = np.hypot(X - cx, Y - cy)
    dist = np.minimum(np.abs(r - radius), np.abs(r - radius * 1.075) + 0.6)
    # One point down, as Doom 3 draws it.
    tips = [
        (cx + radius * math.cos(math.radians(90 + 72 * k)),
         cy + radius * math.sin(math.radians(90 + 72 * k)))
        for k in range(5)
    ]
    for k in range(5):
        dist = np.minimum(dist, segment_distance(X, Y, tips[k], tips[(k + 2) % 5]))
    core = np.exp(-(dist / 1.9) ** 2)
    halo = np.exp(-(dist / 9.0) ** 2)
    return core, halo


def panel_layers(shape, bbox, rng):
    """Plating for the lettering: per-panel tone, grooves and bright traces."""
    tone = np.zeros(shape, np.float32)
    grooves = np.zeros(shape, np.uint8)
    traces = np.zeros(shape, np.uint8)
    x0, y0, x1, y1 = bbox

    def px(v):
        return int(round(v * SS))

    def split(ax0, ay0, ax1, ay1, depth):
        w, h = ax1 - ax0, ay1 - ay0
        if depth > 6 or (max(w, h) < 46 and rng.random() < 0.75) or max(w, h) < 20:
            tone[px(ay0):px(ay1), px(ax0):px(ax1)] = (
                rng.uniform(-0.42, -0.26) if rng.random() < 0.12 else rng.uniform(-0.17, 0.14))
            cv2.rectangle(grooves, (px(ax0), px(ay0)), (px(ax1), px(ay1)), 255,
                          thickness=max(1, px(0.9)), lineType=cv2.LINE_AA)
            roll = rng.random()
            cut = min(w, h) * rng.uniform(0.3, 0.6)
            if roll < 0.30:      # a chamfered corner
                cv2.line(grooves, (px(ax0), px(ay0 + cut)), (px(ax0 + cut), px(ay0)), 255,
                         max(1, px(0.9)), cv2.LINE_AA)
            elif roll < 0.48:    # a bright trace with a 45 degree bend
                bend = ay0 + h * rng.uniform(0.3, 0.7)
                pts = np.array([[px(ax0 + 3), px(bend + cut * 0.5)],
                                [px(ax0 + 3 + cut * 0.5), px(bend)],
                                [px(ax1 - 3), px(bend)]], np.int32)
                cv2.polylines(traces, [pts], False, 255, max(1, px(1.1)), cv2.LINE_AA)
            return
        if h > w * rng.uniform(0.8, 1.5):
            cut = ay0 + h * rng.uniform(0.32, 0.68)
            split(ax0, ay0, ax1, cut, depth + 1)
            split(ax0, cut, ax1, ay1, depth + 1)
        else:
            cut = ax0 + w * rng.uniform(0.32, 0.68)
            split(ax0, ay0, cut, ay1, depth + 1)
            split(cut, ay0, ax1, ay1, depth + 1)

    split(x0, y0, x1, y1, 0)
    return tone, grooves.astype(np.float32) / 255.0, traces.astype(np.float32) / 255.0


def unit_gradient(field, sigma):
    smooth = cv2.GaussianBlur(field, (0, 0), sigma)
    gx = cv2.Sobel(smooth, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(smooth, cv2.CV_32F, 0, 1, ksize=3)
    norm = np.maximum(np.hypot(gx, gy), 1e-6)
    return gx / norm, gy / norm


def render_lettering(X, Y, rng):
    shape = X.shape
    face = np.zeros(shape, np.uint8)
    three_x = 1.0 + GLYPH_GAP
    fill_polygon(face, glyph_points(D_OUTER, 0.0), 255)
    fill_polygon(face, glyph_points(D_COUNTER, 0.0), 0)
    fill_polygon(face, glyph_points(THREE, three_x), 255)
    face_b = face > 0

    # Sweep the face along the extrusion to get the solid's silhouette.
    solid = face_b.copy()
    steps = int(max(EXTRUDE) * SS)
    for i in range(1, steps + 1):
        dx = int(round(EXTRUDE[0] * SS * i / steps))
        dy = int(round(EXTRUDE[1] * SS * i / steps))
        solid[dy:, dx:] |= face_b[:shape[0] - dy, :shape[1] - dx]

    d_out = cv2.distanceTransform((~face_b).astype(np.uint8), cv2.DIST_L2, 5) / SS
    d_in = cv2.distanceTransform(face_b.astype(np.uint8), cv2.DIST_L2, 5) / SS
    d_solid = cv2.distanceTransform((~solid).astype(np.uint8), cv2.DIST_L2, 5) / SS

    # --- face ---------------------------------------------------------
    ox, oy = GLYPH_ORIGIN
    top, bottom = oy, oy + GLYPH_HEIGHT * GLYPH_SCALE
    left = ox
    right = ox + (2.0 + GLYPH_GAP) * GLYPH_SCALE * GLYPH_STRETCH
    grime = fbm(shape, rng, 30 * SS, octaves=4)
    rust = fbm(shape, rng, 52 * SS, octaves=3)
    t = np.clip((Y - top) / (bottom - top) + 0.05 * rust, 0.0, 1.0)
    rgb = ramp(t, FACE_STOPS)

    tone, grooves, traces = panel_layers(shape, (left - 4, top - 4, right + 4, bottom + 4), rng)
    rgb *= (1.0 + tone)[..., None]
    # Rust creeping into the steel at the top.
    creep = smoothstep(0.15, 0.7, rust) * (1.0 - smoothstep(0.25, 0.55, t)) * 0.55
    rgb += (np.array([0.58, 0.31, 0.13], np.float32) - rgb) * creep[..., None]
    rgb *= (1.0 + 0.17 * grime)[..., None]
    grain = rng.random((shape[0] // 2, shape[1] // 2)).astype(np.float32)
    grain = cv2.resize(grain, (shape[1], shape[0]), interpolation=cv2.INTER_LINEAR)
    rgb *= (0.93 + 0.14 * grain)[..., None]

    # Grooves are dark with a lit lower-right lip.
    lip = np.roll(np.roll(grooves, SS, axis=0), SS, axis=1)
    rgb *= (1.0 - 0.62 * grooves)[..., None]
    rgb += (np.clip(lip - grooves, 0.0, 1.0) * 0.16)[..., None] * np.array([1.0, 0.86, 0.62], np.float32)
    rgb += (np.array([1.0, 0.76, 0.28], np.float32) - rgb) * (traces * 0.8)[..., None]

    # Bevel: a gold rim lit from the upper left, then a dark seam inside it.
    nx, ny = unit_gradient(d_in, 1.0 * SS)
    light = np.clip(0.5 + 0.5 * (nx * 0.5 + ny * 0.866), 0.0, 1.0)
    gold = (np.array([0.66, 0.38, 0.07], np.float32)
            + light[..., None] * (np.array([1.0, 0.93, 0.60], np.float32)
                                  - np.array([0.66, 0.38, 0.07], np.float32)))
    rim = 1.0 - smoothstep(2.3, 3.1, d_in)
    seam = smoothstep(2.3, 3.0, d_in) * (1.0 - smoothstep(3.6, 4.6, d_in))
    occlusion = 0.72 + 0.28 * smoothstep(3.6, 13.0, d_in)
    rgb *= occlusion[..., None]
    rgb *= (1.0 - 0.7 * seam)[..., None]
    rgb += (gold - rgb) * rim[..., None]
    face_rgb = np.clip(rgb, 0.0, 1.0)

    # --- side walls ---------------------------------------------------
    gx, gy = unit_gradient(d_out, 1.2 * SS)
    depth = np.clip(d_out / math.hypot(*EXTRUDE), 0.0, 1.0)
    below = np.clip(gy, 0.0, 1.0)
    beside = np.clip(gx, 0.0, 1.0)
    weight = below + beside + 1e-4
    lower = (np.array([1.0, 0.80, 0.30], np.float32)
             + (depth ** 0.7)[..., None] * (np.array([0.80, 0.27, 0.04], np.float32)
                                            - np.array([1.0, 0.80, 0.30], np.float32)))
    side = (np.array([0.34, 0.31, 0.34], np.float32)
            + depth[..., None] * (np.array([0.10, 0.08, 0.09], np.float32)
                                  - np.array([0.34, 0.31, 0.34], np.float32)))
    wall_rgb = (lower * below[..., None] + side * beside[..., None]) / weight[..., None]
    wall_rgb *= (1.0 + 0.12 * grime)[..., None]

    letter_rgb = np.where(face_b[..., None], face_rgb, np.clip(wall_rgb, 0.0, 1.0))
    solid_f = solid.astype(np.float32)
    outline = np.clip(2.2 - d_solid, 0.0, 1.0)          # black keyline, also covers the solid
    shadow = cv2.GaussianBlur(solid_f, (0, 0), 7.0 * SS)
    shadow = np.roll(np.roll(shadow, 5 * SS, axis=0), 3 * SS, axis=1) * 0.8
    return letter_rgb, solid_f, outline, shadow


def render() -> Image.Image:
    rng = np.random.default_rng(666)
    h, w = HEIGHT * SS, WIDTH * SS
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    X = (xs + 0.5) / SS
    Y = (ys + 0.5) / SS
    del xs, ys

    plate_rgb, plate_a, heat = render_plate(X, Y, rng)
    core, halo = render_pentagram(X, Y)
    # Hotter than the glow it sits in, and only just: an ember line with a faint bloom.
    ember = ramp(np.clip(heat + 0.20, 0.0, 1.0), GLOW_STOPS)
    plate_rgb += (ember - plate_rgb) * (PENTAGRAM_LINE * core + PENTAGRAM_BLOOM * halo)[..., None]
    plate_rgb = np.clip(plate_rgb, 0.0, 1.0)

    rgb = plate_rgb * plate_a[..., None]     # premultiplied from here on
    alpha = plate_a.copy()

    letter_rgb, solid, outline, shadow = render_lettering(X, Y, rng)
    black = np.zeros_like(letter_rgb)
    over(rgb, alpha, black, shadow)
    over(rgb, alpha, black, outline)
    over(rgb, alpha, letter_rgb, solid)

    rgb = cv2.resize(rgb, (WIDTH, HEIGHT), interpolation=cv2.INTER_AREA)
    alpha = cv2.resize(alpha, (WIDTH, HEIGHT), interpolation=cv2.INTER_AREA)

    layer = np.asarray(Image.open(OPEN_LAYER).convert("RGBA"), np.float32) / 255.0
    if layer.shape[:2] != (HEIGHT, LAYER_WIDTH):
        raise SystemExit(f"{OPEN_LAYER} is not {LAYER_WIDTH}x{HEIGHT}")
    layer = layer[:, :WIDTH]
    over(rgb, alpha, layer[..., :3], layer[..., 3])

    straight = rgb / np.maximum(alpha, 1e-5)[..., None]
    out = np.dstack([np.clip(straight, 0.0, 1.0), np.clip(alpha, 0.0, 1.0)])
    out[out[..., 3] < 0.5 / 255.0] = 0.0
    return Image.fromarray(np.round(out * 255.0).astype(np.uint8))


def extract_open(source: Path) -> None:
    """Lift the "open" lettering out of openQ4's banner, on the banner's canvas."""
    banner = np.asarray(Image.open(source).convert("RGBA"))
    if banner.shape[:2] != (HEIGHT, LAYER_WIDTH):
        raise SystemExit(f"{source} is not {LAYER_WIDTH}x{HEIGHT}")
    alpha = banner[..., 3].astype(np.float32) / 255.0
    box = np.zeros(alpha.shape, bool)
    box[156:252, 12:398] = True
    fill = (banner[..., :3].min(axis=2) > 150) & (alpha > 0.5) & box
    # Keep the white fill and the keyline around it; drop the plate's haze beyond.
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    near = cv2.dilate(fill.astype(np.uint8), kernel).astype(np.float32)
    near = np.clip((cv2.GaussianBlur(near, (0, 0), 1.2) - 0.25) / 0.5, 0.0, 1.0)
    layer = banner.copy()
    layer[..., 3] = np.round(alpha * near * 255.0).astype(np.uint8)
    layer[layer[..., 3] == 0] = 0
    OPEN_LAYER.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(layer).save(OPEN_LAYER, optimize=True)
    print(f"wrote {OPEN_LAYER.relative_to(REPO)}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--extract-open", type=Path, metavar="BANNER",
                        help="rebuild the 'open' layer from openQ4's banner and exit")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    if args.extract_open:
        extract_open(args.extract_open)
        return
    image = render()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    image.save(args.output, optimize=True)
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
