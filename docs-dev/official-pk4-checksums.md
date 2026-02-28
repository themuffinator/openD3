# Official Doom 3 PK4 Checksum Notes

This document tracks official Doom 3 PK4 checksum validation inputs for OpenD3.

## Scope

- Base game install path (typical Steam): `C:\Program Files (x86)\Steam\steamapps\common\Doom 3\base`
- Optional expansion path: `C:\Program Files (x86)\Steam\steamapps\common\Doom 3\d3xp`
- Log source: startup lines in `fs_savepath\<gameDir>\logs\opend3.log`

## Current Status

- OpenD3 validates required Doom 3 base media PK4 files on startup (`fs_validateOfficialPaks=1`).
- Quake 4-era required pack rules are removed from `src/framework/FileSystem.cpp`.
- Validation now targets Doom 3 `base/pak000.pk4` through `base/pak004.pk4`.

## Required Base PK4 Set

These are the required packs validated by OpenD3:

- `pak000.pk4`: `0x28d208f1`
- `pak001.pk4`: `0x40244be0`
- `pak002.pk4`: `0xc51ecdcd`
- `pak003.pk4`: `0xcd79d028`
- `pak004.pk4`: `0x765e4f8b`

## Optional Official Packs

These are recognized official packs but not required for startup validation:

Base updates:

- `pak005.pk4`: `0x8ffc3621`
- `pak006.pk4`: `0x095b65ab`
- `pak007.pk4`: `0x666bdb3c`
- `pak008.pk4`: `0x23ae5993`

Legacy game-code packs:

- `game00.pk4`: `0x29cdb978`
- `game01.pk4`: `0x51c6981f`
- `game02.pk4`: `0x0f3ec6f7`
- `game03.pk4`: `0x5d4230ea`

## Capture Procedure (Reference)

1. Launch OpenD3 against a clean retail Doom 3 install.
2. Exit after initialization.
3. Open `fs_savepath\<gameDir>\logs\opend3.log`.
4. Collect `Loaded pk4 ... with checksum ...` lines for `base` (and `d3xp` when relevant).
5. Record required set in this document.

## Notes

- Base path validation now checks for Doom 3 retail media (`base/pak000.pk4` + `base/pak001.pk4`) instead of Quake 4-era pack names.
- Auto-discovery candidates now target Doom 3 install paths (Steam/GOG).
