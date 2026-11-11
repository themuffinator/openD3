"""Embed openD3's reconstructed Doom 3 faces into the Interface Atlas.

Usage:
    python tools/assets/fonts/embed_atlas_fonts.py [--atlas <page.html>] [--fonts <dir>]

Subsets ``content/baseod3/pak0/fonts/{english,bank,an,micro,bigchars}.ttf`` to
the Latin range the atlas draws, packs each as WOFF and rewrites the
``@font-face`` block between the ``opend3-atlas-fonts`` markers in
``docs/dev/ui/atlas/opend3-interface-atlas.html``. Run it after rebuilding the
faces with ``build_opend3_fonts.py`` so the atlas never drifts from what the
engine ships. The retail atlases are not read here.
"""
from __future__ import annotations

import argparse
import base64
import io
import re
import sys
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[3]
FONTS = ROOT / "content" / "baseod3" / "pak0" / "fonts"
ATLAS = ROOT / "docs" / "dev" / "ui" / "atlas" / "opend3-interface-atlas.html"
START = "/* opend3-atlas-fonts-start */"
END = "/* opend3-atlas-fonts-end */"

# CSS family name -> shipped face
FACES = {
	"openD3 Default": "english.ttf",
	"openD3 Bank": "bank.ttf",
	"openD3 AN": "an.ttf",
	"openD3 Micro": "micro.ttf",
	"openD3 BigChars": "bigchars.ttf",
}

# Basic Latin, Latin-1, general punctuation, arrows, multiplication and minus.
UNICODES = (
	list(range(0x20, 0x7F))
	+ list(range(0xA0, 0x100))
	+ list(range(0x2010, 0x2028))
	+ list(range(0x2190, 0x2194))
	+ [0x2212, 0x20AC]
)


def packed(path: Path) -> tuple[str, int]:
	font = TTFont(path)
	options = subset.Options()
	options.flavor = "woff"
	options.layout_features = ["kern"]
	options.name_IDs = ["*"]
	options.name_legacy = True
	options.notdef_outline = True
	options.hinting = False
	subsetter = subset.Subsetter(options)
	subsetter.populate(unicodes=UNICODES)
	subsetter.subset(font)
	buffer = io.BytesIO()
	font.flavor = "woff"
	font.save(buffer)
	data = buffer.getvalue()
	return base64.b64encode(data).decode("ascii"), len(data)


def main() -> int:
	parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
	parser.add_argument("--atlas", type=Path, default=ATLAS)
	parser.add_argument("--fonts", type=Path, default=FONTS)
	arguments = parser.parse_args()

	rules = [START]
	for family, filename in FACES.items():
		path = arguments.fonts / filename
		if not path.is_file():
			print(f"{path}: missing; build the faces first", file=sys.stderr)
			return 1
		encoded, size = packed(path)
		rules.append(
			f'@font-face{{font-family:"{family}";src:url(data:font/woff;base64,{encoded}) format("woff");'
			f"font-weight:400;font-style:normal;font-display:block}}"
		)
		print(f"{family}: {filename} -> {size} bytes woff")
	rules.append(END)
	block = "\n".join(rules)

	text = arguments.atlas.read_text(encoding="utf-8")
	pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
	if not pattern.search(text):
		print(f"{arguments.atlas}: markers not found", file=sys.stderr)
		return 1
	arguments.atlas.write_text(pattern.sub(lambda _: block, text, count=1), encoding="utf-8", newline="\n")
	print(f"updated {arguments.atlas}")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
