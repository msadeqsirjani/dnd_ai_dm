import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_SAVE_DIR = "saves"
DEFAULT_HISTORY_TURNS = 8


@dataclass(frozen=True)
class Settings:
    openai_api_key: str | None
    model: str
    save_dir: Path
    history_turns: int
    seed: int | None


def load_settings(env: Mapping[str, str] = os.environ) -> Settings:
    seed = env.get("DND_SEED")
    return Settings(
        openai_api_key=env.get("OPENAI_API_KEY") or None,
        model=env.get("DND_MODEL") or DEFAULT_MODEL,
        save_dir=Path(env.get("DND_SAVE_DIR") or DEFAULT_SAVE_DIR),
        history_turns=int(env.get("DND_HISTORY_TURNS") or DEFAULT_HISTORY_TURNS),
        seed=int(seed) if seed else None,
    )
