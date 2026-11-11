# openD3 on the openQ4 engine: rebase record

This is the working record of openD3's move onto the current openQ4 engine. It
states what was done, what has been verified and how, and what is still open.
Update it when any of that changes; it is the place a future upstream sync
starts from.

## Where openD3 came from

- openD3 forked from openQ4 `abb9a688` (2026-02-18) and carried six commits of
  Doom 3 adaptation on that snapshot. The fork tree was byte-identical to that
  openQ4 commit apart from 42 stripped Quake 4 asset files.
- The game library lived in a companion repository, `openD3-GameLibs`, and was
  synchronised into `src/game` by script.
- openQ4 then gained about 2,350 commits: the renderer module split with the
  modern OpenGL and native Vulkan backends, shadow mapping, the SDL3 platform
  layer, the hardened savegame framework, the content pack pipeline and
  in-tree game sources.

The pre-rebase tree, including the uncommitted work that was on `main` at the
time, is preserved on the branch `pre-oq4-rebase` and is the first parent of
the rebase merge.

## How the rebase was done

The branch history, oldest first:

1. **Merge openQ4** through `55bbe166a`, taking the upstream tree unchanged.
   openQ4's history is now part of openD3's, so later syncs are ordinary
   merges of `openq4-upstream/main`. The latest sync merged upstream through
   `7c74cd712` (2026-11-11), which brought its shadow-mapping fixes.
2. **Remove the Quake 4 game library and content.** `src/game` and
   `src/mpgame` (Quake 4 SDK), the SDK licence and the Quake 4 runtime content
   leave the tree. The engine-side content moves to `content/baseod3`.
3. **Import the Doom 3 game library with its history.** `src/game` (base game)
   and `src/d3xp` (Resurrection of Evil) come from `openD3-GameLibs` `c450f9c`
   at their existing paths; that repository's history is a parent of the
   import commit. See [game-source-provenance.md](game-source-provenance.md).
4. **Transplant openPREY's engine layer.** openPREY already carried, on openQ4
   `b4d3fd700`, the engine work a Doom 3-lineage game needs: the unified
   in-tree game module build, Doom 3 particle and FX declarations,
   `idRenderModelPrt`, the Doom 3 `.proc` header, AAS 1.07, the collision
   world fallbacks, `idBitMsg` helpers, `idSoundEmitter` reference sounds, ARB
   interaction stages and the game API bridging in the session and async
   layers. That delta was applied by three-way merge, unedited, as its own
   commit.
5. **Convert that layer from Prey to Doom 3** and get the tree building,
   running and staging. The sections below describe the result.

## Engine/game contract

- **One define marks the difference from upstream.** `OPEND3` is set for every
  target. It guards the engine sites where Doom 3's game API or file formats
  differ from openQ4's Quake 4 ones: the AAS file version (1.07), the map
  geometry CRC (Doom 3 does not hash `model` key/values), the Quake 4 game
  services BSE and the async layer would otherwise call, Quake 4-only
  precaches and the Quake 4 language-archive check.
- **The game API is Doom 3's**, `GAME_API_VERSION` 8, defined in
  `src/game/Game.h`. The engine includes that header. Call sites pass Doom 3's
  arguments (`ServerClientConnect` with the guid, `ClientPrediction` with
  `lastPredictFrame`). `src/framework/Doom3GameCompat.h` answers the Quake 4
  game services upstream's retained screens and ban list ask for.
- **Gate D9.** Bots, multi-view demos and the repeater need game API calls
  Doom 3 does not have. Their entry points are compiled but inert and carry
  `OPEND3-GATED(D9)` markers. Re-enabling one is game API design work.
- **Collision handles.** Doom 3 game code uses integer collision handles (0 is
  the world). `idCollisionModelManager` provides them as inline overloads over
  the engine's pointer interface, so the vtable matches upstream.
- **Decl parsing.** The engine parses decls through the three-argument
  `Parse( text, length, noCaching )`. Game-side decl classes must implement
  it; `idDeclModelDef` forwards it to its two-argument parser.
