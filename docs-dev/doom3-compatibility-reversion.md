# Doom 3 Compatibility Reversion Guide

Use this note to drive incremental reversion from OpenQ4-era behavior back toward Doom 3 compatibility.

## Primary Local Reference

- `E:\_SOURCE\_CODE\dhewm3-master`

This is the authoritative local behavior/code reference for what to restore where current OpenD3 behavior is Quake 4-biased.

## Companion Repo

- `E:\Repositories\OpenD3-GameLibs`

Game-library changes should be made canonically in `OpenD3-GameLibs` and synchronized into this repository.

## Reversion Workflow

1. Reproduce mismatch in OpenD3 (startup/map/runtime behavior).
2. Locate equivalent path in `dhewm3-master`.
3. Document divergence and intended direction in a short task note.
4. Apply minimal code change in OpenD3 (or OpenD3-GameLibs where appropriate).
5. Run the launch/log loop and verify improvement without introducing new regressions.

## Priority Areas

- Filesystem/game-dir assumptions (`base`, `d3xp`, save/config paths).
- Effects paths and declarations (Doom 3-native FX behavior, no external Quake 4 legacy-effects companion dependency).
- Material/parser behavior where Quake 4-specific extensions diverge from Doom 3 expectations.
- AAS parsing compatibility (`1.07` Doom 3/BFG navigation data vs OpenQ4-era `1.08` extensions).
- Map geometry CRC behavior used to validate AAS/CM data.
- Session/startup commands and map bootstrapping defaults.
- Platform/runtime paths (logs, crash dumps, executable naming).

## Known AAS/Map CRC Divergence

- Doom 3 and Doom 3 BFG assets use AAS format `1.07`.
- OpenQ4-era code introduced `1.08` area feature fields and strict version checks.
- For Doom 3 compatibility, AAS loading must accept `1.07` and parse area records without `numFeatures/firstFeature`.
- Doom 3/BFG map geometry CRC for AAS validation does not hash entity `model` epairs for brush/patch primitives.
- OpenQ4-era map CRC behavior added that `model` hashing, producing false AAS "out of date" failures on Doom 3 maps.

## Intentional Runtime Divergence

- Trigger touching now supports a swept check from the player's previous origin to current origin.
- Rationale: this avoids missed `trigger_once`/progression touches when movement steps skip over narrow trigger volumes.
- Scope: the sweep is only applied for player-trigger checks; existing overlap checks remain intact.

## Validation Loop

1. Launch OpenD3 (SP/MP mode as needed).
2. Let startup reach map/session initialization.
3. Exit and inspect `${workspaceFolder}\.home\openbase\logs\opend3.log`.
4. Resolve errors/warnings in code, not with compatibility-breaking content hacks.
5. Repeat until clean for the changed scenario.
