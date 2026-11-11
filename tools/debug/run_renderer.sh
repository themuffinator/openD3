#!/usr/bin/env bash
# Portable staged-runtime launchers adapted from Emile Belanger's openD3 fork.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
API="${1:?renderer required: gl, gles, or vulkan}"
shift
RUNTIME="${OPEND3_RUNTIME:-$REPO_ROOT/.install}"
case "$(uname -m)" in
    arm64|aarch64) ARCH=arm64 ;;
    x86_64|amd64) ARCH=x64 ;;
    *) echo "Unsupported architecture" >&2; exit 1 ;;
esac
CLIENT="$RUNTIME/openD3-client_$ARCH"
[ -x "$CLIENT" ] || { echo "Missing staged client: $CLIENT" >&2; exit 1; }
ARGS=(+set r_renderApi "$API" +set r_fullscreen 0 +set ui_autoJoin 0
      +set fs_savepath "${OPEND3_SAVEPATH:-$REPO_ROOT/.home}"
      +set logFile 2 +set logFileName "logs/opend3-$API.log")
if [ -n "${OPEND3_BASEPATH:-}" ]; then ARGS+=(+set fs_basepath "$OPEND3_BASEPATH"); fi
case "$API" in
    gl) ARGS+=(+set r_renderer arb2 +set r_glTier auto) ;;
    gles) ARGS+=(+set r_renderer glesd3) ;;
    vulkan) ;;
    *) echo "Unknown renderer: $API" >&2; exit 1 ;;
esac
cd "$RUNTIME"
exec "$CLIENT" "${ARGS[@]}" "$@"
