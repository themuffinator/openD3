# OpenD3 Release Completion List

Use this file as the source list for release changelog entries.

Process:
1. Add completed work under "Ready For Changelog".
2. When cutting a release, copy relevant entries into that release section in `CHANGELOG.md` (or release notes).
3. Keep forward work in "Carry Forward".

## Ready For Changelog

- [x] Repository rebrand baseline started: `OpenQ4` -> `OpenD3` in project/docs/tooling metadata.
- [x] Companion game-libs default switched to `../OpenD3-GameLibs` in helper scripts.
- [x] Added `tools/build/opend3_devcmd.cmd` and retained legacy wrapper compatibility entrypoint.
- [x] Removed Meson-level external Quake 4 legacy-effects companion-repo build option and repo-path discovery logic.
- [x] Nightly packaging updated to no longer require external legacy-effects runtime artifacts.
- [x] VS Code tasks/launch profiles updated for OpenD3 executable naming and Doom 3 basepath defaults.
- [x] AGENTS guidance rewritten for Doom 3 reinstatement and dhewm3 reference workflow.
- [x] Ported OpenQ4 x64 robustness fixes relevant to Doom 3: player trigger overlap fallback, immediate post-teleport trigger sweep, AAS node/depth validation hardening, AI look_joint warning aggregation, bound rigid-body proxy push handling, generated image-cache writes to `fs_savepath`, DDS (`DXT1`/`DXT5`) image fallback loading, and optional missing-image warning suppression.

## Carry Forward

- [ ] Complete remaining source-level user-facing OpenQ4 string cleanup.
- [ ] Reconcile current `openbase/` staging with final Doom 3 directory strategy (`base`/`d3xp`).
- [x] Validate `fs_validateOfficialPaks` checksum rules against retail Doom 3 assets.
- [ ] Run full SP/MP launch-loop validation and document residual compatibility gaps.
- [ ] Retire temporary `OPENQ4_*` compatibility environment-variable aliases after downstream updates.