- **Shutdown order.** The engine destroys game-owned decls after
  `idGame::Shutdown` returns. The game releases model-def animation references
  in `Shutdown`, before its animation manager goes away.
- **BSE** stays compiled and linked, as in openPREY, but nothing drives it:
  Doom 3 uses its own particle and FX declarations.

## Game modules

| Module | Source | Defines | State |
| --- | --- | --- | --- |
| `game_<arch>` | `src/game` | | Builds, loads and runs |
| `game-d3xp_<arch>` | `src/d3xp` | `_D3XP`, `CTF` | Builds, loads and initialises; not played |

`src/d3xp` was imported in id's GPL form. The 64-bit and engine-ABI port that
`src/game` already carried was applied to it by three-way merge per file
(base: id's GPL `neo/game`; incoming: the ported `src/game`; target:
`src/d3xp`). `Anim_Import.cpp`, `SaveGame.cpp` and `PlayerView.cpp` were
resolved by hand. A fix that applies to both games goes into both trees.

The engine selects `game-d3xp` when `d3xp` is `fs_game` or `fs_game_base`.
`d3xp` is an official game directory: it needs no `mod.json`, its retail
`game0x.pk4` binary packs are left out of the search path like the base
game's, and the module is loaded from `baseod3/`. The engine's own expansion
switch, `ID_ALLOW_D3XP`, is on.

## Verified

Windows x64, `debugoptimized`, MSVC 19.50, 2026-11-11, against the Steam
release of Doom 3 (1.3.1 packs):

- Configure, compile, link and stage of the client, the dedicated server, the
  OpenGL and Vulkan renderer modules and both game modules.
- `vk_shader_header_pin` passes after the Vulkan SPIR-V headers were
  regenerated from the merged shader sources.
- Startup finds the Steam install without `fs_basepath`, validates
  `pak000`–`pak004` by checksum and leaves `game00`–`game03` out of the search
  path.
- `game/mars_city1` loads in single player (1,969 entities), plays the intro
  cinematic with its in-world GUIs and remote camera views, writes its
  autosave and exits cleanly, on OpenGL. The same map loads and renders on the
  native Vulkan renderer (`r_renderApi vulkan`).
- The stock main menu path starts and plays the intro video.
- Both consoles carry Doom 3's colours, seen over the main menu: the in-game
  console draws cyan text, prompt, version and rule on opaque black, and the
  Win32 system console draws the same cyan on a dark slate taken from the
  menus' dialog plate. The completion popup, text selection and the SDL system
  console on Linux and macOS take the same palette but were not looked at.
- GUI and console text is drawn from the five reconstructed TrueType faces by
  default ([font system](ttf-font-system.md)). At startup the engine loads
  `fonts/english.ttf`, `an.ttf`, `bank.ttf`, `micro.ttf` and `bigchars.ttf`
  from `baseod3/pak0.pk4`, fits each face's 12, 24 and 48 point slots to the
  retail `.dat` metrics and rebuilds the console sheet. Captured at 2560x1440
  on OpenGL: the main menu, and the HUD on `game/alphalabs1` (loaded with
  `devmap`, 2,106 entities). `tools/tests/ttf_font_integrity.py` passes.
- Wide and tall screens ([layout](widescreen-layout.md)): with the layout
  patches in `baseod3/pak0.pk4`, captured on OpenGL at 4:3 (1280x960, unchanged
  from the stock layout), 16:9 (2560x1440), 21:9 (2400x1028) and 4:5
  (1024x1280). The main menu and its Options, New Game, Load Game,
  Multiplayer (Create Server), Credits and Exit screens (driven with
  `opend3_guiAction`) reach both screen edges at 21:9 and stay centred
  vertically at 4:5 with no parked panel in view. The HUD on
  `game/alphalabs1` sits in the screen corners at 16:9 and 21:9. The PDA,
  opened there with `give pda` and `impulse 19`, keeps its 4:3 canvas over the
  softened view, also on Vulkan at 1920x1080. The loading screens
  (`alphalabs1`, `generic`), the death screen, the multiplayer HUD, the
  scoreboard and the game-over screen were shown with `testGUI` at 21:9 and,
  for the loading screen and multiplayer HUD, at 4:5.
