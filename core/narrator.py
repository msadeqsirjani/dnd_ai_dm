import random
import re
from dataclasses import dataclass
from typing import Protocol

from content.rules import skill_label
from models.npc import NPC


@dataclass(frozen=True)
class Scene:
    character: str
    location: str
    description: str
    danger: int
    time: str
    weather: str
    npcs: tuple[str, ...]
    exits: tuple[str, ...]
    quests: tuple[str, ...]
    journal: tuple[str, ...]

    def render(self) -> str:
        events = [f"- {entry}" for entry in self.journal] or ["- none yet"]
        return "\n".join(
            [
                f"Player character: {self.character}",
                f"Location: {self.location}. {self.description}",
                f"Danger level: {self.danger} of 3",
                f"Time: {self.time}. Weather: {self.weather}.",
                f"People here: {', '.join(self.npcs) or 'nobody'}",
                f"Paths lead to: {', '.join(self.exits) or 'nowhere'}",
                f"Active quests: {'; '.join(self.quests) or 'none'}",
                "Recent events:",
                *events,
            ]
        )


@dataclass(frozen=True)
class CheckRequest:
    skill: str
    dc: int


@dataclass(frozen=True)
class Narration:
    text: str
    check: CheckRequest | None = None
    disposition_change: int = 0


class Narrator(Protocol):
    def describe_location(self, scene: Scene) -> str: ...

    def resolve_action(self, scene: Scene, action: str) -> Narration: ...

    def narrate_outcome(
        self, scene: Scene, action: str, check: CheckRequest, total: int, success: bool
    ) -> str: ...

    def npc_reply(self, scene: Scene, npc: NPC, message: str) -> Narration: ...

    def name_quest(
        self, scene: Scene, objective: str, giver: NPC
    ) -> tuple[str, str]: ...


SKILL_KEYWORDS = (
    (("pick", "lock", "steal", "pickpocket", "pilfer"), "sleight_of_hand"),
    (("sneak", "hide", "creep"), "stealth"),
    (("climb", "jump", "swim", "lift", "push", "force", "break"), "athletics"),
    (("balance", "tumble", "flip", "vault"), "acrobatics"),
    (("search", "investigate", "examine", "inspect", "study"), "investigation"),
    (("listen", "spot", "watch", "scan", "peer"), "perception"),
    (("track", "forage", "hunt", "navigate"), "survival"),
    (("persuade", "convince", "negotiate", "bargain", "haggle"), "persuasion"),
    (("lie", "bluff", "deceive", "trick"), "deception"),
    (("intimidate", "threaten", "scare"), "intimidation"),
    (("perform", "sing", "dance"), "performance"),
    (("pray", "bless"), "religion"),
    (("recall", "remember"), "history"),
    (("magic", "arcane", "rune", "runes", "spell"), "arcana"),
    (("heal", "bandage", "treat"), "medicine"),
    (("calm", "tame", "ride"), "animal_handling"),
    (("sense", "read", "gauge"), "insight"),
)

AMBIENT = (
    "The world carries on around you, indifferent.",
    "Nothing stirs except the wind.",
    "For a moment all is quiet.",
    "Somewhere in the distance a crow calls.",
)

SUCCESS_LINES = (
    "You pull it off with confidence.",
    "Your effort pays off.",
    "It works, better than you hoped.",
)

FAILURE_LINES = (
    "It doesn't go as planned.",
    "You fall short this time.",
    "Despite your efforts, nothing comes of it.",
)

GREETINGS = {
    "hostile": "Get out of my sight.",
    "unfriendly": "What do you want?",
    "neutral": "Can I help you, traveler?",
    "friendly": "Good to see you again, friend!",
    "helpful": "Anything you need, just ask.",
}

REPLIES = (
    "Hmm. I'll think on that.",
    "Strange times we live in.",
    "Keep your wits about you out there.",
    "I've heard rumors, but nothing I'd stake my life on.",
)

QUEST_TITLES = (
    "A Call for Aid",
    "Trouble on the Road",
    "An Urgent Errand",
    "The Elder's Request",
    "Shadows Over the Valley",
)


class OfflineNarrator:
    def __init__(self, rng: random.Random):
        self._rng = rng

    def describe_location(self, scene: Scene) -> str:
        return (
            f"{scene.description} It is {scene.time}, "
            f"and the weather is {scene.weather}."
        )

    def resolve_action(self, scene: Scene, action: str) -> Narration:
        skill = _skill_for(action)
        if skill is None:
            return Narration(
                f"You {_second_person(action)}. {self._rng.choice(AMBIENT)}"
            )
        dc = 10 + 2 * scene.danger + self._rng.choice((-2, 0, 3))
        return Narration(
            f"You attempt to {_second_person(action)}.", CheckRequest(skill, dc)
        )

    def narrate_outcome(
        self, scene: Scene, action: str, check: CheckRequest, total: int, success: bool
    ) -> str:
        lines = SUCCESS_LINES if success else FAILURE_LINES
        return f"{self._rng.choice(lines)} ({skill_label(check.skill)})"

    def npc_reply(self, scene: Scene, npc: NPC, message: str) -> Narration:
        if not message:
            line = GREETINGS[npc.attitude]
            return Narration(
                f'{npc.name} the {npc.occupation} ({npc.personality}) says: "{line}"'
            )
        return Narration(
            f'{npc.name} listens, then replies: "{self._rng.choice(REPLIES)}"',
            disposition_change=1,
        )

    def name_quest(self, scene: Scene, objective: str, giver: NPC) -> tuple[str, str]:
        description = (
            f'{giver.name} leans in: "{objective}. Do this for us, '
            'and you will be well rewarded."'
        )
        return self._rng.choice(QUEST_TITLES), description


def _skill_for(action: str) -> str | None:
    words = set(re.findall(r"[a-z]+", action.lower()))
    return next(
        (skill for keywords, skill in SKILL_KEYWORDS if words.intersection(keywords)),
        None,
    )


def _second_person(action: str) -> str:
    text = action.strip().rstrip(".!")
    text = re.sub(r"^(i|I)\s+(try to |attempt to )?", "", text)
    return text[:1].lower() + text[1:]
