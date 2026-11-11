#!/usr/bin/env bash
# Portable adaptation of Emile Belanger's engine-render-target capture harness.
# Usage: OPEND3_BASEPATH=/path/to/Quake4 render_shot.sh arb2|glesd3|vulkan [--mode mp ...]
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
case "${1:-}" in
    arb2) API=gl ;;
    glesd3) API=gles ;;
    vulkan) API=vk ;;
    *) echo "usage: $0 arb2|glesd3|vulkan [smoke options]" >&2; exit 2 ;;
esac
shift
exec python3 "$REPO_ROOT/tools/debug/render_smoke.py" \
    --runtime "${OPEND3_RUNTIME:-$REPO_ROOT/.install}" \
    --basepath "${OPEND3_BASEPATH:?set OPEND3_BASEPATH to the retail Quake 4 installation}" \
    --render-api "$API" "$@"
