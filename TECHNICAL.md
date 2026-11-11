# openD3 technical overview

openD3 is the openQ4 engine carrying Doom 3's game code. This page covers what
is specific to openD3. For the state of the port, see the
[rebase record](docs/dev/doom3-rebase.md); for building, [BUILDING.md](BUILDING.md).

## Repository layout

| Path | Contents |
|---|---|
| `src/` | Engine. First-level directories are subsystems: `framework`, `renderer`, `sound`, `ui`, `cm`, `aas`, `idlib`, `sys`, `tools`, `bse`, `imagetools`, `rendergeo` |
| `src/game/` | Doom 3 game library |
| `src/d3xp/` | Resurrection of Evil game library |
| `src/external/`, `subprojects/` | Vendored and wrapped third-party code |
| `content/baseod3/pak0/` | openD3's own runtime content: GLSL and ARB programs, post-process materials, two fonts, default configs and engine string tables |
| `tools/build/` | Build helpers Meson invokes, plus packaging and release scripts |
| `tools/debug/` | VS Code launch generator and debugging helpers |
| `tools/tests/`, `tools/validation/` | Test corpus and validation profiles inherited from openQ4; not yet adapted to openD3 |
| `docs/dev/` | The rebase record, the game source provenance note and the Android/GLES integration record |
| `LICENSES/` | Licence notices |
| `.install/` | Staged runtime package (generated) |
| `builddir/` | Build output (generated) |

## Directories at run time

openD3 reads three kinds of directory:

- **`base/`** inside your Doom 3 install: the retail packs. Found through
  `fs_basepath`, which the engine fills in from Steam, GOG, the Windows
  registry or known install folders, or from `OPEND3_DOOM3_PATH`.
- **`baseod3/`** beside the openD3 executables: openD3's game modules,
  `pak0.pk4` and `mod.json`. It stays in the search path under any mod.
- **The save path**, `fs_savepath`: your config (`openD3Config.cfg`), saves,
  screenshots and logs, under `<fs_savepath>/baseod3/`.

Do not put retail packs in `baseod3/`; startup reports misplaced ones.

### Retail pack validation

With `fs_validateOfficialPaks 1` (the default), startup requires
`pak000.pk4`–`pak004.pk4` in `base/` and checks them against the 1.3.1
checksums. `pak005.pk4`–`pak008.pk4` are recognised patch packs.
`game00.pk4`–`game03.pk4` hold only the original game binaries and are left out
of the search path.

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

## Modules

| Module | Loaded when |
|---|---|
| `game_<arch>` | Always, unless the expansion is selected |
| `game-d3xp_<arch>` | `fs_game` or `fs_game_base` is `d3xp` (loads; no map run yet) |
| `renderer-gl_<arch>` | `r_renderApi gl`, the default |
| `renderer-vk_<arch>` | `r_renderApi vulkan` |

Game modules are looked up in the active game directory and then in
`baseod3/`. The game API is Doom 3's, version 8 (`src/game/Game.h`); the engine
refuses a module that reports another version. The renderer modules use a
versioned C ABI (`src/renderer/RenderModuleAPI.h`) and are likewise refused on
a mismatch, so always stage the engine and its modules together.

## Mods

The engine's mod support comes from openQ4. A mod folder selected with
`fs_game` needs a `mod.json` manifest naming the mod and the engine version it
requires (`requiredopenD3Version`); `content/baseod3/mod.json.in` shows the
fields. A mod may carry only content and use `baseod3/`'s game modules. Mods
that ship a game DLL built for the original Doom 3 `gamex86` interface do not
load. No Doom 3 mod has been tried on openD3 yet.

## File formats

Where Doom 3's formats differ from Quake 4's, the engine reads Doom 3's:

- `.proc` files with the `mapProcFile003` header.
- AAS files version 1.07.
- Collision models version 1.00, and Doom 3's map geometry CRC.
- Particle (`.prt`) and FX (`.fx`) declarations, alongside the PDA, video,
  audio and email declarations.
- Doom 3's bitmap fonts, and interaction programs through the ARB path.

The `OPEND3` compile define marks the engine sites that choose Doom 3
behaviour.

## Savegames

The engine writes its own header, screenshot and atomic commit. The Doom 3 game
library writes its original game payload inside it, which the engine accepts
for the build that wrote it. Saves are therefore not portable across builds,
and the game payload has no integrity check yet.

## Useful console variables

| CVar | Purpose |
|---|---|
| `r_renderApi` | `gl` or `vulkan`; read at startup |
| `r_fullscreen`, `r_mode`, `r_customWidth`, `r_customHeight`, `r_screen` | Window and display mode |
| `ui_retained` | Keep at `0`: Doom 3 uses its stock GUIs |
| `fs_basepath`, `fs_savepath`, `fs_game`, `fs_game_base` | Filesystem roots and mod selection |
| `fs_validateOfficialPaks` | Retail pack validation |
| `logFile`, `logFileName` | Log to a file under the save path |
| `com_platformProfile` | Platform profile, for example `steamdeck` |

The many renderer and platform features inherited from openQ4 (shadow maps,
light grids, post-processing, presets, controller support) are described in
[openQ4's guides](https://github.com/themuffinator/openQ4/tree/main/docs/user).
None has been checked with Doom 3 yet.

## Environment variables

| Variable | Purpose |
|---|---|
| `OPEND3_DOOM3_PATH`, `OPEND3_DOOM3_ROOT` | Doom 3 install folder candidates |
| `OPEND3_STEAM_ROOT(S)`, `OPEND3_STEAM_LIBRARY`, `OPEND3_STEAM_LIBRARIES` | Extra Steam roots and libraries to search |
| `OPEND3_OPENAL_ROOT` | OpenAL Soft package used when staging on Windows |
| `OPEND3_FORCE_X11` | Prefer XWayland on Linux |


## Dependencies

Fetched or vendored through Meson: SDL3, OpenAL Soft (prebuilt headers and
import library; the runtime DLL is supplied separately on Windows), GLEW,
stb_vorbis, libogg and libvorbis, RmlUi, JsonCpp, libtess2, glslang, the
OpenXR loader, and the Vulkan headers with volk and VMA under `src/external/`.
