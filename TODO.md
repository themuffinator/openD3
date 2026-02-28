# OpenD3 TODO

This file tracks migration and stabilization work for the OpenD3 transition.

## High Priority

- [ ] Reconcile filesystem/game-dir defaults with Doom 3 expectations (`base`/`d3xp`) while preserving current staged workflow.
- [ ] Review `src/game` against `../OpenD3-GameLibs` and eliminate sync drift.
- [ ] Audit remaining OpenQ4 naming strings in user-facing output and tools.
- [ ] Complete launch + log validation loops on stock Doom 3 assets.

## Compatibility Work

- [ ] Compare renderer/material behavior with `E:\_SOURCE\_CODE\dhewm3-master` and document required reversions.
- [ ] Validate savegame/config path behavior on Windows/Linux/macOS defaults.
- [ ] Confirm multiplayer map/bootstrap flow with Doom 3 MP maps.
- [ ] Verify asset validation paths/checksums for retail Doom 3 (`base`) and expansion content (`d3xp`).

## Modernization

- [ ] Continue SDL3 parity improvements for non-English layouts and UTF-8 text input.
- [ ] Bring Linux/macOS Meson host support from staged to validated.
- [ ] Remove temporary migration compatibility shims (`OPENQ4_*` env variable aliases) after downstream tooling updates.
