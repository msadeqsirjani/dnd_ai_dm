# AGENTS.md

## Overview

Console D&D 5e-inspired RPG. Python 3.10+. The game engine is deterministic and owns all rules. A pluggable narrator writes the prose: `OpenAINarrator` (OpenAI Chat Completions) or `OfflineNarrator` (templates). Dependencies: `openai`, `python-dotenv`, `rich` (terminal UI).

## Commands

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
python main.py --offline --quick --seed 1   # play without network
python -m pytest                            # run tests
black .                                     # format
```

## Layout

```text
main.py            CLI entry point: args, narrator choice, input loop
config.py          Settings from environment variables
content/           Static game data: rules tables, races, classes, monsters, items, places
models/            Mutable state dataclasses with to_dict/from_dict
core/              Engine: game_manager (command dispatch), combat, quests, world generation,
                   narrators, persistence
ui/                Rich terminal UI: screen layout (screen.py), views (widgets.py),
                   ASCII art (art.py), character wizard, console wrapper
utils/             Dice parser and fuzzy name matching
tests/             pytest suite; tests/helpers.py has FixedRandom for deterministic dice
docs/              Diátaxis docs: getting-started, guides/, reference/, architecture.md
```

Dependencies point one way: `main/ui → core → models → content/utils`.

## Conventions

- No comments or docstrings in code. Document in `docs/`.
- Small modules, one job each. Plain dataclasses and functions.
- All randomness goes through an injected `random.Random` or `Dice`. Never call the `random` module's global functions.
- The engine returns output as `list[str]`. Only `ui/` prints. Line prefixes control style: `== `, `!! `, `*** `, `[`.
- `ui/screen.py` redraws the full screen after each command from `GameManager` state (`player`, `world`, `encounter`). Info commands (`stats`, `inventory`, `quests`, `map`, `help`, `shop`) render as rich views instead of their text lines.
- Use BMP symbols with a reliable width (♥ ◆ ★) in table cells; emoji with variation selectors (🛡 ❤️) break alignment.
- Narrators never change game state directly. They return text and, at most, a `CheckRequest` or a disposition shift that the engine clamps.
- New game data goes in `content/`. See `docs/guides/add-content.md`.
- Format with Black (line length 88).

## Testing

- Tests must not use the network. Use `OfflineNarrator` or the `FakeClient` in `tests/test_openai_narrator.py`.
- Use `tests/helpers.fixed_dice(n)` for exact rolls and `random.Random(seed)` for reproducible runs.
- Add a test with each new rule or command.

## Commits and PRs

- Use Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`).
- Run `python -m pytest` before you commit.

## Never

- Commit `.env` or anything under `saves/`.
- Change the save format without bumping `SAVE_VERSION` in `core/persistence.py`.
- Let model output bypass validation in `core/openai_narrator.py`.
