#!/usr/bin/env python3
"""Generate .vscode/launch.json, the VS Code launch configurations.

The JSON is generated: edit the tables here and rerun this script.
tools/tests/vscode_fast_build.py fails while launch.json holds anything else
(formatting aside, so reformatting it in the editor is harmless).

Every configuration runs the client that the VS Code build task stages into
.install, with .home as the savepath, and pins the archived CVars that decide
what a launch exercises, so a value left in .home/<game>/openD3Config.cfg
cannot change it: r_renderApi (each launch is a GL and Vulkan pair),
ui_retained 0 because Doom 3 runs its stock GUIs (the retained RmlUi
interface inherited from openD3 has no Doom 3 documents) and r_fullscreen 0.

fs_basepath is left unset: the engine finds the installed Doom 3 through
Steam or GOG, or OPEND3_DOOM3_PATH, so no machine's path is baked in.

Each group gets a separator in the Run and Debug list. VS Code orders the
groups by name, so every name starts with its position.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LAUNCH_JSON = ROOT / ".vscode" / "launch.json"

GL = ("GL", "gl")
VULKAN = ("Vulkan", "vulkan")
RENDERERS = (GL, VULKAN)

# Set first on every launch. A launch's own value replaces one in place.
COMMON_CVARS = (
    ("logFile", "2"),
    ("logFileName", "logs/opend3.log"),
    ("developer", "1"),
    ("r_fullscreen", "0"),
    ("fs_savepath", "${workspaceFolder}\\.home"),
    ("fs_devpath", "${workspaceFolder}\\.install"),
)
SINGLE_PLAYER_CVARS = (
    ("si_gameType", "singleplayer"),
    ("com_skipLoadingContinue", "1"),
)
# A listen server; si_gameType and si_map come from the launch.
MULTIPLAYER_CVARS = (
    ("net_serverDedicated", "0"),
    ("net_serverAllowServerMod", "1"),
    ("si_pure", "0"),
    ("net_allowCheats", "1"),
)


@dataclass(frozen=True)
class Launch:
    """One launch, written as one configuration per renderer."""

    name: str
    game_type: str = "singleplayer"
    game: str = "baseod3"
    command: tuple[str, ...] = ()
    cvars: tuple[tuple[str, str], ...] = ()
    retained: bool = False
    renderers: tuple[tuple[str, str], ...] = RENDERERS

    @property
    def multiplayer(self) -> bool:
        return self.game_type != "singleplayer"


def campaign(maps: tuple[tuple[str, str], ...], game: str = "baseod3", prefix: str = "") -> tuple[Launch, ...]:
    # A second word in the label is the visit for maps played twice.
    launches = []
    for label, title in maps:
        map_name, *visit = label.split()
        launches.append(Launch(f"{prefix}{label} '{title}'", game=game, command=("+map", f"game/{map_name}", *visit)))
    return tuple(launches)


def servers(
    maps: tuple[tuple[str, str], ...], game_type: str, game: str = "baseod3", prefix: str = ""
) -> tuple[Launch, ...]:
    return tuple(
        Launch(
            f"{prefix}{map_name} '{title}' ({game_type})",
            game_type,
            game,
            ("+spawnServer",),
            cvars=(("si_map", f"game/mp/{map_name}"),),
        )
        for map_name, title in maps
    )


DOOM3_CAMPAIGN = (
    ("mars_city1", "MARS CITY"),
    ("mc_underground", "MARS CITY UNDERGROUND"),
    ("mars_city2", "MARS CITY (RETURN)"),
    ("admin", "ADMINISTRATION"),
    ("alphalabs1", "ALPHA LABS SECTOR 1"),
    ("alphalabs2", "ALPHA LABS SECTOR 2"),
    ("alphalabs3", "ALPHA LABS SECTOR 3"),
    ("alphalabs4", "ALPHA LABS SECTOR 4"),
    ("enpro", "ENPRO PLANT"),
    ("commoutside", "COMMUNICATIONS TRANSFER"),
    ("communications", "COMMUNICATIONS"),
    ("recycling1", "MONORAIL SKYBRIDGE"),
    ("recycling2", "RECYCLING SECTOR 2"),
    ("monorail", "MONORAIL"),
    ("delta1", "DELTA LABS LEVEL 1"),
    ("delta2a", "DELTA LABS LEVEL 2A"),
    ("delta2b", "DELTA LABS LEVEL 2B"),
    ("delta3", "DELTA LABS LEVEL 3"),
    ("delta4", "DELTA LABS LEVEL 4"),
    ("hell1", "HELL"),
    ("delta5", "DELTA COMPLEX"),
    ("cpu", "CPU COMPLEX"),
    ("cpuboss", "CENTRAL PROCESSING"),
    ("site3", "SITE 3"),
    ("caverns1", "CAVERNS AREA 1"),
    ("caverns2", "CAVERNS AREA 2"),
    ("hellhole", "PRIMARY EXCAVATION"),
)

DOOM3_CAMPAIGN_TESTS = (
    Launch(
        "mars_city1 'MARS CITY' - Load and Quit",
        command=("+map", "game/mars_city1", "+wait", "240", "+quit"),
    ),
)

DEATHMATCH = (
    ("d3dm1", "TOMIKO REACTOR"),
    ("d3dm2", "DELTA LAB"),
    ("d3dm3", "FRAG CHAMBER"),
    ("d3dm4", "THE EDGE"),
    ("d3dm5", "LIGHTS OUT"),
)

GROUPS = (
    ("01 Main menu", (
        Launch("Main menu"),
        Launch("Main menu - Validation Layers", cvars=(("r_vkValidation", "1"),), renderers=(VULKAN,)),
    )),
    ("02 Doom 3 campaign", campaign(DOOM3_CAMPAIGN)),
    ("03 Doom 3 campaign tests", DOOM3_CAMPAIGN_TESTS),
    ("04 Multiplayer: Deathmatch", servers(DEATHMATCH, "deathmatch")),
    ("05 Multiplayer: Team Deathmatch", servers(DEATHMATCH, "Team DM")),
    ("06 Multiplayer: Tourney", servers(DEATHMATCH, "Tourney")),
    ("07 Multiplayer: Last Man Standing", servers(DEATHMATCH, "Last Man")),
)


def configuration(launch: Launch, renderer: tuple[str, str], group: str, order: int) -> dict[str, object]:
    renderer_name, render_api = renderer
    cvars = dict(COMMON_CVARS)
    cvars["fs_game"] = launch.game
    # r_renderApi has to precede the map command: the module loads at startup.
    cvars["r_renderApi"] = render_api
    cvars["ui_retained"] = "1" if launch.retained else "0"
    if launch.multiplayer:
        cvars["si_gameType"] = launch.game_type
        cvars.update(MULTIPLAYER_CVARS)
    else:
        cvars.update(SINGLE_PLAYER_CVARS)
    cvars.update(launch.cvars)
    args = [token for key, value in cvars.items() for token in ("+set", key, value)]
    mode = "MP" if launch.multiplayer else "SP"
    return {
        "name": f"({mode}) {launch.name} — {renderer_name}",
        "type": "cppvsdbg",
        "request": "launch",
        "presentation": {"group": group, "order": order},
        "program": "${workspaceFolder}\\.install\\openD3-client_x64.exe",
        "args": args + list(launch.command),
        "cwd": "${workspaceFolder}\\.install",
        "console": "integratedTerminal",
    }


def build() -> dict[str, object]:
    configurations = []
    for group, launches in GROUPS:
        order = 0
        for launch in launches:
            for renderer in launch.renderers:
                order += 1
                configurations.append(configuration(launch, renderer, group, order))
    names = [config["name"] for config in configurations]
    duplicates = sorted({name for name in names if names.count(name) > 1})
    if duplicates:
        raise ValueError("duplicate launch configuration names: " + ", ".join(duplicates))
    return {"version": "0.2.0", "configurations": configurations}


def argument_rows(args: list[str]) -> list[list[str]]:
    # One +set per row; any other command keeps its arguments on its row.
    rows: list[list[str]] = []
    index = 0
    while index < len(args):
        if args[index] in ("+set", "+seta"):
            rows.append(args[index:index + 3])
            index += 3
            continue
        row = [args[index]]
        index += 1
        while index < len(args) and not args[index].startswith("+"):
            row.append(args[index])
            index += 1
        rows.append(row)
    return rows


def render(launch: dict[str, object]) -> str:
    def value(item: object) -> str:
        return json.dumps(item, ensure_ascii=False)

    blocks = []
    for config in launch["configurations"]:
        members = []
        for key, item in config.items():
            if key == "args":
                rows = ",\n".join(" " * 16 + ", ".join(value(token) for token in row) for row in argument_rows(item))
                text = "[\n" + rows + "\n" + " " * 12 + "]"
            else:
                text = value(item)
            members.append(" " * 12 + value(key) + ": " + text)
        blocks.append(" " * 8 + "{\n" + ",\n".join(members) + "\n" + " " * 8 + "}")
    text = "{\n    \"version\": " + value(launch["version"]) + ",\n    \"configurations\": [\n"
    text += ",\n".join(blocks) + "\n    ]\n}\n"
    if json.loads(text) != launch:
        raise AssertionError("rendered launch.json does not round-trip")
    return text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="exit 1 if the file differs from the generated configurations")
    parser.add_argument("--output", type=Path, default=LAUNCH_JSON, help="launch.json to write or check")
    options = parser.parse_args(argv)
    launch = build()
    count = len(launch["configurations"])
    if options.check:
        current = json.loads(options.output.read_text(encoding="utf-8-sig"))
        if current != launch:
            print(f"{options.output} is stale; run python tools/debug/generate_vscode_launch.py", file=sys.stderr)
            return 1
        print(f"{options.output}: {count} configurations, up to date")
        return 0
    options.output.write_text(render(launch), encoding="utf-8")
    print(f"Wrote {count} configurations in {len(GROUPS)} groups to {options.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