- Shadow maps (`r_useShadowMap 1`, with `r_shadowMapPointLights 1`) on
  OpenGL and Vulkan, after the `7c74cd712` sync. Captured from the starting
  view of `mc_underground`, `alphalabs1`, `delta2a`, `hell1`, `recycling1` and
  `site3` with shadow maps and with stencil shadows. The pictures match, and no
  log reports a shadow-map error. Frozen with `g_stopTime 1` and measured, the
  mapped and stencil pictures of `alphalabs1` differ in about 5,000 of 3.7
  million pixels on both backends (the contact edges of the soft shadows),
  `hell1` in 0 (OpenGL) and 182 (Vulkan), and no mapped pixel is brighter than
  the unshadowed picture. Before the specular fix below, OpenGL differed in
  311,739 pixels there. On `hell1` three lights with nothing to cast keep
  entering and leaving the stencil fallback; see "Open items".
- Stock specular follows Doom 3 on every path. `r_correctspecular` and
  `r_normalizebumpmap` default to 0 (they came from Prey at 1), and the OpenGL
  ARB path passes the specular constant unscaled, as id's `draw_arb2.cpp`
  does, because Doom 3's `interaction.vfp` doubles the specular map itself.
  This was measured against the shadow-map and Vulkan pictures above, not
  against retail Doom 3.
- The player's own shadow, in first person. With a light spawned behind the
  player, the body, head and held weapon cast their shadow on the surface in
  front: in single player on `mc_underground` (`g_showPlayerShadow` now
  defaults to 1; 0 removes the shadow) and in a `d3dm1` deathmatch listen
  server, each on OpenGL and Vulkan, with stencil shadows and with shadow
  maps. The shadow-map report confirms that the test light was shadow-mapped
  in each case, with the player's models among its casters.
- The dedicated server spawns `game/mp/d3dm1` (887 entities).
- The VS Code tasks and launches. The default build task compiles `builddir`
  and fast-stages `.install`. Run with their own arguments and an isolated
  `fs_savepath`, these launches load their map and exit cleanly on the given
  renderer: `mars_city1` load-and-quit (OpenGL), `comm1` (Vulkan) and the
  `d3dm1` deathmatch listen server (OpenGL). `tools/tests/vscode_fast_build.py`
  passes.
- The "Bake Light Grids (All MP)" task (`bakeLightGrids all-mp`) bakes Doom
  3's five `game/mp/` maps as deathmatch maps in one batch on OpenGL, writes a
  `.lightgridpack` for each and exits cleanly. A later `d3dm3` listen server
  loads its pack from the save path and draws with it. The bake still warns,
  for every map, that another copy of the pack comes first; none exists, and
  the warning is the bake's own read-back check failing (see "Open items").
- `+set fs_game d3xp` mounts the expansion directory, loads `game-d3xp_x64`
  and initialises the game. On the test machine, which has only the
  expansion's patch pack, startup then stops with a parse error in the
  expansion's `guis/mainmenu.gui`.

That is all that has been run. In particular, nothing here is evidence for:
playing past the first cinematic, combat, AI, the PDA beyond its first page,
video playback, level transitions, loading a savegame, a multiplayer client
joining a server,
Linux, macOS, Android, ARM64 or VR. The TrueType text was not compared
screen by screen with the bitmap path, and was not checked on Vulkan, in the
PDA, on in-world screens or in a language other than English. The wide and
tall layouts were not checked in a multiplayer match, with the HUD's
objective, inventory and pickup notices showing, on the message boxes, intro
and credits as the game raises them, or in Resurrection of Evil.

## Open items

Listed roughly by how much they block a player.

1. **Resurrection of Evil is unverified.** The expansion mounts and its
   module initialises, but no map has been loaded: the machine this was done
   on has no complete RoE data, and with the patch pack alone the expansion's
   main menu fails to parse. That needs repeating with a full install before
   deciding whether it is a GUI parser gap. The renderer carries
   `renderEntity_t::xrayIndex` and the sound world `SetSlowmo` only so the
   game compiles; neither has an effect.
