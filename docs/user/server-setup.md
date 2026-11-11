# Server Setup Guide

> **Development documentation:** openD3 has no release yet. This page follows the current source tree. See [release status](release-status.md) for what has been run and what has not.

> **Startup only.** A dedicated server has been started and has loaded a map.
> No client has joined an openD3 server yet, so nothing here says that a match
> can be played.

This guide covers starting an openD3 dedicated server.

## What You Need

- A staged openD3 build; see [Getting Started](getting-started.md)
- Access to the original Doom 3 retail assets on the same machine
- The `openD3-ded_x64` executable from that build

## Quick Start

```text
openD3-ded_x64 +set si_gameType deathmatch +set si_map game/mp/d3dm1 +spawnServer
```

The server finds Doom 3 the same way the client does. Add `+set fs_basepath "<Doom 3 folder>"` if it does not. It opens a console window, loads the map and reports the port it is listening on:

```text
Server spawned on port 28004.
```

Type `quit` in the console to stop it.

## Maps and Game Types

Doom 3 ships five multiplayer maps:

| Map | Name |
| --- | --- |
| `game/mp/d3dm1` | Tomiko Reactor |
| `game/mp/d3dm2` | Delta Lab |
| `game/mp/d3dm3` | Frag Chamber |
| `game/mp/d3dm4` | The Edge |
| `game/mp/d3dm5` | Lights Out |

`si_gameType` takes Doom 3's game types: `deathmatch`, `Team DM`, `Tourney` and `Last Man`. Quote the ones with a space:

```text
openD3-ded_x64 +set si_gameType "Team DM" +set si_map game/mp/d3dm2 +spawnServer
```

Only `deathmatch` on `d3dm1` has been started.

## Ports

The server listens on UDP port 28004 unless `net_port` says otherwise. If players are to reach it from outside your network, that port has to be allowed through your firewall and forwarded by your router. None of this has been tried with openD3.

## Common Server Variables

| Variable | Purpose |
| --- | --- |
| `si_map` | The map to load, for example `game/mp/d3dm1` |
| `si_gameType` | `deathmatch`, `Team DM`, `Tourney` or `Last Man` |
| `si_maxPlayers` | Player limit, 1 to 4 |
| `net_port` | The port to listen on |

## Notes

- Use the same openD3 build on the server and on every client. Retail Doom 3 clients are not expected to be able to join.
- Capture the Flag belongs to Resurrection of Evil, which is [not playable yet](campaigns.md#resurrection-of-evil).
- The bots, multi-view demos and repeater described in openQ4's guides need game code Doom 3 does not have. They are switched off in openD3.
