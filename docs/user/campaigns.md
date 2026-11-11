# Doom 3 and Resurrection of Evil campaigns

> **Development documentation:** openD3 has no release yet. This page follows the current source tree. See [release status](release-status.md) for what has been run and what has not.

openD3 builds a game module for each campaign: one for Doom 3 and one for its expansion, Resurrection of Evil. Doom 3's first level loads and plays its opening; nothing beyond that has been played yet. Resurrection of Evil's module loads, but no expansion level has been run.

## Doom 3

Start the first level directly from the command line:

```text
openD3-client_x64 +set ui_retained 0 +map game/mars_city1
```

`game/mars_city1` loads, plays the intro cinematic with its in-world screens and writes its autosave. That is as far as testing has gone: combat, the PDA, level changes and the rest of the campaign have not been played on openD3.

Doom 3's own main menu also starts and plays the intro video. Starting a new game from that menu has not been checked.

## Levels

The campaign's levels in order, with the name to give `map`. Only the first has been loaded.

| Level | Map |
| --- | --- |
| Mars City | `game/mars_city1` |
| Mars City Underground | `game/mc_underground` |
| Mars City (return) | `game/mars_city2` |
| Administration | `game/admin` |
| Alpha Labs Sector 1 | `game/alphalabs1` |
| Alpha Labs Sector 2 | `game/alphalabs2` |
| Alpha Labs Sector 3 | `game/alphalabs3` |
| Alpha Labs Sector 4 | `game/alphalabs4` |
| EnPro Plant | `game/enpro` |
| Communications Transfer | `game/commoutside` |
| Communications | `game/communications` |
| Monorail Skybridge | `game/recycling1` |
| Recycling Sector 2 | `game/recycling2` |
| Monorail | `game/monorail` |
| Delta Labs Level 1 | `game/delta1` |
| Delta Labs Level 2A | `game/delta2a` |
| Delta Labs Level 2B | `game/delta2b` |
| Delta Labs Level 3 | `game/delta3` |
| Delta Labs Level 4 | `game/delta4` |
| Hell | `game/hell1` |
| Delta Complex | `game/delta5` |
| CPU Complex | `game/cpu` |
| Central Processing | `game/cpuboss` |
| Site 3 | `game/site3` |
| Caverns Area 1 | `game/caverns1` |
| Caverns Area 2 | `game/caverns2` |
| Primary Excavation | `game/hellhole` |

## Resurrection of Evil

Resurrection of Evil is not playable yet.

Select it the way the original game does:

```text
openD3-client_x64 +set ui_retained 0 +set fs_game d3xp
```

openD3 then mounts the `d3xp` folder of your Doom 3 install and loads its own expansion module, `game-d3xp`, from `baseod3/`. The retail expansion's game binaries are never loaded.

What has been seen so far:

- The expansion folder mounts, the module loads and the game initialises.
- No expansion level has been loaded.
- On the one machine it was tried on, which has the expansion's patch pack but not its full data, startup then stopped with an error reading the expansion's main menu. It has not been repeated with a complete install, so it is not yet known whether a complete install gets further.

You need the expansion's own data in `d3xp/` beside `base/`. openD3 does not include it.

## Saves and switching

- Doom 3's saves go under `baseod3/` in your save folder; see [Client Settings](client-settings.md#where-settings-are-saved).
- A save loads only in the build that wrote it. openD3 does not yet stamp saves with a version it can check, so a save from another build is not accepted. Expect to start again after updating.
- Loading a saved game has not been tested at all. The first level writes its autosave; nothing has read one back.

## Console use

- `map game/<name>` starts a level, for example `map game/mars_city1`.
- `+map game/<name>` on the command line does the same at startup.
