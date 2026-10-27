# Configuration reference

## Command-line options

```text
python main.py [--offline] [--quick] [--load NAME] [--seed N] [--model NAME]
```

| Option | Effect |
|---|---|
| `--offline` | Use the template narrator. Makes no network calls. |
| `--quick` | Skip character creation. Plays a random race and class with the standard array. |
| `--load NAME` | Load the save `NAME` and continue. Exits with code 1 if the save is missing or invalid. |
| `--seed N` | Seed the world generator, NPCs, dice and offline narrator. Overrides `DND_SEED`. |
| `--model NAME` | OpenAI model for this run. Overrides `DND_MODEL`. |
| `-h`, `--help` | Show usage. |

## Environment variables

The game reads these from the environment, and from a `.env` file in the working directory. See `.env.example`.

| Variable | Default | Meaning |
|---|---|---|
| `OPENAI_API_KEY` | *(none)* | OpenAI API key. If it is empty, the game uses the offline narrator and shows a warning. |
| `DND_MODEL` | `gpt-4o-mini` | Chat Completions model. It must support JSON mode. |
| `DND_SAVE_DIR` | `saves` | Folder for save files. The game creates it on the first save. |
| `DND_HISTORY_TURNS` | `8` | Number of past request/response pairs that the AI narrator keeps. |
| `DND_SEED` | *(random)* | Integer seed for reproducible runs. |

## Files

| Path | Purpose |
|---|---|
| `.env` | Your local settings. Git ignores it. |
| `saves/*.json` | Save files. Git ignores them. See the save format below. |

## Save file format

```json
{
  "version": 1,
  "player": { "name": "...", "race": "...", "character_class": "...", "abilities": {}, "level": 1, "xp": 0, "max_hp": 12, "hp": 12, "gold": 25, "inventory": {}, "feature_uses": 1 },
  "world": { "locations": {}, "current_location": "...", "npcs": {}, "quests": [], "journal": [], "day": 1, "hour": 8, "weather": "...", "next_quest_id": 2 }
}
```

The game refuses to load a file whose `version` is not the current `SAVE_VERSION` (`core/persistence.py`).
