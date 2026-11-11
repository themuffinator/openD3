"""Extract every retail Doom 3 bitmap font needed by the TTF generator.

Doom 3 keeps four GUI faces under ``fonts/english``: the default face directly
in that folder and ``an``, ``bank`` and ``micro`` beside it.  Each
``fontImage_<size>.dat`` is a Quake 3-style ``fontInfo_t`` whose glyphs point at
one or more ``fontImage_<page>_<size>.tga`` atlas pages.  ``bigchars`` is a
separate 16x16 console sheet under ``textures``.  The source files live in the
game's pk4 files, so no game code needs to run to rebuild the derived TTFs.

Usage:
    python extract_source_fonts.py --install "C:/.../Doom 3" --output .tmp/fontsrc
"""
from __future__ import annotations

import argparse
from pathlib import Path
from zipfile import BadZipFile, ZipFile

FONT_PREFIX = "fonts/english/"
BIGCHARS_PATH = "textures/bigchars.tga"

# The 48 point sources the builder traces, and the console sheet.
REQUIRED = (
	"fonts/english/fontimage_48.dat",
	"fonts/english/an/fontimage_48.dat",
	"fonts/english/bank/fontimage_48.dat",
	"fonts/english/micro/fontimage_48.dat",
	BIGCHARS_PATH,
)


def _is_wanted(path: str) -> bool:
	return (path.startswith(FONT_PREFIX) and path.endswith((".dat", ".tga"))) or path == BIGCHARS_PATH


def _base_directory(install: Path) -> Path:
	"""Accept either the Doom 3 install root or its ``base`` directory."""
	nested = install / "base"
	return nested if nested.is_dir() else install


def extract(install: Path, output: Path) -> int:
	output.mkdir(parents=True, exist_ok=True)
	base = _base_directory(install)
	found = 0

	# Later archives override earlier ones, matching the engine's virtual file
	# system: the 1.3 patch replaces the default face's 12 and 24 point pages
	# and the console sheet.  Keep the original relative paths, lower-cased: the
	# four faces share the same fontImage_*.dat names, so flattening would
	# corrupt the source, and the archives disagree on the case of "fontImage".
	for archive in sorted(base.glob("pak*.pk4")):
		try:
			bundle = ZipFile(archive)
		except BadZipFile:
			print(f"  skipping unreadable archive: {archive.name}")
			continue

		with bundle:
			for entry in bundle.infolist():
				normalized = entry.filename.replace("\\", "/").lower()
				if entry.is_dir() or not _is_wanted(normalized):
					continue
				destination = output / normalized
				destination.parent.mkdir(parents=True, exist_ok=True)
				destination.write_bytes(bundle.read(entry))
				found += 1

	if found == 0:
		return 0

	# Do not silently produce a partial set: a missing page would otherwise
	# appear much later as a blank glyph range.
	missing = [path for path in REQUIRED if not (output / path).is_file()]
	if missing:
		raise RuntimeError("retail Doom 3 font extraction is incomplete: " + ", ".join(missing))
	return found


def main() -> int:
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("--install", required=True, type=Path, help="path to the Doom 3 install root or its base directory")
	parser.add_argument("--output", required=True, type=Path)
	arguments = parser.parse_args()

	if not arguments.install.is_dir():
		parser.error(f"not a directory: {arguments.install}")

	found = extract(arguments.install, arguments.output)
	if found == 0:
		print(f"No retail Doom 3 font entries found under {_base_directory(arguments.install)}")
		return 1

	print(f"extracted {found} files to {arguments.output}")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
