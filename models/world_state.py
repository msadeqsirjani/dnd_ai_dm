from dataclasses import asdict, dataclass, field

from models.npc import NPC
from models.quest import Quest
from utils.matching import find_match

JOURNAL_LIMIT = 50


@dataclass
class Location:
    id: str
    name: str
    kind: str
    description: str
    danger: int
    encounters: list[str]
    connections: list[str] = field(default_factory=list)
    safe: bool = False
    visited: bool = False


@dataclass
class WorldState:
    locations: dict[str, Location]
    current_location: str
    npcs: dict[str, NPC] = field(default_factory=dict)
    quests: list[Quest] = field(default_factory=list)
    journal: list[str] = field(default_factory=list)
    day: int = 1
    hour: int = 8
    weather: str = "clear"
    next_quest_id: int = 1

    @property
    def location(self) -> Location:
        return self.locations[self.current_location]

    @property
    def time_of_day(self) -> str:
        if 5 <= self.hour < 12:
            return "morning"
        if 12 <= self.hour < 17:
            return "afternoon"
        if 17 <= self.hour < 21:
            return "evening"
        return "night"

    @property
    def active_quests(self) -> list[Quest]:
        return [quest for quest in self.quests if quest.is_active]

    @property
    def home(self) -> Location:
        return next(location for location in self.locations.values() if location.safe)

    def advance_time(self, hours: int) -> None:
        total = self.hour + hours
        self.day += total // 24
        self.hour = total % 24

    def neighbors(self) -> list[Location]:
        return [self.locations[key] for key in self.location.connections]

    def npcs_at(self, location_id: str) -> list[NPC]:
        return [npc for npc in self.npcs.values() if npc.location == location_id]

    def find_neighbor(self, query: str) -> Location | None:
        return find_match(query, self.neighbors(), lambda loc: f"{loc.name} {loc.kind}")

    def find_location(self, query: str) -> Location | None:
        return find_match(
            query, self.locations.values(), lambda loc: f"{loc.name} {loc.kind}"
        )

    def find_npc_here(self, query: str) -> NPC | None:
        return find_match(
            query,
            self.npcs_at(self.current_location),
            lambda npc: f"{npc.name} {npc.occupation}",
        )

    def add_journal(self, entry: str) -> None:
        stamped = f"Day {self.day}, {self.time_of_day}: {entry}"
        self.journal = [*self.journal, stamped][-JOURNAL_LIMIT:]

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "WorldState":
        return cls(
            **{
                **data,
                "locations": {
                    key: Location(**value) for key, value in data["locations"].items()
                },
                "npcs": {
                    key: NPC.from_dict(value) for key, value in data["npcs"].items()
                },
                "quests": [Quest.from_dict(value) for value in data["quests"]],
            }
        )
