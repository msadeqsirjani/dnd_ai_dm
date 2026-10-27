# Save and load games

## Save during play

```text
> save
> save before-the-keep
```

Without a name, the game uses your character's name. You cannot save during combat.

`quit` writes `autosave` automatically, unless you quit mid-fight.

## Load during play

```text
> load
Load which save? Available: autosave, before-the-keep, kara.
> load before-the-keep
```

## Load at startup

```bash
python main.py --load autosave
```

## Where saves live

By default, saves go in `saves/` in the current directory. To change the folder:

```bash
DND_SAVE_DIR=~/dnd-saves python main.py
```

Each save is one JSON file. The game converts the name to lowercase and replaces characters other than `a-z`, `0-9`, `_` and `-` with `-`. For example, `save Before The Keep!` writes `before-the-keep.json`.

## Back up or share a save

Copy the JSON file. Saves are complete: a save holds the character, the world, NPC memories, quests and the journal.

## Reproduce a run

Save files do not store the random number generator state. To replay the same world and the same dice from the start, use a seed:

```bash
python main.py --offline --quick --seed 42
```
