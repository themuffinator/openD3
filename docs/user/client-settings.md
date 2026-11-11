# Client Settings Guide

> **Development documentation:** openD3 has no release yet. This page follows the current source tree. See [release status](release-status.md) for what has been run and what has not.

This guide covers the handful of settings you need to run openD3 today, and where the rest will come from.

## Best Places to Start

For now, most of what you will change is on the command line:

- **The interface**: every launch needs `+set ui_retained 0`
- **The window**: windowed or fullscreen
- **The renderer**: OpenGL or Vulkan
- **Logging**: a log file to attach when something goes wrong

Doom 3's own Options menu is there too, reached from the main menu. It has not been gone through page by page on openD3, and at least one of its entries refers to a setting the engine no longer has, so expect some options to do nothing.

## Recommended First Checks

- Launch in a window the first time: `+set r_fullscreen 0`
- Leave the renderer on OpenGL unless you want to try Vulkan
- Turn on the log file before reporting a problem

## Launch Options

Put these after the executable name. Each `+set` takes a name and a value.

| Option | What it does |
|---|---|
| `+set ui_retained 0` | Use Doom 3's own menus and HUD. Always needed; see [The Interface](#the-interface) |
| `+set r_fullscreen 0` | Start in a window. `1` starts fullscreen |
| `+set r_renderApi vulkan` | Use the Vulkan renderer. `gl`, the default, is OpenGL. Read at startup only |
| `+set fs_basepath "<folder>"` | The Doom 3 folder that contains `base/`, if openD3 does not find it by itself |
| `+set fs_savepath "<folder>"` | Keep settings, saves and logs in this folder instead of the default |
| `+set fs_game d3xp` | Select Resurrection of Evil. Not playable yet; see [Campaigns](campaigns.md#resurrection-of-evil) |
| `+set logFile 2 +set logFileName logs/opend3.log` | Write a log under your save folder |
| `+map game/mars_city1` | Start a map directly |

A complete example:

```text
openD3-client_x64 +set r_fullscreen 0 +set ui_retained 0 +set logFile 2 +set logFileName logs/opend3.log
```

`r_mode`, `r_customWidth`, `r_customHeight` and `r_screen` choose the display mode and monitor. They come from openQ4 and have not been checked on openD3.

## The Renderer

openD3 has two renderers, each in its own module beside the executable:

- **OpenGL** (`r_renderApi gl`) is the default and the one most of the testing has used.
- **Vulkan** (`r_renderApi vulkan`) has loaded and drawn the first campaign map. It needs a Vulkan 1.3 driver.

The choice is read when openD3 starts, so set it on the command line or restart after changing it.

## The Interface

openD3 uses Doom 3's original menus, HUD and in-world screens. The engine also carries the newer interface openQ4 built, switched by `ui_retained`, but that interface has no Doom 3 pages. Launch with `+set ui_retained 0` every time.

On a widescreen or tall display the menus, HUD and loading screens use the whole screen: the HUD sits in the corners and the menu frame reaches the edges, without stretching the artwork. The PDA keeps its 4:3 screen, with a softened view of the game beside it.

| Setting | Default | What it does |
| --- | --- | --- |
| `ui_widescreenLayouts` | `1` | `0` draws the stock menus and HUD as a centred 4:3 picture instead. Takes effect when the menu or map next loads |
| `ui_aspectCorrection` | `1` | `0` stretches all 2D interface to the screen shape instead of keeping its proportions |

## Shadows

Doom 3's stencil shadows are the default. Shadow maps replace them light by light: soft edges, and the same shapes as the stencil shadows. Both draw your own shadow: your body, head and held weapon throw a shadow you can see in first person, in single player and in multiplayer.

| Setting | Default | What it does |
| --- | --- | --- |
| `g_showPlayerShadow` | `1` | `0` hides your own shadow from your view in single player, as Doom 3 did. Other players always see it, and multiplayer always draws it |
| `r_useShadowMap` | `0` | `1` draws shadow maps instead of stencil shadows. A light the shadow-map path cannot take that frame keeps its stencil shadows |
| `r_shadowMapPointLights` | `1` | `0` keeps stencil shadows for point lights, which are most of Doom 3's lights, and shadow-maps only projected lights |

The performance presets choose these for you. **Balanced** and below use stencil shadows only (**Minimum** and **Low Power** draw no shadows). **Enhanced** shadow-maps projected lights only and leaves point lights on stencil shadows. **Quality**, **Ultra** and **Maximum** shadow-map every light.

These settings are saved like any other, so a settings file written by an earlier build keeps its old values: `g_showPlayerShadow 0`, and Prey's specular model in `r_correctspecular 1` and `r_normalizebumpmap 1`. Set them to `1`, `0` and `0` once for your shadow and Doom 3's lighting.

## Where Settings Are Saved

Settings are written to `openD3Config.cfg` in your save folder, together with saves, screenshots and logs:

- On Windows the save folder is `%LOCALAPPDATA%\openD3\baseod3\`.
- `+set fs_savepath "<folder>"` moves it; the files then go under `<folder>\baseod3\`.

## Which Guide Covers What?

- [Getting Started](getting-started.md) - what you need, first launch and folder layout
- [Campaigns](campaigns.md) - starting levels, Resurrection of Evil and saves
- [Server Setup](server-setup.md) - starting a dedicated server
- [Release Status](release-status.md) - what has been run and what has not

## Settings Inherited from openQ4

The engine brings openQ4's display, input and rendering features with it: performance presets, shadow maps, light grids, post-processing, controller support and more. They are described in [openQ4's guides](https://github.com/themuffinator/openQ4/tree/main/docs/user). Apart from shadow maps (see "Shadows" above), none has been checked with Doom 3 yet, and those guides describe menus openD3 does not have, so use their console variable names rather than their menu paths.

If you want deeper technical details or console-level configuration, see [TECHNICAL.md](../../TECHNICAL.md).
