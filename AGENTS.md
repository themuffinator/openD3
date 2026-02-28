# OpenD3 Agent Guide

This file describes project goals, rules, and upstream references for anyone working on OpenD3.

**Project Metadata**
- Name: OpenD3
- Author: themuffinator
- Company: DarkMatter Productions
- Version: 0.0.1
- Website: `www.darkmatter-quake.com`
- Repository: `https://github.com/themuffinator/OpenD3`
- Companion GameLibs Repo (local): `E:\Repositories\OpenD3-GameLibs`
- Doom 3 Compatibility Reference (local): `E:\_SOURCE\_CODE\dhewm3-master`

**Goals**
- Deliver a minimal, practical adaptation of this engine/game tree from the prior OpenQ4 baseline to Doom 3.
- Restore Doom 3 asset/runtime compatibility first, then modernize incrementally.
- Keep the project open-source and avoid closed-source runtime dependencies.
- Keep cross-platform modernization direction through SDL3 + Meson while maintaining a stable Windows x64 baseline.
- Treat `OpenD3-GameLibs` as canonical for game-library source ownership.

**Rules**
- Do not reintroduce Quake 4 external legacy-effects companion-repo dependencies.
- Treat `E:\Repositories\OpenD3-GameLibs` as part of the same active workspace for planning, edits, and validation.
- For game-library work, make canonical source edits in `OpenD3-GameLibs` first; this repo's `src/game` is synchronized from that companion repo via `tools/build/sync_gamelibs.ps1`.
- Use `OPEND3_GAMELIBS_REPO=<path>` to override the default game-libs companion location (`../OpenD3-GameLibs`) when needed.
- Legacy `OPENQ4_*` env var names may exist temporarily for migration compatibility, but new automation/docs should use `OPEND3_*` names.
- Keep `builddir/` as the standard Meson build output directory.
- Treat `.install/` as the release-style package root; stage runtime artifacts into `.install/` and `.install/openbase/`.
- Keep `.install/` focused on runtime/staged content; keep linker/build intermediates in `builddir/`.
- On Windows, do not invoke raw `meson ...` from arbitrary shells; use `tools/build/meson_setup.ps1 ...` (or `tools/build/opend3_devcmd.cmd`) so MSVC tooling is initialized consistently.
- Prefer fixes in engine/game/loader/parser over shipping new content overrides.
- Keep documentation synchronized with behavior changes.
- Use `.tmp/` for temporary task files.

**Doom 3 Reinstatement Direction**
- Use `E:\_SOURCE\_CODE\dhewm3-master` as the primary local behavior/reference baseline when identifying what to revert to restore Doom 3 compatibility.
- Document any intentional divergences from dhewm3 in `docs-dev/`.

**.install/ Folder Layout (Staging Target)**
- `.install/` is the runtime package root used by local staging and `fs_cdpath` overlays.
- Keep executable/runtime artifacts in `.install/` (for example `.install/OpenD3-client_x64.exe`, `.install/OpenD3-ded_x64.exe`).
- Keep staged game module and override content in `.install/openbase/`.

**Procedure 1 (Debug Loop)**
1. Launch using the correct mode-specific task (`SP` launch for single-player, `MP` launch for multiplayer).
2. Close the game after 3 seconds.
3. Read `fs_savepath\<gameDir>\logs\opend3.log` (commonly `${workspaceFolder}\\.home\\openbase\\logs\\opend3.log`).
4. Identify errors and warnings.
5. Fix issues in code/configuration, not by adding compatibility-breaking content hacks.
6. Repeat until clean.

**References (Local, Not Included In Repo)**
- dhewm3 baseline/reference: `E:\_SOURCE\_CODE\dhewm3-master`
- OpenD3 game libraries (canonical): `E:\Repositories\OpenD3-GameLibs`
- Doom 3 installation (Steam): `C:\Program Files (x86)\Steam\steamapps\common\Doom 3`

**Upstream Credits**
- id Software.
- Raven Software.
- Justin Marshall.
- Robert Backebans.
