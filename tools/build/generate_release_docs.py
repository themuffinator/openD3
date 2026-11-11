#!/usr/bin/env python3
"""Generate packaged HTML documentation for openD3 releases."""

from __future__ import annotations

import argparse
import html
import os
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import urlsplit


ROOT_DOCS = (
    Path("README.md"),
    Path("BUILDING.md"),
    Path("TECHNICAL.md"),
    Path("LICENSING.md"),
)
COMMUNITY_DOCS = (
    Path(".github") / "CONTRIBUTING.md",
    Path(".github") / "CODE_OF_CONDUCT.md",
)
SAFE_LINK_SCHEMES = {
    "http",
    "https",
    "mailto",
}
REPOSITORY_BLOB_BASE = "https://github.com/themuffinator/openD3/blob/main/"
REPOSITORY_TREE_BASE = "https://github.com/themuffinator/openD3/tree/main/"
DEVELOPMENT_ROADMAP = Path("docs/dev/roadmap.md")


SITE_CSS = r"""
/* The look follows docs/dev/ui-visual-design.md: the Doom 3 front-end menu family.
   Steel-blue transparency over space, chamfered slate plates without outlines,
   glowing hairlines on controls, black wells for rows, pale cyan for anything that
   acts, and console cyan on black for code. 1 u of the stock canvas = 1.5 px.
   The faces are embedded from assets/release/README.html when the site is built. */
:root {
  color-scheme: dark;
  --u: 1.5px;
  --text-active: #ffffff;
  --text-action: #99ffff;
  --text-value: #99cccc;
  --text-caption: #ccffff;
  --text-dim: rgba(255, 255, 255, 0.5);
  --chrome-line-hover: #8ca6bf;
  --chrome-line-flash: #cce6ff;
  --chrome-fill-hover: rgba(140, 166, 191, 0.5);
  --chrome-bar: rgba(115, 153, 178, 0.2);
  --plate-page: rgba(46, 64, 82, 0.8);
  --plate-sheen: rgba(255, 255, 255, 0.14);
  --rule-title: rgba(153, 204, 255, 0.2);
  --rule-group: rgba(153, 204, 255, 0.1);
  --rule-group-header: rgba(153, 204, 255, 0.22);
  --well-row: rgba(0, 0, 0, 0.6);
  --well-inset: rgba(0, 0, 0, 0.5);
  --well-select: rgba(76, 133, 128, 0.5);
  --notice-panel: rgba(0, 0, 0, 0.7);
  --notice-title: #ff9933;
  --danger: #ff1a00;
  --console: #00ffff;
  --face-default: "openD3 Default", "Eurostile", "Bahnschrift", "Segoe UI", sans-serif;
  --face-bank: "openD3 Bank", "Bank Gothic", "Copperplate Gothic Light", "Bahnschrift", sans-serif;
  --face-an: "openD3 AN", "Arial Narrow", "Roboto Condensed", "Segoe UI", sans-serif;
  --face-micro: "openD3 Micro", "Microgramma", "Eurostile Extended", "Bahnschrift", sans-serif;
  --face-console: "openD3 BigChars", "Cascadia Mono", Consolas, monospace;
  --cut-control: calc(5 * var(--u));
  --cut-near: calc(22 * var(--u));
  --cut-far: calc(32 * var(--u));
  --plate-shape: polygon(var(--cut-near) 0, calc(100% - var(--cut-far)) 0, 100% var(--cut-far), 100% calc(100% - var(--cut-near)), calc(100% - var(--cut-near)) 100%, var(--cut-far) 100%, 0 calc(100% - var(--cut-far)), 0 var(--cut-near));
  --shell-shape: polygon(var(--cut-near) 0, 100% 0, 100% calc(100% - var(--cut-near)), calc(100% - var(--cut-near)) 100%, 0 100%, 0 var(--cut-near));
  --control-shape: polygon(0 0, calc(100% - var(--cut-control)) 0, 100% var(--cut-control), 100% 100%, 0 100%);
}

* {
  box-sizing: border-box;
}

html {
  scroll-behavior: smooth;
  background: #000000;
}

body {
  position: relative;
  min-height: 100vh;
  margin: 0;
  overflow-x: hidden;
  color: var(--text-active);
  font-family: var(--face-an);
  font-size: 17px;
  line-height: 1.55;
  background:
    radial-gradient(1px 1px at 12% 18%, rgba(226, 226, 226, 0.7), transparent 60%),
    radial-gradient(1px 1px at 58% 9%, rgba(226, 226, 226, 0.8), transparent 60%),
    radial-gradient(1px 1px at 88% 23%, rgba(226, 226, 226, 0.6), transparent 60%),
    radial-gradient(1px 1px at 33% 72%, rgba(200, 200, 200, 0.5), transparent 60%),
    radial-gradient(1px 1px at 71% 61%, rgba(180, 180, 180, 0.5), transparent 60%),
    #000000;
  background-size: 420px 420px, 420px 420px, 420px 420px, 420px 420px, 420px 420px, auto;
}

/* The planet low and right of centre with its limb halo, and the 15 u grid. */
body::before {
  content: "";
  position: fixed;
  inset: 0;
  z-index: -1;
  pointer-events: none;
  background:
    radial-gradient(160vmax 160vmax at 62% calc(100% + 118vmax), rgba(0, 0, 0, 0) 66.5%, rgba(239, 137, 89, 0.26) 68.2%, rgba(239, 137, 89, 0.08) 69.4%, rgba(0, 0, 0, 0) 71%),
    radial-gradient(160vmax 160vmax at 62% calc(100% + 118vmax), rgba(134, 95, 72, 0.28) 0%, rgba(40, 22, 14, 0.5) 50%, #0a0605 66%, rgba(0, 0, 0, 0) 66.8%),
    linear-gradient(rgba(153, 255, 255, 0.025) 1px, transparent 1px) 0 0 / calc(15 * var(--u)) calc(15 * var(--u)),
    linear-gradient(90deg, rgba(153, 255, 255, 0.025) 1px, transparent 1px) 0 0 / calc(15 * var(--u)) calc(15 * var(--u));
}

/* Scan lines at a 2 u pitch and the edge glow, over everything. */
body::after {
  content: "";
  position: fixed;
  inset: 0;
  z-index: 10;
  pointer-events: none;
  background: repeating-linear-gradient(180deg, rgba(0, 0, 0, 0.08) 0 1.5px, rgba(0, 0, 0, 0) 1.5px 3px);
  box-shadow: inset 0 0 70px rgba(51, 59, 64, 0.9);
}

a {
  color: var(--text-action);
  text-decoration: none;
  transition: color 400ms linear;
}

a:hover,
a:focus-visible {
  color: var(--text-active);
  outline: none;
  transition: none;
}

img {
  max-width: 100%;
}

code,
pre,
kbd,
samp {
  font-family: var(--face-console);
}

.shell {
  width: min(1400px, calc(100% - 32px));
  margin: 0 auto 48px;
}

/* The top bar (section 6.8), full bleed above the page. */
.shell::before {
  content: "";
  display: block;
  height: calc(16 * var(--u));
  margin: 0 calc(50% - 50vw) calc(10 * var(--u));
  background: linear-gradient(180deg, rgba(115, 153, 178, 0.12) 0 75%, var(--chrome-bar) 75% 100%);
}

/* Page plates: slate at 80%, chamfered, no outline, a sheen from the top-leading corner. */
.topbar,
.sidebar,
.article,
.toc,
.hero,
.catalog,
.footer {
  background:
    radial-gradient(calc(340 * var(--u)) calc(279 * var(--u)) at 0 0, var(--plate-sheen), rgba(255, 255, 255, 0) 50%),
    var(--plate-page);
  clip-path: var(--plate-shape);
}

.sidebar,
.toc,
.footer {
  clip-path: var(--shell-shape);
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  padding: 18px 34px;
  margin-bottom: 16px;
}

.brand {
  display: grid;
  gap: 2px;
}

.brand a {
  color: var(--text-active);
}

.eyebrow {
  display: inline-block;
  color: var(--text-dim);
  font-family: var(--face-bank);
  font-size: calc(48 * 0.25 * var(--u));
}

.brand-title {
  font-family: var(--face-default);
  font-size: calc(48 * 0.32 * var(--u));
  text-transform: uppercase;
}

.brand-subtitle {
  color: var(--text-value);
  font-size: 0.95rem;
}

.action-row,
.hero-actions,
.hero-meta,
.article-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

/* Small glow buttons (section 6.5): hairline frame, soft fill, 5 u chamfer top-trailing. */
.button {
  position: relative;
  display: inline-flex;
  align-items: center;
  padding: 6px 18px 5px;
  background: linear-gradient(180deg, rgba(128, 178, 204, 0.27), rgba(128, 178, 204, 0.2) 50%, rgba(128, 178, 204, 0.27));
  clip-path: var(--control-shape);
  color: var(--text-action);
  font-family: var(--face-default);
  font-size: calc(48 * 0.25 * var(--u));
  text-transform: uppercase;
  transition: background 400ms linear, color 400ms linear;
}

.button::after {
  content: "";
  position: absolute;
  inset: 0;
  background: rgba(128, 178, 204, 0.5);
  clip-path: polygon(evenodd, 0 0, calc(100% - var(--cut-control)) 0, 100% var(--cut-control), 100% 100%, 0 100%, 0 0, 1px 1px, 1px calc(100% - 1px), calc(100% - 1px) calc(100% - 1px), calc(100% - 1px) calc(var(--cut-control) + 0.5px), calc(100% - var(--cut-control) - 0.5px) 1px, 1px 1px);
  transition: background 400ms linear;
}

.button:hover,
.button:focus-visible {
  background: linear-gradient(180deg, rgba(153, 204, 230, 0.53), rgba(153, 204, 230, 0.4) 50%, rgba(153, 204, 230, 0.53));
  color: var(--text-active);
  outline: none;
  transition: none;
}

.button:hover::after,
.button:focus-visible::after {
  background: #99cce6;
  animation: line-flash 250ms linear;
  transition: none;
}

.button:active {
  background: rgba(255, 255, 255, 0.8);
}

.button.primary {
  color: var(--text-active);
  background: linear-gradient(180deg, rgba(140, 166, 191, 0.5), rgba(115, 140, 178, 0.4) 50%, rgba(140, 166, 191, 0.5));
}

@keyframes line-flash {
  from { background: var(--chrome-line-flash); }
}

/* Chips are bare values on a black well (section 6.7). */
.chip {
  display: inline-flex;
  align-items: center;
  padding: 3px 12px;
  background: var(--well-row);
  clip-path: var(--control-shape);
  color: var(--text-value);
  font-family: var(--face-bank);
  font-size: calc(48 * 0.25 * var(--u));
}

.layout {
  display: grid;
  grid-template-columns: 270px minmax(0, 1fr) 240px;
  gap: 16px;
}

.sidebar,
.toc {
  position: sticky;
  top: 16px;
  align-self: start;
  padding: 18px 16px 26px;
}

/* Titles with the title rule under them (section 6.6). */
.sidebar h2,
.toc h2 {
  margin: 0 -16px 12px;
  padding: 0 16px 6px 34px;
  border-bottom: calc(2 * var(--u)) solid var(--rule-title);
  font-family: var(--face-default);
  font-size: calc(48 * 0.26 * var(--u));
  font-weight: 400;
  text-transform: uppercase;
}

.nav-group + .nav-group {
  margin-top: 16px;
}

/* Group captions in Bank on a header band. */
.nav-group h3 {
  margin: 0 0 6px;
  padding: 2px 8px;
  background: var(--rule-group-header);
  color: var(--text-caption);
  font-family: var(--face-bank);
  font-size: calc(48 * 0.25 * var(--u));
  font-weight: 400;
}

.nav-links,
.toc-links {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: calc(1 * var(--u));
}

/* Sub-menu items (section 6.4): no idle plate; a plate on hover; the current page selected. */
.nav-links a,
.toc-links a {
  display: block;
  padding: 3px 10px;
  clip-path: var(--control-shape);
  color: var(--text-action);
  line-height: 1.3;
  transition: background 400ms linear, color 400ms linear;
}

.nav-links a:hover,
.toc-links a:hover,
.nav-links a:focus-visible,
.toc-links a:focus-visible {
  background: var(--chrome-fill-hover);
  color: var(--text-active);
  transition: none;
}

.nav-links a.active,
.toc-links a.active {
  background: var(--well-select);
  color: var(--text-active);
}

.toc-links ul {
  list-style: none;
  margin: 2px 0 0 12px;
  padding: 0 0 0 8px;
  border-left: 1px solid var(--rule-title);
}

.article,
.hero,
.catalog,
.footer {
  padding: 26px 34px 34px;
}

.hero-banner {
  display: block;
  width: min(100%, 720px);
  margin: 0 auto 18px;
}

/* Page titles: Default, capitals, white. */
.hero h1,
.article-header h1 {
  margin: 0 0 10px;
  font-family: var(--face-default);
  font-size: calc(48 * 0.42 * var(--u));
  font-weight: 400;
  line-height: 1.2;
  text-transform: uppercase;
}

.hero p,
.article-header p {
  margin: 0 0 14px;
}

.hero .lead,
.article-header .lead {
  max-width: 820px;
  color: var(--text-value);
}

.catalog {
  margin-top: 16px;
}

.catalog h2 {
  margin: 0 0 14px;
  padding-bottom: 6px;
  border-bottom: calc(2 * var(--u)) solid var(--rule-title);
  font-family: var(--face-default);
  font-size: calc(48 * 0.32 * var(--u));
  font-weight: 400;
  text-transform: uppercase;
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

/* Cards are group boxes: a faint body with a chamfered bottom-trailing corner. */
.card {
  padding: 14px 16px 16px;
  background: var(--rule-group);
  clip-path: polygon(0 0, 100% 0, 100% calc(100% - var(--cut-control)), calc(100% - var(--cut-control)) 100%, 0 100%);
}

.card h3 {
  margin: 4px 0 8px;
  font-family: var(--face-default);
  font-size: calc(48 * 0.26 * var(--u));
  font-weight: 400;
  text-transform: uppercase;
}

.card p {
  margin: 0 0 10px;
  color: var(--text-value);
}

.card ul {
  margin: 0;
  padding-left: 18px;
}

.card li + li {
  margin-top: 5px;
}

.article-header {
  margin: 0 -34px 20px;
  padding: 0 34px 16px;
  border-bottom: calc(2 * var(--u)) solid var(--rule-title);
}

.article-content {
  min-width: 0;
}

.article-content h1,
.article-content h2,
.article-content h3,
.article-content h4,
.article-content h5,
.article-content h6 {
  margin: 28px 0 12px;
  font-weight: 400;
  line-height: 1.25;
}

.article-content h1,
.article-content h2 {
  padding: 3px 12px;
  background: var(--rule-group-header);
  font-family: var(--face-default);
  font-size: calc(48 * 0.32 * var(--u));
  text-transform: uppercase;
}

.article-content h3 {
  color: var(--text-caption);
  font-family: var(--face-bank);
  font-size: calc(48 * 0.3 * var(--u));
}

.article-content h4,
.article-content h5,
.article-content h6 {
  color: var(--text-caption);
  font-family: var(--face-bank);
  font-size: calc(48 * 0.25 * var(--u));
}

.article-content p {
  margin: 0 0 14px;
}

.article-content ul,
.article-content ol {
  margin: 0 0 16px;
  padding-left: 24px;
}

.article-content li + li {
  margin-top: 6px;
}

.article-content li::marker {
  color: var(--chrome-line-hover);
}

.article-content strong {
  color: var(--text-caption);
  font-weight: 400;
}

.article-content hr {
  height: calc(2 * var(--u));
  margin: 26px 0;
  border: 0;
  background: var(--rule-title);
}

/* Callouts are notices (section 10.2): a dark panel, the kind as a Micro title. */
.article-content blockquote,
.article-content .admonition {
  margin: 18px 0;
  padding: 12px 16px;
  background: var(--notice-panel);
  clip-path: var(--control-shape);
  color: var(--text-value);
}

.article-content .admonition-title {
  margin: 0 0 4px;
  color: var(--text-action);
  font-family: var(--face-micro);
  font-size: calc(48 * 0.31 * var(--u));
  text-transform: uppercase;
}

.article-content .admonition.tip .admonition-title {
  color: #33cc99;
}

.article-content .admonition.warning .admonition-title {
  color: var(--notice-title);
}

.article-content .admonition.caution .admonition-title {
  color: var(--danger);
}

/* Code is console text (section 10.15): cyan on black in BigChars. Its square cells are
   drawn at half width by the engine, so the advance is pulled in to match. */
.article-content pre {
  margin: 16px 0;
  padding: 14px 16px;
  overflow-x: auto;
  background: rgba(0, 0, 0, 0.85);
  border-top: calc(2 * var(--u)) solid rgba(0, 255, 255, 0.5);
  color: var(--console);
  font-size: 0.95rem;
  line-height: 1.45;
  letter-spacing: -0.4em;
}

.article-content code {
  padding: 0 calc(3 * var(--u) + 0.4em) 0 calc(3 * var(--u));
  background: var(--well-inset);
  color: var(--console);
  font-size: 0.95em;
  letter-spacing: -0.4em;
}

.article-content pre code {
  padding: 0;
  background: transparent;
  font-size: inherit;
}

.article-content a code {
  color: inherit;
}

/* Tables are option rows: black wells under a header band. */
.article-content table {
  width: 100%;
  margin: 18px 0;
  border-collapse: separate;
  border-spacing: 0 calc(3 * var(--u));
}

.article-content th {
  padding: 4px 12px;
  background: var(--rule-group-header);
  color: var(--text-caption);
  font-family: var(--face-bank);
  font-size: calc(48 * 0.25 * var(--u));
  font-weight: 400;
  text-align: left;
}

.article-content td {
  padding: 6px 12px;
  background: var(--well-row);
  color: var(--text-value);
  vertical-align: top;
}

.article-content td:first-child {
  color: var(--text-active);
}

.article-content details {
  margin: 18px 0;
  padding: 10px 16px;
  background: var(--rule-group);
  clip-path: var(--control-shape);
}

.article-content summary {
  cursor: pointer;
  color: var(--text-action);
  font-family: var(--face-default);
  text-transform: uppercase;
}

/* Check boxes (section 6.6): an 8 u box, filled when set. */
.article-content .task-box {
  display: inline-grid;
  place-items: center;
  width: calc(8 * var(--u));
  height: calc(8 * var(--u));
  margin-right: 0.45rem;
  border: 1px solid rgba(128, 178, 178, 0.8);
  color: transparent;
  font-size: 0.7rem;
}

.article-content .task-box.done {
  border-color: rgba(153, 255, 255, 0.8);
  background: rgba(153, 255, 255, 0.4);
}

.article-content img {
  display: block;
  margin: 18px auto;
}

.article-content p[align="center"],
.article-content div[align="center"] {
  text-align: center;
}

.article-content sub {
  color: var(--text-value);
}

.footer {
  margin-top: 16px;
  color: var(--text-dim);
  font-size: 0.92rem;
}

.footer p:last-child {
  margin-bottom: 0;
}

::selection {
  background: var(--well-select);
  color: #ffffff;
}

@media (prefers-reduced-motion: reduce) {
  .button:hover::after,
  .button:focus-visible::after {
    animation: none;
  }
}

@media (max-width: 1180px) {
  .layout {
    grid-template-columns: 250px minmax(0, 1fr);
  }

  .toc {
    display: none;
  }
}

@media (max-width: 860px) {
  :root {
    --u: 1.25px;
  }

  .topbar,
  .hero,
  .catalog,
  .sidebar,
  .article,
  .footer {
    padding: 18px 22px 24px;
  }

  .article-header {
    margin: 0 -22px 18px;
    padding: 0 22px 14px;
  }

  .topbar {
    align-items: start;
    flex-direction: column;
  }

  .layout,
  .card-grid {
    grid-template-columns: 1fr;
  }

  .sidebar,
  .toc {
    position: static;
  }
}
"""


