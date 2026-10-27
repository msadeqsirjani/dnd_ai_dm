# Getting started

In this tutorial you install the game, create a hero, take your first quest and win your first fight. It takes about ten minutes. You do not need an API key: this tutorial uses the offline narrator, so your run matches the steps below.

## 1. Install

```bash
git clone https://github.com/msadeqsirjani/dnd_ai_dm.git
cd dnd_ai_dm
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2. Start a game

```bash
python main.py --offline
```

The game asks for a name, then shows a table for each choice: race, class and ability scores. Answer by number or by name:

```text
👤 What is your hero's name? Kara
              👥 Choose a race
╭───┬──────────┬──────────────────────────────────────────────╮
│ # │ Race     │ Bonuses                                      │
├───┼──────────┼──────────────────────────────────────────────┤
│ 1 │ Human    │ STR +1, DEX +1, CON +1, INT +1, WIS +1, CHA +1 │
│ 2 │ Elf      │ DEX +2, INT +1                               │
...
❯ human
```

The game assigns your highest scores to your class's most important abilities and then shows your character sheet. A Fighter is the most forgiving class for a first game.

## 3. Read the screen

After every command, the game redraws one screen:

```text
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 🏠 Oakvale ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓   ← where you are, with art
┗━━━━━━━━━━━━━━━━━━━━━━━━ Day 1 · morning · fog ━━━━━━━━━━━━━━━━━━━━━━━┛   ← time and weather
╭── Kara · Level 1 Human Fighter ──╮ ╭──── 👣 Paths from here ────╮
│ HP    ██████████████ 12/12       │ │ 📍 Oakvale                 │      ← where you can go:
│ XP    ░░░░░░░░░░░░░░ 0/300       │ │ ├── 🚩 Hollow Fork  ●○○ ★  │        ●○○ = danger, ★ = quest
│ Goal  Travel to Hollow Fork      │ │ └── 🌲 Elderglade  ●○○ new │
╰──────────────────────────────────╯ ╰────────────────────────────╯
╭─────────────────────────────── 📖 Story ───────────────────────────────╮   ← what just happened
╰────────────────────────────────────────────────────────────────────────╯
  go <place>    explore    talk <name>    quests    map    ...               ← commands to try
```

In a fight, the paths panel becomes an enemy panel with HP bars, and the header shows the monster.

## 4. Read the opening

You start in a village. The elder approaches and gives you a quest:

```text
*** New quest: Trouble on the Road ***
Objective: Defeat a Wolf at Whisperwood. Reward: 250 XP, 50 gold.
```

Your village, quest and NPC names will be different, because each world is generated. Type `quests` at any time to see the objective again.

## 5. Look around and prepare

```text
> look
> talk elder
> shop
> buy 1 healing potion
> map
```

`look` describes the place again. `shop` shows a price table and works only where a merchant is present. `map` draws a tree of every place you know, starting from the village.

## 6. Travel

Travel to the place named in your objective. If it is not directly connected, go through a place that is:

```text
> go whisperwood
You travel to Whisperwood. (2 hours pass.)
```

When your quest asks you to defeat a monster, that monster attacks as soon as you arrive.

## 7. Fight

The game rolls initiative and runs enemy turns for you. On your turn:

```text
> attack
Kara hits Wolf (17 vs AC 13) for 7 damage.
> ability
> use healing potion
```

`attack` without a name targets the first enemy. When there are two enemies with the same name, they are numbered, so use `attack wolf 2`. If the fight goes badly, `dodge` makes enemies attack with disadvantage, and `flee` tries to escape.

After you win, you get XP and gold, and the quest completes.

## 8. Act in your own words

Any input that is not a command is an action for the Dungeon Master:

```text
> search the hollow tree
You attempt to search the hollow tree.
[Investigation check: 12 +0 = 12 vs DC 12: success]
```

## 9. Rest and save

```text
> go oakvale
> rest
> save kara
> quit
```

Resting in the village is free. In the wild, resting uses one ration and you can be ambushed. `quit` also writes an autosave. Continue later with:

```bash
python main.py --load kara
```

## Next steps

- [Configure the AI narrator](guides/configure-the-ai-narrator.md) to get full AI storytelling.
- Read the [command reference](reference/commands.md) and the [rules](reference/rules.md).
