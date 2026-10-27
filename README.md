# AI Dungeon Master

A console role-playing game inspired by Dungeons & Dragons 5th Edition. You create a hero, explore a procedurally generated region, talk to its people, take quests and fight monsters. An OpenAI model narrates the story and voices the characters. The game engine handles every rule: dice, combat, skill checks, XP and loot. Without an API key, a built-in offline narrator takes over, so the game is always playable.

## Features

- **Visual terminal UI** (built with [rich](https://github.com/Textualize/rich)): ASCII art for every place and monster, HP and XP bars, a live "paths from here" map, an enemy panel in combat, color-coded hits and dice rolls, and tables for stats, inventory, quests and shop.
- **Character creation:** 5 races, 4 classes (Fighter, Rogue, Wizard, Cleric), standard array or 4d6-drop-lowest ability scores.
- **5e-style rules:** ability modifiers, proficiency, armor class, skill checks, advantage and disadvantage, critical hits, levels 1–10.
- **Turn-based combat:** initiative, attack, dodge, flee, potions and one class feature per class.
- **Procedural world:** a connected map of 7 places with NPCs, weather, a day/night clock and danger levels.
- **Free-form actions:** type anything ("climb the old well"). The DM decides whether a skill check is needed, the engine rolls it, and the DM narrates the outcome.
- **Talking NPCs:** each NPC has a personality and a disposition, and remembers recent conversations.
- **Quests:** the village elder hands out defeat, visit and talk objectives, with XP and gold rewards.
- **Saving:** save, load and autosave as JSON files.
- **Reproducibility:** `--seed` produces the same world and dice rolls each run.

## Requirements

- Python 3.10 or newer
- An OpenAI API key (optional; without one the game uses the offline narrator)

## Quick start

```bash
git clone https://github.com/msadeqsirjani/dnd_ai_dm.git
cd dnd_ai_dm
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env    # then set OPENAI_API_KEY in .env
python main.py
```

To play without an API key:

```bash
python main.py --offline --quick
```

## Usage

```text
python main.py [--offline] [--quick] [--load NAME] [--seed N] [--model NAME]
```

In the game, type `help` to see all commands. Common ones:

```text
look                      talk elder about the wolves
go whisperwood            explore
attack goblin 2           use healing potion
stats                     save my-hero
```

## Development

```bash
pip install -r requirements-dev.txt
python -m pytest
black .
```

## Documentation

- [Getting started](docs/getting-started.md): your first adventure, step by step
- How-to guides:
  - [Configure the AI narrator](docs/guides/configure-the-ai-narrator.md)
  - [Save and load games](docs/guides/save-and-load.md)
  - [Add monsters, places, items and classes](docs/guides/add-content.md)
- Reference:
  - [Commands](docs/reference/commands.md)
  - [Configuration and CLI](docs/reference/configuration.md)
  - [Game rules](docs/reference/rules.md)
- [Architecture](docs/architecture.md): how the engine and the narrator fit together

## License

MIT. See [LICENSE](LICENSE).