@dataclass(frozen=True)
class DocSpec:
    source_relative: Path
    output_relative: Path
    group: str
    title: str
    nav_title: str
    summary: str


@dataclass(frozen=True)
class GeneratedDocSite:
    output_root: Path
    index_path: Path
    page_count: int


RELEASE_README = Path("assets") / "release" / "README.html"
FONT_FACES_START = "/* opend3-atlas-fonts-start */"
FONT_FACES_END = "/* opend3-atlas-fonts-end */"


def site_font_faces(source_root: Path) -> str:
    """Return the @font-face rules embedded in the release readme.

    The readme carries openD3's reconstructed Doom 3 faces (written there by
    tools/assets/fonts/embed_atlas_fonts.py), so the site draws the same type.
    Without them the stylesheet falls back to system faces.
    """
    readme = source_root / RELEASE_README
    if readme.is_symlink() or not readme.is_file():
        return ""
    text = readme.read_text(encoding="utf-8")
    start = text.find(FONT_FACES_START)
    end = text.find(FONT_FACES_END, start + 1)
    if start < 0 or end < 0:
        return ""
    return text[start : end + len(FONT_FACES_END)] + "\n\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate packaged HTML documentation for an openD3 release."
    )
    parser.add_argument("--source-root", default=".", help="openD3 repository root.")
    parser.add_argument("--output-dir", required=True, help="Directory to populate with HTML docs.")
    parser.add_argument("--version", required=True, help="Release version string.")
    parser.add_argument("--platform", required=True, help="Target package platform.")
    parser.add_argument("--arch", required=True, help="Target package architecture.")
    return parser.parse_args(argv[1:])


