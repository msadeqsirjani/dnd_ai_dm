import random
import re

from content.places import EXTRA_PATHS, LOCATION_KINDS, WEATHER, WORLD_LAYOUT
from core.npc_manager import NPCManager
from models.world_state import Location, WorldState

MAX_CONNECTIONS = 3


def generate_world(rng: random.Random) -> WorldState:
    locations: dict[str, Location] = {}
    for kind_key in WORLD_LAYOUT:
        location = _create_location(rng, kind_key)
        if locations:
            open_slots = [
                loc
                for loc in locations.values()
                if len(loc.connections) < MAX_CONNECTIONS
            ]
            _connect(rng.choice(open_slots or list(locations.values())), location)
        locations[location.id] = location
    _add_extra_paths(rng, list(locations.values()))

    start = next(iter(locations.values()))
    start.visited = True
    world = WorldState(
        locations=locations, current_location=start.id, weather=rng.choice(WEATHER)
    )
    npc_manager = NPCManager(rng)
    for location in locations.values():
        for occupation in LOCATION_KINDS[location.kind].occupations:
            npc = npc_manager.create(location.id, occupation)
            world.npcs[npc.key] = npc
    return world


def _create_location(rng: random.Random, kind_key: str) -> Location:
    kind = LOCATION_KINDS[kind_key]
    name = rng.choice(kind.names)
    return Location(
        id=_slug(name),
        name=name,
        kind=kind_key,
        description=rng.choice(kind.descriptions),
        danger=kind.danger,
        encounters=list(kind.encounters),
        safe=kind.safe,
    )


def _add_extra_paths(rng: random.Random, locations: list[Location]) -> None:
    candidates = [
        (a, b)
        for index, a in enumerate(locations)
        for b in locations[index + 1 :]
        if b.id not in a.connections
    ]
    for a, b in rng.sample(candidates, min(EXTRA_PATHS, len(candidates))):
        _connect(a, b)


def _connect(a: Location, b: Location) -> None:
    a.connections.append(b.id)
    b.connections.append(a.id)


def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
