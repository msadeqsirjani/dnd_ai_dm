# Game rules reference

The rules follow D&D 5th Edition, simplified for a single player. Values are taken from `content/` and `core/`.

## Abilities and checks

- Ability modifier: `(score - 10) // 2`.
- Proficiency bonus: `2 + (level - 1) // 4`.
- Skill check: d20 + ability modifier, plus proficiency if the skill is one of your class skills. You succeed if the total is at least the DC.
- Advantage rolls 2d20 and keeps the higher die. Disadvantage keeps the lower die. If you have both, they cancel.

## Races

| Race | Bonuses |
|---|---|
| Human | +1 to all abilities |
| Elf | DEX +2, INT +1 |
| Dwarf | CON +2, WIS +1 |
| Halfling | DEX +2, CHA +1 |
| Half-Orc | STR +2, CON +1 |

## Classes

| Class | Hit die | Weapon | AC | Feature | Uses per long rest |
|---|---|---|---|---|---|
| Fighter | d10 | Longsword 1d8 (STR) | 16 | Second Wind: heal 1d10 + level | 1 |
| Rogue | d8 | Shortsword 1d6 (finesse) | 11 + DEX | Cunning Strike: attack with advantage, +⌈level/2⌉d6 on a hit | 2 |
| Wizard | d6 | Fire Bolt 1d10 (INT) | 10 + DEX | Magic Missile: 3d4+3, always hits | 2 + level // 2 |
| Cleric | d8 | Mace 1d6 (STR) | 14 + DEX (max +2) | Cure Wounds: heal 1d8 + WIS | 2 + level // 2 |

- Starting HP: hit die + CON modifier.
- HP gained per level: `hit_die // 2 + 1 + CON modifier` (at least 1).
- Starting kit: 25 gold, 2 healing potions, 3 rations, 2 torches.

## Levels

| Level | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| XP | 0 | 300 | 900 | 2700 | 6500 | 14000 | 23000 | 34000 | 48000 | 64000 |

The maximum level is 10.

## Combat

- Initiative: d20 + DEX modifier. The game sorts combatants from highest to lowest. On a tie, you act first.
- Attack: d20 + attack bonus against the target's AC. Your attack bonus is your weapon ability modifier + proficiency.
- A natural 20 always hits and doubles the damage dice. A natural 1 always misses.
- Damage dealt is at least 1.
- Flee: an Acrobatics check against DC `10 + living enemies`.
- Victory: you get each enemy's XP, plus gold equal to the sum of `max(1, xp // 10)` for each enemy, plus 1d6.
- Defeat: you wake in the village with half your max HP and lose half your gold. 8 hours pass.

## Monsters

| Monster | HP | AC | Attack | Damage | XP | Tier |
|---|---|---|---|---|---|---|
| Giant Rat | 2d6 | 12 | +4 | 1d4+2 | 25 | 1 |
| Bandit | 2d8+2 | 12 | +3 | 1d6+1 | 25 | 1 |
| Wolf | 2d8+2 | 13 | +4 | 2d4+2 | 50 | 1 |
| Goblin | 2d6 | 15 | +4 | 1d6+2 | 50 | 1 |
| Skeleton | 2d8+4 | 13 | +4 | 1d6+2 | 50 | 1 |
| Orc | 2d8+6 | 13 | +5 | 1d12+3 | 100 | 2 |
| Giant Spider | 4d10+4 | 14 | +5 | 1d8+3 | 200 | 2 |
| Ogre | 7d10+21 | 11 | +6 | 2d8+4 | 450 | 3 |

- Your tier is `1 + level // 3`. Encounters only include monsters at or below your tier. If a place has no such monsters, it uses its lowest-tier monster.
- Group size: 1 enemy, with a `min(50%, 15% × level)` chance of a second.

## Exploration and time

| Action | Time | Encounter chance |
|---|---|---|
| Travel | 2 hours | `20% + 10% × danger`. Certain if an active defeat quest targets the place. |
| Explore | 1 hour | `40% + 10% × danger`. Certain if a defeat quest targets the place. Otherwise, outside safe places: a 40% chance to find `(danger + 1)d6` gold, else a search action. |
| Rest | 8 hours | Safe places: none. Elsewhere: costs 1 ration, 25% ambush chance. |

- The weather changes with a 30% chance on each trip.
- Time of day: morning 05–11, afternoon 12–16, evening 17–20, night 21–04.

## Free-form actions

- The narrator decides whether an action needs a check, and picks the skill and DC.
- AI narrator: the DC is clamped to 5–25.
- Offline narrator: a keyword picks the skill, and the DC is `10 + 2 × danger` plus one of −2, 0 or +3.
- A successful check gives `DC // 2` XP.

## NPCs

- Disposition runs from 0 to 100. Attitudes: hostile (<20), unfriendly (<40), neutral (<60), friendly (<80), helpful.
- One conversation turn can shift disposition by at most ±10.
- Each NPC remembers its last 6 exchanges with you.

## Quests

- The village elder offers a quest at the start, and again when you talk to the elder with no active quest.
- Objectives: defeat a monster at a place, visit an unvisited place, or speak with an NPC elsewhere.
- Reward: `100 + 150 × danger` XP and `20 + 30 × danger` gold, where danger is that of the target place.