def require_markdown_module() -> Any:
    try:
        import markdown as markdown_lib
    except ImportError as exc:
        raise RuntimeError(
            "Release HTML docs require the Python-Markdown package. "
            "Install it with: python -m pip install markdown"
        ) from exc
    return markdown_lib


def is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def validate_output_root(source_root: Path, output_root: Path) -> None:
    source_root = source_root.resolve()
    raw_output_root = output_root
    output_root = output_root.resolve()
    output_anchor = Path(output_root.anchor).resolve()

    if raw_output_root.is_symlink():
        raise RuntimeError(f"refusing to generate release docs into a symlinked output directory: {raw_output_root}")
    if output_root == output_anchor:
        raise RuntimeError(f"refusing to replace filesystem root while generating docs: {output_root}")
    if output_root == source_root or is_relative_to(source_root, output_root):
        raise RuntimeError(
            "refusing to generate release docs into the source root or one of its parent directories: "
            f"{output_root}"
        )
    if is_relative_to(output_root, source_root):
        relative = output_root.relative_to(source_root)
        first_part = relative.parts[0] if relative.parts else ""
        if first_part not in {".tmp", ".install"} and not first_part.startswith("builddir"):
            raise RuntimeError(
                "refusing to replace a source-controlled repository directory while generating docs: "
                f"{output_root}"
            )
    if output_root.exists() and not output_root.is_dir():
        raise RuntimeError(f"release docs output path exists but is not a directory: {output_root}")


