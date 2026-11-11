<div align="center">

# Building openD3 from Source

</div>

This guide covers compiling openD3 from source. openD3 builds with [Meson](https://mesonbuild.com/) and Ninja; dependencies come from Meson subprojects, fetched at configure time.

> [!NOTE]
> **openD3 has no release yet**, so building from source is currently the only way to run it. Only the Windows x64 build has been exercised. The Linux, macOS and Android paths that applied to the openQ4 engine are expected to carry over, but they have not been tried here; see the [rebase record](docs/dev/doom3-rebase.md#verified).

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [In-tree Game Sources](#in-tree-game-sources)
- [Build Setup](#build-setup)
- [Build Options](#build-options)
- [Validation Scripts](#validation-scripts)
- [Building on Windows](#building-on-windows)
- [Building on Linux / macOS](#building-on-linux--macos)
- [Output Files](#output-files)
- [Packaging a Distributable](#packaging-a-distributable)

---

## Prerequisites

| | |
|---|---|
| Compiler | MSVC 19.46 or newer (Visual Studio 2022 17.14+ or 2026) with the x64 C++ tools |
| Meson | 1.6.0 or newer |
| Ninja | any recent release |
| Python | 3.11 or newer, with Pillow for the icon sync step |
| OpenAL Soft runtime | `OpenAL32.dll` for x64 on Windows, see below |

The engine is C++20; the game modules build as C++17.

Fetched or vendored through Meson: SDL3, OpenAL Soft (prebuilt headers and import library; the runtime DLL is supplied separately on Windows), GLEW, stb_vorbis, libogg and libvorbis, RmlUi, JsonCpp, libtess2, glslang, the OpenXR loader, and the Vulkan headers with volk and VMA under `src/external/`.

### OpenAL runtime on Windows

Staging copies an OpenAL Soft `OpenAL32.dll` next to the executables. The DLL is not tracked in Git. Provide one of:

- the file at `src/external/openal-soft/bin/win64/OpenAL32.dll`, or
- `OPEND3_OPENAL_ROOT` set to a folder that contains `bin/OpenAL32.dll`.

`tools/build/prepare_windows_openal.ps1` can build a package to point `OPEND3_OPENAL_ROOT` at.

---

## In-tree Game Sources

The game library is part of this repository and builds with the engine; there is nothing to check out separately.

| Path | Module | Game |
|---|---|---|
| `src/game/` | `game_<arch>` | Doom 3 |
| `src/d3xp/` | `game-d3xp_<arch>` | Resurrection of Evil (`_D3XP` and `CTF` defined) |

Both are id Software's GPL Doom 3 game code and are GPLv3 like the engine. [Game source provenance](docs/dev/game-source-provenance.md) records the import; the historical `openD3-GameLibs` repository is not used by the build.

---

## Build Setup

`builddir/` is the standard build directory and `.install/` the staged package root. Configure once, compile after every change, and stage when you want to run the package:

1. **Configure** `builddir/` with Meson.
2. **Compile**.
3. **Stage** into `.install/` with `meson install --no-rebuild --skip-subprojects`. `--skip-subprojects` keeps third-party installs out of the package tree.

The generated version header carries the Git commit, so the first compile after a new commit rebuilds most of the tree. New files under `content/baseod3/pak0/` reach `pak0.pk4` only after `meson setup --reconfigure`.

---

## Build Options

Pass with `-D<name>=<value>` at configure time.

| Option | Default | Effect |
|---|---|---|
| `build_engine` | `true` | Build the client, dedicated server and renderer modules |
| `build_games` | `true` | Build the game modules |
| `build_game_d3xp` | `true` | Build the Resurrection of Evil module |
| `build_renderer_vk` | `true` | Build the Vulkan renderer module |
| `use_pch` | `true` | Use precompiled headers |
| `platform_backend` | `sdl3` | Window and input backend |

`meson_options.txt` lists the rest, most of them inherited from openQ4. The optional native test suite (`-Dbuild_native_tests=true`) references Quake 4 interface files that are no longer in the tree and will not configure.

---

## Validation Scripts

The scripts under `tools/tests/` and `tools/validation/` are inherited from openQ4. They were renamed mechanically and most still test Quake 4 maps and content; treat them as unadapted until someone has run them for openD3. The ones that have been run for openD3:

- `python tools/tests/vk_shader_header_pin.py` checks the committed Vulkan SPIR-V headers against the shader sources (needs `glslangValidator` on `PATH`) and prints the exact command for a stale one.

### Regenerating the Vulkan shader headers

The Vulkan module embeds SPIR-V from committed headers, so a normal build needs no shader compiler. After changing a shader under `src/renderer/Vulkan/shaders`, regenerate the headers with `tools/build/spirv_to_header.py` and rerun `vk_shader_header_pin.py`.

---

## Building on Windows

Always run Meson through `tools/build/meson_setup.ps1` rather than calling `meson` from an arbitrary shell. The wrapper puts the MSVC tools on `PATH` and syncs the icon set first. `tools/build/opend3_devcmd.cmd` opens a prompt with the same environment.

```powershell
# 1. Configure
powershell -ExecutionPolicy Bypass -File tools/build/meson_setup.ps1 setup builddir . --backend ninja --buildtype=debugoptimized --wrap-mode=forcefallback

# 2. Compile
powershell -ExecutionPolicy Bypass -File tools/build/meson_setup.ps1 compile -C builddir

# 3. Stage the runtime package into .install/
powershell -ExecutionPolicy Bypass -File tools/build/meson_setup.ps1 install -C builddir --no-rebuild --skip-subprojects
```

Use `--buildtype=debug` or `--buildtype=release` as needed.

### Running

```powershell
.install\openD3-client_x64.exe +set r_fullscreen 0 +set ui_retained 0 +set logFile 2 +set logFileName logs/opend3.log
```

- The engine finds Doom 3 through Steam, GOG, the registry and known folders. Otherwise add `+set fs_basepath "<Doom 3 folder>"`, or set `OPEND3_DOOM3_PATH`.
- `+set r_renderApi vulkan` selects the Vulkan renderer.
- `+set fs_savepath <folder>` redirects saves, config and logs, which is how to keep a test run from touching your normal profile.
- `+map game/mars_city1` starts a map directly.

The VS Code launch configurations in `.vscode/launch.json` cover the campaign and multiplayer maps on both renderers. They are generated by `tools/debug/generate_vscode_launch.py`.

---

## Building on Linux / macOS

Not yet built for openD3. The openQ4 engine underneath builds on both with `tools/build/meson_setup.sh`, which takes the same Meson arguments as the Windows wrapper:

```bash
# 1. Configure
bash tools/build/meson_setup.sh setup builddir . --backend ninja --buildtype=debugoptimized --wrap-mode=forcefallback

# 2. Compile
bash tools/build/meson_setup.sh compile -C builddir

# 3. Stage the runtime package into .install/
bash tools/build/meson_setup.sh install -C builddir --no-rebuild --skip-subprojects
```

Expect to need the system OpenGL, OpenAL, Wayland or X11 and audio development packages that [openQ4's build guide](https://github.com/themuffinator/openQ4/blob/main/BUILDING.md#building-on-linux--macos) lists. Please report what happens on the [issue tracker](https://github.com/themuffinator/openD3/issues).

---

## Output Files

### Build directory (`builddir/`)

| File | Description |
|---|---|
| `openD3-client_<arch>[.exe]` | The game client |
| `openD3-ded_<arch>[.exe]` | The dedicated server |
| `renderer-gl_<arch>[.dll/.so/.dylib]` | OpenGL renderer module |
| `renderer-vk_<arch>[.dll/.so/.dylib]` | Vulkan renderer module |
| `baseod3/game_<arch>[.dll/.so/.dylib]` | Doom 3 game module, from `src/game` |
| `baseod3/game-d3xp_<arch>[.dll/.so/.dylib]` | Resurrection of Evil game module, from `src/d3xp` |
| `baseod3/pak0.pk4` | openD3's runtime content, packed from `content/baseod3/pak0` |
| `baseod3/mod.json` | The runtime directory's manifest |

`content/baseod3/pak0/` is compiled into a deterministic `pak0.pk4` before the engine is built, as listed in `tools/build/content_packs.json`, and the pack's checksum is embedded into the executable so startup can reject a missing or modified pack.

### Install directory (`.install/`)

After the install step, `.install/` is the staged package root to run from. `builddir/` holds the same binaries plus compiler and linker intermediates.

```
.install/
├── openD3-client_<arch>[.exe]   # The game client
├── openD3-ded_<arch>[.exe]      # Dedicated server
├── renderer-gl_<arch>           # OpenGL renderer module
├── renderer-vk_<arch>           # Vulkan renderer module
├── OpenAL32.dll                 # (Windows) runtime dependency
└── baseod3/
    ├── pak0.pk4                 # openD3 runtime content
    ├── mod.json                 # Game-directory manifest
    ├── game_<arch>              # Doom 3 game module
    └── game-d3xp_<arch>         # Resurrection of Evil game module
```

Repo-authored runtime content lives under `content/baseod3/pak0/`; `.install/baseod3/` is output, not an editing target. Never put retail `.pk4` files in `baseod3/`.

---

## Packaging a Distributable

The staged `.install/` directory is the package. The release tooling inherited from openQ4 turns it into an archive with an offline documentation site:

- `tools/build/package_nightly.py` copies the package, adds `VERSION.txt` and the licence files, places `assets/release/README.html` at the package root as its home page, and calls `tools/build/generate_release_docs.py` to convert the Markdown documentation into `docs/` (it needs `python -m pip install markdown`).
- `tools/build/build_windows_installer.py` builds an Inno Setup installer from a packaged Windows directory.
- `docs/dev/releases/` holds the curated release notes; the next release's are in [`unreleased.md`](docs/dev/releases/unreleased.md).

None of these has been run end to end for openD3, and openD3 has no release workflow yet ([open items](docs/dev/doom3-rebase.md#open-items)).

---

[← Back to README](README.md)
