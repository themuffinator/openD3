"""Rebuild openD3's TrueType faces from the retail Doom 3 bitmap fonts.

Usage:
    python build_opend3_fonts.py --source .tmp/fontsrc
        --donors .tmp/fontdonors --output content/baseod3/pak0/fonts
        [--faces english,an,bank,micro,bigchars]

The source directory is populated by ``extract_source_fonts.py``.  The output
file names match the paths the renderer asks for after it resolves ``fonts``,
``fonts/an``, ``fonts/bank`` and ``fonts/micro`` through ``fonts/english``:
``fonts/english.ttf`` for the default face, then ``fonts/<face>.ttf``.
"""
from __future__ import annotations

import argparse
import sys
import time
from dataclasses import replace
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))

from d3font.build import FaceBuilder, FaceSpec
from d3font.charset import unicode_ranges
from d3font.curvefit import CurveOptions, trace_glyph
from d3font.path import Path2D
from d3font.trace import TraceOptions

VERSION = "1.000"

# Coverage level at which the console sheet's sub-texel counters are picked up.
CONSOLE_COUNTER_LEVEL = 0.8
# Scale of the tracer's distances for the console sheet, against the 48 point
# faces; a third would be proportional. Chosen by coverage error over the
# sheet's letters and digits (0.33: 1.7%, 0.45: 1.25%, 0.6: 1.3%).
CONSOLE_TRACE_SCALE = 0.45