def validate_source_root(source_root: Path) -> Path:
    if source_root.is_symlink():
        raise RuntimeError(f"release docs source root must not be a symlink: {source_root}")
    resolved = source_root.resolve()
    if not resolved.is_dir():
        raise RuntimeError(f"release docs source root not found: {resolved}")
    return resolved


def require_regular_doc_source(path: Path, relative: Path) -> None:
    if path.is_symlink():
        raise RuntimeError(f"refusing to package symlinked documentation source: {relative.as_posix()}")
    if not path.is_file():
        raise RuntimeError(f"documentation source is not a regular file: {relative.as_posix()}")


def collect_doc_sources(source_root: Path) -> list[Path]:
    docs: list[Path] = []
    seen: set[str] = set()

    for relative in (*ROOT_DOCS, *COMMUNITY_DOCS):
        candidate = source_root / relative
        if candidate.exists() or candidate.is_symlink():
            require_regular_doc_source(candidate, relative)
            docs.append(relative)
            seen.add(relative.as_posix().lower())

    for base in (Path("docs/user"), Path("docs/dev")):
        base_path = source_root / base
        if not base_path.is_dir():
            continue
        for path in sorted(base_path.rglob("*")):
            relative = path.relative_to(source_root)
            if path.is_symlink():
                raise RuntimeError(f"refusing to package symlinked documentation source: {relative.as_posix()}")
            if path.suffix.lower() != ".md":
                continue
            if not path.is_file():
                continue
            key = relative.as_posix().lower()
            if key in seen:
                continue
            docs.append(relative)
            seen.add(key)

    return docs


def classify_group(relative: Path) -> str:
    if relative.parent == Path("."):
        return "Project"
    if relative.parts[0] == ".github":
        return "Project"
    if len(relative.parts) >= 2 and relative.parts[0] == "docs" and relative.parts[1] == "user":
        return "User Guides"
    if relative.parts[:3] == ("docs", "dev", "archive"):
        return "Planning Archive"
    if len(relative.parts) >= 3 and relative.parts[0] == "docs" and relative.parts[1] == "dev" and relative.parts[2] == "proposals":
        return "Research and Proposals"
    if len(relative.parts) >= 3 and relative.parts[0] == "docs" and relative.parts[1] == "dev" and relative.parts[2] == "legacy":
        return "Legacy Notes"
    return "Developer Guides"


