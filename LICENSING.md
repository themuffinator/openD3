# Licensing

openD3 is free software. Its engine and its game code are both under the GNU
General Public License version 3, and its dependencies keep their own licences.

| Component | Terms |
| --- | --- |
| Engine and engine-authored support code (everything under `src/` outside the game trees and `src/external/`) | [GNU GPL version 3](LICENSE), retained per-file notices and the applicable [Doom 3](LICENSES/DOOM-3-ADDITIONAL-TERMS.txt) or [Doom 3 BFG](LICENSES/DOOM-3-BFG-ADDITIONAL-TERMS.txt) Additional Terms |
| Game library in `src/game/` (Doom 3) and `src/d3xp/` (Resurrection of Evil), including openD3's changes to it | [GNU GPL version 3](LICENSE) with the [Doom 3 Additional Terms](LICENSES/DOOM-3-ADDITIONAL-TERMS.txt), as id Software released it; original notices preserved |
| Third-party dependencies | Their own retained licences; see the [dependency notices](LICENSES/), the individual source trees and the Meson wraps |
| Retail Doom 3 content | Not included or relicensed; users supply their own copy |

Because both sides are GPLv3, openD3 has no licence boundary between engine and
game code. This is different from its sibling projects.

The engine is derived from [openQ4](https://github.com/themuffinator/openQ4),
whose engine history is merged into this repository's history, and it carries
engine work adapted from [openPREY](https://github.com/themuffinator/openPREY).
Both projects' game libraries are derived from SDKs under their own licence
agreements. That game code (`src/game/` and `src/mpgame/` in openQ4;
`src/game/`, `src/Prey/` and `src/preyengine/` in openPREY) and those SDK
agreements are deliberately not part of openD3's tree, and must not be copied
into it. Older commits reachable through the merged openQ4 history still
contain openQ4's files under their original terms.

The [game import record](docs/dev/game-source-provenance.md) identifies where
the game library came from. This overview is a guide to the notices in the
tree, not a substitute for them or for legal advice.