class CurveFaceBuilder(FaceBuilder):
    """FaceBuilder that traces with the curve-fitting tracer.

    Doom 3's 48 point atlases are antialiased renders of drawn typefaces, with
    capitals 26 to 35 pixels tall and stems about three pixels wide.  The
    tracer openQ4's faces were built with models a glyph as stems, diagonals
    and simple arcs and facets these; ``d3font/curvefit.py`` is the tracer
    written for them.  The console sheet is traced the same way, with every
    distance scaled to its 16 pixel cell.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.curve_options = CurveOptions().scaled(self.source.point_size)
        if self.spec.grid_atlas is not None:
            # The tracer's distances shrink with the source so that they keep
            # meaning the same fraction of a letter, but how far contouring
            # rounds a corner does not shrink: it is a texel or so at any size.
            # On a 16 pixel cell the fully scaled corner window is narrower than
            # that rounding and every corner is read as a curve. Scaled part of
            # the way, corners are found again and the coverage error is lowest.
            # A 16 pixel cell also holds counters under a texel wide.
            self.curve_options = replace(CurveOptions().scaled(48.0 * CONSOLE_TRACE_SCALE),
                                         counter_level=CONSOLE_COUNTER_LEVEL)

    def _trace(self, coverage) -> Path2D:
        return trace_glyph(coverage, self.curve_options)


DOOM3_BITMAP_ATTRIBUTION = "the Doom 3 (2004) bitmap fonts by id Software"

# Every Doom 3 atlas draws the same missing-glyph box in DEL and the whole
# 0x80-0x9F band: 33 slots.  Nothing else in a face repeats more than twice
# (the hyphen and the soft hyphen, the underscore and the macron).
PLACEHOLDER_SLOTS = 8

FACES: dict[str, FaceSpec] = {
    "english": FaceSpec(
        source="fonts/english",
        family="openD3 Default",
        description="Doom 3's default face: the wide square sans of the menus, HUD readouts and most device screens.",
        dat_format=True,
        placeholder_slots=PLACEHOLDER_SLOTS,
        project_name="openD3",
        bitmap_attribution=DOOM3_BITMAP_ATTRIBUTION,
    ),
    "an": FaceSpec(
        source="fonts/english/an",
        family="openD3 AN",
        description="Doom 3's narrow grotesque: PDA mail, lists and other dense reading text.",
        dat_format=True,
        placeholder_slots=PLACEHOLDER_SLOTS,
        project_name="openD3",
        bitmap_attribution=DOOM3_BITMAP_ATTRIBUTION,
    ),
    "bank": FaceSpec(
        source="fonts/english/bank",
        family="openD3 Bank",
        # The lowercase slots hold small capitals, and sharp s is drawn "SS".
        all_caps=True,
        description="Doom 3's wide engraver's capitals with small capitals: titles and UAC signage.",
        dat_format=True,
        placeholder_slots=PLACEHOLDER_SLOTS,
        project_name="openD3",
        bitmap_attribution=DOOM3_BITMAP_ATTRIBUTION,
    ),
    "micro": FaceSpec(
        source="fonts/english/micro",
        family="openD3 Micro",
        description="Doom 3's heavy extended square face: large numerals, headings and warnings.",
        dat_format=True,
        placeholder_slots=PLACEHOLDER_SLOTS,
        project_name="openD3",
        bitmap_attribution=DOOM3_BITMAP_ATTRIBUTION,
    ),
    "bigchars": FaceSpec(
        source="textures/bigchars",
        family="openD3 BigChars",
        grid_atlas="textures/bigchars.tga",
        description="Doom 3's fixed-cell console and loading-screen face.",
        project_name="openD3",
        bitmap_attribution=DOOM3_BITMAP_ATTRIBUTION,
    ),
}


def composable_codepoints(second_pass: bool = False) -> list[int]:
    """Everything worth attempting as base plus mark, in a stable order."""
    ranges = unicode_ranges()
    blocks = ("greek", "cyrillic", "cyrillic_supp") if second_pass else ("latin_ext_a", "latin_ext_b", "latin_ext_add")
    wanted: list[int] = []
    for block in blocks:
        low, high = ranges[block]
        wanted.extend(range(low, high + 1))
    return wanted


def build_face(key: str, spec: FaceSpec, source: Path, donors: Path, output: Path) -> dict:
    started = time.perf_counter()
    builder = CurveFaceBuilder(spec, source, donors, TraceOptions())

    builder.trace_source()
    metrics = builder.measure()
    builder.extract_marks(metrics)
    builder.extend_marks(metrics)
    # Dotless i must exist before composing, so i-acute and friends are built
    # on it rather than stacking the accent on the dot.
    builder.synthesize_letters(metrics)
    builder.compose(composable_codepoints())
    builder.alias_homoglyphs()
    # Accented Cyrillic whose base is a shared Latin shape (Yo, for instance)
    # is composed here so it uses the face's own letter rather than the donor's.
    builder.compose(composable_codepoints(second_pass=True))
    # Doom 3's atlases leave DEL and the whole Windows-1252 band as boxes;
    # these are built from the face's own parts before the donor is asked.
    builder.synthesize_latin1(metrics)
    builder.synthesize_shapes(metrics)
    builder.import_donors(metrics)
    builder.fit_to_cell(metrics)
    builder.force_monospace()
    builder.fold_to_base()

    destination = output / f"{key}.ttf"
    builder.emit(destination, metrics, VERSION)

    elapsed = time.perf_counter() - started
    report = dict(builder.report)
    report.update(
        {
            "file": destination.name,
            "glyphs": len(builder.glyphs),
            "mapped": len(builder.cmap),
            "cap": metrics.cap_height,
            "xheight": metrics.x_height,
            "ascender": metrics.ascender,
            "descender": metrics.descender,
            "seconds": round(elapsed, 1),
            "bytes": destination.stat().st_size,
        }
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--donors", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--faces", default="")
    arguments = parser.parse_args()

    keys = [key.strip() for key in arguments.faces.split(",") if key.strip()] or list(FACES)
    unknown = [key for key in keys if key not in FACES]
    if unknown:
        parser.error(f"unknown face(s): {', '.join(unknown)}")

    arguments.output.mkdir(parents=True, exist_ok=True)
    for key in keys:
        report = build_face(key, FACES[key], arguments.source, arguments.donors, arguments.output)
        summary = " ".join(f"{name}={value}" for name, value in report.items())
        print(f"{key:9s} {summary}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