def default_nav_title(relative: Path) -> str:
    if relative == DEVELOPMENT_ROADMAP:
        return "Development roadmap"
    if relative == Path("README.md"):
        return "Overview"
    if relative == Path("BUILDING.md"):
        return "Build Guide"
    if relative == Path("TECHNICAL.md"):
        return "Technical Reference"
    if relative == Path(".github") / "CONTRIBUTING.md":
        return "Contributing"
    if relative == Path(".github") / "CODE_OF_CONDUCT.md":
        return "Code of Conduct"

    stem = relative.stem.replace("-", " ").replace("_", " ").strip()
    if not stem:
        stem = relative.name
    return " ".join(part.capitalize() if part.islower() else part for part in stem.split())


def resolve_site_relative(source_relative: Path, target: str) -> str | None:
    """Resolve a relative link target against a document's site location.

    Returns the normalized root-relative posix path, or None when the target
    escapes the documentation root.
    """
    parts: list[str] = []
    combined = PurePosixPath(source_relative.parent.as_posix()) / target
    for part in combined.parts:
        if part == ".":
            continue
        if part == "..":
            if not parts:
                return None
            parts.pop()
        else:
            parts.append(part)
    return "/".join(parts)


def rewrite_markdown_links(
    text: str,
    *,
    source_relative: Path | None = None,
    rendered_sources: set[str] | None = None,
) -> str:
    pattern = re.compile(r"(!?\[(?:[^\[\]]|!\[[^\]]*\]\([^)]+\))+\]\()([^)]+)(\))")

    def replace(match: re.Match[str]) -> str:
        prefix, target, suffix = match.groups()
        stripped_target = target.strip()
        if stripped_target.startswith("#"):
            return match.group(0)

        parsed = urlsplit(stripped_target)
        if parsed.scheme:
            scheme = parsed.scheme.lower()
            if scheme not in SAFE_LINK_SCHEMES:
                return prefix + "#" + suffix
            return match.group(0)

        hash_suffix = ""
        if "#" in stripped_target:
            base, fragment = stripped_target.split("#", 1)
            stripped_target = base
            hash_suffix = "#" + fragment

        if stripped_target.lower().endswith(".md"):
            if rendered_sources is not None and source_relative is not None:
                resolved = resolve_site_relative(source_relative, stripped_target)
                if resolved is None or resolved.lower() not in rendered_sources:
                    # The target exists in the repository but is not part of the
                    # generated site; keep the link alive by pointing at the
                    # repository copy instead of a dead local page.
                    repo_target = resolved if resolved is not None else stripped_target
                    return prefix + REPOSITORY_BLOB_BASE + repo_target + hash_suffix + suffix
            stripped_target = stripped_target[:-3] + ".html"

        elif stripped_target.endswith("/") and source_relative is not None:
            # Source directories are browsed in the repository, rather than
            # copied into player documentation with compiler inputs.
            resolved = resolve_site_relative(source_relative, stripped_target)
            if resolved is not None:
                return prefix + REPOSITORY_TREE_BASE + resolved + hash_suffix + suffix

        return prefix + stripped_target + hash_suffix + suffix

    return pattern.sub(replace, text)


def copy_docs_asset_tree(source_root: Path, destination_root: Path) -> None:
    if source_root.is_symlink():
        raise RuntimeError(f"refusing to copy symlinked documentation asset directory: {source_root}")
    if not source_root.is_dir():
        return

    for path in sorted(source_root.rglob("*")):
        relative = path.relative_to(source_root)
        if path.is_symlink():
            raise RuntimeError(f"refusing to copy symlinked documentation asset: {relative.as_posix()}")
        destination = destination_root / relative
        if path.is_dir():
            destination.mkdir(parents=True, exist_ok=True)
        elif path.is_file():
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination)
        else:
            raise RuntimeError(f"refusing to copy non-regular documentation asset: {relative.as_posix()}")


def copy_docs_auxiliary_file(source_root: Path, relative: Path, destination: Path) -> None:
    source = source_root / relative
    if source.is_symlink():
        raise RuntimeError(f"refusing to copy symlinked documentation auxiliary file: {relative.as_posix()}")
    if not source.is_file():
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def convert_github_callouts(text: str) -> str:
    lines = text.splitlines()
    result: list[str] = []
    index = 0

    while index < len(lines):
        stripped = lines[index].strip()
        match = re.match(r"^>\s*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\s*$", stripped)
        if match is None:
            result.append(lines[index])
            index += 1
            continue

        level = match.group(1).lower()
        result.append(f"!!! {level}")
        index += 1
        while index < len(lines) and lines[index].lstrip().startswith(">"):
            content = lines[index].lstrip()[1:]
            if content.startswith(" "):
                content = content[1:]
            if content:
                result.append("    " + content)
            else:
                result.append("")
            index += 1

    return "\n".join(result)


def convert_task_lists(text: str) -> str:
    result: list[str] = []
    pattern = re.compile(r"^(\s*[-*+]\s+)\[( |x|X)\]\s+(.*)$")

    for line in text.splitlines():
        match = pattern.match(line)
        if match is None:
            result.append(line)
            continue

        prefix, state, body = match.groups()
        classes = "task-box done" if state.lower() == "x" else "task-box"
        symbol = "&#10003;" if state.lower() == "x" else "&nbsp;"
        result.append(f'{prefix}<span class="{classes}">{symbol}</span> {body}')

    return "\n".join(result)


def prepare_markdown(
    text: str,
    *,
    source_relative: Path | None = None,
    rendered_sources: set[str] | None = None,
) -> str:
    normalized = text.replace("\r\n", "\n")
    normalized = re.sub(
        r"(?m)^<details(?![^>]*markdown=)",
        '<details markdown="1"',
        normalized,
    )
    normalized = re.sub(
        r"(?m)^<div(?![^>]*markdown=)",
        '<div markdown="1"',
        normalized,
    )
    normalized = rewrite_markdown_links(
        normalized,
        source_relative=source_relative,
        rendered_sources=rendered_sources,
    )
    normalized = convert_task_lists(normalized)
    normalized = convert_github_callouts(normalized)
    return normalized


