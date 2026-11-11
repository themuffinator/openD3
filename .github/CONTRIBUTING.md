# Contributing to openD3

Thank you for your interest in openD3, an open-source engine and game-code
replacement for Doom 3. Bug reports, compatibility reports, testing feedback,
documentation improvements and code contributions are all welcome.

openD3 is in early development and has no release yet. The
[rebase record](../docs/dev/doom3-rebase.md) says what works and what is open;
please read it before reporting something as broken.

## Code of Conduct

This project is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By
participating, you are expected to uphold it.

## Reporting bugs

Search the [existing issues](https://github.com/themuffinator/openD3/issues)
first. Then include as much of the following as you can:

- The commit you built.
- Your operating system, CPU architecture, GPU and driver version.
- Which Doom 3 release you have (Steam, GOG, retail discs) and its patch level.
- Clear steps to reproduce, what you expected and what happened.
- The log: launch with `+set logFile 2 +set logFileName logs/opend3.log` and
  attach `<fs_savepath>/baseod3/logs/opend3.log`.
- For crashes on Windows, the log and minidump from the `crashes/` folder beside
  the executable.

Confirm that a compatibility problem reproduces with the original retail packs,
and say whether it affects single-player, multiplayer, the dedicated server or
one particular map.

## Contributing code

1. Fork the repository and create a topic branch.
2. Read [AGENTS.md](../AGENTS.md): it holds the project rules, including how
   openD3 stays close to its upstream engine, openQ4.
3. Build and stage with [BUILDING.md](../BUILDING.md).
4. Run the debug loop in `AGENTS.md` and enter gameplay on a map your change
   affects. Main-menu startup alone is not validation.
5. Check the log for new warnings or errors.
6. Update the documentation your change affects, and the rebase record if it
   changes what works or what is open.
7. Open a pull request that references any related issue.

### Where things go

- **Engine code** lives under `src/`. Engine changes that are not specific to
  Doom 3 are better made upstream in
  [openQ4](https://github.com/themuffinator/openQ4), where openD3 will receive
  them by merge.
- **Game code** lives in `src/game/` (Doom 3) and `src/d3xp/` (Resurrection of
  Evil). A fix that applies to both goes into both.
- **Runtime content** openD3 authors lives under `content/baseod3/pak0/`.
  Prefer fixing the engine, game, parser or loader over shipping replacement
  content.

### Style

- Match the style of the file you are editing.
- Prefer SDL3 abstractions over new platform-specific code in shared paths.
- Keep the project name written openD3.

## Licensing

openD3's engine and game code are both under the
[GNU General Public License v3.0](../LICENSE); see
[LICENSING.md](../LICENSING.md). Contributions are accepted under the same
terms. Do not contribute code copied from SDK-licensed game code, including the
game trees of openQ4 and openPREY. Doom 3's assets remain the property of their
rights holders.

## Getting help

- [Discord](https://discord.gg/T32mFejwR4) for informal questions.
- The [issue tracker](https://github.com/themuffinator/openD3/issues) for bug
  reports and feature requests.
- The [website](https://www.darkmatter-quake.com) for project news.
