import random

from content.monsters import MONSTERS
from models.npc import NPC
from models.quest import Quest
from models.world_state import WorldState


def player_tier(level: int) -> int:
    return 1 + level // 3


def create_quest(
    world: WorldState, rng: random.Random, giver: NPC, level: int
) -> Quest | None:
    taken = {(quest.objective, quest.target) for quest in world.active_quests}
    options = []
    for location in world.locations.values():
        if location.id == giver.location:
            continue
        foes = [
            key
            for key in location.encounters
            if MONSTERS[key].tier <= player_tier(level)
        ]
        options += [("defeat", key, location) for key in foes]
        if not location.visited:
            options.append(("visit", location.id, location))
        options += [("talk", npc.key, location) for npc in world.npcs_at(location.id)]
    options = [option for option in options if option[:2] not in taken]
    if not options:
        return None
    objective, target, location = rng.choice(options)
    quest = Quest(
        id=world.next_quest_id,
        objective=objective,
        target=target,
        location=location.id,
        giver=giver.name,
        reward_xp=100 + 150 * location.danger,
        reward_gold=20 + 30 * location.danger,
    )
    world.next_quest_id += 1
    return quest


def objective_text(quest: Quest, world: WorldState) -> str:
    place = world.locations[quest.location].name
    if quest.objective == "defeat":
        return f"Defeat a {MONSTERS[quest.target].name} at {place}"
    if quest.objective == "visit":
        return f"Travel to {place}"
    return f"Speak with {world.npcs[quest.target].name} at {place}"


def complete_matching(
    world: WorldState, objective: str, target: str, location_id: str
) -> list[Quest]:
    completed = [
        quest
        for quest in world.active_quests
        if (quest.objective, quest.target, quest.location)
        == (objective, target, location_id)
    ]
    for quest in completed:
        quest.status = "completed"
    return completed
