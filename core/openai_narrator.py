import json
import random
from collections import deque
from collections.abc import Callable
from typing import Any, TypeVar

from openai import OpenAI, OpenAIError

from content.rules import SKILLS
from core.narrator import CheckRequest, Narration, OfflineNarrator, Scene
from models.npc import NPC

T = TypeVar("T")

SYSTEM_PROMPT = (
    "You are the Dungeon Master of a Dungeons & Dragons 5e adventure played in a "
    "text console. Narrate in second person, present tense, in two to four vivid "
    "sentences. Never decide the player's actions, thoughts or feelings. Stay "
    "consistent with the game state you are given. Do not invent exits, items, "
    "rewards or combat: the game engine handles all mechanics."
)

ACTION_FORMAT = (
    'Reply with a JSON object: {"narration": string, "check": null or '
    '{"skill": string, "dc": integer}}. Skills: ' + ", ".join(SKILLS) + "."
)

MIN_DC, MAX_DC = 5, 25
MAX_DISPOSITION_SHIFT = 10


class OpenAINarrator:
    def __init__(
        self,
        api_key: str,
        model: str,
        history_turns: int = 8,
        client: Any = None,
        fallback: OfflineNarrator | None = None,
        on_error: Callable[[str], None] = lambda message: None,
    ):
        self._client = client or OpenAI(api_key=api_key)
        self._model = model
        self._history: deque[dict[str, str]] = deque(maxlen=history_turns * 2)
        self._fallback = fallback or OfflineNarrator(random.Random())
        self._on_error = on_error
        self._failing = False

    def describe_location(self, scene: Scene) -> str:
        prompt = (
            f"{scene.render()}\n\nThe player has just arrived. "
            "Describe what they see, hear and smell."
        )
        return self._attempt(
            lambda: self._complete(prompt),
            lambda: self._fallback.describe_location(scene),
        )

    def resolve_action(self, scene: Scene, action: str) -> Narration:
        prompt = (
            f"{scene.render()}\n\nThe player does this: {action!r}\n\n"
            "If the outcome is uncertain, choose the best-fitting skill and a DC "
            "(5 very easy, 10 easy, 15 medium, 20 hard, 25 very hard), and narrate "
            "only the attempt, not the result. Otherwise narrate the outcome and set "
            f'"check" to null. {ACTION_FORMAT}'
        )

        def run() -> Narration:
            data = self._complete_json(prompt)
            return Narration(str(data["narration"]), _parse_check(data.get("check")))

        return self._attempt(run, lambda: self._fallback.resolve_action(scene, action))

    def narrate_outcome(
        self, scene: Scene, action: str, check: CheckRequest, total: int, success: bool
    ) -> str:
        verdict = "succeeds" if success else "fails"
        prompt = (
            f"The player attempted: {action!r}. They rolled {total} on a "
            f"{check.skill} check against DC {check.dc} and {verdict}. "
            "Narrate the result."
        )
        return self._attempt(
            lambda: self._complete(prompt),
            lambda: self._fallback.narrate_outcome(
                scene, action, check, total, success
            ),
        )

    def npc_reply(self, scene: Scene, npc: NPC, message: str) -> Narration:
        memories = "\n".join(f"- {memory}" for memory in npc.memories) or "- none"
        said = f"The player says: {message!r}" if message else "The player greets them."
        prompt = (
            f"{scene.render()}\n\nYou voice {npc.name}, a {npc.race} {npc.occupation} "
            f"who is {npc.personality} and currently {npc.attitude} toward the player "
            f"(disposition {npc.disposition}/100).\nPrevious conversations:\n{memories}\n"
            f"{said}\n\nReply in character in one to three sentences. Respond with "
            'a JSON object: {"reply": string, "disposition_change": integer from '
            f"-{MAX_DISPOSITION_SHIFT} to {MAX_DISPOSITION_SHIFT}}}."
        )

        def run() -> Narration:
            data = self._complete_json(prompt)
            shift = int(data.get("disposition_change", 0))
            shift = max(-MAX_DISPOSITION_SHIFT, min(MAX_DISPOSITION_SHIFT, shift))
            return Narration(f"{npc.name}: {data['reply']}", disposition_change=shift)

        return self._attempt(run, lambda: self._fallback.npc_reply(scene, npc, message))

    def name_quest(self, scene: Scene, objective: str, giver: NPC) -> tuple[str, str]:
        prompt = (
            f"{scene.render()}\n\n{giver.name} the {giver.occupation} gives the player "
            f"a quest. The objective is exactly: {objective}. Write a short title and "
            "the giver's two-sentence plea, which must state that objective. Respond "
            'with a JSON object: {"title": string, "description": string}.'
        )

        def run() -> tuple[str, str]:
            data = self._complete_json(prompt)
            return str(data["title"]), str(data["description"])

        return self._attempt(
            run, lambda: self._fallback.name_quest(scene, objective, giver)
        )

    def _complete(self, prompt: str, as_json: bool = False) -> str:
        options = {"response_format": {"type": "json_object"}} if as_json else {}
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                *self._history,
                {"role": "user", "content": prompt},
            ],
            **options,
        )
        content = response.choices[0].message.content or ""
        self._history.extend(
            [
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": content},
            ]
        )
        return content.strip()

    def _complete_json(self, prompt: str) -> dict:
        data = json.loads(self._complete(prompt, as_json=True))
        if not isinstance(data, dict):
            raise ValueError("Expected a JSON object from the model.")
        return data

    def _attempt(self, run: Callable[[], T], fallback: Callable[[], T]) -> T:
        try:
            result = run()
        except (OpenAIError, ValueError, KeyError, TypeError) as error:
            if not self._failing:
                self._on_error(str(error))
            self._failing = True
            return fallback()
        self._failing = False
        return result


def _parse_check(raw: Any) -> CheckRequest | None:
    if not isinstance(raw, dict):
        return None
    skill = str(raw.get("skill", "")).strip().lower().replace(" ", "_")
    if skill not in SKILLS:
        return None
    return CheckRequest(skill, max(MIN_DC, min(MAX_DC, int(raw.get("dc", 10)))))
