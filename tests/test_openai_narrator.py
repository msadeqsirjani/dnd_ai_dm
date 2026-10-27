import json
import random
from types import SimpleNamespace

from core.narrator import OfflineNarrator, Scene
from core.openai_narrator import OpenAINarrator
from models.npc import NPC

SCENE = Scene(
    character="Kara, level 1 Human Fighter (12/12 HP)",
    location="Oakvale",
    description="A quiet village.",
    danger=0,
    time="day 1, morning",
    weather="clear",
    npcs=(),
    exits=("Whisperwood",),
    quests=(),
    journal=(),
)


class FakeClient:
    def __init__(self, *replies):
        self.replies = list(replies)
        self.calls = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        reply = self.replies.pop(0)
        if isinstance(reply, Exception):
            raise reply
        message = SimpleNamespace(content=reply)
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])


def narrator(client, errors=None):
    return OpenAINarrator(
        "key",
        "test-model",
        history_turns=1,
        client=client,
        fallback=OfflineNarrator(random.Random(0)),
        on_error=(errors.append if errors is not None else lambda message: None),
    )


def test_resolve_action_parses_check():
    reply = json.dumps(
        {
            "narration": "You reach for the ledge.",
            "check": {"skill": "Athletics", "dc": 40},
        }
    )
    result = narrator(FakeClient(reply)).resolve_action(SCENE, "climb the wall")
    assert result.text == "You reach for the ledge."
    assert (result.check.skill, result.check.dc) == ("athletics", 25)


def test_unknown_skill_means_no_check():
    reply = json.dumps({"narration": "Done.", "check": {"skill": "flying", "dc": 10}})
    assert narrator(FakeClient(reply)).resolve_action(SCENE, "fly").check is None


def test_invalid_json_falls_back_and_reports_once():
    errors = []
    dm = narrator(FakeClient("not json", "still not json"), errors)
    first = dm.resolve_action(SCENE, "wave")
    dm.resolve_action(SCENE, "wave again")
    assert first.text.startswith("You wave")
    assert len(errors) == 1


def test_npc_reply_clamps_disposition():
    npc = NPC("Mara Ashdown", "human", "elder", "oakvale", "cheerful")
    reply = json.dumps({"reply": "Welcome!", "disposition_change": 50})
    result = narrator(FakeClient(reply)).npc_reply(SCENE, npc, "hello")
    assert result.text == "Mara Ashdown: Welcome!"
    assert result.disposition_change == 10


def test_history_is_bounded():
    client = FakeClient("one", "two", "three")
    dm = narrator(client)
    for _ in range(3):
        dm.describe_location(SCENE)
    assert len(client.calls[-1]["messages"]) == 1 + 2 + 1
