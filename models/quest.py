from dataclasses import asdict, dataclass

OBJECTIVES = ("defeat", "visit", "talk")


@dataclass
class Quest:
    id: int
    objective: str
    target: str
    location: str
    giver: str
    reward_xp: int
    reward_gold: int
    title: str = ""
    description: str = ""
    status: str = "active"

    @property
    def is_active(self) -> bool:
        return self.status == "active"

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Quest":
        return cls(**data)
