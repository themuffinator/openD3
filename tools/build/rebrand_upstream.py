#!/usr/bin/env python3
"""Rename upstream's project name to openD3 after merging openQ4 (docs/dev/doom3-rebase.md).

Renames the openQ4 token family to openD3 in tracked text files and in tracked paths.

  openQ4 -> openD3, OpenQ4 -> openD3, OPENQ4 -> OPEND3, openq4 -> opend3
  baseoq4 -> baseod3, and the capitalised-O spelling of this project's name -> openD3

References to the upstream project itself (its repository URLs and the git remote name) are
kept. Run with --check to report identifier and path collisions without changing anything.
"""
import pathlib
import re
import subprocess
import sys
from collections import defaultdict

CHECK = "--check" in sys.argv
SKIP_PREFIX = ("src/external/", "src/game/", "src/d3xp/", ".tmp/")
SELF = "tools/build/rebrand_upstream.py"
# Prose files that legitimately talk about the upstream project; handled by hand.
SKIP_FILES = {
    "README.md", "LICENSING.md", "AGENTS.md", "CONTRIBUTORS.md", "BUILDING.md", "TECHNICAL.md",
    ".github/CONTRIBUTING.md", "docs/dev/doom3-rebase.md", "docs/dev/game-source-provenance.md",
    "docs/dev/android-gles-integration.md", SELF,
}
PROTECT = [b"themuffinator/openQ4", b"emileb/openQ4", b"openq4-upstream"]
PAIRS = [(b"openQ4", b"openD3"), (b"OpenQ4", b"openD3"), (b"OPENQ4", b"OPEND3"), (b"openq4", b"opend3"),
         (b"baseoq4", b"baseod3"), (b"Open" + b"D3", b"openD3")]
IDENT = re.compile(rb"[A-Za-z0-9_]*(?:[Oo]pen[Qq]4|OPENQ4)[A-Za-z0-9_]*")


def convert(data: bytes) -> bytes:
    for i, token in enumerate(PROTECT):
        data = data.replace(token, b"\x00PROTECT%d\x00" % i)
    for old, new in PAIRS:
        data = data.replace(old, new)
    for i, token in enumerate(PROTECT):
        data = data.replace(b"\x00PROTECT%d\x00" % i, token)
    return data


files = [f for f in subprocess.run(["git", "ls-files", "-z"], capture_output=True).stdout.decode().split("\0") if f]
files = [f for f in files if not f.startswith(SKIP_PREFIX) and pathlib.Path(f).is_file()]

# --- collisions -------------------------------------------------------------------
existing = set(files)
path_targets = defaultdict(list)
for f in files:
    path_targets[convert(f.encode()).decode()].append(f)
path_collisions = {t: s for t, s in path_targets.items() if len(s) > 1 or (t not in s and t in existing)}

ident_sources = defaultdict(set)
all_idents = set()
texts = {}
for f in files:
    if f in SKIP_FILES:
        continue
    data = pathlib.Path(f).read_bytes()
    if b"\0" in data[:8192]:
        continue
    texts[f] = data
    for m in IDENT.finditer(data):
        ident_sources[convert(m.group(0))].add(m.group(0))
ident_collisions = {t: s for t, s in ident_sources.items() if len(s) > 1}
# identifiers that already exist under the target name
plain = re.compile(rb"[A-Za-z_][A-Za-z0-9_]*(?:openD3|OPEND3|opend3)[A-Za-z0-9_]*|(?:openD3|OPEND3|opend3)[A-Za-z0-9_]+")
already = set()
for data in texts.values():
    already.update(m.group(0) for m in plain.finditer(data))
clash_existing = {t: s for t, s in ident_sources.items() if t in already}

print("files in scope:", len(files), "| text files scanned:", len(texts))
print("path collisions:", len(path_collisions))
for t, s in list(path_collisions.items())[:20]:
    print("  ", t, "<-", s)
print("identifier collisions (two sources, one target):", len(ident_collisions))
for t, s in list(ident_collisions.items())[:40]:
    print("  ", t.decode(), "<-", sorted(x.decode() for x in s))
print("identifiers whose target name already exists:", len(clash_existing))
for t, s in list(clash_existing.items())[:60]:
    print("  ", t.decode(), "<-", sorted(x.decode() for x in s))

if CHECK:
    sys.exit(0)

# --- apply -----------------------------------------------------------------------
changed = 0
for f, data in texts.items():
    new = convert(data)
    if new != data:
        pathlib.Path(f).write_bytes(new)
        changed += 1
renamed = 0
for f in files:
    target = convert(f.encode()).decode()
    if target != f:
        pathlib.Path(target).parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "mv", "-k", f, target], check=True)
        renamed += 1
print("files rewritten:", changed, "| paths renamed:", renamed)
