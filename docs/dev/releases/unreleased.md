# Unreleased openD3 development changes

These changes belong to the development tree. openD3 has **no release yet**;
the first will be 0.0.1. This file collects material for that release's notes,
with no date promised, in the layout of openQ4's release notes. Each claim here
is limited to what the [rebase record](../doom3-rebase.md#verified) covers. See
[release status](../../user/release-status.md) for the player view.

## Highlights

- **Doom 3 on the current openQ4 engine.** openD3 moved off its older engine
  onto openQ4, keeping Doom 3's GPL game library in this repository. The
  [rebase record](../doom3-rebase.md) describes how.
- **Finds and checks your game files.** Startup finds a Steam install of Doom 3
  without `fs_basepath`, validates `pak000`–`pak004` by checksum and leaves the
  retail game-binary packs out of the search path.
- **The first campaign map runs.** `game/mars_city1` loads, plays its opening
  cinematic with working in-world screens and remote camera views, writes its
  autosave and exits cleanly.
- **OpenGL and Vulkan.** The same map renders on the default OpenGL renderer
  and on the native Vulkan renderer (`+set r_renderApi vulkan`).
- **Doom 3's own menus and consoles.** The stock main menu starts and plays the
  intro video, and both consoles carry Doom 3's colours.
- **Dedicated server.** `openD3-ded_x64` spawns `game/mp/d3dm1`.
- **Resurrection of Evil module.** `src/d3xp` builds `game-d3xp_<arch>`, which
  `+set fs_game d3xp` loads and initialises. No expansion map has been run.

## Upgrade Notes

- There is no earlier openD3 release to upgrade from. Builds from the
  pre-rebase tree do not share saves or configs with this one.
- Saves load only in the build that wrote them; loading a save has not been
  tested.
- Launch with `ui_retained 0`. openQ4's retained interface has no Doom 3 pages.
- Only Windows x64 has been built and run.

## Change Log

- Remove the Quake 4 game library and content, and preserve the pre-rebase
  openD3 tree in history.
- Transplant openPREY's Doom 3-lineage engine layer and convert it to Doom 3:
  map, AAS and collision formats, particle and FX declarations, the game API
  bridge.
- Build the Doom 3 game module from `src/game` and run Doom 3 on the rebased
  engine.
- Build Resurrection of Evil as a second game module from `src/d3xp`.
- Rename openQ4 identifiers to openD3 throughout and remove handling that
  existed only for Quake 4 or Prey content.
- Give the in-game and system consoles Doom 3's colours.
- Document openD3: README, building and technical references, player guides,
  the rebase record and game source provenance, laid out like openQ4's.
- Add the openD3 banner and the packaged HTML readmes.
