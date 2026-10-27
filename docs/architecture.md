# Architecture

This page explains how the game is built and why.

## The core idea: the engine rules, the model narrates

Language models write vivid prose, but they are unreliable at arithmetic, at remembering state, and at keeping to rules. So the game splits the work:

- The **engine** (`core/`, `models/`, `content/`) owns every fact: HP, positions, dice, XP, quests and time. It is deterministic for a given seed.
- The **narrator** (`core/narrator.py`, `core/openai_narrator.py`) only writes text. It can *suggest* two things, and the engine validates both:
  - a `CheckRequest(skill, dc)`: the skill must exist, and the DC is clamped to 5–25.
  - a disposition shift for an NPC, clamped to ±10.

A model can't make you rich, teleport you or skip a fight. At worst it writes a dull sentence.

## Request flow

```text
input ─► commands.parse ─► GameManager.handle ─► handler
                                                  │
                    ┌─────────────────────────────┼───────────────────────────┐
                    ▼                             ▼                           ▼
           Encounter (combat)            world/quests/inventory         Narrator
           attacks, features             state changes                  text only
                    └──────────────► list[str] lines ◄────────────────────────┘
                                             │
                                             ▼
                                     ui.Screen.show
                         (header · hero · paths/enemies · story · hints)
```

`GameManager.handle` returns lines and never prints. This keeps the engine testable: tests call `handle("attack")` and assert on the returned lines.

## Modules

| Module | Responsibility |
|---|---|
| `content/` | Frozen data tables: rules constants, races, classes, features, weapons, monsters, items, places, names. No logic beyond small formulas. |
| `models/` | Mutable dataclasses (`Character`, `Monster`, `NPC`, `Quest`, `Location`, `WorldState`) with `to_dict` / `from_dict`. |
| `core/commands.py` | Turns text into a `Command(verb, args, raw)`. Unknown verbs become `do`, a free-form action. |
| `core/game_manager.py` | Dispatches commands, coordinates exploration, quests, rest, shopping, saves and the combat lifecycle. |
| `core/combat_system.py` | `Encounter`: initiative order, player actions, automatic monster turns, and end-of-combat detection. |
| `core/attacks.py` | One attack resolution (`resolve_attack`), shared by weapon attacks, monster attacks and Cunning Strike. |
| `core/class_features.py` | Feature rules and the `FeatureUnavailable` error. |
| `core/world_generator.py` | Builds the location graph and places NPCs. |
| `core/quests.py` | Creates quests from world facts and completes them on matching events. |
| `core/narrator.py` | `Scene`, `Narration`, the `Narrator` protocol and `OfflineNarrator`. |
| `core/openai_narrator.py` | `OpenAINarrator`: prompts, JSON parsing, validation, rolling history and fallback. |
| `core/persistence.py` | Versioned JSON saves. |
| `ui/screen.py` | Redraws the game screen after each command: a location or monster art header, a hero panel with HP/XP bars, a paths or enemies panel, the story log and a hint bar. |
| `ui/widgets.py` | Rich views for `stats`, `inventory`, `quests`, `map`, `shop` and `help`, plus bar and pip helpers. |
| `ui/art.py` | ASCII art for the logo, the location kinds and the monsters, plus location icons and colors. |
| `ui/character_wizard.py`, `ui/console.py` | Character creation with rich tables, and a thin wrapper around `rich.Console`. |
| `utils/` | Dice notation parser and fuzzy name matching. |

## Design decisions

**Quests come from world facts, not from the model.** `create_quest` picks a real target (a monster type at a place, an unvisited place, or an NPC). The narrator only writes the title and the giver's plea. Every quest can therefore be completed, and `complete_matching` detects completion from game events.

**Free-form actions use two phases.** For "climb the wall", the narrator first narrates the attempt and can ask for a check. The engine then rolls with the player's real bonus. Finally the narrator describes the result it is told. This is the same order as at a real table: the DM asks for the roll, and the player rolls.

**The game falls back to offline narration.** `OpenAINarrator` wraps each call. If there is an API error, invalid JSON or a missing field, it reports the error once and uses `OfflineNarrator` for that call. The game never crashes because of the network.

**Context stays bounded.** The model gets a compact `Scene` snapshot (character, place, time, people, exits, quests, the last 8 journal entries) and a rolling window of recent exchanges. It does not get the full history. So the cost per turn stays flat over a long session, and the model's view of state never drifts from the engine's.

**All randomness is injected.** Every random choice goes through one seeded `random.Random`: the world, NPCs, dice and the offline narrator. `--seed` therefore reproduces a run, and tests can use `FixedRandom` to force exact rolls.

**The UI is a view of the state, not of the text.** The engine still returns plain lines, which keeps it testable and UI-agnostic. After every command, `Screen` rebuilds the whole screen from `GameManager.player`, `.world` and `.encounter`. As a result, HP bars, the paths panel and the enemy list are always correct, whatever the command printed. For information commands, `Screen` replaces the text lines with a rich table or tree. It also drops story lines that the panels above already show, such as "People here:" and "Paths lead to:". Line prefixes (`== `, `!! `, `*** `, `[`) and combat patterns ("X hits Y") pick the colors and icons in the story log. The engine never imports `rich`.

## Extending

- New data: see [Add monsters, places, items and classes](guides/add-content.md).
- A new narrator backend (for example, a different LLM provider): implement the five methods of the `Narrator` protocol in `core/narrator.py`, and select it in `main.build_narrator`.
- A new command: add aliases in `core/commands.py`, a handler in `GameManager._handlers`, a `HELP` entry, and a row in `docs/reference/commands.md`.
