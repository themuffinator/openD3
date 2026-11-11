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
- **Wide and tall screens.** The stock menus, HUDs and loading screens reach
  the screen edges at any aspect: frames and bars stretch, docked pieces move
  to the edges, panels stay centred. The PDA keeps its 4:3 screen over a
  softened view of the world. No retail GUI script is shipped: small layout
  patches name the windows ([layout](../widescreen-layout.md)).
- **Dedicated server.** `openD3-ded_x64` spawns `game/mp/d3dm1`.
- **Your own shadow, and shadow maps that match.** In first person your body,
  head and weapon cast a shadow, in single player (`g_showPlayerShadow`, now on
  by default) and in multiplayer. Shadow maps (`r_useShadowMap 1`) draw the
  same lighting as stencil shadows on OpenGL and Vulkan.
- **Resurrection of Evil module.** `src/d3xp` builds `game-d3xp_<arch>`, which
  `+set fs_game d3xp` loads and initialises. No expansion map has been run.

## Upgrade Notes

- There is no earlier openD3 release to upgrade from. Builds from the
  pre-rebase tree do not share saves or configs with this one.
- Saves load only in the build that wrote them; loading a save has not been
  tested.
- Launch with `ui_retained 0`. openQ4's retained interface has no Doom 3 pages.
- Only Windows x64 has been built and run.
- A settings file written by an earlier build keeps `g_showPlayerShadow 0`,
  `r_correctspecular 1` and `r_normalizebumpmap 1`. Set the new defaults
  (1, 0, 0) by hand to get the player shadow and Doom 3's specular.

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
- Add GUI layout patches (`guis/layouts/*.layout`), the `screenstretchx`/`y`,
  `canvasclip` and `softfocus` window properties, and wide and tall layouts for
  the main menu, HUDs, PDA, loading screens and full-screen GUIs. Remove the
  hard-coded Quake 4 message dimmer and Tourney bar stretching.
- Continue the main menu's grid across wide and tall screens
  (`screenrepeatx`/`y`), its brighter fifth lines in step, let the menu cursor
  reach the whole screen whatever GUI drew last, draw it at Doom 3's 32 units,
  and leave it out while the window lacks focus, when the system pointer
  shows instead. Buttons inside a stretched menu container now take the
  pointer where they are drawn; they had answered a whole expansion to the
  left.
- The VS Code compile task reconfigures `builddir` when source files are
  added or removed.
- Merge openQ4 through `7c74cd712`, with its shadow-mapping fixes.
- Default `g_showPlayerShadow` to 1 in both game modules.
- Shade stock specular as Doom 3 does: `r_correctspecular` and
  `r_normalizebumpmap` default to 0, and the OpenGL ARB path no longer doubles
  the specular constant that Doom 3's `interaction.vfp` doubles itself.
