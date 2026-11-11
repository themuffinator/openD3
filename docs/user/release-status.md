# Release status and matching documentation

**openD3 has no release.** The version in the source tree is 0.0.1. There are no packages to download, and the only way to run openD3 is to build it. Status checked on 11 November 2026.

openD3 has just moved onto the current openQ4 engine. Since then very little of the game has been run: the first campaign map, the main menu and a dedicated-server start, all on Windows x64. Treat it as a development build for people who want to follow or help the port, not as a way to play Doom 3 through yet.

## Running openD3 today

Build and stage openD3 with [BUILDING.md](../../BUILDING.md), then follow [Getting Started](getting-started.md). Keep your legitimate Doom 3 installation where it is and let openD3 locate it, or point `+set fs_basepath` at the directory containing `base`, not at `base` itself.

## What has been run

On Windows x64, against the Steam release of Doom 3 with the 1.3.1 packs:

- Startup finds the Steam install by itself, checks `pak000`–`pak004` by checksum and leaves the retail game binaries out.
- `game/mars_city1`, the campaign's first map, loads on the OpenGL renderer, plays its intro cinematic with its in-world screens, writes its autosave and exits cleanly.
- The same map loads and renders on the Vulkan renderer.
- Doom 3's own main menu starts and plays the intro video.
- The dedicated server starts the deathmatch map `game/mp/d3dm1`.

## What has not been run

Nothing in this list is known to be broken. Nobody has tried it yet:

- Playing past the first cinematic: combat, AI, the PDA and video playback.
- Moving from one level to the next.
- Loading a saved game.
- A multiplayer client joining a server.
- Linux, macOS, Android, ARM64 and VR.

## Known problems

- **Resurrection of Evil is unverified.** `+set fs_game d3xp` loads the expansion's game module, but no expansion map has been run, and the one attempt so far stopped at the expansion's main menu. See [Campaigns](campaigns.md#resurrection-of-evil).
- **Saves are tied to the build that wrote them.** See [Campaigns](campaigns.md#saves-and-switching).
- **The newer menus and HUD inherited from openQ4 have no Doom 3 pages.** Launch with `+set ui_retained 0` to use Doom 3's own.
- **Startup logs warnings.** A `mars_city1` load currently logs about 25 distinct warnings, some of them from the retail content itself.

## These guides follow the source tree

The guides in this directory describe the current source. There is no released version for them to drift away from yet.

| Area | State today |
| --- | --- |
| Renderers | OpenGL is the default. Vulkan is selectable and has drawn the first map |
| Campaign | The first map loads; nothing further has been played |
| Resurrection of Evil | The game module loads; no map has been run |
| Saves | Written on autosave; loading is untested and saves do not carry across builds |
| Multiplayer | A dedicated server starts a map; no client has joined one |
| Platforms | Windows x64 only |
| Interface | Doom 3's own menus and HUD, with `ui_retained 0` |

The [rebase record](../dev/doom3-rebase.md) is the detailed and current statement of what has been verified, how, and what is still open. Where this page and that record disagree, the record is right.
