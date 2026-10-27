from dataclasses import asdict, dataclass, field

ATTITUDES = (
    (20, "hostile"),
    (40, "unfriendly"),
    (60, "neutral"),
    (80, "friendly"),
    (101, "helpful"),
)
MEMORY_LIMIT = 6


@dataclass
class NPC:
    name: str
    race: str
    occupation: str
    location: str
    personality: str
    disposition: int = 50
    memories: list[str] = field(default_factory=list)

    @property
    def key(self) -> str:
        return self.name.lower()

    @property
    def attitude(self) -> str:
        return next(label for limit, label in ATTITUDES if self.disposition < limit)

    def modify_disposition(self, amount: int) -> None:
        self.disposition = max(0, min(100, self.disposition + amount))

    def remember(self, memory: str) -> None:
        self.memories = [*self.memories, memory][-MEMORY_LIMIT:]

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "NPC":
        return cls(**data)
