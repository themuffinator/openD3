# Wide and Tall Screen Layout

Doom 3's menus and HUDs are authored on a 640x480 canvas. With
`ui_aspectCorrection 1` (the default) the engine keeps that canvas undistorted
and centred, and on any other shape of screen it widens or heightens the
drawable area beyond it: the *expansion*, `(screen aspect / 4:3 - 1) * 320`
units on each side of a wide screen (106.7 at 16:9, 248 at 21:9) or the same
above and below a tall one. The stock GUIs know nothing of it, so by
themselves they draw a 4:3 picture with the expansion empty.

openD3 gives them a layout for every shape of screen without shipping copies of
id's GUI scripts. **Layout patches** add window properties to a stock GUI as it
is parsed, and a few window properties say how a window behaves in the
expansion.

## Layout patches

Patch files are `guis/layouts/*.layout`, in `content/baseod3/pak0/guis/layouts/`
(packed into `baseod3/pak0.pk4`). They hold window names and properties only:
no retail script text.

```
gui "guis/hud.gui" {
	window Border, BgL, Lines1_?, ammovalue*, MiddleLeftAngle#2 {
		screenalignx left
		screenaligny bottom
	}
}
```

- `gui` takes the GUI's path; `*` and `?` match, without regard to case
  (`guis/map/*.gui` is every loading screen).
- `window` takes window names with the same wildcards, matched against the
  whole name. `name#N` is the Nth window the GUI defines under that name, for
  the scripts that reuse a name (`mainmenu.gui` has two `MiddleLeftAngle`).
- The block's properties are read by the GUI parser, after the window's own
  definition and before its expressions are first evaluated, exactly as if the
  window's definition had ended with them. Any property a window accepts can be
  set, including an expression (`rect`), but the layouts use the expansion
  properties below. Every matching block applies, in file order, then in the
  order of the files' names.
- A GUI that a mod ships itself (a copy in a mod's `fs_game` or
  `fs_game_base` directory, `idLegacyHudLayout::ModOwns`) takes no patch: the
  mod's GUI is its own. `ui_widescreenLayouts 0` turns patches off; it takes
  effect as each GUI loads (`reloadGuis`, or a map change for the HUDs).
- `ui_widescreenLayoutsDebug 1` logs every window a patch changes and warns
  about each pattern that matched no window; `2` also logs every window as it
  parses. Set it before the GUI loads, or run `reloadGuis`, which also rereads
  the patch files.

The loader is `src/ui/GuiLayoutPatch.cpp`; `idWindow::Parse` applies the GUI's
set (`idUserInterfaceLocal::LayoutPatches`).

## Expansion properties

All of these apply only where the window's parent is the desktop or is itself
centred on that axis, and only while the screen has an expansion on that axis
(nothing changes on a 4:3 screen or with `ui_aspectCorrection 0`).

| Property | Values | Effect |
| --- | --- | --- |
| `screenalignx`, `screenaligny` | `left`/`middle`/`right`, `top`/`middle`/`bottom` | Moves the window (and its children) by the expansion toward that screen edge. Inherited from openQ4 |
| `screenstretchx`, `screenstretchy` | `none`, `fill`, `left`/`top`, `right`/`bottom` | Carries the window's edges out with the expansion: both (`fill`), or only the leading or trailing one. Its children keep their authored places. A negative extent (a mirrored material) still covers `x..x+|w|`. A window collapsed to zero on the axis (a closed dialog) stays collapsed |
| `canvasclip` | `none`, `x`, `y`, `both` | Clips the window and its children to the authored canvas on that axis, also on a `noclip` window. A panel parked just beyond the canvas edge then stays hidden in the expansion. On the desktop it stops the desktop's clip widening |
| `softfocus` | virtual units of the canvas height | On a desktop: before the GUI draws, blurs what is already on screen (the retained interface's REN-016 Gaussian passes, `RetainedUI_SoftenScreen`) |
| `softfocussaturation`, `softfocusdim` | 0 to 1 | Saturation of the blur, and a black dim over it. On GLES, which has no soft focus, only the dim draws |

`softfocus` draws only where the screen shows more than the canvas.

## The rules the stock layouts follow

- **Layers fill.** Backgrounds, scan lines, fades, the dimming behind dialogs
  and the full-canvas containers that clip their children stretch over the
  whole screen. A picture keeps its proportions (`matcover 1` crops it).
- **Docked pieces go to the edge, bars between them stretch.** Doom 3's menu
  frames are built from pieces touching the canvas edges. A piece docked to an
  edge aligns with it; the bar joining it to the centre stretches on that side,
  so the frame stays connected at any width.
- **Content stays centred.** Panels, dialogs, lists and the crosshair keep
  their authored place.
- **Parked panels stay hidden.** Retail scripts slide panels in from just
  beyond the canvas. On the axis they slide along, a container keeps its
  authored extent and clips to the canvas, so nothing waits in view in the
  expansion. The main menu therefore centres vertically on a tall screen.
- **The PDA keeps 4:3**, like the screen of the PDA model in the player's
  hand. While it is open the game also renders the view
  (`idPlayerView::SingleView`, both game trees), and the PDA softens and dims
  it beside the canvas.

## What each layout covers

| File | GUIs | Layout |
| --- | --- | --- |
| `hud.layout` | `guis/hud.gui` | Health, armour, stamina, air and the pickup and download notices at the bottom-left; ammunition, the weapon strip and the soul cube at the bottom-right; objective updates from the right, inventory items and tips from the left |
| `mphud.layout` | `guis/mphud.gui`, `chat.gui`, `mpmsgmode.gui`, `spectate.gui` | The same corners for the multiplayer HUD, the clock and scores at the top-right, chat and votes on the left |
| `mainmenu.layout` | `guis/mainmenu.gui` (the expansion's extra dialogs are named too, unverified) | Frame and bars to the edges; Options, New Game and multiplayer lists docked to their sides; credits and multiplayer frames across the width; dialogs dim the whole screen |
| `pda.layout` | `guis/pda.gui` | 4:3 over the softened view |
| `loading.layout` | `guis/map/*.gui` | The level picture fills (cropped), the bars span the width, the title and meter keep to the left |
| `screens.layout` | `msg.gui`, `netmenu.gui`, `restart.gui`, `gameover.gui`, `credits.gui`, `intro.gui` | Full-screen layers and dims fill; the boxes, choices and films stay centred |

Not patched, because they need nothing: `scoreboard.gui`, `mpmain.gui` (floating
panels over the game), `cursor.gui` (the crosshair), `takenotes*.gui`, and the
in-world GUIs, which are never aspect-corrected. Cinematics keep their own
framing.

## Writing a layout

1. Extract the GUI from the retail packs (they are zips) and list its windows
   with their absolute rectangles; keep the extraction under `.tmp/`.
2. Group the windows by the edge they belong to. Check the GUI's scripts for
   `transition "<window>::rect"`: a window that slides must stay in one group
   for the whole slide, and the container it slides in must not widen on that
   axis.
3. Run with `ui_widescreenLayoutsDebug 1` and check every unmatched pattern.
   A block shared by variant GUIs names windows only some of them have (the
   loading screens' `Text`, `bgBlackTopFill`; the expansion's extra dialogs).
4. Capture the GUI at 4:3, 16:9, 21:9 and a tall shape. `testGUI <path>` shows
   one directly; `opend3_guiAction <window>` clicks through a menu.
