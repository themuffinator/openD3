# Game source provenance

The Doom 3 game library lives in this repository: `src/game/` is the base game
and `src/d3xp/` is Resurrection of Evil. Both are id Software's Doom 3 game
code as released under the GNU GPL version 3, the same licence as the engine.
[LICENSING.md](../../LICENSING.md) describes each component's terms.

## Import

- Source: [openD3-GameLibs at `c450f9c`](https://github.com/themuffinator/openD3-GameLibs/tree/c450f9c),
  the companion repository openD3 used before the game library moved in-tree.
- `src/game/` and `src/d3xp/` were imported at their existing paths without
  source edits, so their relative includes resolve against this repository's
  engine headers.
- The companion repository's copies of the engine sources (`src/idlib/`,
  `src/framework/`, `src/renderer/` and the rest), its Visual Studio projects
  and its bundled curl and OpenAL trees were never compiled by openD3 and are
  not imported. They remain available in the imported history.
- The companion history is a merge parent of the import commit, so
  `git log --follow` traces a game file back to its import there.

The companion repository is historical. Game-library changes are made here.

## State at import

- `src/game/` carried a 64-bit and engine-ABI port relative to id's GPL
  release: 28 files, about 1,400 changed lines.
- `src/d3xp/` was id's GPL release unchanged.

openD3 then applied the base game's port to `src/d3xp/` by three-way merge and
made the further changes the current engine needs. openD3's commit history
identifies every change after the import; [doom3-rebase.md](doom3-rebase.md)
summarises them.

## Licence boundary

There is none between engine and game: both are GPLv3 with the Doom 3
Additional Terms retained in the files that carry them. This differs from
openQ4 and openPREY, whose game trees are SDK-licensed. Code from those game
trees must not be copied into openD3.

## Content boundary

No retail Doom 3 game data is committed or distributed. The engine reads the
user's own copy.