def strip_markdown_preview(text: str) -> str:
    preview = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", text)
    preview = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", preview)
    preview = re.sub(r"`([^`]+)`", r"\1", preview)
    preview = re.sub(r"<[^>]+>", "", preview)
    preview = preview.replace("**", "").replace("__", "").replace("*", "").replace("_", "")
    preview = re.sub(r"\s+", " ", preview)
    return preview.strip()


def extract_title_and_summary(relative: Path, text: str) -> tuple[str, str]:
    lines = text.replace("\r\n", "\n").splitlines()

    title = default_nav_title(relative)
    for line in lines:
        match = re.match(r"^#\s+(.*)$", line.strip())
        if match is not None:
            title = strip_markdown_preview(match.group(1))
            break

    summary_lines: list[str] = []
    in_code_block = False
    title_found = False
    for raw_line in lines:
        stripped = raw_line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        if not title_found:
            if re.match(r"^#\s+", stripped):
                title_found = True
            continue

        if not stripped:
            if summary_lines:
                break
            continue

        if stripped.startswith(("#", ">", "-", "*", "|", "<")):
            if summary_lines:
                break
            continue

        if re.match(r"^\d+\.\s+", stripped):
            if summary_lines:
                break
            continue

        summary_lines.append(stripped)

    summary = strip_markdown_preview(" ".join(summary_lines))
    return title, summary


def build_doc_specs(source_root: Path) -> list[DocSpec]:
    specs: list[DocSpec] = []
    for relative in collect_doc_sources(source_root):
        title, summary = extract_title_and_summary(
            relative,
            (source_root / relative).read_text(encoding="utf-8"),
        )
        if not summary and relative == Path("README.md"):
            summary = (
                "Project overview, runtime scope, compatibility goals, and the main "
                "documentation map for openD3."
            )
        specs.append(
            DocSpec(
                source_relative=relative,
                output_relative=relative.with_suffix(".html"),
                group=classify_group(relative),
                title=title,
                nav_title=default_nav_title(relative) if relative == DEVELOPMENT_ROADMAP or relative.parent in (Path("."), Path(".github")) else title,
                summary=summary,
            )
        )
    # Keep the active plan first within developer navigation; retain the
    # established relative order of all other documents.
    specs.sort(key=lambda spec: spec.source_relative != DEVELOPMENT_ROADMAP)
    return specs


def relative_href(current_parent: Path, target: Path) -> str:
    return os.path.relpath(target, start=current_parent if current_parent != Path(".") else Path(".")).replace("\\", "/")


def render_sidebar(specs: list[DocSpec], current_output: Path) -> str:
    grouped: dict[str, list[DocSpec]] = {}
    for spec in specs:
        grouped.setdefault(spec.group, []).append(spec)

    group_order = (
        "Project",
        "User Guides",
        "Developer Guides",
        "Research and Proposals",
        "Legacy Notes",
        "Planning Archive",
    )

    sections: list[str] = []
    current_parent = current_output.parent
    for group in group_order:
        group_specs = grouped.get(group)
        if not group_specs:
            continue

        links = []
        for spec in group_specs:
            href = relative_href(current_parent, spec.output_relative)
            if spec.output_relative == current_output:
                links.append(
                    f'<li><a class="active" href="{html.escape(href)}">{html.escape(spec.nav_title)}</a></li>'
                )
            else:
                links.append(
                    f'<li><a href="{html.escape(href)}">{html.escape(spec.nav_title)}</a></li>'
                )

        sections.append(
            "\n".join(
                [
                    '<section class="nav-group">',
                    f"<h3>{html.escape(group)}</h3>",
                    '<ul class="nav-links">',
                    *links,
                    "</ul>",
                    "</section>",
                ]
            )
        )

    return "\n".join(sections)


def normalize_toc_tokens(tokens: list[dict[str, Any]], title: str) -> list[dict[str, Any]]:
    if len(tokens) == 1 and tokens[0].get("level") == 1:
        token_name = strip_markdown_preview(str(tokens[0].get("name", "")))
        if token_name == title:
            return list(tokens[0].get("children", []))
    return tokens


def render_toc_items(items: list[dict[str, Any]]) -> str:
    if not items:
        return ""

    rendered: list[str] = ['<ul class="toc-links">']
    for item in items:
        heading_id = html.escape(str(item.get("id", "")))
        heading_name = strip_markdown_preview(str(item.get("name", "")))
        rendered.append(f'<li><a href="#{heading_id}">{html.escape(heading_name)}</a>')
        children = item.get("children") or []
        if children:
            rendered.append(render_toc_items(list(children)))
        rendered.append("</li>")
    rendered.append("</ul>")
    return "\n".join(rendered)


