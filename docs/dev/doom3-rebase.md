# openD3 on the openQ4 engine: rebase record

This is the working record of openD3's move onto the current openQ4 engine. It
states what was done, what has been verified and how, and what is still open.
Update it when any of that changes; it is the place a future upstream sync
starts from.

## Where openD3 came from

- openD3 forked from openQ4 `abb9a688` (2026-02-18) and carried six commits of
  Doom 3 adaptation on that snapshot. The fork tree was byte-identical to that
  openQ4 commit apart from 42 stripped Quake 4 asset files.
- The game library lived in a companion repository, `OpenD3-GameLibs`, and was
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
   merges of `openq4-upstream/main`.
2. **Remove the Quake 4 game library and content.** `src/game` and
   `src/mpgame` (Quake 4 SDK), the SDK licence and the Quake 4 runtime content
   leave the tree. The engine-side content moves to `content/baseod3`.
3. **Import the Doom 3 game library with its history.** `src/game` (base game)
   and `src/d3xp` (Resurrection of Evil) come from `OpenD3-GameLibs` `c450f9c`
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
| `game-d3xp_<arch>` | `src/d3xp` | `_D3XP`, `CTF` | Builds and stages; not run |

`src/d3xp` was imported in id's GPL form. The 64-bit and engine-ABI port that
`src/game` already carried was applied to it by three-way merge per file
(base: id's GPL `neo/game`; incoming: the ported `src/game`; target:
`src/d3xp`). `Anim_Import.cpp`, `SaveGame.cpp` and `PlayerView.cpp` were
resolved by hand. A fix that applies to both games goes into both trees.

The engine selects `game-d3xp` when `d3xp` is `fs_game` or `fs_game_base`.

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
- The dedicated server spawns `game/mp/d3dm1` (887 entities).

That is all that has been run. In particular, nothing here is evidence for:
playing past the first cinematic, combat, AI, PDA and video playback, level
transitions, loading a savegame, a multiplayer client joining a server,
Linux, macOS, Android, ARM64 or VR.

## Open items

Listed roughly by how much they block a player.

1. **Resurrection of Evil is not playable.** The filesystem's official
   expansion handling still describes Quake 4's Awakening (`q4xbase`) and
   resets `fs_game d3xp`. The module is untested, and the machine this was
   done on has no complete RoE data. The renderer carries
   `renderEntity_t::xrayIndex` and the sound world `SetSlowmo` only so the
   game compiles; neither has an effect.
2. **Savegames are not stamped.** The engine's hardened savegame framework
   expects the game to write a versioned, checksummed payload. Doom 3's game
   library writes its original unstamped payload, which `Session.cpp` accepts
   under `OPEND3` for the build that wrote it. Writing the stamped payload is
   game-side work; it must be written for openD3, not copied from openQ4's or
   openPREY's game trees, which are under their SDK licences. Loading a save
   has not been tested.
3. **Prey-only engine code remains.** The transplanted layer includes features
   only Prey used: spirit-walk views, glow stages, Prey material keywords and
   deforms, Prey GUI window types, Prey sound classes and subtitles, the
   loading-music player, Prey font face folding and the libogg/libvorbis
   decode fallback. They are inert for Doom 3 content and many comments still
   say Prey. The Prey data blocks formerly behind `HUMANHEAD` are compiled
   out. Each of these should be removed or, where Doom 3 mods benefit, kept
   deliberately.
4. **Startup warnings still to clear** (Procedure 1 in `AGENTS.md`): the
   engine's chat window and menu background precache four Quake 4 menu images;
   the retained HUD looks for a Quake 4 HUD document; the engine asks for a
   `guisounds` shader and string `#str_107240`, which Doom 3 does not have;
   the stock menus reference the removed `s_driver` cvar; the engine and the
   game both declare `r_showSkel`; sound shader volumes above +10 dB are
   clamped. A `mars_city1` load currently logs about 25 distinct warnings,
   some of them the retail content's own.
5. **The retained RmlUi interface has no Doom 3 documents.** Launches pin
   `ui_retained 0`. The stock Doom 3 GUIs are the interface.
6. **Tooling under `tools/` is inherited and unadapted.** The test corpus,
   validation profiles, packaging, installer and release scripts were written
   for openQ4 and partly adapted for Prey. They were renamed mechanically and
   have not been run for openD3. The build helpers Meson invokes are adapted
   and exercised.
7. **No CI.** openQ4's GitHub workflows were removed rather than left to fail;
   they need rebuilding for openD3.
8. **Documentation under `docs/`** other than this file and
   `game-source-provenance.md` is openQ4's and describes Quake 4 work.

## Naming

The project name is openD3 everywhere a user or packager sees it: binaries,
window titles, config and log names, environment variables (`OPEND3_*`),
package metadata and messages. Identifiers that are engine code shared with
upstream keep upstream's names (`OPENQ4_*` macros, `openQ4_` functions,
`openq4_*` generated headers and Meson variables, `*_openq4` content file
names). Renaming them would turn every upstream merge into a conflict; openPREY
makes the same choice.

## Syncing with upstream

```
git fetch openq4-upstream
git merge openq4-upstream/main
```

Keep openD3's side for `src/game`, `src/d3xp`, `content/baseod3`, the openD3
identity and the `OPEND3` sites. Never take `src/mpgame`, upstream's `src/game`
or `content/baseoq4`. Where new upstream engine code calls a Quake 4-only
`idGame` method, adapt it to Doom 3's API or gate it as D9. Regenerate the
Vulkan SPIR-V headers if both sides touched the shader sources, then rebuild
and repeat the checks under "Verified".
