#!/usr/bin/env python3
"""Keep active runtime diagnostics and artifacts branded as openD3."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


CONTRACTS = {
    "src/framework/RenderDoc.cpp": {
        "required": (
            'captureTemplate.AppendPath( "opend3" );',
            "Launch openD3 through RenderDoc first",
        ),
        "forbidden": (
            'captureTemplate.AppendPath( "openq4" );',
            "Launch openQ4 through RenderDoc first",
        ),
    },
    "src/framework/Session.cpp": {
        "required": (
            "stamped game payload/footer",
            "openD3 loads each map automatically",
            "openD3 map state assertion needs a non-empty expected map",
            "openD3 map state: map=%s",
            "openD3 map state mismatch: expected map=%s",
            "bakes openD3-compatible lightgrid metadata",
        ),
        "forbidden": (
            "stamped openQ4 payload/footer",
            "openQ4 loads each map automatically",
            '"openQ4 map state',
            "bakes openQ4-compatible lightgrid metadata",
        ),
    },
    "src/renderer/draw_arb2.cpp": {
        "required": ("but openD3 keeps ARB2 because the legacy NV20 backend is not shipped",),
        "forbidden": ("but openQ4 keeps ARB2 because the legacy NV20 backend is not shipped",),
    },
    "src/renderer/RenderSystem.cpp": {
        "required": ("but openD3 only ships the ARB2 backend",),
        "forbidden": ("but openQ4 only ships the ARB2 backend",),
    },
    "src/renderer/RenderWorld_load.cpp": {
        "required": ("openD3 will prefer it before the classic proc world",),
        "forbidden": ("openQ4 will prefer it before the classic proc world",),
    },
    "src/renderer/RenderWorld_lightgrid.cpp": {
        "required": ("previous openD3 bake through the runtime light-grid pass",),
        "forbidden": ("previous openQ4 bake through the runtime light-grid pass",),
    },
    "src/sys/posix/posix_main.cpp": {
        "required": (
            '"%s/opend3-%u.lock"',
            "another openD3 instance is already running",
        ),
        "forbidden": (
            '"%s/openq4-%u.lock"',
            "another openQ4 instance is already running",
        ),
    },
    "tools/build/prepare_macos_moltenvk.sh": {
        "required": (
            "above openD3's ${MOLTENVK_MAX_MINOS} deployment target",
            "until openD3's own macos_deployment_target moves off",
        ),
        "forbidden": (
            "above openQ4's ${MOLTENVK_MAX_MINOS} deployment target",
            "until openQ4's own macos_deployment_target moves off",
        ),
    },
}


def main() -> None:
    failures: list[str] = []

    for relative_path, contract in CONTRACTS.items():
        source = (ROOT / relative_path).read_text(encoding="utf-8")
        for expected in contract["required"]:
            if expected not in source:
                failures.append(f"{relative_path}: missing {expected!r}")
        for stale in contract["forbidden"]:
            if stale in source:
                failures.append(f"{relative_path}: stale runtime branding {stale!r}")

    if failures:
        raise SystemExit("Runtime-branding contract failed:\n  - " + "\n  - ".join(failures))

    print("openD3 runtime-branding checks passed")


if __name__ == "__main__":
    main()