2. **Savegames are not stamped.** The engine's hardened savegame framework
   expects the game to write a versioned, checksummed payload. Doom 3's game
   library writes its original unstamped payload, which `Session.cpp` accepts
   under `OPEND3` for the build that wrote it. Writing the stamped payload is
   game-side work; it must be written for openD3, not copied from openQ4's or
   openPREY's game trees, which are under their SDK licences. Loading a save
   has not been tested.
3. **Engine features with no stock Doom 3 content.** Kept deliberately,
   because custom content and mods could use them: BSE effects, MD5R models,
   light grids, the retained RmlUi interface, the Arena ladder (it loads only
   when a package ships its campaign file), and the extensions that came with
   the openPREY layer (glow stages, extra material keywords and deforms, GUI
   window types, subtitles, loading music, the libogg/libvorbis decode
   fallback). Many of their comments still describe Quake 4 or Prey content.
   Handling tied to one retail product was removed: the Awakening expansion's
   campaign, content checks and substitutions, the Quake 4 savegame names and
   the Prey data blocks formerly behind `HUMANHEAD`, and the stretching of
   Quake 4's message dimmer and Tourney warm-up bar, which layout patches
   replace. The chapter list and the campaign commands now name Doom 3's maps. Still to go through: the Quake 4
   HUD routes in the retained HUD, the Quake 4 language-pack listing, and
   Quake 4 image and font fallbacks.
4. **Startup warnings still to clear** (Procedure 1 in `AGENTS.md`): the
   engine's chat window and menu background precache four Quake 4 menu images;
   the retained HUD looks for a Quake 4 HUD document; the engine asks for a
   `guisounds` shader and string `#str_107240`, which Doom 3 does not have;
   the stock menus reference the removed `s_driver` cvar; the engine and the
   game both declare `r_showSkel`; sound shader volumes above +10 dB are
   clamped. A `mars_city1` load currently logs about 25 distinct warnings,
   some of them the retail content's own.
5. **The retained RmlUi interface has no Doom 3 documents.** Launches pin
   `ui_retained 0`. The stock Doom 3 GUIs are the interface. The contract
   those documents will be built to is the
   [visual design specification](ui-visual-design.md), drawn in the
   [Interface Atlas](ui/atlas/opend3-interface-atlas.html); none of it is
   implemented yet.
6. **Tooling under `tools/` is inherited and unadapted.** The test corpus,
   validation profiles, packaging, installer and release scripts were written
   for openQ4. They were renamed mechanically and have not been run for
   openD3; many still test Quake 4 maps and content. The optional native test
   suite (`-Dbuild_native_tests=true`) references Quake 4 interface files that
   are no longer in the tree and will not configure. The build helpers Meson
   invokes are adapted and exercised, as are the VS Code tasks, launches and
   `tools/tests/vscode_fast_build.py`. Of the release tooling, only the
   documentation side has been run: `generate_release_docs.py` builds the
   offline documentation site and `tools/tests/docs_link_integrity.py` passes
   over it, the source documents and the two HTML readmes. The packager,
   installer and release verifiers still name Quake 4 and Prey layers and have
   not been run.
7. **No CI.** openQ4's GitHub workflows were removed rather than left to fail;
   they need rebuilding for openD3.
8. **Player guides are a first pass.** openQ4's documentation was removed
   because it describes Quake 4. `docs/user/` now holds five guides laid out
   like openQ4's (getting started, release status, client settings, campaigns
   and server setup). They state only what "Verified" covers and must follow
   it when it changes. openQ4's display, input, gameplay and rendering guides
   have no openD3 counterpart, because none of those features has been checked
   with Doom 3. The README has no screenshots yet. The rest of the
   documentation follows openQ4's layout: `BUILDING.md` and `TECHNICAL.md`
   take its sections, `docs/dev/` has the [source layout](source-layout.md)
   and [unreleased release notes](releases/unreleased.md), and
   `assets/release/README.html` (the package home page) and
   `assets/docs/README.html` (the project overview) are drawn in Doom 3's
   front-end menu style with openD3's TrueType faces, as is the generated
   documentation site.
