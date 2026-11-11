# Source Layout and Naming

This is the contract for where code lives in the repository and how files and
folders are named. It follows openQ4's
[source layout](https://github.com/themuffinator/openQ4/blob/main/docs/dev/source-layout.md),
so engine work merged from upstream lands where upstream put it.
`tools/tests/repository_path_portability.py` checks the path rules; it is
inherited from openQ4 and has not been run for openD3.

## Repository Root

| Path | Contents |
| --- | --- |
| `src/` | Engine, game and tool sources |
| `src/external/` | Vendored third-party code, kept in its upstream layout |
| `subprojects/` | Meson wraps, with openD3 patches under `subprojects/packagefiles/<project>/` |
| `content/baseod3/pak0/` | Authored runtime content, packed into `baseod3/pak0.pk4`: GLSL and ARB programs, post-process materials, the five TrueType faces rebuilt from Doom 3's bitmap fonts, default configs and engine string tables |
| `assets/` | Packaging and branding inputs: icons, splash, desktop entries, documentation images and the packaged HTML readmes (`assets/docs/`, `assets/release/`) |
| `tools/` | Build, packaging, debugging, test, validation and asset scripts; `tools/assets/fonts/` rebuilds the TrueType faces from an installed Doom 3 |
| `docs/dev/`, `docs/user/` | Developer and player documentation; curated release notes live in `docs/dev/releases/`, and the [UI visual design specification](ui-visual-design.md) is drawn in `docs/dev/ui/atlas/` |
| `LICENSES/` | Licence terms and third-party notices; mirrors the `licenses/` folder that packages install |
| `mobile/android/` | The Android launcher application, inherited and not built for openD3 |

The root itself holds only the project documents (`README.md`, `BUILDING.md`,
`TECHNICAL.md`, `LICENSING.md`, `CONTRIBUTORS.md`, `AGENTS.md`, `LICENSE`) and
the Meson entry points. Launch helpers belong in `tools/debug/`. The record of
what works and what is open is [the rebase record](doom3-rebase.md). Build
directories (`builddir*/`), the staged package (`.install/`), save paths
(`.home*/`) and scratch space (`.tmp/`) are local and untracked.

## `src/`

| Directory | Contents |
| --- | --- |
| `aas` | AAS navigation runtime |
| `bse` | Basic Set of Effects, built into the client; kept for custom content |
| `cm` | Collision model |
| `d3xp` | Resurrection of Evil game library: `src/game` with `_D3XP` and `CTF` defined |
| `external` | Vendored code (see below) |
| `framework` | Common services, file system, cvars, declarations; `async` holds networking |
| `game` | Doom 3 game library (GPL, id Software's release) |
| `idlib` | Core library |
| `imagetools` | CPU image codecs and colour handling shared by the engine and renderer modules |
| `mayaimport` | Interface to the optional Maya import DLL |
| `renderer` | Renderer front end and the `OpenGL`, `Vulkan`, `GLES` and `GLES_D3` backends |
| `rendergeo` | CPU render geometry shared by dmap and the renderer |
| `sound` | Sound system and its `OpenAL` backend |
| `sys` | Platform layer: `sdl3`, `posix`, `win32`, `linux`, `macos`, `android`, `openxr`, `stub` |
| `tools` | dmap and AAS compilers, the level editor, and the legacy MFC editors |
| `ui` | GUI system, the `retained` RmlUi interface and its `application` layer |

`src/game` and `src/d3xp` are the same game. A fix that applies to both goes
into both trees. openD3 has no `src/mpgame`: Doom 3's multiplayer is part of
the one game library.

## Path Rules (Checked)

- Path components use only `A-Z a-z 0-9 . _ + -`, never end in a dot, and are
  never a Windows device name such as `con` or `aux`.
- No two tracked paths differ only by letter case.
- File extensions are lowercase.
- Paths stay within 160 characters, which leaves room for a worktree root under
  the Windows 260-character limit.
- First-level directories under `src/` are single lowercase words with no
  separators.

## Naming Conventions

**C and C++ sources** follow the family the file belongs to. Do not rename
inherited files to a new style: they are compared against id Software's Doom 3
release, dhewm3 and openQ4.

- Classes and subsystems use PascalCase named after their main type
  (`RenderWorld.cpp`, `Game_local.cpp`).
- Platform files carry a lowercase platform prefix: `win_`, `posix_`, `linux_`,
  `macos_` and `android_`.
- Inherited renderer files keep their lowercase stage prefixes (`tr_light.cpp`,
  `draw_arb2.cpp`). Backend translation units use an API prefix with a
  PascalCase name (`vk_Backend.cpp`).
- Engine sites that differ from upstream for Doom 3's sake are marked with the
  `OPEND3` define and kept few and small.

**Scripts and data**

- Python modules are snake_case. Entry points that exist for both shells share
  one name (`meson_setup.sh` and `meson_setup.ps1`).
- Documentation is lowercase-kebab (`source-layout.md`). Release notes are
  `docs/dev/releases/vX.Y.Z.md`, with the next release's in
  `docs/dev/releases/unreleased.md`.
- The project name is `openD3` in mixed-case names and prose, `OPEND3_*` in
  macros and environment variables, and `opend3` inside lowercase snake or
  kebab names (`opend3_version.py`, `opend3.desktop.in`). The runtime directory
  is `baseod3`. Upstream's name appears only in prose about upstream, its URLs
  and the `openq4-upstream` remote; `tools/build/rebrand_upstream.py` renames
  what a merge brings in.

## Vendored Code and Licences

Third-party code lives either in `src/external/<project>/` with its upstream
file names or in `subprojects/` as a Meson wrap. It follows only the checked
path rules, not the naming conventions. Do not place vendored code inside
first-party directories.

`LICENSES/` holds the id Software terms (`DOOM-3-ADDITIONAL-TERMS.txt`,
`DOOM-3-BFG-ADDITIONAL-TERMS.txt`) and third-party notices named after their
project (`RmlUi.txt`, `glslang.txt`). Packages install the same files into
`licenses/`. Never copy code from the game trees of openQ4 or openPREY: they
are under SDK licences. Their engine code is GPL and may be ported.
