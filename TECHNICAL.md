<div align="center">

# openD3 Technical Reference

</div>

> **Development reference:** openD3 has no release yet. This page follows the current source, and the [rebase record](docs/dev/doom3-rebase.md) states what of it has been run. See [release status](docs/user/release-status.md).

This reference is for advanced players, server operators and modders. It covers the install layout, asset checks, useful console settings, file paths, mod packaging and version numbers.

For installation and a feature overview, see the [README](README.md). For building from source, see [BUILDING.md](BUILDING.md). Where the code lives is described in [Source Layout](docs/dev/source-layout.md).

---

## Table of Contents

- [Compatibility](#compatibility)
- [Install Layout](#install-layout)
- [Asset Validation](#asset-validation)
- [Console Settings](#console-settings)
- [File System Paths](#file-system-paths)
- [Crash Reports](#crash-reports)
- [Mods](#mods)
- [Game Code and Resurrection of Evil](#game-code-and-resurrection-of-evil)
- [Version Numbers](#version-numbers)

---

## Compatibility

openD3 is the openQ4 engine carrying Doom 3's game code. It runs the official Doom 3 game data (the `base` PK4s at version 1.3.1) with its own engine and game modules. It never loads the retail `gamex86` binaries, so mods that depend on them are not supported. Doom 3: BFG Edition's data is a different format and is not supported either.

Where Doom 3's formats differ from Quake 4's, the engine reads Doom 3's:

- `.proc` files with the `mapProcFile003` header.
- AAS files version 1.07.
- Collision models version 1.00, and Doom 3's map geometry CRC.
- Particle (`.prt`) and FX (`.fx`) declarations, alongside the PDA, video, audio and email declarations.
- Doom 3's bitmap fonts, and interaction programs through the ARB path.

The `OPEND3` compile define marks the engine sites that choose Doom 3 behaviour.

**Savegames.** The engine writes its own header, screenshot and atomic commit. The Doom 3 game library writes its original game payload inside it, which the engine accepts for the build that wrote it. Saves are therefore not portable across builds, the game payload has no integrity check yet, and loading a save has not been tested.

So far only the first campaign map and a dedicated-server start have been run; the [rebase record](docs/dev/doom3-rebase.md#verified) lists exactly what. Please report anything that breaks on the [issue tracker](https://github.com/themuffinator/openD3/issues).

---

## Install Layout

The staged package in `.install/` uses this layout:

```
openD3/
├── openD3-client_<arch>     # The game (.exe on Windows)
├── openD3-ded_<arch>        # Dedicated server (.exe on Windows)
├── renderer-gl_<arch>       # OpenGL renderer module (.dll / .so / .dylib), the default
├── renderer-vk_<arch>       # Vulkan renderer module (.dll / .so / .dylib)
├── OpenAL32.dll             # (Windows) OpenAL Soft runtime
└── baseod3/                 # The single openD3 game directory
    ├── pak0.pk4             # openD3 runtime content
    ├── mod.json             # Game-directory manifest
    ├── game_<arch>          # Doom 3 game module (.dll / .so / .dylib)
    └── game-d3xp_<arch>     # Resurrection of Evil game module
```

| Module | Loaded when |
|---|---|
| `game_<arch>` | Always, unless the expansion is selected |
| `game-d3xp_<arch>` | `fs_game` or `fs_game_base` is `d3xp` (loads; no map run yet) |
| `renderer-gl_<arch>` | `r_renderApi gl`, the default |
| `renderer-vk_<arch>` | `r_renderApi vulkan` |

- Game modules are looked up in the active game directory and then in `baseod3/`. The game API is Doom 3's, version 8 (`src/game/Game.h`); the engine refuses a module that reports another version.
- The renderer modules use a versioned C ABI (`src/renderer/RenderModuleAPI.h`) and are likewise refused on a mismatch.
- Your retail game data stays in the Doom 3 install's `base` directory, and the expansion's in `d3xp`; openD3 reads them from there. Do not put retail packs in `baseod3/`; startup reports misplaced ones.
- When upgrading, replace the whole package. The engine, renderer modules and game modules must come from the same build.

---

## Asset Validation

openD3 checks that your Doom 3 installation has legitimate, unmodified game data.

1. With `fs_validateOfficialPaks 1` (the default, set at startup) it requires `pak000.pk4` to `pak004.pk4` in `base/` and checks them against the 1.3.1 checksums.
2. It refuses to run if a required pack is missing or modified.
3. `pak005.pk4` to `pak008.pk4` are recognised patch packs, used when present.
4. It leaves `game00.pk4` to `game03.pk4` out of the search path: they hold only the original game binaries, and openD3 ships its own game modules.

| Pack | Checksum |
|---|---|
| `pak000.pk4` | `0x28d208f1` |
| `pak001.pk4` | `0x40244be0` |
| `pak002.pk4` | `0xc51ecdcd` |
| `pak003.pk4` | `0xcd79d028` |
| `pak004.pk4` | `0x765e4f8b` |
| `pak005.pk4` | `0x8ffc3621` |
| `pak006.pk4` | `0x095b65ab` |
| `pak007.pk4` | `0x666bdb3c` |
| `pak008.pk4` | `0x23ae5993` |

openD3 also checks its own `baseod3/pak0.pk4` against a checksum built into the executable and refuses to start if it is missing or modified. A pack that passed is remembered under the save path and hashed again only after the file changes; `+set fs_cacheVerifiedPaks 0` checks it at every launch.

---

## Console Settings

The stock Doom 3 menus cover the usual options. These settings are the ones that matter for openD3 itself.

- `r_renderApi gl|vulkan`: the renderer, read at startup.
- `r_fullscreen 0|1`, `r_mode`, `r_customWidth`, `r_customHeight`, `r_screen`: window and display mode.
- `ui_retained 0`: keep at `0`. openD3 uses Doom 3's own GUIs; openQ4's retained interface has no Doom 3 pages.
- `fs_basepath`, `fs_savepath`, `fs_game`, `fs_game_base`: filesystem roots and mod selection (see [File System Paths](#file-system-paths)).
- `fs_validateOfficialPaks`: retail pack validation.
- `logFile 2`, `logFileName`: write a log under the save path.
- `com_platformProfile`: platform profile, for example `steamdeck`.

The renderer and platform features inherited from openQ4 (shadow maps, light grids, post-processing, presets, controller support) are described in [openQ4's guides](https://github.com/themuffinator/openQ4/tree/main/docs/user). None has been checked with Doom 3 yet. The [client settings guide](docs/user/client-settings.md) puts the common launch options in player terms.

---

## File System Paths

openD3 reads three kinds of directory:

- **`base/`** inside your Doom 3 install: the retail packs. Found through `fs_basepath`, which the engine fills in from Steam, GOG, the Windows registry or known install folders.
- **`baseod3/`** beside the openD3 executables: openD3's game modules, `pak0.pk4` and `mod.json`. It stays in the search path under any mod.
- **The save path**, `fs_savepath`: your config (`openD3Config.cfg`), saves, screenshots and logs, under `<fs_savepath>/baseod3/`.

The search can be widened with environment variables:

| Variable | Purpose |
|---|---|
| `OPEND3_DOOM3_PATH`, `OPEND3_DOOM3_ROOT` | Doom 3 install folder candidates |
| `OPEND3_STEAM_ROOT(S)`, `OPEND3_STEAM_LIBRARY`, `OPEND3_STEAM_LIBRARIES` | Extra Steam roots and libraries to search |
| `OPEND3_FORCE_X11` | Prefer XWayland on Linux |

If your Doom 3 installation is not found automatically, launch with:

```
openD3-client_x64 +set fs_basepath "C:\path\to\Doom 3"
```

---

## Crash Reports

On Windows, a crash writes `opend3_crash_*.log` and `opend3_crash_*.dmp` files to a `crashes/` folder beside the executable. Attach both files, with your log, when [reporting a crash](https://github.com/themuffinator/openD3/issues).

---

## Mods

Every runnable mod needs a `mod.json` file in its root directory, including `baseod3/` itself. The manifest is a flat JSON object with these required string fields:

- `name`
- `version`
- `releaseDate`
- `website`
- `author`
- `requiredopenD3Version`: the oldest openD3 version the mod works with, as `major.minor.patch`

Example:

```json
{
  "name": "My Mod",
  "version": "1.0.0",
  "releaseDate": "2026-11-01",
  "website": "https://example.com",
  "author": "Your Name",
  "requiredopenD3Version": "0.0.1"
}
```

`content/baseod3/mod.json.in` is openD3's own manifest. Game modules are optional: a mod may carry only content and use `baseod3/`'s modules. Mods that ship a game DLL built for the original Doom 3 `gamex86` interface do not load.

When a mod ships a declaration file with the same name as one beneath it (for example `def/player.def`), the engine reads the mod's copy first and then the copies below it. Set `decl_layerModFiles 0` at startup to have a mod's file hide the base file entirely, as in the original game.

The mod support comes from openQ4. No Doom 3 mod has been tried on openD3 yet.

---

## Game Code and Resurrection of Evil

openD3's game code is id Software's GPL Doom 3 game library, kept in this repository and licensed under GPLv3 like the engine:

- [`src/game`](src/game/) builds `game_<arch>`, for Doom 3.
- [`src/d3xp`](src/d3xp/) builds `game-d3xp_<arch>`, for **Resurrection of Evil**. It is the same game with `_D3XP` and `CTF` defined, so a fix that applies to both goes into both trees.

[Game source provenance](docs/dev/game-source-provenance.md) records where the library came from. `+set fs_game d3xp` mounts the expansion's `d3xp` directory and loads its module, but no expansion map has been run yet; see the [campaign guide](docs/user/campaigns.md#resurrection-of-evil).

Resurrection of Evil was developed by Nerve Software with id Software. openD3 includes none of its content.

---

## Version Numbers

openD3 is at version 0.0.1 and has no release. Development builds add a track and the source commit, for example `0.0.1-dev+gabcdef12`. Type `si_version` in the console to see the running build's version, and include it in bug reports.

---

[← Back to README](README.md)