9. **The light-grid bake warns falsely about its packs.**
   `LightGrid_BakeLoadsNextTime` reads the new pack back through the file
   system to confirm that it will load. For a pack written into a directory
   the bake created, that read fails, and the bake reports that another copy
   comes first although the pack loads on the next start.
10. **Shadow-map follow-ups.**
    - The performance presets are openQ4's, unchanged by decision: openD3
      follows upstream's table (identical to openQ4 `822de6800`). So the
      **Enhanced** preset (the one startup picked on the test machine) sets
      `r_shadowMapPointLights 0`: its shadow maps cover projected lights only,
      and Doom 3's point lights, most of its lighting, keep stencil shadows.
      Quality and above shadow-map every light. The split was measured by
      upstream on Quake 4 content, not on Doom 3.
    - A light whose pass has nothing to cast (three lights at the start of
      `hell1`) is treated as a failed pass: the engine restores its stencil
      volumes, which are empty too, lets it leave the fallback after 240 views
      and repeats. Nothing changes on screen. The rule is upstream's.
    - Stale profiles keep old values: a config written before these defaults
      changed still holds `g_showPlayerShadow 0` and `r_correctspecular 1`,
      `r_normalizebumpmap 1`. There is no config migration.
    - On OpenGL, setting `r_correctspecular 1` or `r_normalizebumpmap 1`
      changes only the GLSL and Vulkan paths: the ARB program cannot follow
      them, so mapped and stencil pictures differ again.
    - OpenGL draws `hell1`'s first view brighter than Vulkan (about 420,000
      pixels), the same with shadow maps, stencil or no shadows. Not
      investigated.
    - Not covered: Resurrection of Evil, subviews (mirrors, remote cameras),
      moving lights, cascaded shadow maps (`r_shadowMapCSM`), other players'
      shadows as a client.

## Naming

The project name is openD3 everywhere, in what users see and in the source:
binaries, window titles, config and log names, environment variables and
macros (`OPEND3_*`), functions (`openD3_*`), generated headers, Meson
variables, content file names (`*_opend3`) and the dependency patches. The
runtime directory is `baseod3`. The only places upstream's name appears are
prose about the upstream project, its repository URLs and the
`openq4-upstream` remote.

`tools/build/rebrand_upstream.py` performs the rename. It
maps `openQ4`/`OpenQ4` to `openD3`, `OPENQ4` to `OPEND3`, `openq4` to `opend3`
and `baseoq4` to `baseod3`, in file contents and in paths, and reports
collisions with `--check`. It also rewrites prose that is about the upstream
project ("built on the openQ4 engine") outside its list of skipped files: in
`assets/`, `docs/` and `tools/assets/` it did so on the `7c74cd712` sync.
After running it, keep its changes only in the files the merge brought in and
restore the rest.

## Syncing with upstream

Because openD3 renames upstream's identifiers, a plain merge conflicts on
every line upstream touched that carries its name. Merge in upstream's naming
instead:

```
git fetch openq4-upstream
git switch -c sync/upstream
git merge openq4-upstream/main        # resolve as described below
python tools/build/rebrand_upstream.py --check
python tools/build/rebrand_upstream.py
```

Expect conflicts wherever both sides changed a renamed line; taking upstream's
text for such a line and letting the script rename it afterwards is usually
right. Delete the extracted dependency folders under `subprojects/` and
reconfigure if the dependency patches changed.

Keep openD3's side for `src/game`, `src/d3xp`, `content/baseod3`, the openD3
identity and the `OPEND3` sites. Never take `src/mpgame`, upstream's `src/game`
or `content/baseoq4`. Where new upstream engine code calls a Quake 4-only
`idGame` method, adapt it to Doom 3's API or gate it as D9. Regenerate the
Vulkan SPIR-V headers if both sides touched the shader sources, then rebuild
and repeat the checks under "Verified".