def render_doc_page(
    spec: DocSpec,
    specs: list[DocSpec],
    version: str,
    platform: str,
    arch: str,
    body_html: str,
    toc_tokens: list[dict[str, Any]],
) -> str:
    current_parent = spec.output_relative.parent
    css_href = relative_href(current_parent, Path("_static") / "site.css")
    docs_home_href = relative_href(current_parent, Path("index.html"))
    package_home_href = relative_href(current_parent, Path("..") / "README.html")
    overview_href = relative_href(current_parent, Path("README.html"))

    sidebar_html = render_sidebar(specs, spec.output_relative)
    toc_html = render_toc_items(normalize_toc_tokens(toc_tokens, spec.title))
    if not toc_html:
        toc_html = '<p class="brand-subtitle">This page has no generated section index.</p>'

    summary_html = (
        f'<p class="lead">{html.escape(spec.summary)}</p>'
        if spec.summary
        else '<p class="lead">Included in the packaged openD3 offline documentation set.</p>'
    )

    return "\n".join(
        [
            "<!DOCTYPE html>",
            '<html lang="en">',
            "<head>",
            '  <meta charset="UTF-8">',
            '  <meta name="viewport" content="width=device-width, initial-scale=1.0">',
            '  <meta name="color-scheme" content="dark">',
            f"  <title>{html.escape(spec.title)} | openD3 Documentation</title>",
            f'  <link rel="stylesheet" href="{html.escape(css_href)}">',
            "</head>",
            "<body>",
            '  <div class="shell">',
            '    <header class="topbar">',
            '      <div class="brand">',
            '        <span class="eyebrow">Packaged HTML documentation</span>',
            f'        <a class="brand-title" href="{html.escape(docs_home_href)}">openD3 Documentation</a>',
            f'        <div class="brand-subtitle">Release {html.escape(version)} · {html.escape(platform)} · {html.escape(arch)}</div>',
            "      </div>",
            '      <div class="action-row">',
            f'        <a class="button primary" href="{html.escape(docs_home_href)}">Docs Home</a>',
            f'        <a class="button" href="{html.escape(overview_href)}">Project Overview</a>',
            f'        <a class="button" href="{html.escape(package_home_href)}">Package Home</a>',
            '        <a class="button" href="https://github.com/themuffinator/openD3">GitHub</a>',
            "      </div>",
            "    </header>",
            '    <div class="layout">',
            '      <aside class="sidebar">',
            '        <h2>Documentation</h2>',
            sidebar_html,
            "      </aside>",
            '      <main class="article">',
            '        <header class="article-header">',
            f'          <span class="eyebrow">{html.escape(spec.group)}</span>',
            f"          <h1>{html.escape(spec.title)}</h1>",
            summary_html,
            '          <div class="article-meta">',
            f'            <span class="chip">{html.escape(spec.source_relative.as_posix())}</span>',
            f'            <span class="chip">Release {html.escape(version)}</span>',
            "          </div>",
            "        </header>",
            f'        <article class="article-content">{body_html}</article>',
            "      </main>",
            '      <aside class="toc">',
            '        <h2>On This Page</h2>',
            toc_html,
            "      </aside>",
            "    </div>",
            '    <footer class="footer">',
            f'      <p>Offline release documentation generated from the openD3 repository sources for version <strong>{html.escape(version)}</strong>.</p>',
            f'      <p><a href="{html.escape(docs_home_href)}">Documentation home</a> | <a href="{html.escape(package_home_href)}">Package home</a> | <a href="https://www.darkmatter-quake.com">Website</a></p>',
            "    </footer>",
            "  </div>",
            "</body>",
            "</html>",
        ]
    )


def render_index_page(
    specs: list[DocSpec],
    version: str,
    platform: str,
    arch: str,
) -> str:
    grouped: dict[str, list[DocSpec]] = {}
    for spec in specs:
        grouped.setdefault(spec.group, []).append(spec)

    def render_group(group: str, description: str) -> str:
        links = grouped.get(group, [])
        if not links:
            return ""

        items = [
            f'<li><a href="{html.escape(spec.output_relative.as_posix())}">{html.escape(spec.nav_title)}</a></li>'
            for spec in links
        ]
        return "\n".join(
            [
                '<article class="card">',
                f'<span class="eyebrow">{html.escape(group)}</span>',
                f"<h3>{html.escape(description)}</h3>",
                '<ul>',
                *items,
                "</ul>",
                "</article>",
            ]
        )

    cards = [
        render_group("Project", "Core project guides and high-level references."),
        render_group("User Guides", "Runtime settings, gameplay-facing features, and troubleshooting."),
        render_group("Developer Guides", "Implementation notes, audits, and current engineering references."),
        render_group("Research and Proposals", "Long-form technical investigations and design proposals."),
        render_group("Legacy Notes", "Historical context and archived notes kept for reference."),
        render_group("Planning Archive", "Historical plans and proposals, superseded by the development roadmap."),
    ]
    cards = [card for card in cards if card]

    return "\n".join(
        [
            "<!DOCTYPE html>",
            '<html lang="en">',
            "<head>",
            '  <meta charset="UTF-8">',
            '  <meta name="viewport" content="width=device-width, initial-scale=1.0">',
            '  <meta name="color-scheme" content="dark">',
            "  <title>openD3 Documentation Portal</title>",
            '  <link rel="stylesheet" href="_static/site.css">',
            "</head>",
            "<body>",
            '  <div class="shell">',
            '    <header class="topbar">',
            '      <div class="brand">',
            '        <span class="eyebrow">Offline HTML documentation</span>',
            '        <a class="brand-title" href="index.html">openD3 Documentation Portal</a>',
            f'        <div class="brand-subtitle">Release {html.escape(version)} · {html.escape(platform)} · {html.escape(arch)} · {len(specs)} documents</div>',
            "      </div>",
            '      <div class="action-row">',
            '        <a class="button primary" href="README.html">Project Overview</a>',
            '        <a class="button" href="BUILDING.html">Build Guide</a>',
            '        <a class="button" href="TECHNICAL.html">Technical Reference</a>',
            '        <a class="button" href="../README.html">Package Home</a>',
            "      </div>",
            "    </header>",
            '    <section class="hero">',
            '      <img class="hero-banner" src="assets/docs/img/banner.png" alt="openD3 banner">',
            '      <span class="eyebrow">openD3 Release Documentation</span>',
            '      <h1>Full offline HTML docs, shipped with the release package.</h1>',
            '      <p class="lead">This package includes the project overview, build and technical references, player guides and developer notes, converted into a browsable HTML site with internal links preserved.</p>',
            '      <div class="hero-actions">',
            '        <a class="button primary" href="README.html">Open Project Overview</a>',
            '        <a class="button" href="docs/user/getting-started.html">Getting Started</a>',
            '        <a class="button" href="docs/dev/doom3-rebase.html">Rebase Record</a>',
            '      </div>',
            '      <div class="hero-meta">',
            f'        <span class="chip">Release {html.escape(version)}</span>',
            f'        <span class="chip">{html.escape(platform)}</span>',
            f'        <span class="chip">{html.escape(arch)}</span>',
            '        <span class="chip">Generated from repository Markdown sources</span>',
            "      </div>",
            "    </section>",
            '    <section class="catalog">',
            "      <h2>Included Documentation</h2>",
            '      <div class="card-grid">',
            *cards,
            "      </div>",
            "    </section>",
            '    <footer class="footer">',
            '      <p>These pages are bundled directly into the release archive so the package remains self-documenting even when viewed offline.</p>',
            '      <p><a href="../README.html">Package home</a> | <a href="https://github.com/themuffinator/openD3">Repository</a> | <a href="https://www.darkmatter-quake.com">Website</a></p>',
            "    </footer>",
            "  </div>",
            "</body>",
            "</html>",
        ]
    )


