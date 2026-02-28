# OpenD3 Platform And Architecture Roadmap

This document defines platform direction for OpenD3 and how SDL3 + Meson are used during the Doom 3 compatibility transition.

## Target End State

- First-class support on modern desktop operating systems:
  - Windows
  - Linux
  - macOS
- First-class support for modern 64-bit desktop architecture:
  - x64 (`x86_64`)
- Maintain Doom 3 gameplay/content compatibility while modernizing platform/build layers.

## Current Baseline (0.0.1 era)

- Primary validated host target: Windows x64.
- Build system: Meson + Ninja.
- Platform backend direction: SDL3-first (`legacy_win32` remains transitional).
- C++ baseline target: C++23 semantics (`vc++latest` on current MSVC front-end).
- Toolchain direction: MSVC 19.46+ (VS 2026 generation), with optional strict enforcement.

## SDL3 Direction

- SDL3 is the default portability layer for window/input handling.
- New platform-facing work should prefer SDL3 abstractions first.
- Platform-specific code should stay isolated under `src/sys/<platform>/` when SDL3 cannot cover a requirement.

## Meson Direction

- Meson is the canonical build system.
- External dependencies should be consumed through Meson subprojects/wraps.
- New build logic should remain host-aware and architecture-aware.
- Use `tools/build/meson_setup.ps1` on Windows to guarantee MSVC environment setup.

## Bring-Up Staging

1. Keep Windows x64 stable with SDL3 default backend.
2. Incrementally enable Linux host build/source selection and validation.
3. Incrementally enable macOS host build/source selection and validation.
4. Promote Linux/macOS once compile/link/runtime loops are consistently clean.

## Definition Of Done For First-Class Platform Support

- Clean configure + build with Meson.
- Engine reaches gameplay/map startup with stock Doom 3 assets.
- Core input/render/audio/network paths function without platform-specific content hacks.
- Regressions are fixed in code (engine/game/platform), not by shipping override assets.
