# OpenD3 SDL3 Input Key Matrix Audit (2026-02-20)

This checklist audits SDL3 input parity against the legacy Win32 path for:

- console
- GUI edit fields
- chat
- binds
- numpad
- modifiers

## Method

- Reviewed SDL3 event generation in `src/sys/win32/win_sdl3.cpp`.
- Compared behavior with legacy `WM_KEY*` + `WM_CHAR`/DirectInput paths in:
  - `src/sys/win32/win_wndproc.cpp`
  - `src/sys/win32/win_input.cpp`
- Reviewed common consumer paths in framework/UI subsystems.

## Checklist

| Area | Coverage | Result | Notes |
|---|---|---|---|
| Console input | Toggle key, submit, history, paging, backspace, ctrl shortcuts | Pass (core) | `SE_KEY` + `SE_CHAR` flow aligned for baseline behavior. |
| GUI edit fields | Backspace/delete, cursor movement, enter handling, control chars | Pass (core) | Control-char synthesis behavior is in place for SDL3 path. |
| Chat input | Text entry/editing in GUI chat fields | Pass (ASCII/control) | Same event flow as edit controls. |
| Binds | Key-down bind execution (function keys, mouse/wheel) | Pass (core) | Common key families behave as expected. |
| Numpad | KP enter/arrows/home/end/ins/del/operators | Pass (core) | KP mapping coverage is present in SDL3 path. |
| Modifiers | Ctrl/Shift/Alt/RightAlt behavior | Pass (core) | Locale edge-cases remain for some layouts. |

## Remaining Gaps

1. Non-English key layout parity remains incomplete.
2. Console-toggle localization parity outside default mapping remains incomplete.
3. UTF-8 text payload handling remains byte-oriented at `SE_CHAR` queue points.

## Next Steps

1. Implement layout-aware key translation preserving legacy bind semantics.
2. Make `Sys_GetConsoleKey` layout-aware in SDL3 path.
3. Decode UTF-8 text input before queuing `SE_CHAR` events.
