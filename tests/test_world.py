import random

from content.places import WORLD_LAYOUT
from core.world_generator import generate_world
from models.world_state import WorldState


def reachable(world: WorldState) -> set[str]:
    seen, stack = set(), [world.current_location]
    while stack:
        key = stack.pop()
        if key not in seen:
            seen.add(key)
            stack.extend(world.locations[key].connections)
    return seen


def test_world_is_connected_and_starts_in_a_safe_village():
    for seed in range(25):
        world = generate_world(random.Random(seed))
        assert len(world.locations) == len(WORLD_LAYOUT)
        assert reachable(world) == set(world.locations)
        assert world.location.safe and world.location.visited


def test_connections_are_symmetric():
    world = generate_world(random.Random(4))
    for location in world.locations.values():
        for key in location.connections:
            assert location.id in world.locations[key].connections


def test_village_has_an_elder_and_merchant():
    world = generate_world(random.Random(9))
    occupations = {npc.occupation for npc in world.npcs_at(world.current_location)}
    assert {"elder", "merchant"} <= occupations


def test_same_seed_same_world():
    first = generate_world(random.Random(42)).to_dict()
    assert generate_world(random.Random(42)).to_dict() == first


def test_time_rolls_over_days():
    world = generate_world(random.Random(1))
    world.advance_time(20)
    assert (world.day, world.hour, world.time_of_day) == (2, 4, "night")


def test_round_trip_serialization():
    world = generate_world(random.Random(7))
    world.add_journal("Something happened.")
    assert WorldState.from_dict(world.to_dict()) == world
