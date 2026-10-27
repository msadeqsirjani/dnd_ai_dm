# Command reference

Commands are not case-sensitive. The parser drops filler words after the verb (`to`, `with`, `the`, `at`, `into`, `towards`, `a`, `an`), so `go to the forest` and `go forest` are the same command. Names match by exact name, then by prefix, then by the start of a word, then by substring. For example, `talk elder` finds "Mara Ashdown the elder".

## Exploration

| Command | Aliases | Effect |
|---|---|---|
| `look` | `l` | Show the place, time, weather, people and paths. With extra words (`look under the bridge`), it is a free-form action. |
| `go <place>` | `move`, `travel`, `walk` | Travel to a connected place. 2 hours pass. Can trigger an encounter. |
| `map` | `exits` | List visited places and their connections. |
| `explore` | | 1 hour passes. Can trigger an encounter, find gold, or become a search action. |
| `talk <person> [message]` | `speak`, `ask` | Talk to an NPC here. `talk elder about the ruins` sends "the ruins" as the message. |
| `rest` | `sleep`, `camp` | Long rest: 8 hours, full HP and full feature uses. Outside safe places it uses 1 ration and can be ambushed. |
| `shop` | | List a merchant's wares. Needs a merchant here. |
| `buy [quantity] <item>` | | Buy items, for example `buy 3 rations`. |
| `use <item>` | `drink` | Drink a healing potion. A non-healing item becomes a free-form action. |
| `ability` | `special`, `cast` | Use a non-combat feature (Second Wind, Cure Wounds). |
| *anything else* | | A free-form action. The DM can ask for a skill check. |

## Combat

During combat, only these commands work: `attack`, `dodge`, `flee`, `use`, `ability`, `look`, `stats`, `inventory`, `roll`, `help` and `quit`.

| Command | Aliases | Effect |
|---|---|---|
| `attack [enemy]` | `hit`, `fight` | Attack with your weapon. Without a name, attacks the first living enemy. |
| `dodge` | | Attacks against you have disadvantage until your next turn. |
| `flee` | `run` | Acrobatics check against DC 10 + the number of living enemies. On a success, you escape. |
| `use <item>` | `drink` | Drink a potion. This uses your turn. |
| `ability [enemy]` | `special`, `cast` | Use your class feature. Cunning Strike and Magic Missile need a target. |
| `look` | `l` | Show the round, your HP and the enemies' HP. |

If a command fails (an unknown target, or no uses left), your turn is not used.

## Information

| Command | Aliases | Effect |
|---|---|---|
| `stats` | `sheet`, `character` | Character sheet. |
| `inventory` | `inv`, `i` | Gold and items. |
| `quests` | `journal` | Active `[ ]` and completed `[x]` quests. |
| `check <skill or ability>` | | Roll a check yourself, for example `check perception` or `check strength`. |
| `roll <dice>` | | Roll dice: `d20`, `2d6+3`, `4d6kh3`, `2d20kl1`. Default: `d20`. |
| `help` | `?` | List commands. |

## Session

| Command | Effect |
|---|---|
| `save [name]` | Save the game. The default name is your character's name. |
| `load [name]` | Load a save. Without a name, lists the saves. |
| `quit` / `exit` | Write `autosave` (unless in combat) and exit. |

## Dice notation

```text
[count]d<sides>[kh<n>|kl<n>][+/-modifier]
```

The count can be 1–100, the sides 2–1000. `kh` keeps the highest dice and `kl` keeps the lowest.