def generate_release_docs_site(
    *,
    source_root: Path,
    output_root: Path,
    version: str,
    platform: str,
    arch: str,
) -> GeneratedDocSite:
    source_root = validate_source_root(source_root)
    validate_output_root(source_root, output_root)
    output_root = output_root.resolve()

    markdown_lib = require_markdown_module()
    specs = build_doc_specs(source_root)
    if not specs:
        raise RuntimeError(f"no Markdown documentation sources were found under {source_root}")

    if output_root.exists():
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    (output_root / "_static").mkdir(parents=True, exist_ok=True)
    (output_root / "_static" / "site.css").write_text(site_font_faces(source_root) + SITE_CSS, encoding="utf-8")

    docs_assets_source = source_root / "assets" / "docs" / "img"
    if docs_assets_source.is_dir():
        docs_assets_dest = output_root / "assets" / "docs" / "img"
        copy_docs_asset_tree(docs_assets_source, docs_assets_dest)

    for auxiliary in (
        Path("LICENSE"),
        Path("LICENSES/DOOM-3-ADDITIONAL-TERMS.txt"),
        Path("LICENSES/DOOM-3-BFG-ADDITIONAL-TERMS.txt"),
    ):
        copy_docs_auxiliary_file(source_root, auxiliary, output_root / auxiliary)
    khronos_notice = Path("LICENSES") / "KHRONOS-GLES-MIT.txt"
    copy_docs_auxiliary_file(source_root, khronos_notice, output_root / khronos_notice)

    # Keep linked requirement/archive records, UI sources and licence notices
    # available offline. These are authored records/fixtures, not extracted art.
    for relative in (
        "LICENSES/RmlUi.txt", "LICENSES/JsonCpp.txt", "LICENSES/libtess2.txt",
        "LICENSES/MD4.txt", "LICENSES/glslang.txt",
        "LICENSES/openxr-sdk.txt", "subprojects/openxr.wrap",
        "docs/dev/ui/migration-manifest.json",
        "docs/dev/ui/product-requirements.json",
        "docs/dev/ui/inventory-sources.json",
        "docs/dev/game-test-coverage.json",
        "docs/dev/performance-budgets.json",
        "docs/dev/android-device-budgets.json",
        "docs/dev/retail-overlay-audit.csv",
        "docs/dev/archive/2026-10-18/manifest.json",
        # The Interface Atlas the visual design specification draws in.
        "docs/dev/ui/atlas/opend3-interface-atlas.html",
        "subprojects/rmlui.wrap", "subprojects/packagefiles/libtess2/double-precision.patch",
        "subprojects/packagefiles/rmlui/masked-hit-test.patch",
        "subprojects/packagefiles/jsoncpp/subnormal-numbers.patch",
        "tools/ui/retained_system.py",
        "tools/ui/capture_legacy_baseline.py",
        "tools/ui/system_settings_probe.py",
        "tools/ui/fixtures/system-settings-smoke.rui",
        "tools/ui/fixtures/system-settings-smoke.cfg",
        "tools/ui/fixtures/system-settings-smoke-resume.cfg",
        "tools/ui/fixtures/managed-settings-smoke.rui",
        "tools/ui/fixtures/managed-settings-smoke.cfg",
        "tools/ui/fixtures/managed-settings-smoke-resume.cfg",
        "tools/ui/fixtures/presentation-alias-smoke.rui",
        "tools/ui/fixtures/presentation-alias-smoke.cfg",
        "tools/ui/fixtures/presentation-alias-smoke-resume.cfg",
        "tools/ui/fixtures/event-program-smoke.rui",
        "tools/ui/fixtures/event-program-smoke.cfg",
        "tools/ui/fixtures/event-program-smoke-resume.cfg",
        "tools/ui/legacy_import.py", "tools/ui/legacy_inventory.py", "tools/ui/legacy_syntax.py",
        "tools/ui/verify_composition_capture.py", "tools/ui/verify_interaction_capture.py",
        "tools/ui/verify_mask_capture.py",
        "tools/ui/verify_binding_capture.py",
        "tools/ui/fixtures/binding-smoke.rui", "tools/ui/fixtures/binding-smoke.cfg",
        "tools/ui/fixtures/binding-first.json", "tools/ui/fixtures/binding-final.json",
        "tools/ui/fixtures/presentation-smoke.gui", "tools/ui/fixtures/presentation-smoke.cfg",
        "tools/ui/fixtures/composition-smoke.rui", "tools/ui/fixtures/document-smoke.rui",
        "tools/ui/fixtures/interaction-smoke.rui", "tools/ui/fixtures/interaction-smoke.cfg",
        "tools/ui/fixtures/mask-smoke.rui", "tools/ui/fixtures/vector-smoke.rui",
    ):
        auxiliary = Path(relative)
        copy_docs_auxiliary_file(source_root, auxiliary, output_root / auxiliary)

    rendered_sources = {spec.source_relative.as_posix().lower() for spec in specs}
    for spec in specs:
        raw_text = (source_root / spec.source_relative).read_text(encoding="utf-8")
        prepared_text = prepare_markdown(
            raw_text,
            source_relative=spec.source_relative,
            rendered_sources=rendered_sources,
        )
        markdown_engine = markdown_lib.Markdown(
            extensions=[
                "extra",
                "admonition",
                "sane_lists",
                "toc",
                "md_in_html",
            ],
            extension_configs={
                "toc": {
                    "permalink": False,
                }
            },
        )
        body_html = markdown_engine.convert(prepared_text)
        body_html = re.sub(r"<h1[^>]*>.*?</h1>\s*", "", body_html, count=1, flags=re.S)
        body_html = re.sub(r"<div align=\"center\">\s*</div>", "", body_html, flags=re.S)
        page_html = render_doc_page(
            spec,
            specs,
            version,
            platform,
            arch,
            body_html,
            list(markdown_engine.toc_tokens),
        )

        destination = output_root / spec.output_relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(page_html, encoding="utf-8")

    index_path = output_root / "index.html"
    index_path.write_text(
        render_index_page(specs, version, platform, arch),
        encoding="utf-8",
    )

    return GeneratedDocSite(
        output_root=output_root,
        index_path=index_path,
        page_count=len(specs),
    )


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    result = generate_release_docs_site(
        source_root=Path(args.source_root),
        output_root=Path(args.output_dir),
        version=args.version,
        platform=args.platform,
        arch=args.arch,
    )
    print(f"Generated openD3 HTML docs: {result.index_path} ({result.page_count} pages)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv))
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
