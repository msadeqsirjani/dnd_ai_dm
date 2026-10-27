import json
import re
from pathlib import Path

from models.character import Character
from models.world_state import WorldState

SAVE_VERSION = 1


class SaveError(Exception):
    pass


class SaveStore:
    def __init__(self, directory: Path):
        self.directory = directory

    def path(self, name: str) -> Path:
        slug = re.sub(r"[^a-z0-9_-]+", "-", name.lower()).strip("-") or "save"
        return self.directory / f"{slug}.json"

    def save(self, name: str, player: Character, world: WorldState) -> Path:
        path = self.path(name)
        self.directory.mkdir(parents=True, exist_ok=True)
        payload = {
            "version": SAVE_VERSION,
            "player": player.to_dict(),
            "world": world.to_dict(),
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path

    def load(self, name: str) -> tuple[Character, WorldState]:
        path = self.path(name)
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            raise SaveError(
                f"No saved game called '{name}' in {self.directory}."
            ) from None
        except json.JSONDecodeError as error:
            raise SaveError(f"Save file {path} is corrupted: {error}") from None
        if payload.get("version") != SAVE_VERSION:
            raise SaveError(
                f"Save file {path} has version {payload.get('version')}; "
                f"expected {SAVE_VERSION}."
            )
        return (
            Character.from_dict(payload["player"]),
            WorldState.from_dict(payload["world"]),
        )

    def names(self) -> list[str]:
        if not self.directory.is_dir():
            return []
        return sorted(path.stem for path in self.directory.glob("*.json"))
