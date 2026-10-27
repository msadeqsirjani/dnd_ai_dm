import random

from content.places import PERSONALITIES, RACE_NAMES
from models.npc import NPC

NAME_ATTEMPTS = 50


class NPCManager:
    def __init__(self, rng: random.Random):
        self._rng = rng
        self._used_names: set[str] = set()

    def create(self, location_id: str, occupation: str) -> NPC:
        race = self._rng.choice(list(RACE_NAMES))
        return NPC(
            name=self._unique_name(race),
            race=race,
            occupation=occupation,
            location=location_id,
            personality=self._rng.choice(PERSONALITIES),
            disposition=self._rng.randint(35, 65),
        )

    def _unique_name(self, race: str) -> str:
        first_names, last_names = RACE_NAMES[race]
        name = ""
        for attempt in range(NAME_ATTEMPTS):
            name = f"{self._rng.choice(first_names)} {self._rng.choice(last_names)}"
            if name not in self._used_names:
                break
        else:
            name = f"{name} {attempt}"
        self._used_names.add(name)
        return name
