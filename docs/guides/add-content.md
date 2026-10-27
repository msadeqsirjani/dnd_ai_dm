# Add monsters, places, items and classes

All static game data is in `content/`. Most additions need no engine changes. After each change, run `python -m pytest`.

## Add a monster

Add an entry to `MONSTERS` in `content/monsters.py`:

```python
"zombie": MonsterTemplate("Zombie", "3d8+9", 8, 3, "1d6+1", -2, 50, 1),
```

The fields are: name, hit point dice, armor class, attack bonus, damage dice, Dexterity modifier (for initiative), XP, and tier. The game spawns a monster only when its tier is at most `1 + player level // 3`.

To make the monster appear, add its key to a location kind's `encounters` in `content/places.py`.

## Add a kind of place

1. Add a `LocationKind` to `LOCATION_KINDS` in `content/places.py`:

   ```python
   "mine": LocationKind(
       names=("Old Copper Mine", "Deepdelve"),
       descriptions=("Rotting timbers prop up a tunnel that slopes into darkness.",),
       danger=2,
       encounters=("goblin", "zombie"),
       occupations=("miner",),
   ),
   ```

2. Add the key to `WORLD_LAYOUT`. The generator creates one location per entry, in order, and connects each new location to an earlier one. Keep `"village"` first: the player starts there, and the elder lives there.

Set `safe=True` only for settlements. Resting is free in safe places, and defeated players wake up in the first safe place.

## Add an item

Add an `Item` to `ITEMS` in `content/items.py`:

```python
"greater healing potion": Item("Greater Healing Potion", 150, "A shimmering crimson tonic.", "4d4+4"),
```

Merchants sell every item in `ITEMS`. Only items with `healing` dice are usable with `use`. Using another item becomes a free-form action for the narrator.

To change the starting kit, edit `STARTING_INVENTORY` and `STARTING_GOLD`.

## Add a race

Add a `Race` to `RACES` in `content/heroes.py`, and a pair of name lists to `RACE_NAMES` in `content/places.py`:

```python
"gnome": Race("Gnome", {"intelligence": 2, "constitution": 1}),
```

```python
"gnome": (("Alston", "Nissa", "Orryn"), ("Beren", "Murnig", "Timbers")),
```

## Add a class

A class needs a weapon and a feature.

1. Add a `Weapon` to `WEAPONS`, if the class needs a new one. Set `ability` to `"strength"`, `"dexterity"`, `"finesse"` (the better of the two) or a spellcasting ability such as `"wisdom"`.
2. Add a `Feature` to `FEATURES`.
3. Add a `CharacterClass` to `CLASSES`. `priorities` lists all six abilities, from most to least important. `dex_cap` is the maximum Dexterity bonus to AC (`None` means no limit).
4. Implement the feature in `core/class_features.py`. Write a function with the signature `(character, dice, target) -> list[str]`, and register it in `_HANDLERS` under the feature key.
5. Add a test in `tests/test_combat.py`.
