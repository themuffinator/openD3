# OpenD3 Modernization Proposal (Post-Compatibility)

This proposal defines modernization work that should follow after core Doom 3 compatibility is stable.

## Preconditions

- Doom 3 startup/map/session flows are stable on stock assets.
- High-priority compatibility regressions are resolved.
- Build + staging workflow is consistent across local development and CI.

## Candidate Tracks

1. Renderer modernization
- Improve render quality/performance without changing baseline Doom 3 authored behavior unexpectedly.
- Keep compatibility toggles for risky changes.

2. Platform maturity
- Promote Linux/macOS from staged to validated support.
- Expand automation coverage for non-Windows hosts.

3. Tooling cleanup
- Remove migration shims and obsolete OpenQ4 naming/paths.
- Standardize scripts/docs on `OPEND3_*` env variables and OpenD3 naming.

4. Asset/runtime validation
- Finalize Doom 3 checksum policy documentation.
- Harden startup diagnostics and log-based triage.

## Non-Goals (for this phase)

- Reintroducing Quake 4-specific external legacy-effects companion repository integration.
- Shipping replacement game assets as a substitute for engine/runtime fixes.
