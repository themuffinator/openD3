# Getting Started with openD3

> **Development documentation:** openD3 has no release yet. This page follows the current source tree. See [release status](release-status.md) for what has been run and what has not.

This guide is for players who want to get openD3 running against their own copy of Doom 3.

## What You Need

- A legitimate copy of **Doom 3** (2004), patched to version 1.3.1. The Steam release is the one openD3 has been run against.
- A build of openD3. There are no downloads yet, so you build it yourself with [BUILDING.md](../../BUILDING.md). Only the Windows x64 build has been tried.
- About 1.5 GB of disk space for Doom 3's `base/` files, plus room for the build.

> [!NOTE]
> openD3 does not include Doom 3 assets. It uses the original retail game files from your existing installation. Doom 3: BFG Edition's data is a different format and is not supported.

## System Requirements

Nobody has measured openD3's requirements yet. This table lists what the build needs to start, not what it takes to run well.

| Component | Needed |
|---|---|
| CPU | 64-bit x64 |
| Operating system | Windows x64, the only platform built and run so far |
| Graphics | An OpenGL driver with ARB vertex and fragment program support. The optional Vulkan renderer needs a Vulkan 1.3 driver |
| Storage | About 1.5 GB for Doom 3's `base/` files, plus the openD3 build |
| Assets | Doom 3's retail packs `pak000.pk4`–`pak004.pk4` at version 1.3.1, left unmodified so startup validation can confirm them |
| Audio | A working audio output. The OpenAL Soft runtime (`OpenAL32.dll`) is staged beside the executables |

No memory or performance minimums have been measured.

## Recommended Install Flow

1. Install **Doom 3**.
2. Build openD3 and stage it by following [BUILDING.md](../../BUILDING.md). The staged package lands in `.install/` in the repository.
3. Launch the client from `.install/`:

   ```text
   openD3-client_x64 +set ui_retained 0
   ```

   Add `+set r_fullscreen 0` to start in a window.

openD3 will try to find your Doom 3 install automatically. It looks in your Steam libraries, GOG folders, the Windows registry and the usual install folders.

`ui_retained 0` selects Doom 3's own menus. openD3 has no pages for the newer interface inherited from openQ4, so every launch needs it; see [Client Settings](client-settings.md#the-interface).

## Folder Layout Options

### Recommended

- Leave retail Doom 3 in its original Steam or GOG folder.
- Keep openD3 in its own folder: the staged `.install/`, or a copy of it.
- Let openD3 detect the retail `base/` assets automatically.

### Manual

If openD3 does not find the game, or you keep it somewhere unusual, tell it where the game is as described under [If Auto-Detection Fails](#if-auto-detection-fails).

> [!IMPORTANT]
> Do **not** copy retail PK4 files into `baseod3/`. That folder is for openD3's own modules and content, and startup reports retail packs it finds there.

## Updating openD3

Until there is a release, updating means building again:

1. Update your checkout.
2. Compile and stage as in [BUILDING.md](../../BUILDING.md).

Always stage the whole package. The executables, the renderer modules and the game modules check each other's versions when they load, and a mismatched set is refused.

Do not expect saved games to survive an update. A save loads only in the build that wrote it; see [Campaigns](campaigns.md#saves-and-switching).

## Platform Notes

### Windows

- This is the only platform openD3 has been built and run on.
- Your settings, saves, screenshots and logs go under `%LOCALAPPDATA%\openD3\baseod3\`. Add `+set fs_savepath "<folder>"` to keep them somewhere else, which is useful for a test run that should not touch your normal profile.
- If openD3 crashes, check the `crashes/` folder beside the executable for log and dump files.

### Linux, Steam Deck, macOS and Android

The openQ4 engine openD3 is built on supports these platforms, but openD3 has not been built or run on any of them. If you try, the [rebase record](../dev/doom3-rebase.md) is the place to start, and a report of what happened is welcome.

## If Auto-Detection Fails

Point openD3 at the **Doom 3 root folder** that contains `base/`.

Example:

```text
openD3-client_x64 +set ui_retained 0 +set fs_basepath "C:\path\to\Doom 3"
```

Do not point it directly at `base/` or `baseod3/`.

You can also set the `OPEND3_DOOM3_PATH` environment variable to the same folder.

For the other search paths, pack validation and file layout details, see [TECHNICAL.md](../../TECHNICAL.md).

## Next Steps

- Want to know what works today? See [Release Status](release-status.md).
- Want to change the renderer or the window? See the [Client Settings Guide](client-settings.md).
- Want to start a level? See [Campaigns](campaigns.md).
- Want to host a server? See the [Server Setup Guide](server-setup.md).
